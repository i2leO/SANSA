"""Focused edit coverage for the food diary API using synthetic SQLite data."""
from datetime import date
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import FoodDiaryEntry, Respondent, Visit
from app.routers.food_diary import router


class FoodDiaryUpdateTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        tables = [Base.metadata.tables[name] for name in (
            "users", "facilities", "respondents", "visits",
            "food_diary_entries", "food_diary_photos",
        )]
        Base.metadata.create_all(self.engine, tables=tables)
        self.db = Session(self.engine)
        respondent = Respondent(respondent_code="FOOD-DIARY-SYNTHETIC")
        self.db.add(respondent); self.db.flush()
        visit = Visit(respondent_id=respondent.id, visit_number=1, visit_date=date.today())
        self.db.add(visit); self.db.flush()
        self.entry = FoodDiaryEntry(
            visit_id=visit.id, entry_date=date.today(), meal_type="breakfast",
            menu_name="ข้าวต้ม", portion_description="1 ชาม",
        )
        self.db.add(self.entry); self.db.commit()
        app = FastAPI(); app.include_router(router)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close(); self.db.close(); self.engine.dispose()

    def test_update_changes_requested_fields_and_preserves_identity(self):
        response = self.client.put(
            f"/food-diary/{self.entry.id}",
            json={"menu_name": "โจ๊กปลา", "portion_description": "2 ถ้วย"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.entry.id)
        self.assertEqual(response.json()["menu_name"], "โจ๊กปลา")
        self.assertEqual(response.json()["meal_type"], "breakfast")

    def test_update_rejects_empty_menu_name(self):
        response = self.client.put(
            f"/food-diary/{self.entry.id}", json={"menu_name": "   "}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
