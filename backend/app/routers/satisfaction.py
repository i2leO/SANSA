from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import SatisfactionResponse, Visit, User
from app.schemas import (
    SatisfactionResponseCreate,
    SatisfactionResponseUpdate,
    SatisfactionResponseFull,
    MessageResponse,
)
from app.auth import get_current_staff_or_admin
from typing import Optional

router = APIRouter(prefix="/satisfaction", tags=["satisfaction"])


@router.post("", response_model=SatisfactionResponseFull)
def create_satisfaction_response(
    satisfaction_create: SatisfactionResponseCreate, db: Session = Depends(get_db)
):
    """
    Create satisfaction survey response
    Can be submitted by respondent (no auth) or staff (with auth)
    """
    # Verify visit exists
    visit = db.query(Visit).filter(Visit.id == satisfaction_create.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Check if satisfaction already exists for this visit
    existing = (
        db.query(SatisfactionResponse)
        .filter(SatisfactionResponse.visit_id == satisfaction_create.visit_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Satisfaction response already exists for this visit",
        )

    # Create response with all 7 Likert questions
    satisfaction_response = SatisfactionResponse(
        visit_id=satisfaction_create.visit_id,
        q1_clarity=satisfaction_create.q1_clarity,
        q2_ease_of_use=satisfaction_create.q2_ease_of_use,
        q3_confidence=satisfaction_create.q3_confidence,
        q4_presentation=satisfaction_create.q4_presentation,
        q5_results_display=satisfaction_create.q5_results_display,
        q6_usefulness=satisfaction_create.q6_usefulness,
        q7_overall_satisfaction=satisfaction_create.q7_overall_satisfaction,
        comments=satisfaction_create.comments,
        completed_at=datetime.utcnow(),
    )

    db.add(satisfaction_response)
    db.commit()
    db.refresh(satisfaction_response)

    return satisfaction_response


@router.get("/{satisfaction_response_id}", response_model=SatisfactionResponseFull)
def get_satisfaction_response(
    satisfaction_response_id: int, db: Session = Depends(get_db)
):
    """Get satisfaction response by ID"""
    satisfaction_response = (
        db.query(SatisfactionResponse)
        .filter(SatisfactionResponse.id == satisfaction_response_id)
        .first()
    )

    if not satisfaction_response:
        raise HTTPException(status_code=404, detail="Satisfaction response not found")

    return satisfaction_response


@router.get("/visit/{visit_id}", response_model=SatisfactionResponseFull)
def get_satisfaction_by_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get satisfaction response by visit ID"""
    satisfaction_response = (
        db.query(SatisfactionResponse)
        .filter(SatisfactionResponse.visit_id == visit_id)
        .first()
    )

    if not satisfaction_response:
        raise HTTPException(
            status_code=404, detail="Satisfaction response not found for this visit"
        )

    return satisfaction_response


@router.put("/{satisfaction_response_id}", response_model=SatisfactionResponseFull)
def update_satisfaction_response(
    satisfaction_response_id: int,
    satisfaction_update: SatisfactionResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Update existing satisfaction response (staff/admin only)"""
    satisfaction_response = (
        db.query(SatisfactionResponse)
        .filter(SatisfactionResponse.id == satisfaction_response_id)
        .first()
    )

    if not satisfaction_response:
        raise HTTPException(status_code=404, detail="Satisfaction response not found")

    # Update fields that are provided
    update_data = satisfaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(satisfaction_response, field, value)

    db.commit()
    db.refresh(satisfaction_response)

    return satisfaction_response


@router.delete("/{satisfaction_response_id}", response_model=MessageResponse)
def delete_satisfaction_response(
    satisfaction_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Delete satisfaction response (staff/admin only)"""
    satisfaction_response = (
        db.query(SatisfactionResponse)
        .filter(SatisfactionResponse.id == satisfaction_response_id)
        .first()
    )

    if not satisfaction_response:
        raise HTTPException(status_code=404, detail="Satisfaction response not found")

    db.delete(satisfaction_response)
    db.commit()

    return {"message": "Satisfaction response deleted successfully"}


@router.get("/visit/{visit_id}/summary")
def get_satisfaction_summary(visit_id: int, db: Session = Depends(get_db)):
    """Get satisfaction summary with averages"""
    satisfaction_response = (
        db.query(SatisfactionResponse)
        .filter(SatisfactionResponse.visit_id == visit_id)
        .first()
    )

    if not satisfaction_response:
        raise HTTPException(
            status_code=404, detail="Satisfaction response not found for this visit"
        )

    # Calculate average score
    scores = [
        (
            int(satisfaction_response.q1_clarity)
            if satisfaction_response.q1_clarity
            else 0
        ),
        (
            int(satisfaction_response.q2_ease_of_use)
            if satisfaction_response.q2_ease_of_use
            else 0
        ),
        (
            int(satisfaction_response.q3_confidence)
            if satisfaction_response.q3_confidence
            else 0
        ),
        (
            int(satisfaction_response.q4_presentation)
            if satisfaction_response.q4_presentation
            else 0
        ),
        (
            int(satisfaction_response.q5_results_display)
            if satisfaction_response.q5_results_display
            else 0
        ),
        (
            int(satisfaction_response.q6_usefulness)
            if satisfaction_response.q6_usefulness
            else 0
        ),
        (
            int(satisfaction_response.q7_overall_satisfaction)
            if satisfaction_response.q7_overall_satisfaction
            else 0
        ),
    ]

    valid_scores = [s for s in scores if s > 0]
    average_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    # Determine satisfaction level
    if average_score >= 4.5:
        level = "มากที่สุด"
        level_en = "Excellent"
    elif average_score >= 3.5:
        level = "มาก"
        level_en = "Good"
    elif average_score >= 2.5:
        level = "ปานกลาง"
        level_en = "Moderate"
    elif average_score >= 1.5:
        level = "น้อย"
        level_en = "Poor"
    else:
        level = "น้อยที่สุด"
        level_en = "Very Poor"

    return {
        "average_score": round(average_score, 2),
        "satisfaction_level_th": level,
        "satisfaction_level_en": level_en,
        "total_responses": 7,
        "comments": satisfaction_response.comments,
        "completed_at": satisfaction_response.completed_at,
    }
