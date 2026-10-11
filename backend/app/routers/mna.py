from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import BIARecord, MNAResponse, Visit, User
from app.services.mna_definition import MNA_ITEMS, answers_from_bia
from app.services.mna_result_service import build_mna_result_summary
from app.schemas import (
    MNAResponseCreate,
    MNAResponseUpdate,
    MNAResponseFull,
    MNAResultSummary,
    MessageResponse,
)
from app.services.scoring_service import ScoringService
from app.auth import get_current_staff_or_admin
from app.services.assessment_revision_service import append_assessment_revision, ensure_assessment_baseline

router = APIRouter(prefix="/mna", tags=["mna"])


def present_mna(record):
    payload = MNAResponseFull.model_validate(record)
    payload.history_requires_review = record.scoring_version is None or record.scoring_version.instrument_name != "MNA"
    payload.current_result = MNAResultSummary(**build_mna_result_summary(record))
    return payload


@router.get("/definition", dependencies=[Depends(get_current_staff_or_admin)])
def get_mna_definition():
    scoring = ScoringService(None)
    return {"items": [
        {**item, "options": [
            {**option, "score": scoring.calculate_mna_question_score(index, option["value"])}
            for option in item["options"]
        ]} for index, item in enumerate(MNA_ITEMS, 1)
    ]}


@router.get("/visit/{visit_id}/bia-suggestions", dependencies=[Depends(get_current_staff_or_admin)])
def get_bia_suggestions(visit_id: int, db: Session = Depends(get_db)):
    bia = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).first()
    if bia is None:
        raise HTTPException(status_code=404, detail="ยังไม่มีข้อมูล BIA ที่บันทึกไว้")
    return {"answers": answers_from_bia(bia)}


