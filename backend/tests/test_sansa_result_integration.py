"""Focused API/ORM tests against isolated synthetic SQLite data."""
from datetime import date
from decimal import Decimal
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.models import Respondent, Visit, SANSAResponse, BIARecord, ScoringRuleVersion, SANSAPredictionResult
from app.routers.sansa import router
from app.auth import get_current_staff_or_admin
from app.services.sansa_definition import DB_SCORING_VERSION
from app.services.scoring_service import ScoringService


def fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    event.listen(engine, "connect", lambda con, _: con.execute("PRAGMA foreign_keys=ON"))
    tables = [Base.metadata.tables[n] for n in ("users", "facilities", "source_import_batches", "respondents", "visits",
              "scoring_rule_versions", "sansa_responses", "bia_records", "sansa_prediction_results",
              "assessment_revisions")]
    Base.metadata.create_all(engine, tables=tables)
    db = Session(engine)
    respondent = Respondent(respondent_code="SYNTHETIC-INTEGRATION", age=69, sex="male")
    version = ScoringRuleVersion(
        instrument_name="SANSA", version_number=DB_SCORING_VERSION, is_active=True
    )
    db.add_all([respondent, version]); db.flush()
    visit = Visit(respondent_id=respondent.id, visit_number=1, visit_date=date(2026, 1, 1))
    db.add(visit); db.flush()
    answers = {
        "q1_weight_change": "stable", "q2_food_intake": "normal",
        "q3_daily_activities": "normal", "q4_chronic_disease": "yes",
        "q5_meals_per_day": "3", "q6_portion_size": "100",
        "q7_food_texture": "normal", "q8_rice_starch": "7-9",
        "q9_protein": "3-5", "q10_milk": "1", "q11_fruits": "3-5",
        "q12_vegetables": "2-3", "q13_water": "7-8",
        "q14_sweet_drinks": "1", "q15_cooking_method": "stir_fry",
        "q16_oil_coconut": "5-6",
    }
    transient = type("Answers", (), answers)()
    scores = ScoringService(None).calculate_sansa_scores(transient, version_id=version.id)
    sansa = SANSAResponse(visit_id=visit.id, **answers, **scores)
    bia = BIARecord(visit_id=visit.id, age=85, sex="female", waist_circumference_cm=80,
                    bmi=22, body_fat_percentage=20)
    db.add_all([sansa, bia]); db.commit()
    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_staff_or_admin] = lambda: object()
    return engine, db, app, visit, sansa, bia


class ResultIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.db, self.app, self.visit, self.sansa, self.bia = fixture()
        self.client = TestClient(self.app)
        self.url = f"/sansa/visit/{self.visit.id}"

    def tearDown(self):
        self.client.close(); self.db.close(); self.engine.dispose()

    def test_get_result_uses_respondent_and_selected_bia_without_writes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        payload = response.json(); revised = payload["revised"]
        self.assertIsNone(payload["result_level"])
        self.assertTrue(revised["verified_024"])
        self.assertEqual([Decimal(v) for v in revised["domain_scores"].values()], [6, 12, 6])
        self.assertEqual(revised["prediction"]["age_group01"], 0)
        self.assertEqual(Decimal(revised["prediction"]["waist_cm"]), 80)
        self.assertEqual(revised["bia_record_id"], self.bia.id)
        self.assertEqual(revised["prediction"]["predicted_group"], "NORMAL")
        self.assertEqual(revised["reference"]["nutrition_reference"], "NORMAL")
        self.assertTrue(revised["comparison"]["matches"])
        self.assertEqual(self.db.query(SANSAPredictionResult).count(), 0)

    def test_save_and_update_api_persists_computed_values(self):
        first = self.client.post(self.url + "/prediction")
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()["saved"])
        saved = self.db.query(SANSAPredictionResult).one(); identity = saved.id
        self.assertEqual(saved.l_over, Decimal("2.261"))
        self.bia.waist_circumference_cm = 100; self.db.commit()
        second = self.client.post(self.url + "/prediction")
        self.assertEqual(second.status_code, 200)
        self.db.expire_all()
        saved = self.db.query(SANSAPredictionResult).one()
        self.assertEqual(saved.id, identity)
        self.assertEqual(saved.predicted_group, "OVER")
        self.assertFalse(second.json()["comparison"]["matches"])
        self.assertEqual(self.sansa.total_score, 34)
        self.assertEqual(self.bia.bmi, 22)

    def test_missing_bia_and_no_fabricated_prediction(self):
        self.db.delete(self.bia); self.db.commit()
        revised = self.client.get(self.url).json()["revised"]
        self.assertIsNone(revised["prediction"])
        self.assertIn("missing_bia", revised["issues"])
        self.assertIsNotNone(revised["domain_scores"])
        self.assertEqual(self.client.post(self.url + "/prediction").status_code, 422)

    def test_second_bia_for_same_occurrence_is_rejected(self):
        self.db.add(BIARecord(visit_id=self.visit.id, waist_circumference_cm=100))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()
        self.assertEqual(self.db.query(BIARecord).filter_by(visit_id=self.visit.id).count(), 1)

    def test_missing_inputs_and_unsupported_sex(self):
        self.bia.waist_circumference_cm = None; self.db.commit()
        revised = self.client.get(self.url).json()["revised"]
        self.assertIn("missing_waist", revised["issues"])
        self.assertIsNotNone(revised["reference"])
        self.bia.waist_circumference_cm = 80
        self.visit.respondent.sex = "other"; self.db.commit()
        revised = self.client.get(self.url).json()["revised"]
        self.assertIsNotNone(revised["prediction"])
        self.assertIsNone(revised["reference"])
        self.assertIn("invalid_reference_inputs", revised["issues"])
        self.sansa.q8_score = None; self.db.commit()
        self.assertIn("score_definition_mismatch", self.client.get(self.url).json()["revised"]["issues"])

    def test_missing_recorded_score_blocks_unverified_prediction(self):
        self.sansa.q5_score = None; self.db.commit()
        revised = self.client.get(self.url).json()["revised"]
        self.assertIsNone(revised["domain_scores"])
        self.assertIn("score_definition_mismatch", revised["issues"])
        self.assertIsNone(revised["prediction"])
        saved = self.client.post(self.url + "/prediction")
        self.assertEqual(saved.status_code, 422)
        self.assertEqual(self.db.query(SANSAPredictionResult).count(), 0)

    def test_missing_raw_answers_are_reported_and_not_treated_as_verified_024(self):
        self.sansa.q1_weight_change = None; self.db.commit()
        revised = self.client.get(self.url).json()["revised"]
        self.assertFalse(revised["verified_024"])
        self.assertIn("missing_raw_answers", revised["issues"])
        self.assertIn("q1_weight_change", revised["missing_answer_fields"])
        self.assertIsNone(revised["domain_scores"])
        self.assertIsNone(revised["prediction"])

    def test_missing_migration_keeps_read_available_save_reports_failure(self):
        SANSAPredictionResult.__table__.drop(self.engine)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.client.post(self.url + "/prediction").status_code, 503)

    def test_rescore_preview_uses_approved_definition_without_writing(self):
        answers = {
            "q1_weight_change": "increase", "q2_food_intake": "increase",
            "q3_daily_activities": "slower", "q4_chronic_disease": "no",
            "q5_meals_per_day": "3", "q6_portion_size": "100",
            "q7_food_texture": "normal", "q8_rice_starch": "4-6",
            "q9_protein": "1-2", "q10_milk": "1", "q11_fruits": "1-2",
            "q12_vegetables": "0-1", "q13_water": "4-6",
            "q14_sweet_drinks": "1", "q15_cooking_method": "stir_fry",
            "q16_oil_coconut": "5-6",
        }
        for field, value in answers.items():
            setattr(self.sansa, field, value)
        recorded_before = [getattr(self.sansa, f"q{i}_score") for i in range(1, 17)]
        self.db.commit()

        result = self.client.get(self.url + "/rescore-preview")
        self.assertEqual(result.status_code, 200)
        payload = result.json()
        self.assertFalse(payload["writes_performed"])
        self.assertTrue(payload["database_version_active"])
        self.assertEqual(payload["changed_item_count"], 9)
        self.assertEqual(payload["domains"], {
            "d1_total": 6, "d2_total": 2, "d3_total": 6
        })
        self.assertEqual(payload["prediction"]["predicted_group"], "NORMAL")
        self.db.expire_all()
        self.assertEqual(
            [getattr(self.sansa, f"q{i}_score") for i in range(1, 17)], recorded_before
        )

    def test_deleted_visit_and_unknown_visit(self):
        self.assertEqual(self.client.get("/sansa/visit/999999").status_code, 404)
        self.visit.is_deleted = True; self.db.commit()
        self.assertEqual(self.client.get(self.url).status_code, 404)
