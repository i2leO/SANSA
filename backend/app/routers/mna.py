from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import MNAResponse, Visit, User
from app.schemas import (
    MNAResponseCreate,
    MNAResponseUpdate,
    MNAResponseFull,
    MessageResponse,
)
from app.services.scoring_service import ScoringService
from app.auth import get_current_staff_or_admin

router = APIRouter(prefix="/mna", tags=["mna"])


@router.post("", response_model=MNAResponseFull)
def create_mna_response(mna_create: MNAResponseCreate, db: Session = Depends(get_db)):
    """
    Create MNA (Mini Nutritional Assessment) response with automatic scoring
    Can be submitted by respondent (no auth) or staff (with auth)
    Implements conditional logic: assessment questions only if screening ≤11
    """
    # Verify visit exists
    visit = db.query(Visit).filter(Visit.id == mna_create.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Check if MNA already exists for this visit
    existing = (
        db.query(MNAResponse)
        .filter(MNAResponse.visit_id == mna_create.visit_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="MNA response already exists for this visit"
        )

    # Calculate scores
    scoring_service = ScoringService(db)
    try:
        scores = scoring_service.calculate_mna_score(mna_create, version_id=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create response with all 18 question columns
    mna_response = MNAResponse(
        visit_id=mna_create.visit_id,
        scoring_version_id=1,  # Default to version 1
        # Screening questions (Q1-Q7) - always required
        q1_food_intake_decline=mna_create.q1_food_intake_decline,
        mna_s1=scores.get("mna_s1"),
        q2_weight_loss=mna_create.q2_weight_loss,
        mna_s2=scores.get("mna_s2"),
        q3_mobility=mna_create.q3_mobility,
        mna_s3=scores.get("mna_s3"),
        q4_psychological_stress=mna_create.q4_psychological_stress,
        mna_s4=scores.get("mna_s4"),
        q5_neuropsychological_problems=mna_create.q5_neuropsychological_problems,
        mna_s5=scores.get("mna_s5"),
        q6_bmi_or_calf=mna_create.q6_bmi_or_calf,
        mna_s6=scores.get("mna_s6"),
        q7_independent_living=mna_create.q7_independent_living,
        mna_s7=scores.get("mna_s7"),
        # Assessment questions (Q8-Q18) - only if screening ≤11
        q8_medications=mna_create.q8_medications,
        mna_a1=scores.get("mna_a1"),
        q9_pressure_ulcers=mna_create.q9_pressure_ulcers,
        mna_a2=scores.get("mna_a2"),
        q10_meals_per_day=mna_create.q10_meals_per_day,
        mna_a3=scores.get("mna_a3"),
        q11_protein_markers=mna_create.q11_protein_markers,
        mna_a4=scores.get("mna_a4"),
        q12_fruits_vegetables=mna_create.q12_fruits_vegetables,
        mna_a5=scores.get("mna_a5"),
        q13_fluid_intake=mna_create.q13_fluid_intake,
        mna_a6=scores.get("mna_a6"),
        q14_feeding_ability=mna_create.q14_feeding_ability,
        mna_a7=scores.get("mna_a7"),
        q15_self_nutrition_view=mna_create.q15_self_nutrition_view,
        mna_a8=scores.get("mna_a8"),
        q16_health_comparison=mna_create.q16_health_comparison,
        mna_a9=scores.get("mna_a9"),
        q17_mid_arm_circumference=mna_create.q17_mid_arm_circumference,
        mna_a10=scores.get("mna_a10"),
        q18_calf_circumference=mna_create.q18_calf_circumference,
        mna_a11=scores.get("mna_a11"),
        # Totals
        mna_screen_total=scores["mna_screen_total"],
        mna_ass_total=scores.get("mna_ass_total", 0),
        mna_total=scores["mna_total"],
        result_category=scores["result_category"],
        completed_at=datetime.utcnow(),
    )

    db.add(mna_response)
    db.commit()
    db.refresh(mna_response)

    return mna_response


@router.get("/{mna_response_id}", response_model=MNAResponseFull)
def get_mna_response(mna_response_id: int, db: Session = Depends(get_db)):
    """Get MNA response by ID"""
    mna_response = (
        db.query(MNAResponse).filter(MNAResponse.id == mna_response_id).first()
    )

    if not mna_response:
        raise HTTPException(status_code=404, detail="MNA response not found")

    return mna_response


@router.get("/visit/{visit_id}", response_model=MNAResponseFull)
def get_mna_by_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get MNA response by visit ID"""
    mna_response = (
        db.query(MNAResponse).filter(MNAResponse.visit_id == visit_id).first()
    )

    if not mna_response:
        raise HTTPException(
            status_code=404, detail="MNA response not found for this visit"
        )

    return mna_response


@router.put("/{mna_response_id}", response_model=MNAResponseFull)
def update_mna_response(
    mna_response_id: int,
    mna_update: MNAResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Update existing MNA response (staff/admin only)"""
    mna_response = (
        db.query(MNAResponse).filter(MNAResponse.id == mna_response_id).first()
    )

    if not mna_response:
        raise HTTPException(status_code=404, detail="MNA response not found")

    # Recalculate scores
    scoring_service = ScoringService(db)

    # Build complete MNAResponseCreate from update + existing data
    complete_data = MNAResponseCreate(
        visit_id=mna_response.visit_id,
        q1_food_intake_decline=mna_update.q1_food_intake_decline
        or mna_response.q1_food_intake_decline,
        q2_weight_loss=mna_update.q2_weight_loss or mna_response.q2_weight_loss,
        q3_mobility=mna_update.q3_mobility or mna_response.q3_mobility,
        q4_psychological_stress=mna_update.q4_psychological_stress
        or mna_response.q4_psychological_stress,
        q5_neuropsychological_problems=mna_update.q5_neuropsychological_problems
        or mna_response.q5_neuropsychological_problems,
        q6_bmi_or_calf=mna_update.q6_bmi_or_calf or mna_response.q6_bmi_or_calf,
        q7_independent_living=mna_update.q7_independent_living
        or mna_response.q7_independent_living,
        q8_medications=mna_update.q8_medications or mna_response.q8_medications,
        q9_pressure_ulcers=mna_update.q9_pressure_ulcers
        or mna_response.q9_pressure_ulcers,
        q10_meals_per_day=mna_update.q10_meals_per_day
        or mna_response.q10_meals_per_day,
        q11_protein_markers=mna_update.q11_protein_markers
        or mna_response.q11_protein_markers,
        q12_fruits_vegetables=mna_update.q12_fruits_vegetables
        or mna_response.q12_fruits_vegetables,
        q13_fluid_intake=mna_update.q13_fluid_intake or mna_response.q13_fluid_intake,
        q14_feeding_ability=mna_update.q14_feeding_ability
        or mna_response.q14_feeding_ability,
        q15_self_nutrition_view=mna_update.q15_self_nutrition_view
        or mna_response.q15_self_nutrition_view,
        q16_health_comparison=mna_update.q16_health_comparison
        or mna_response.q16_health_comparison,
        q17_mid_arm_circumference=mna_update.q17_mid_arm_circumference
        or mna_response.q17_mid_arm_circumference,
        q18_calf_circumference=mna_update.q18_calf_circumference
        or mna_response.q18_calf_circumference,
    )

    try:
        scores = scoring_service.calculate_mna_score(complete_data, version_id=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update all fields
    update_data = mna_update.dict(exclude_unset=True, exclude={"visit_id"})
    for field, value in update_data.items():
        if not field.endswith("_score"):  # Don't manually set scores
            setattr(mna_response, field, value)

    # Update scores (Q1-Q7 use mna_s1-mna_s7, Q8-Q18 use mna_a1-mna_a11)
    for q_num in range(1, 8):
        score_field = f"mna_s{q_num}"
        if score_field in scores:
            setattr(mna_response, score_field, scores[score_field])

    for q_num in range(8, 19):
        score_field = f"mna_a{q_num - 7}"
        if score_field in scores:
            setattr(mna_response, score_field, scores[score_field])

    mna_response.mna_screen_total = scores["mna_screen_total"]
    mna_response.mna_ass_total = scores.get("mna_ass_total", 0)
    mna_response.mna_total = scores["mna_total"]
    mna_response.result_category = scores["result_category"]

    db.commit()
    db.refresh(mna_response)

    return mna_response


@router.delete("/{mna_response_id}", response_model=MessageResponse)
def delete_mna_response(
    mna_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Delete MNA response (staff/admin only)"""
    mna_response = (
        db.query(MNAResponse).filter(MNAResponse.id == mna_response_id).first()
    )

    if not mna_response:
        raise HTTPException(status_code=404, detail="MNA response not found")

    db.delete(mna_response)
    db.commit()

    return {"message": "MNA response deleted successfully"}


@router.get("/{mna_response_id}/advice")
def get_mna_advice(mna_response_id: int, db: Session = Depends(get_db)):
    """Get advice text based on MNA result category"""
    mna_response = (
        db.query(MNAResponse).filter(MNAResponse.id == mna_response_id).first()
    )

    if not mna_response:
        raise HTTPException(status_code=404, detail="MNA response not found")

    # Return advice based on result category
    advice_map = {
        "normal": {
            "th": "สถานะโภชนาการปกติ (24-30 คะแนน) ควรรักษาสุขภาพและพฤติกรรมการกินที่ดีนี้ไว้",
            "en": "Normal nutritional status (24-30 points). Maintain good health and eating habits.",
        },
        "at_risk": {
            "th": "มีความเสี่ยงต่อภาวะทุพโภชนาการ (17-23.5 คะแนน) ควรปรับพฤติกรรมการกิน เพิ่มโภชนาการ และติดตามอย่างใกล้ชิด",
            "en": "At risk of malnutrition (17-23.5 points). Adjust eating behaviors, increase nutrition, and monitor closely.",
        },
        "malnourished": {
            "th": "พบภาวะทุพโภชนาการ (<17 คะแนน) ควรพบแพทย์และนักโภชนาการทันทีเพื่อรับการดูแลและการรักษา",
            "en": "Malnourished (<17 points). Urgently consult a doctor and nutritionist for care and treatment.",
        },
    }

    advice = advice_map.get(mna_response.result_category, advice_map["normal"])

    return {
        "result_category": mna_response.result_category,
        "total_score": (
            float(mna_response.mna_total) if mna_response.mna_total else None
        ),
        "screening_total": (
            float(mna_response.mna_screen_total)
            if mna_response.mna_screen_total
            else None
        ),
        "assessment_total": (
            float(mna_response.mna_ass_total) if mna_response.mna_ass_total else None
        ),
        "advice_text_th": advice["th"],
        "advice_text_en": advice["en"],
    }
