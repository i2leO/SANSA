from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import Visit, Respondent, User
from app.schemas import VisitCreate, VisitResponse
from app.auth import get_current_staff_or_admin, get_current_user_optional

router = APIRouter(prefix="/visits", tags=["visits"])


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
        visit_date=visit_create.visit_date or datetime.utcnow(),
        visit_type=visit_create.visit_type,
        facility_id=visit_create.facility_id,
        entry_mode=visit_create.entry_mode,
        staff_id=current_user.id if current_user else None,
        notes=visit_create.notes,
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