@router.post("", response_model=MNAResponseFull)
def create_mna_response(
    mna_create: MNAResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """
    Create MNA (Mini Nutritional Assessment) response with automatic scoring
    Staff/admin only (router dependencies enforced at app registration).
    Requires complete A-R answers for a full assessment.
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

    # Resolve the instrument version; never attach MNA results to SANSA ID 1.
    scoring_service = ScoringService(db)
    version = scoring_service.get_active_scoring_version("MNA")
    if version is None:
        raise HTTPException(status_code=409, detail="ไม่พบเวอร์ชัน MNA ที่เปิดใช้งาน")
    try:
        scores = scoring_service.calculate_mna_score(mna_create, version_id=version.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create response with all 18 question columns
    mna_response = MNAResponse(
        visit_id=mna_create.visit_id,
        scoring_version_id=version.id,
        source_dataset="web",
        answer_capture_mode="raw_answers",
        # Screening A-F; preserve the separate historical screening calf slot.
        q1_food_intake_decline=mna_create.q1_food_intake_decline,
        mna_s1=scores.get("mna_s1"),
        q2_weight_loss=mna_create.q2_weight_loss,
        mna_s2=scores.get("mna_s2"),
        q3_mobility=mna_create.q3_mobility,
        mna_s3=scores.get("mna_s3"),
        q4_stress_illness=mna_create.q4_stress_illness,
        mna_s4=scores.get("mna_s4"),
        q5_neuropsychological=mna_create.q5_neuropsychological,
        mna_s5=scores.get("mna_s5"),
        q6_bmi=mna_create.q6_bmi,
        mna_s6=scores.get("mna_s6"),
        q19_calf_circumference_assess=mna_create.q19_calf_circumference_assess,
        mna_a12=scores["mna_a12"],
        # Assessment G-Q; all required for the full A-R instrument.
        q8_independent_living=mna_create.q8_independent_living,
        mna_a1=scores.get("mna_a1"),
        q9_medications=mna_create.q9_medications,
        mna_a2=scores.get("mna_a2"),
        q10_pressure_sores=mna_create.q10_pressure_sores,
        mna_a3=scores.get("mna_a3"),
        q11_full_meals=mna_create.q11_full_meals,
        mna_a4=scores.get("mna_a4"),
        q12_protein_consumption=mna_create.q12_protein_consumption,
        mna_a5=scores.get("mna_a5"),
        q13_fruits_vegetables=mna_create.q13_fruits_vegetables,
        mna_a6=scores.get("mna_a6"),
        q14_fluid_intake=mna_create.q14_fluid_intake,
        mna_a7=scores.get("mna_a7"),
        q15_eating_independence=mna_create.q15_eating_independence,
        mna_a8=scores.get("mna_a8"),
        q16_self_nutrition=mna_create.q16_self_nutrition,
        mna_a9=scores.get("mna_a9"),
        q17_health_comparison=mna_create.q17_health_comparison,
        mna_a10=scores.get("mna_a10"),
        q18_mid_arm_circumference=mna_create.q18_mid_arm_circumference,
        mna_a11=scores.get("mna_a11"),
        # Totals
        mna_screen_total=scores["mna_screen_total"],
        mna_ass_total=scores.get("mna_ass_total", 0),
        mna_total=scores["mna_total"],
        result_category=scores["result_category"],
        completed_at=datetime.utcnow(),
        created_by=getattr(current_user, "id", None),
    )

    db.add(mna_response)
    db.flush()
    append_assessment_revision(db, "MNA", mna_response, current_user, "create")
    db.commit()
    db.refresh(mna_response)

    return present_mna(mna_response)


@router.get("/{mna_response_id}", response_model=MNAResponseFull)
def get_mna_response(mna_response_id: int, db: Session = Depends(get_db)):
    """Get MNA response by ID"""
    mna_response = (
        db.query(MNAResponse).filter(MNAResponse.id == mna_response_id).first()
    )

    if not mna_response:
        raise HTTPException(status_code=404, detail="MNA response not found")

    return present_mna(mna_response)


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

    return present_mna(mna_response)


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

    version = scoring_service.get_scoring_version(mna_response.scoring_version_id)
    if version is None or version.instrument_name != "MNA":
        raise HTTPException(status_code=409, detail="เวอร์ชันคะแนนเดิมไม่ใช่ MNA กรุณาให้ผู้ดูแลตรวจสอบประวัติก่อนแก้ไข")
    ensure_assessment_baseline(db, "MNA", mna_response)
    update_data = mna_update.model_dump(exclude_unset=True)
    complete_data = MNAResponseCreate(
        visit_id=mna_response.visit_id,
        **{item["field"]: update_data.get(item["field"], getattr(mna_response, item["field"]))
           for item in MNA_ITEMS},
    )

    try:
        scores = scoring_service.calculate_mna_score(complete_data, version_id=version.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update all fields
    for field, value in update_data.items():
        if not field.endswith("_score"):  # Don't manually set scores
            setattr(mna_response, field, value)

    # A-F use mna_s1-s6; G-R use mna_a1-a12.
    for q_num in range(1, 7):
        score_field = f"mna_s{q_num}"
        if score_field in scores:
            setattr(mna_response, score_field, scores[score_field])

    for q_num in range(8, 20):
        score_field = f"mna_a{q_num - 7}"
        if score_field in scores:
            setattr(mna_response, score_field, scores[score_field])

    mna_response.mna_screen_total = scores["mna_screen_total"]
    mna_response.mna_ass_total = scores.get("mna_ass_total", 0)
    mna_response.mna_total = scores["mna_total"]
    mna_response.result_category = scores["result_category"]
    mna_response.source_dataset = "web"
    mna_response.answer_capture_mode = "raw_answers"
    mna_response.entry_mode = "staff"
    mna_response.completed_at = datetime.utcnow()

    db.flush()
    append_assessment_revision(db, "MNA", mna_response, current_user, "update")

    db.commit()
    db.refresh(mna_response)

    return present_mna(mna_response)


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

    raise HTTPException(status_code=409, detail="ข้อมูลวิจัย MNA ห้ามลบ กรุณาบันทึกการแก้ไขเป็น revision ใหม่")


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

    advice = advice_map.get(mna_response.result_category)
    if advice is None:
        raise HTTPException(status_code=409, detail="ยังไม่มีผล MNA ที่แปลผลได้")

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
