from fastapi.testclient import TestClient
from app.models import AssessmentRevision, BIARecord
from app.routers.bia import router
from tests.test_sansa_result_integration import fixture


def test_staff_updates_waist_record_and_clearing_measurements_clears_derived_bmi():
    engine, db, app, visit, _, bia = fixture()
    app.include_router(router)
    try:
        with TestClient(app) as client:
            response = client.put(f'/bia/{bia.id}', json={'weight_kg': 64, 'height_cm': 160, 'mac_cm': 22, 'cc_cm': 31})
            assert response.status_code == 200
            assert float(response.json()['bmi']) == 25
            assert float(response.json()['waist_circumference_cm']) == 80
            reloaded = client.get(f'/bia/visit/{visit.id}').json()
            assert reloaded['id'] == bia.id
            assert float(reloaded['cc_cm']) == 31
            assert db.query(BIARecord).count() == 1
            revisions = db.query(AssessmentRevision).filter_by(
                instrument="BIA", record_id=bia.id
            ).order_by(AssessmentRevision.revision_number).all()
            assert [item.action_type for item in revisions] == ["baseline", "update"]
            assert float(revisions[0].snapshot['weight_kg'] or 0) == 0
            assert float(revisions[1].snapshot['weight_kg']) == 64
            response = client.put(f'/bia/{bia.id}', json={'weight_kg': None})
            assert response.status_code == 200
            assert response.json()['bmi'] is None
            assert response.json()['bmi_category'] is None
            assert float(response.json()['height_cm']) == 160
            assert db.query(AssessmentRevision).filter_by(
                instrument="BIA", record_id=bia.id
            ).count() == 3
            assert client.delete(f'/bia/{bia.id}').status_code == 409
            assert client.put(f'/bia/{bia.id}', json={'height_cm': 0}).status_code == 422
    finally:
        db.close()
        engine.dispose()
