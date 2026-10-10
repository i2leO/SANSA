"""Append-only research audit snapshots for repeatable MNA/BIA writes."""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import func

from app.models import AssessmentRevision, Visit


def _json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value


def model_snapshot(record):
    return {column.name: _json_value(getattr(record, column.name)) for column in record.__table__.columns}


def append_assessment_revision(db, instrument, record, actor=None, action_type="update", change_reason=None):
    visit = db.query(Visit).filter(Visit.id == record.visit_id).one()
    current = (
        db.query(AssessmentRevision)
        .filter_by(instrument=instrument, record_id=record.id, is_current=True)
        .all()
    )
    for revision in current:
        revision.is_current = False
    number = (
        db.query(func.max(AssessmentRevision.revision_number))
        .filter_by(instrument=instrument, record_id=record.id)
        .scalar()
        or 0
    ) + 1
    revision = AssessmentRevision(
        respondent_id=visit.respondent_id,
        visit_id=visit.id,
        instrument=instrument,
        record_id=record.id,
        revision_number=number,
        action_type=action_type,
        snapshot=model_snapshot(record),
        changed_by=getattr(actor, "id", None),
        change_reason=change_reason,
        is_current=True,
    )
    db.add(revision)
    return revision


def ensure_assessment_baseline(db, instrument, record):
    exists = db.query(AssessmentRevision.id).filter_by(
        instrument=instrument, record_id=record.id
    ).first()
    if exists is None:
        return append_assessment_revision(db, instrument, record, action_type="baseline")
    return None
