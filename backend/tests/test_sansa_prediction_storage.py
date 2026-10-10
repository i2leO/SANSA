"""Run with DATABASE_URL=sqlite:// and DEBUG=False; never uses a real database."""

import importlib.util
from datetime import date
from decimal import Decimal
from pathlib import Path
import unittest

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, Respondent, Visit, SANSAPredictionResult
from app.services.sansa_prediction_service import MODEL_VERSION
from app.services.sansa_prediction_storage import save_sansa_prediction


class PredictionStorageTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        event.listen(self.engine, "connect", lambda con, _: con.execute("PRAGMA foreign_keys=ON"))
        # Only the existing parent tables and their required FK targets are fixtures.
        parent_names = ("users", "facilities", "source_import_batches", "respondents", "visits")
        Base.metadata.create_all(self.engine, tables=[Base.metadata.tables[n] for n in parent_names])
        path = Path(__file__).resolve().parents[1] / "alembic/versions/20260912_01_sansa_prediction_results.py"
        spec = importlib.util.spec_from_file_location("prediction_revision", path)
        self.migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.migration)
        with self.engine.begin() as connection:
            with Operations.context(MigrationContext.configure(connection)):
                self.migration.upgrade()
        self.db = Session(self.engine)
        respondent = Respondent(respondent_code="SYNTHETIC-TASK4", age=69)
        self.db.add(respondent)
        self.db.flush()
        self.visit = Visit(respondent_id=respondent.id, visit_number=1, visit_date=date(2026, 1, 1))
        self.db.add(self.visit)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def save(self, **overrides):
        params = dict(d2_total=6, d3_total=3, waist_cm=80, age_group01=0)
        params.update(overrides)
        return save_sansa_prediction(self.db, self.visit.id, **params)

    def test_store_relationship_and_probability_roundtrip(self):
        result = self.save()
        result_id = result.id
        self.db.commit()
        self.db.expire_all()
        saved = self.db.get(SANSAPredictionResult, result_id)
        self.assertEqual(saved.visit.id, self.visit.id)
        self.assertIn(saved, self.visit.prediction_results)
        self.assertEqual(saved.model_version, MODEL_VERSION)
        self.assertEqual(saved.predicted_group, "NORMAL")
        self.assertEqual(saved.d2_total, Decimal("6"))
        self.assertEqual(saved.l_over, Decimal("3.278"))
        self.assertEqual(saved.l_normal, Decimal("4.178"))
        self.assertAlmostEqual(saved.p_under + saved.p_normal + saved.p_over, Decimal("1"), places=14)
        self.assertGreater(saved.p_normal, saved.p_over)
        self.assertIsNotNone(saved.created_at)
        self.assertIsNotNone(saved.updated_at)

    def test_upsert_reuses_row(self):
        first = self.save()
        identity, created = first.id, first.created_at
        self.db.commit()
        updated = self.save(waist_cm=100)
        self.db.commit()
        self.assertEqual(updated.id, identity)
        self.assertEqual(updated.created_at, created)
        self.assertEqual(updated.waist_cm, Decimal("100"))
        self.assertEqual(updated.predicted_group, "OVER")
        self.assertEqual(self.db.query(SANSAPredictionResult).count(), 1)

    def test_unique_constraint_and_distinct_versions(self):
        original = self.save()
        self.db.commit()
        values = {c.name: getattr(original, c.name) for c in original.__table__.columns if c.name != "id"}
        self.db.add(SANSAPredictionResult(**values))
        with self.assertRaises(IntegrityError):
            self.db.flush()
        self.db.rollback()
        values["model_version"] = "SYNTHETIC-OTHER-VERSION"
        self.db.add(SANSAPredictionResult(**values))
        self.db.commit()
        self.assertEqual(self.db.query(SANSAPredictionResult).count(), 2)

    def test_visit_foreign_key_and_category_constraint(self):
        original = self.save()
        self.db.commit()
        with self.assertRaises(IntegrityError):
            self.db.execute(text("UPDATE sansa_prediction_results SET visit_id=999999 WHERE id=:id"), {"id": original.id})
        self.db.rollback()
        with self.assertRaises(IntegrityError):
            self.db.execute(text("UPDATE sansa_prediction_results SET predicted_group='UNKNOWN'"))
        self.db.rollback()

    def test_precision_and_missing_visit_rejected(self):
        with self.assertRaises(ValueError):
            self.save(waist_cm=Decimal("80.12345"))
        with self.assertRaisesRegex(ValueError, "Visit not found"):
            save_sansa_prediction(self.db, 999999, d2_total=6, d3_total=3, waist_cm=80, age_group01=0)

    def test_migration_downgrade_only_removes_prediction_table(self):
        self.db.close()
        with self.engine.begin() as connection:
            with Operations.context(MigrationContext.configure(connection)):
                self.migration.downgrade()
        names = inspect(self.engine).get_table_names()
        self.assertNotIn("sansa_prediction_results", names)
        self.assertIn("visits", names)
