"""Focused checks for the three account roles."""
import asyncio
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import get_current_active_admin, get_current_staff_or_admin
from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate


class UserRoleTests(unittest.TestCase):
    def test_schema_accepts_three_roles(self):
        for role in ('user', 'staff', 'admin'):
            payload = UserCreate(username='synthetic', email='test@example.com', password='secret123', role=role)
            self.assertEqual(payload.role.value, role)
            self.assertEqual(UserUpdate(role=role).role.value, role)

    def test_database_enum_round_trip(self):
        engine = create_engine('sqlite:///:memory:')
        User.__table__.create(engine)
        with Session(engine) as db:
            db.add(User(username='synthetic', email='test@example.invalid', hashed_password='x', role=UserRole.USER))
            db.commit()
            self.assertEqual(db.query(User).one().role, UserRole.USER)
        engine.dispose()

    def test_user_cannot_use_staff_or_admin_permissions(self):
        user = User(role=UserRole.USER, is_active=True)
        for dependency in (get_current_staff_or_admin, get_current_active_admin):
            with self.assertRaises(HTTPException) as context:
                asyncio.run(dependency(user))
            self.assertEqual(context.exception.status_code, 403)

    def test_staff_and_admin_permissions(self):
        staff = User(role=UserRole.STAFF, is_active=True)
        admin = User(role=UserRole.ADMIN, is_active=True)
        self.assertIs(asyncio.run(get_current_staff_or_admin(staff)), staff)
        self.assertIs(asyncio.run(get_current_staff_or_admin(admin)), admin)
        self.assertIs(asyncio.run(get_current_active_admin(admin)), admin)
