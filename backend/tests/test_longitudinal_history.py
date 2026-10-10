"""Longitudinal records remain children of one respondent and keep prior values."""
from datetime import date

from fastapi.testclient import TestClient

from app.database import Base
from app.models import BIARecord, Respondent, Visit
from app.routers.assessment_history import router as history_router
from app.routers.visits import router as visits_router
from tests.test_sansa_result_integration import fixture


def test_next_occurrence_keeps_one_respondent_and_timeline_compares_values():
    engine, db, app, first_visit, _, first_bia = fixture()
    Base.metadata.create_all(engine, tables=[Base.metadata.tables["mna_responses"]])
    app.include_router(visits_router)
    app.include_router(history_router)
    try:
        respondent_id = first_visit.respondent_id
        with TestClient(app) as client:
            response = client.post(
                f"/visits/respondent/{respondent_id}/next",
                json={"assessment_date": "2026-02-01", "visit_type": "follow_up"},
            )
            assert response.status_code == 200
            second_visit_id = response.json()["id"]
            assert response.json()["visit_number"] == 2
            assert db.query(Respondent).count() == 1
            assert db.query(Visit).filter_by(respondent_id=respondent_id).count() == 2

            db.add(BIARecord(
                visit_id=second_visit_id,
                weight_kg=65,
                bmi=23,
                waist_circumference_cm=82,
                body_fat_percentage=21,
            ))
            first_bia.weight_kg = 63
            db.commit()

            timeline = client.get(f"/assessment-history/respondent/{respondent_id}")
            assert timeline.status_code == 200
            occurrences = timeline.json()["occurrences"]
            assert [item["occurrence_number"] for item in occurrences] == [1, 2]
            weight_change = occurrences[1]["changes_from_previous"]["weight_kg"]
            assert weight_change == {
                "previous": 63.0,
                "current": 65.0,
                "difference": 2.0,
                "direction": "increased",
            }
    finally:
        db.close()
        engine.dispose()
