from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import func
from app.database import get_db
from app.models import Visit, Respondent, User, VisitType
from app.schemas import VisitCreate, VisitResponse
from app.auth import get_current_staff_or_admin, get_current_user_optional

router = APIRouter(prefix="/visits", tags=["visits"])


class NextAssessmentOccurrence(BaseModel):
    assessment_date: Optional[date] = None
    visit_type: VisitType = VisitType.FOLLOW_UP
    notes: Optional[str] = None


@router.post("", response_model=VisitResponse)
async def create_visit(
    visit_create: VisitCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Create a new visit for a respondent
    Can be created by respondent (no auth) or staff/admin (with auth)
    """
    # Verify respondent exists
    respondent = (
        db.query(Respondent)
        .filter(
            Respondent.id == visit_create.respondent_id, Respondent.is_deleted == False
        )
        .first()
    )

    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    # Create visit
    new_visit = Visit(
        respondent_id=visit_create.respondent_id,
        visit_number=visit_create.visit_number,
        visit_date=visit_create.visit_date,
        visit_time=visit_create.visit_time,
        visit_type=visit_create.visit_type,
        facility_id=visit_create.facility_id,
        notes=visit_create.notes,
        created_by=current_user.id if current_user else None,
    )

    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)

    return new_visit


@router.get("/{visit_id}", response_model=VisitResponse)
def get_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get visit by ID"""
    visit = db.query(Visit).filter(Visit.id == visit_id).first()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    return visit


@router.get("/respondent/{respondent_id}", response_model=list[VisitResponse])
def get_respondent_visits(respondent_id: int, db: Session = Depends(get_db)):
    """Get all visits for a respondent"""
    visits = (
        db.query(Visit)
        .filter(Visit.respondent_id == respondent_id)
        .order_by(Visit.visit_date.desc())
        .all()
    )

    return visits


@router.get("", response_model=list[VisitResponse])
def list_visits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """List all visits (staff/admin only)"""
    visits = (
        db.query(Visit)
        .order_by(Visit.visit_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return visits


@router.post("/respondent/{respondent_id}/next", response_model=VisitResponse)
def create_next_assessment_occurrence(
    respondent_id: int,
    payload: NextAssessmentOccurrence,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    respondent = db.query(Respondent).filter_by(id=respondent_id, is_deleted=False).first()
    if respondent is None:
        raise HTTPException(status_code=404, detail="Respondent not found")
    next_number = (db.query(func.max(Visit.visit_number)).filter_by(respondent_id=respondent_id).scalar() or 0) + 1
    occurrence = Visit(
        respondent_id=respondent_id,
        visit_number=next_number,
        visit_date=payload.assessment_date or date.today(),
        visit_type=payload.visit_type,
        notes=payload.notes,
        created_by=getattr(current_user, "id", None),
    )
    db.add(occurrence)
    db.commit()
    db.refresh(occurrence)
    return occurrence
