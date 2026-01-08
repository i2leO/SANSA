from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import SANSAResponse, Visit, User
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
    Create SANSA response with automatic scoring (column-based approach)
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
        scores = scoring_service.calculate_sansa_scores(sansa_create, version_id=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create response with all 16 question columns
    sansa_response = SANSAResponse(
        visit_id=sansa_create.visit_id,
        scoring_version_id=1,  # Default to version 1
        # Screening questions (Q1-Q4)
        q1_weight_change=sansa_create.q1_weight_change,
        q1_score=scores.get("q1_score"),
        q2_food_intake=sansa_create.q2_food_intake,
        q2_score=scores.get("q2_score"),
        q3_daily_activities=sansa_create.q3_daily_activities,
        q3_score=scores.get("q3_score"),
        q4_chronic_disease=sansa_create.q4_chronic_disease,
        q4_score=scores.get("q4_score"),
        # Dietary questions (Q5-Q16)
        q5_meals_per_day=sansa_create.q5_meals_per_day,
        q5_score=scores.get("q5_score"),
        q6_portion_size=sansa_create.q6_portion_size,
        q6_score=scores.get("q6_score"),
        q7_food_texture=sansa_create.q7_food_texture,
        q7_score=scores.get("q7_score"),
        q8_rice_grains=sansa_create.q8_rice_grains,
        q8_score=scores.get("q8_score"),
        q9_protein_legumes=sansa_create.q9_protein_legumes,
        q9_score=scores.get("q9_score"),
        q10_milk_yogurt=sansa_create.q10_milk_yogurt,
        q10_score=scores.get("q10_score"),
        q11_fruits=sansa_create.q11_fruits,
        q11_score=scores.get("q11_score"),
        q12_vegetables=sansa_create.q12_vegetables,
        q12_score=scores.get("q12_score"),
        q13_water_intake=sansa_create.q13_water_intake,
        q13_score=scores.get("q13_score"),
        q14_sweet_drinks=sansa_create.q14_sweet_drinks,
        q14_score=scores.get("q14_score"),
        q15_cooking_method=sansa_create.q15_cooking_method,
        q15_score=scores.get("q15_score"),
        q16_oil_coconut=sansa_create.q16_oil_coconut,
        q16_score=scores.get("q16_score"),
        # Totals
        screening_total=scores["screening_total"],
        diet_total=scores["diet_total"],
        total_score=scores["total_score"],
        result_level=scores["result_level"],
        completed_at=datetime.utcnow(),
    )

    db.add(sansa_response)
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


@router.put("/{sansa_response_id}", response_model=SANSAResponseFull)
def update_sansa_response(
    sansa_response_id: int,
    sansa_update: SANSAResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Update existing SANSA response (staff/admin only)"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    # Recalculate scores
    scoring_service = ScoringService(db)
    try:
        scores = scoring_service.calculate_sansa_scores(sansa_update, version_id=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update all fields
    sansa_response.q1_weight_change = sansa_update.q1_weight_change
    sansa_response.q1_score = scores.get("q1_score")
    sansa_response.q2_food_intake = sansa_update.q2_food_intake
    sansa_response.q2_score = scores.get("q2_score")
    sansa_response.q3_daily_activities = sansa_update.q3_daily_activities
    sansa_response.q3_score = scores.get("q3_score")
    sansa_response.q4_chronic_disease = sansa_update.q4_chronic_disease
    sansa_response.q4_score = scores.get("q4_score")
    sansa_response.q5_meals_per_day = sansa_update.q5_meals_per_day
    sansa_response.q5_score = scores.get("q5_score")
    sansa_response.q6_portion_size = sansa_update.q6_portion_size
    sansa_response.q6_score = scores.get("q6_score")
    sansa_response.q7_food_texture = sansa_update.q7_food_texture
    sansa_response.q7_score = scores.get("q7_score")
    sansa_response.q8_rice_grains = sansa_update.q8_rice_grains
    sansa_response.q8_score = scores.get("q8_score")
    sansa_response.q9_protein_legumes = sansa_update.q9_protein_legumes
    sansa_response.q9_score = scores.get("q9_score")
    sansa_response.q10_milk_yogurt = sansa_update.q10_milk_yogurt
    sansa_response.q10_score = scores.get("q10_score")
    sansa_response.q11_fruits = sansa_update.q11_fruits
    sansa_response.q11_score = scores.get("q11_score")
    sansa_response.q12_vegetables = sansa_update.q12_vegetables
    sansa_response.q12_score = scores.get("q12_score")
    sansa_response.q13_water_intake = sansa_update.q13_water_intake
    sansa_response.q13_score = scores.get("q13_score")
    sansa_response.q14_sweet_drinks = sansa_update.q14_sweet_drinks
    sansa_response.q14_score = scores.get("q14_score")
    sansa_response.q15_cooking_method = sansa_update.q15_cooking_method
    sansa_response.q15_score = scores.get("q15_score")
    sansa_response.q16_oil_coconut = sansa_update.q16_oil_coconut
    sansa_response.q16_score = scores.get("q16_score")

    sansa_response.screening_total = scores["screening_total"]
    sansa_response.diet_total = scores["diet_total"]
    sansa_response.total_score = scores["total_score"]
    sansa_response.result_level = scores["result_level"]

    db.commit()
    db.refresh(sansa_response)

    return sansa_response


@router.delete("/{sansa_response_id}", response_model=MessageResponse)
def delete_sansa_response(
    sansa_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Delete SANSA response (staff/admin only)"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    db.delete(sansa_response)
    db.commit()

    return {"message": "SANSA response deleted successfully"}


@router.get("/{sansa_response_id}/advice")
def get_sansa_advice(sansa_response_id: int, db: Session = Depends(get_db)):
    """Get advice text based on SANSA result level"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    # Return advice based on result level
    advice_map = {
        "normal": {
            "th": "สถานะโภชนาการปกติ ควรรักษาพฤติกรรมการกินที่ดีนี้ไว้ และตรวจสุขภาพอย่างสม่ำเสมอ",
            "en": "Normal nutritional status. Maintain good eating habits and regular health checkups.",
        },
        "at_risk": {
            "th": "มีความเสี่ยงต่อภาวะทุพโภชนาการ ควรปรับพฤติกรรมการกิน เพิ่มการบริโภคอาหารที่มีคุณค่าทางโภชนาการ และปรึกษานักโภชนาการ",
            "en": "At risk of malnutrition. Adjust eating behaviors, increase nutritious food intake, and consult a nutritionist.",
        },
        "malnourished": {
            "th": "พบภาวะทุพโภชนาการ ควรพบแพทย์และนักโภชนาการโดยด่วนเพื่อรับการดูแลและวางแผนการรักษา",
            "en": "Malnourished. Urgently consult a doctor and nutritionist for care and treatment planning.",
        },
    }

    advice = advice_map.get(sansa_response.result_level, advice_map["normal"])

    return {
        "result_level": sansa_response.result_level,
        "total_score": (
            float(sansa_response.total_score) if sansa_response.total_score else None
        ),
        "screening_total": (
            float(sansa_response.screening_total)
            if sansa_response.screening_total
            else None
        ),
        "diet_total": (
            float(sansa_response.diet_total) if sansa_response.diet_total else None
        ),
        "advice_text_th": advice["th"],
        "advice_text_en": advice["en"],
    }
