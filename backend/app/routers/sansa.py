from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.models import BIARecord, SANSAResponse, Visit, User
from app.schemas import SANSAResponseCreate, SANSAResponseFull, MessageResponse
from app.services.scoring_service import ScoringService
from app.auth import get_current_staff_or_admin
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import SANSARevisedResult, SANSAParticipantResult
from app.services.sansa_result_service import revised_visit_result
from app.services.sansa_definition import DB_SCORING_VERSION, DEFINITION_VERSION, SANSA_QUESTIONS
from app.services.sansa_domain_service import age_group01
from app.services.sansa_prediction_service import predict_sansa_nutrition_status

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
    version = scoring_service.get_active_sansa_definition_version()
    if version is None:
        raise HTTPException(
            status_code=409,
            detail="ยังไม่ได้เปิดใช้ scoring version 0.2.4-20261008 ที่ตรงกับนิยาม SANSA 0/2/4",
        )
    try:
        scores = scoring_service.calculate_sansa_scores(sansa_create, version_id=version.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create response with all 16 question columns
    sansa_response = SANSAResponse(
        visit_id=sansa_create.visit_id,
        scoring_version_id=version.id,
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
        q8_rice_starch=sansa_create.q8_rice_starch,
        q8_score=scores.get("q8_score"),
        q9_protein=sansa_create.q9_protein,
        q9_score=scores.get("q9_score"),
        q10_milk=sansa_create.q10_milk,
        q10_score=scores.get("q10_score"),
        q11_fruits=sansa_create.q11_fruits,
        q11_score=scores.get("q11_score"),
        q12_vegetables=sansa_create.q12_vegetables,
        q12_score=scores.get("q12_score"),
        q13_water=sansa_create.q13_water,
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
def get_sansa_response(
    sansa_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Get SANSA response by ID"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    return sansa_response


@router.get("/visit/{visit_id}", response_model=SANSAResponseFull)
def get_sansa_by_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Get SANSA response by visit ID"""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.visit_id == visit_id).first()
    )

    if not sansa_response:
        raise HTTPException(
            status_code=404, detail="SANSA response not found for this visit"
        )

    payload = SANSAResponseFull.model_validate(sansa_response)
    try:
        payload.revised = SANSARevisedResult(**revised_visit_result(db, sansa_response))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return payload


@router.get("/visit/{visit_id}/rescore-preview")
def preview_visit_rescore(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Compare recorded scores with the approved definition without writing data."""
    response = db.query(SANSAResponse).filter(SANSAResponse.visit_id == visit_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="SANSA response not found for this visit")

    scoring = ScoringService(db)
    approved_version = scoring.get_active_sansa_definition_version()
    try:
        proposed = scoring.calculate_sansa_scores(
            response,
            version_id=approved_version.id if approved_version is not None else -1,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=f"คำนวณใหม่ไม่ได้ เพราะคำตอบเดิมไม่ครบหรือไม่ตรงนิยาม: {error}",
        )

    items = []
    for question in SANSA_QUESTIONS:
        number = question["number"]
        recorded = getattr(response, f"q{number}_score")
        recalculated = proposed[f"q{number}_score"]
        items.append({
            "number": number,
            "field": question["field"],
            "answer": getattr(response, question["field"]),
            "recorded_score": recorded,
            "recalculated_score": recalculated,
            "changed": recorded is None or Decimal(str(recorded)) != recalculated,
        })

    domains = {
        "d1_total": sum(proposed[f"q{i}_score"] for i in range(5, 8)),
        "d2_total": sum(proposed[f"q{i}_score"] for i in range(8, 14)),
        "d3_total": sum(proposed[f"q{i}_score"] for i in range(14, 17)),
    }
    prediction = None
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    bia_rows = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).limit(2).all()
    if (
        visit is not None
        and visit.respondent is not None
        and visit.respondent.age is not None
        and len(bia_rows) == 1
        and bia_rows[0].waist_circumference_cm is not None
        and bia_rows[0].waist_circumference_cm > 0
    ):
        prediction = predict_sansa_nutrition_status(
            d2_total=domains["d2_total"],
            d3_total=domains["d3_total"],
            waist_cm=bia_rows[0].waist_circumference_cm,
            age_group01=age_group01(visit.respondent),
        )

    return {
        "definition_version": DEFINITION_VERSION,
        "database_version": DB_SCORING_VERSION,
        "database_version_active": approved_version is not None,
        "writes_performed": False,
        "changed_item_count": sum(1 for item in items if item["changed"]),
        "items": items,
        "domains": domains,
        "prediction": prediction,
    }


@router.post(
    "/visit/{visit_id}/participant-result",
    response_model=SANSAParticipantResult,
)
def get_participant_result(visit_id: int, db: Session = Depends(get_db)):
    """Persist a complete prediction while returning only its final label."""
    response = db.query(SANSAResponse).filter(SANSAResponse.visit_id == visit_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="SANSA response not found for this visit")
    try:
        result = revised_visit_result(db, response, persist=True)
        if result["saved"]:
            db.commit()
        else:
            db.rollback()
        prediction = result.get("prediction")
        return {
            "predicted_group": prediction["predicted_group"] if prediction else None,
            "ready": bool(prediction),
        }
    except (ValueError, SQLAlchemyError):
        db.rollback()
        raise HTTPException(status_code=422, detail="ข้อมูลสำหรับผลทำนายยังไม่พร้อม")


@router.post("/visit/{visit_id}/prediction", response_model=SANSARevisedResult)
def save_visit_prediction(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Persist server-derived inputs only, following the existing self-service SANSA flow."""
    response = db.query(SANSAResponse).filter(SANSAResponse.visit_id == visit_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="SANSA response not found for this visit")
    try:
        result = revised_visit_result(db, response, persist=True)
        if not result["saved"]:
            db.rollback()
            raise HTTPException(status_code=422, detail="ข้อมูลไม่ครบหรือมี BIA หลายรายการ ยังบันทึกผลไม่ได้")
        db.commit()
        return result
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(error))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=503, detail="ยังบันทึกผลไม่ได้ กรุณาให้ผู้ดูแลตรวจฐานข้อมูลผลทำนาย")


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
    version = scoring_service.get_active_sansa_definition_version()
    if version is None:
        raise HTTPException(status_code=409, detail="ยังไม่ได้เปิดใช้ scoring version SANSA 0/2/4")
    if sansa_response.scoring_version_id != version.id:
        raise HTTPException(
            status_code=409,
            detail="รายการนี้เป็นคะแนนคนละเวอร์ชัน จึงไม่แก้ไขทับประวัติเดิม กรุณาใช้ขั้นตอน rescore แบบแยกเวอร์ชัน",
        )
    try:
        scores = scoring_service.calculate_sansa_scores(sansa_update, version_id=version.id)
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
    sansa_response.q8_rice_starch = sansa_update.q8_rice_starch
    sansa_response.q8_score = scores.get("q8_score")
    sansa_response.q9_protein = sansa_update.q9_protein
    sansa_response.q9_score = scores.get("q9_score")
    sansa_response.q10_milk = sansa_update.q10_milk
    sansa_response.q10_score = scores.get("q10_score")
    sansa_response.q11_fruits = sansa_update.q11_fruits
    sansa_response.q11_score = scores.get("q11_score")
    sansa_response.q12_vegetables = sansa_update.q12_vegetables
    sansa_response.q12_score = scores.get("q12_score")
    sansa_response.q13_water = sansa_update.q13_water
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
def get_sansa_advice(
    sansa_response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Return the verified Model 3 outcome; no legacy total-score advice."""
    sansa_response = (
        db.query(SANSAResponse).filter(SANSAResponse.id == sansa_response_id).first()
    )

    if not sansa_response:
        raise HTTPException(status_code=404, detail="SANSA response not found")

    revised = revised_visit_result(db, sansa_response, persist=False)
    prediction = revised.get("prediction")
    if prediction is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "ยังให้ผลไม่ได้เพราะข้อมูล 0/2/4 ไม่สมบูรณ์", "issues": revised["issues"]},
        )
    return {
        "predicted_group": prediction["predicted_group"],
        "model_version": prediction["model_version"],
        "verified_024": revised["verified_024"],
        "advice_text_th": None,
        "advice_text_en": None,
        "note": "ยังไม่มีข้อความคำแนะนำรายกลุ่มที่ผ่านการอนุมัติ จึงไม่สร้างคำแนะนำทางคลินิกขึ้นเอง",
    }
