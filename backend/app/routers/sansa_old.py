from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import SANSAResponse, SANSAItem, Visit, User
from app.schemas import SANSAResponseCreate, SANSAResponseFull, MessageResponse
from app.services.scoring_service import ScoringService
from app.auth import get_current_staff_or_admin
from typing import Optional

router = APIRouter(prefix="/sansa", tags=["sansa"])


@router.post("", response_model=SANSAResponseFull)
def create_sansa_response(
    sansa_create: SANSAResponseCreate, db: Session = Depends(get_db)
):
    """
    Create SANSA response with automatic scoring
    Can be submitted by respondent (no auth) or staff (with auth)
    """
    # Verify visit exists
    visit = db.query(Visit).filter(Visit.id == sansa_create.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Check if SANSA already exists for this visit
    existing = (
        db.query(SANSAResponse)
        .filter(SANSAResponse.visit_id == sansa_create.visit_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="SANSA response already exists for this visit"
        )

    # Calculate scores
    scoring_service = ScoringService(db)
    try:
        scores = scoring_service.calculate_sansa_scores(sansa_create.items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create response
    sansa_response = SANSAResponse(
        visit_id=sansa_create.visit_id,
        scoring_version_id=scores["scoring_version_id"],
        screening_total=scores["screening_total"],
        diet_total=scores["diet_total"],
        total_score=scores["total_score"],
        result_level=scores["result_level"],
        completed_at=datetime.utcnow(),
    )

    db.add(sansa_response)
    db.flush()

    # Create items
    for item_input in sansa_create.items:
        item = SANSAItem(
            sansa_response_id=sansa_response.id,
            item_type=item_input.item_type,
            item_number=item_input.item_number,
            item_code=item_input.item_code,
            answer_value=item_input.answer_value,
            item_score=item_input.item_score,
        )
        db.add(item)

    db.commit()
    db.refresh(sansa_response)

    return sansa_response


@router.get("/{sansa_response_id}", response_model=SANSAResponseFull)
def get_sansa_response(sansa_response_id: int, db: Session = Depends(get_db)):
    """Get SANSA response by ID"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    return sansa_response


@router.get("/visit/{visit_id}", response_model=SANSAResponseFull)
def get_sansa_by_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get SANSA response by visit ID"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.visit_id == visit_id).first()
    )

    if not sansa_response:
        raise HTTPException(
            status_code=404, detail="SANSA response not found for this visit"
        )

    return sansa_response


@router.get("/{sansa_response_id}/advice")
def get_sansa_advice(sansa_response_id: int, db: Session = Depends(get_db)):
    """Get advice text based on SANSA result level"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    scoring_service = ScoringService(db)
    advice = scoring_service.get_advice_text(
        sansa_response.scoring_version_id, sansa_response.result_level
    )

    return {
        "result_level": sansa_response.result_level,
        "total_score": (
            float(sansa_response.total_score) if sansa_response.total_score else None
        ),
        "advice_text": advice,
    }
