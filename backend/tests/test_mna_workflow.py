"""Staff form contract and writes, isolated in-memory synthetic database."""
import csv
import io

from fastapi import Depends
from fastapi.testclient import TestClient
from app.auth import get_current_staff_or_admin
from app.database import Base
from app.models import AssessmentRevision, MNAResponse, ScoringRuleVersion
from app.routers.mna import router
from app.services.export_service import ExportService
from tests.test_sansa_result_integration import fixture


def test_definition_create_reject_incomplete_and_update_same_record():
    engine, db, app, visit, _, _ = fixture()
    Base.metadata.create_all(engine, tables=[Base.metadata.tables["mna_responses"]])
    db.add(ScoringRuleVersion(instrument_name='MNA', version_number='test', is_active=True))
    db.commit()
    app.include_router(router, dependencies=[Depends(get_current_staff_or_admin)])
    try:
        with TestClient(app) as client:
            definition = client.get('/mna/definition')
            assert definition.status_code == 200
            items = definition.json()['items']
            assert ''.join(item['letter'] for item in items) == 'ABCDEFGHIJKLMNOPQR'
            payload = {item['field']: max(item['options'], key=lambda option: float(option['score']))['value'] for item in items}
            assert client.post('/mna', json={'visit_id': visit.id}).status_code == 400
            assert db.query(MNAResponse).count() == 0
            response = client.post('/mna', json={'visit_id': visit.id, **payload})
            assert response.status_code == 200
            identity = response.json()['id']
            assert float(response.json()['mna_total']) == 30
            assert response.json()['q19_calf_circumference_assess'] == '>=31'
            assert float(response.json()['mna_a12']) == 1
            assert response.json()['mna_s7'] is None
            # Explicit edits are saved to the same assessment, never POSTed again.
            response = client.put(f'/mna/{identity}', json={'q1_food_intake_decline': 'moderate'})
            assert response.status_code == 200
            assert float(response.json()['mna_total']) == 29
            reloaded = client.get(f'/mna/visit/{visit.id}').json()
            assert reloaded['id'] == identity
            assert reloaded['q1_food_intake_decline'] == 'moderate'
            assert db.query(MNAResponse).count() == 1
            revisions = db.query(AssessmentRevision).filter_by(
                instrument="MNA", record_id=identity
            ).order_by(AssessmentRevision.revision_number).all()
            assert [item.action_type for item in revisions] == ["create", "update"]
            assert revisions[0].snapshot['q1_food_intake_decline'] == payload['q1_food_intake_decline']
            assert revisions[1].snapshot['q1_food_intake_decline'] == 'moderate'
            assert revisions[0].is_current is False
            assert revisions[1].is_current is True
            # R contributes to assessment only; editing it must not alter A-F.
            response = client.put(f'/mna/{identity}', json={'q19_calf_circumference_assess': '<31'})
            assert response.status_code == 200
            assert float(response.json()['mna_a12']) == 0
            assert float(response.json()['mna_screen_total']) == 13
            assert float(response.json()['mna_total']) == 28
            assert db.query(AssessmentRevision).filter_by(
                instrument="MNA", record_id=identity
            ).count() == 3
            history_rows = list(csv.DictReader(io.StringIO(ExportService(db).export_assessment_history_csv())))
            r_score_rows = [item for item in history_rows if item['instrument'] == 'MNA' and item['field'] == 'mna_a12']
            assert len(r_score_rows) == 3
            assert r_score_rows[-1]['value_json'] == '"0"'
            row = next(csv.DictReader(io.StringIO(ExportService(db).export_bia_mna_csv())))
            assert float(row['mna_a12']) == 0
            assert float(row['mna_total']) == 28
            response = client.put(f'/mna/{identity}', json={'q1_food_intake_decline': None})
            assert response.status_code == 400
            db.expire_all()
            assert db.query(MNAResponse).one().q1_food_intake_decline == 'moderate'
            # A legacy row with a SANSA version must not be silently rewritten.
            record = db.query(MNAResponse).one()
            original_version = record.scoring_version_id
            wrong_version = ScoringRuleVersion(instrument_name='SANSA', version_number='legacy', is_active=True)
            db.add(wrong_version)
            db.flush()
            record.scoring_version_id = wrong_version.id
            db.commit()
            assert client.put(f'/mna/{identity}', json={'q1_food_intake_decline': 'none'}).status_code == 409
            db.expire_all()
            assert db.query(MNAResponse).one().q1_food_intake_decline == 'moderate'
            assert original_version != wrong_version.id
    finally:
        db.close()
        engine.dispose()


def test_bia_suggestions_boundaries_missing_and_read_only():
    from types import SimpleNamespace
    from app.services.mna_definition import answers_from_bia
    for bmi, expected in [(18.9, '<19'), (19, '19-21'), (21, '21-23'), (23, '>23')]:
        assert answers_from_bia(SimpleNamespace(bmi=bmi, mac_cm=None, cc_cm=None)) == {'q6_bmi': expected}
    for mac, expected in [(20.9, '<21'), (21, '21-22'), (22, '21-22'), (22.1, '>22')]:
        assert answers_from_bia(SimpleNamespace(bmi=None, mac_cm=mac, cc_cm=None)) == {'q18_mid_arm_circumference': expected}
    assert answers_from_bia(SimpleNamespace(bmi=None, mac_cm=None, cc_cm=31)) == {'q19_calf_circumference_assess': '>=31'}
    assert answers_from_bia(SimpleNamespace(bmi=None, mac_cm=None, cc_cm=30.9)) == {'q19_calf_circumference_assess': '<31'}
    assert answers_from_bia(SimpleNamespace(bmi=0, mac_cm=None, cc_cm=None)) == {}
    engine, db, app, visit, _, bia = fixture()
    Base.metadata.create_all(engine, tables=[Base.metadata.tables['mna_responses']])
    app.include_router(router, dependencies=[Depends(get_current_staff_or_admin)])
    try:
        bia.bmi, bia.mac_cm, bia.cc_cm = 23, 22, 31
        db.commit()
        with TestClient(app) as client:
            response = client.get(f'/mna/visit/{visit.id}/bia-suggestions')
            assert response.status_code == 200
            assert response.json()['answers'] == {'q6_bmi': '>23', 'q18_mid_arm_circumference': '21-22', 'q19_calf_circumference_assess': '>=31'}
            assert db.query(MNAResponse).count() == 0
    finally:
        db.close()
        engine.dispose()


def test_export_level_is_not_mass():
    import csv
    import io
    from app.services.export_service import ExportService
    engine, db, _, _, _, bia = fixture()
    Base.metadata.create_all(engine, tables=[Base.metadata.tables['mna_responses']])
    try:
        bia.visceral_fat_level = 7
        bia.visceral_fat_kg = 2
        db.commit()
        row = next(csv.DictReader(io.StringIO(ExportService(db).export_bia_mna_csv())))
        assert float(row['vfat_level']) == 7
    finally:
        db.close()
        engine.dispose()
