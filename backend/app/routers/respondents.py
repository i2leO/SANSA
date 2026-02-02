from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import random
import string
from app.database import get_db
from app.models import Respondent, User
from app.schemas import (
    RespondentCreate,
    RespondentUpdate,
    RespondentResponse,
    MessageResponse,
)
from app.auth import get_current_staff_or_admin, get_current_user_optional

router = APIRouter(prefix="/respondents", tags=["respondents"])


def generate_respondent_code() -> str:
    """Generate a random anonymous respondent code"""
    # Format: RES + 8 random alphanumeric characters
    return "RES" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


@router.post("", response_model=RespondentResponse)
async def create_respondent(
    respondent_create: RespondentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Create a new respondent
    Can be called by staff/admin (requires auth) or anonymously (no auth)
    """
    # Generate code if not provided
    if not respondent_create.respondent_code:
        while True:
            code = generate_respondent_code()
            # Check if code exists
            existing = (
                db.query(Respondent).filter(Respondent.respondent_code == code).first()
            )
            if not existing:
                respondent_create.respondent_code = code
                break
    else:
        # Check if provided code already exists
        existing = (
            db.query(Respondent)
            .filter(Respondent.respondent_code == respondent_create.respondent_code)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Respondent code already exists"
            )

    new_respondent = Respondent(
        **respondent_create.dict(), created_by=current_user.id if current_user else None
    )

    db.add(new_respondent)
    db.commit()
    db.refresh(new_respondent)

    return new_respondent


@router.get("/{respondent_code}", response_model=RespondentResponse)
def get_respondent_by_code(respondent_code: str, db: Session = Depends(get_db)):
    """Get respondent by code (no auth required for self-service)"""
    respondent = (
        db.query(Respondent)
        .filter(
            Respondent.respondent_code == respondent_code,
            Respondent.is_deleted == False,
        )
        .first()
    )

    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    return respondent


@router.get("", response_model=list[RespondentResponse])
def list_respondents(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """List respondents (staff/admin only)"""
    query = db.query(Respondent).filter(Respondent.is_deleted == False)

    if search:
        query = query.filter(
            (Respondent.respondent_code.contains(search))
            | (Respondent.phone.contains(search))
            | (Respondent.email.contains(search))
        )

    respondents = query.offset(skip).limit(limit).all()
    return respondents


@router.put("/{respondent_id}", response_model=RespondentResponse)
async def update_respondent(
    respondent_id: int,
    respondent_update: RespondentUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Update respondent (staff/admin or self-update)"""
    respondent = (
        db.query(Respondent)
        .filter(Respondent.id == respondent_id, Respondent.is_deleted == False)
        .first()
    )

    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    update_data = respondent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(respondent, field, value)

    db.commit()
    db.refresh(respondent)

    return respondent


@router.delete("/{respondent_id}", response_model=MessageResponse)
def delete_respondent(
    respondent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Soft delete respondent (staff/admin only)"""
    respondent = db.query(Respondent).filter(Respondent.id == respondent_id).first()

    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    respondent.is_deleted = True
    db.commit()

    return {"message": "Respondent deleted successfully"}


@router.post("/check-code")
def check_respondent_code(request: dict, db: Session = Depends(get_db)):
    """Check if respondent code exists (for login/registration flow)"""
    code = request.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")

    respondent = (
        db.query(Respondent)
        .filter(Respondent.respondent_code == code, Respondent.is_deleted == False)
        .first()
    )

    return {
        "exists": respondent is not None,
        "respondent_id": respondent.id if respondent else None,
    }
