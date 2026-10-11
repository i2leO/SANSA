"""Longitudinal assessment occurrences and immutable revision history."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_staff_or_admin
from app.database import get_db
from app.models import AssessmentRevision, BIARecord, MNAResponse, Respondent, User, Visit

router = APIRouter(prefix="/assessment-history", tags=["assessment-history"])


def _number(value):
    return None if value is None else float(value)


def _change(current, previous):
    if current is None or previous is None:
        return {"previous": previous, "current": current, "difference": None, "direction": "unknown"}
    difference = current - previous
    return {
        "previous": previous,
        "current": current,
        "difference": difference,
        "direction": "increased" if difference > 0 else "decreased" if difference < 0 else "unchanged",
    }


@router.get("/respondent/{respondent_id}")
def respondent_timeline(
    respondent_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_or_admin),
):
    respondent = db.query(Respondent).filter_by(id=respondent_id, is_deleted=False).first()
    if respondent is None:
        raise HTTPException(status_code=404, detail="Respondent not found")
    visits = db.query(Visit).filter_by(respondent_id=respondent_id, is_deleted=False).order_by(
        Visit.visit_number.asc(), Visit.id.asc()
    ).all()
    result = []
    previous = None
    for visit in visits:
        mna = db.query(MNAResponse).filter_by(visit_id=visit.id).first()
        bia = db.query(BIARecord).filter_by(visit_id=visit.id).first()
        current = {
            "mna_total": _number(mna.mna_total) if mna else None,
            "weight_kg": _number(bia.weight_kg) if bia else None,
            "bmi": _number(bia.bmi) if bia else None,
            "waist_circumference_cm": _number(bia.waist_circumference_cm) if bia else None,
            "body_fat_percentage": _number(bia.body_fat_percentage) if bia else None,
            "muscle_mass_kg": _number(bia.muscle_mass_kg) if bia else None,
        }
        result.append({
            "occurrence_id": visit.id,
            "occurrence_number": visit.visit_number,
            "assessment_date": visit.visit_date,
            "visit_type": visit.visit_type,
            "mna_id": mna.id if mna else None,
            "mna_result": mna.result_category if mna else None,
            "bia_id": bia.id if bia else None,
            "values": current,
            "changes_from_previous": {
                key: _change(value, previous.get(key) if previous else None)
                for key, value in current.items()
            },
        })
        previous = current
    return {"respondent_id": respondent.id, "respondent_code": respondent.respondent_code, "occurrences": result}


@router.get("/visit/{visit_id}/revisions")
def visit_revisions(
    visit_id: int,
    instrument: str | None = Query(None, pattern="^(SANSA|MNA|BIA)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_or_admin),
):
    query = db.query(AssessmentRevision).filter_by(visit_id=visit_id)
    if instrument:
        query = query.filter_by(instrument=instrument)
    rows = query.order_by(AssessmentRevision.instrument, AssessmentRevision.revision_number).all()
    return [{
        "id": row.id,
        "respondent_id": row.respondent_id,
        "visit_id": row.visit_id,
        "instrument": row.instrument,
        "record_id": row.record_id,
        "revision_number": row.revision_number,
        "action_type": row.action_type,
        "snapshot": row.snapshot,
        "changed_by": row.changed_by,
        "change_reason": row.change_reason,
        "is_current": row.is_current,
        "recorded_at": row.recorded_at,
    } for row in rows]
