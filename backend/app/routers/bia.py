from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import BIARecord, Visit, User
from app.schemas import (
    BIARecordCreate,
    BIARecordUpdate,
    BIARecordResponse,
    MessageResponse,
    ParticipantWaistUpdate,
    BIAStaffSubmission,
)
from app.services.scoring_service import ScoringService
from app.auth import get_current_staff_or_admin
from app.services.assessment_revision_service import append_assessment_revision, ensure_assessment_baseline

router = APIRouter(prefix="/bia", tags=["bia"])


@router.post("", response_model=BIARecordResponse)
def create_bia_record(
    bia_create: BIARecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """
    Create BIA (Body Impedance Analysis) record
    Staff/admin-only full body-composition record.
    """
    # Verify visit exists
    visit = db.query(Visit).filter(Visit.id == bia_create.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Check if BIA already exists for this visit
    existing = (
        db.query(BIARecord).filter(BIARecord.visit_id == bia_create.visit_id).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="BIA record already exists for this visit"
        )

    # Calculate BMI and category if weight and height provided
    bmi = None
    bmi_category = None
    if bia_create.weight_kg and bia_create.height_cm:
        height_m = bia_create.height_cm / 100
        bmi = bia_create.weight_kg / (height_m * height_m)

        # Get BMI category using Asian-Pacific thresholds
        scoring_service = ScoringService(db)
        bmi_category = scoring_service.get_bmi_category(bmi)

    # Create BIA record
    bia_record = BIARecord(
        visit_id=bia_create.visit_id,
        age=bia_create.age,
        sex=bia_create.sex,
        waist_circumference_cm=bia_create.waist_circumference_cm,
        weight_kg=bia_create.weight_kg,
        height_cm=bia_create.height_cm,
        bmi=bmi,
        fat_mass_kg=bia_create.fat_mass_kg,
        body_fat_percentage=bia_create.body_fat_percentage,
        visceral_fat_kg=bia_create.visceral_fat_kg,
        visceral_fat_level=bia_create.visceral_fat_level,
        muscle_mass_kg=bia_create.muscle_mass_kg,
        bone_mass_kg=bia_create.bone_mass_kg,
        water_percentage=bia_create.water_percentage,
        metabolic_rate=bia_create.metabolic_rate,
        mac_cm=bia_create.mac_cm,
        cc_cm=bia_create.cc_cm,
        hip_circumference_cm=bia_create.hip_circumference_cm,
        notes=bia_create.notes,
        bmi_category=bmi_category,
        weight_management=bia_create.weight_management,
        food_recommendation=bia_create.food_recommendation,
        staff_signature=bia_create.staff_signature,
        measurement_date=bia_create.measurement_date or datetime.utcnow().date(),
        created_at=datetime.utcnow(),
    )

    db.add(bia_record)
    db.flush()
    append_assessment_revision(db, "BIA", bia_record, current_user, "create")
    db.commit()
    db.refresh(bia_record)

    return bia_record


@router.get("/{bia_record_id}", response_model=BIARecordResponse)
def get_bia_record(
    bia_record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Get BIA record by ID"""
    bia_record = db.query(BIARecord).filter(BIARecord.id == bia_record_id).first()

    if not bia_record:
        raise HTTPException(status_code=404, detail="BIA record not found")

    return bia_record


@router.get("/visit/{visit_id}", response_model=BIARecordResponse)
def get_bia_by_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Get BIA record by visit ID"""
    bia_record = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).first()

    if not bia_record:
        raise HTTPException(
            status_code=404, detail="BIA record not found for this visit"
        )

    return bia_record


@router.put("/visit/{visit_id}/waist")
def save_participant_waist(
    visit_id: int,
    payload: ParticipantWaistUpdate,
    db: Session = Depends(get_db),
):
    """Store only the Model 3 waist input for the owner of this visit."""
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    records = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).limit(2).all()
    if len(records) > 1:
        raise HTTPException(
            status_code=409,
            detail="พบข้อมูล BIA หลายรายการ กรุณาให้เจ้าหน้าที่ตรวจสอบ",
        )

    if records:
        record = records[0]
        ensure_assessment_baseline(db, "BIA", record)
        record.waist_circumference_cm = payload.waist_circumference_cm
        record.waist_input_value = payload.waist_input_value
        record.waist_input_unit = payload.waist_input_unit
    else:
        record = BIARecord(
            visit_id=visit_id,
            waist_circumference_cm=payload.waist_circumference_cm,
            waist_input_value=payload.waist_input_value,
            waist_input_unit=payload.waist_input_unit,
            measurement_date=datetime.utcnow().date(),
            created_at=datetime.utcnow(),
        )
        db.add(record)

    db.flush()
    append_assessment_revision(db, "BIA", record, action_type="participant_update" if records else "participant_create")

    db.commit()
    return {"saved": True}


@router.put("/visit/{visit_id}/staff", response_model=BIARecordResponse)
def save_complete_staff_bia(
    visit_id: int,
    payload: BIAStaffSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Create/update one complete revised4 staff BIA row for a visit."""
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    records = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).limit(2).all()
    if len(records) > 1:
        raise HTTPException(status_code=409, detail="พบข้อมูล BIA หลายรายการ กรุณาตรวจสอบก่อนบันทึก")

    values = payload.model_dump()
    height_m = values["height_cm"] / 100
    bmi = values["weight_kg"] / (height_m * height_m)
    values["bmi"] = bmi
    values["bmi_category"] = ScoringService(db).get_bmi_category(bmi)

    if records:
        record = records[0]
        ensure_assessment_baseline(db, "BIA", record)
        for field, value in values.items():
            setattr(record, field, value)
    else:
        record = BIARecord(
            visit_id=visit_id,
            measurement_date=datetime.utcnow().date(),
            created_at=datetime.utcnow(),
            **values,
        )
        db.add(record)
    record.measured_by = current_user.id
    db.flush()
    append_assessment_revision(db, "BIA", record, current_user, "update" if records else "create")
    db.commit()
    db.refresh(record)
    return record


@router.put("/{bia_record_id}", response_model=BIARecordResponse)
def update_bia_record(
    bia_record_id: int,
    bia_update: BIARecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Update existing BIA record (staff/admin only)"""
    bia_record = db.query(BIARecord).filter(BIARecord.id == bia_record_id).first()

    if not bia_record:
        raise HTTPException(status_code=404, detail="BIA record not found")

    ensure_assessment_baseline(db, "BIA", bia_record)

    # Update fields that are provided
    update_data = bia_update.model_dump(exclude_unset=True)

    # Recalculate BMI if weight or height changed
    if "weight_kg" in update_data or "height_cm" in update_data:
        weight = update_data.get("weight_kg", bia_record.weight_kg)
        height = update_data.get("height_cm", bia_record.height_cm)

        if weight and height:
            height_m = height / 100
            bmi = weight / (height_m * height_m)
            update_data["bmi"] = bmi

            # Update BMI category
            scoring_service = ScoringService(db)
            update_data["bmi_category"] = scoring_service.get_bmi_category(bmi)
        else:
            update_data["bmi"] = None
            update_data["bmi_category"] = None

    for field, value in update_data.items():
        setattr(bia_record, field, value)

    bia_record.measured_by = getattr(current_user, "id", None)
    db.flush()
    append_assessment_revision(db, "BIA", bia_record, current_user, "update")

    db.commit()
    db.refresh(bia_record)

    return bia_record


@router.delete("/{bia_record_id}", response_model=MessageResponse)
def delete_bia_record(
    bia_record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Delete BIA record (staff/admin only)"""
    bia_record = db.query(BIARecord).filter(BIARecord.id == bia_record_id).first()

    if not bia_record:
        raise HTTPException(status_code=404, detail="BIA record not found")

    raise HTTPException(status_code=409, detail="ข้อมูลวิจัย BIA ห้ามลบ กรุณาบันทึกการแก้ไขเป็น revision ใหม่")


@router.get("/visit/{visit_id}/interpretation")
def get_bia_interpretation(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    """Get BIA interpretation and recommendations"""
    bia_record = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).first()

    if not bia_record:
        raise HTTPException(
            status_code=404, detail="BIA record not found for this visit"
        )

    # Interpret body fat percentage based on age and sex
    body_fat_interpretation = ""
    if bia_record.body_fat_percentage:
        bf = bia_record.body_fat_percentage
        if bia_record.sex == "male":
            if bf < 10:
                body_fat_interpretation = "น้ำมันในร่างกายต่ำเกินไป"
            elif bf < 20:
                body_fat_interpretation = "น้ำมันในร่างกายปกติ"
            elif bf < 25:
                body_fat_interpretation = "น้ำมันในร่างกายสูงเล็กน้อย"
            else:
                body_fat_interpretation = "น้ำมันในร่างกายสูง"
        else:  # female
            if bf < 20:
                body_fat_interpretation = "น้ำมันในร่างกายต่ำเกินไป"
            elif bf < 30:
                body_fat_interpretation = "น้ำมันในร่างกายปกติ"
            elif bf < 35:
                body_fat_interpretation = "น้ำมันในร่างกายสูงเล็กน้อย"
            else:
                body_fat_interpretation = "น้ำมันในร่างกายสูง"

    # Interpret visceral fat
    visceral_fat_interpretation = ""
    if bia_record.visceral_fat_kg:
        vf = bia_record.visceral_fat_kg
        if vf < 10:
            visceral_fat_interpretation = "ไขมันในช่องท้องปกติ"
        elif vf < 15:
            visceral_fat_interpretation = "ไขมันในช่องท้องสูงเล็กน้อย"
        else:
            visceral_fat_interpretation = "ไขมันในช่องท้องสูง มีความเสี่ยงต่อโรคเรื้อรัง"

    return {
        "bmi": float(bia_record.bmi) if bia_record.bmi else None,
        "bmi_category": bia_record.bmi_category,
        "body_fat_percentage": (
            float(bia_record.body_fat_percentage)
            if bia_record.body_fat_percentage
            else None
        ),
        "body_fat_interpretation": body_fat_interpretation,
        "visceral_fat_kg": (
            float(bia_record.visceral_fat_kg) if bia_record.visceral_fat_kg else None
        ),
        "visceral_fat_interpretation": visceral_fat_interpretation,
        "muscle_mass_kg": (
            float(bia_record.muscle_mass_kg) if bia_record.muscle_mass_kg else None
        ),
        "weight_management": bia_record.weight_management,
        "food_recommendation": bia_record.food_recommendation,
        "staff_signature": bia_record.staff_signature,
        "measurement_date": bia_record.measurement_date,
    }
