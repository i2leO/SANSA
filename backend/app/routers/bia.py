from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models import BIARecord, Visit, User
from app.schemas import BIARecordCreate, BIARecordUpdate, BIARecordResponse, MessageResponse
from app.services.scoring_service import ScoringService
from app.auth import get_current_staff_or_admin

router = APIRouter(prefix="/bia", tags=["bia"])


@router.post("", response_model=BIARecordResponse)
def create_bia_record(
    bia_create: BIARecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin)
):
    """
    Create BIA (Body Impedance Analysis) record
    Staff/admin only - this is a clinical measurement tool
    """
    # Verify visit exists
    visit = db.query(Visit).filter(Visit.id == bia_create.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Check if BIA already exists for this visit
    existing = db.query(BIARecord).filter(
        BIARecord.visit_id == bia_create.visit_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="BIA record already exists for this visit"
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
        muscle_mass_kg=bia_create.muscle_mass_kg,
        bone_mass_kg=bia_create.bone_mass_kg,
        water_percentage=bia_create.water_percentage,
        metabolic_rate=bia_create.metabolic_rate,
        bmi_category=bmi_category,
        weight_management=bia_create.weight_management,
        food_recommendation=bia_create.food_recommendation,
        staff_signature=bia_create.staff_signature or current_user.username,
        measurement_date=bia_create.measurement_date or datetime.utcnow().date(),
        created_at=datetime.utcnow()
    )

    db.add(bia_record)
    db.commit()
    db.refresh(bia_record)

    return bia_record


@router.get("/{bia_record_id}", response_model=BIARecordResponse)
def get_bia_record(
    bia_record_id: int,
    db: Session = Depends(get_db)
):
    """Get BIA record by ID"""
    bia_record = db.query(BIARecord).filter(
        BIARecord.id == bia_record_id
    ).first()

    if not bia_record:
        raise HTTPException(status_code=404, detail="BIA record not found")

    return bia_record


@router.get("/visit/{visit_id}", response_model=BIARecordResponse)
def get_bia_by_visit(
    visit_id: int,
    db: Session = Depends(get_db)
):
    """Get BIA record by visit ID"""
    bia_record = db.query(BIARecord).filter(
        BIARecord.visit_id == visit_id
    ).first()

    if not bia_record:
        raise HTTPException(
            status_code=404,
            detail="BIA record not found for this visit"
        )

    return bia_record


@router.put("/{bia_record_id}", response_model=BIARecordResponse)
def update_bia_record(
    bia_record_id: int,
    bia_update: BIARecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin)
):
    """Update existing BIA record (staff/admin only)"""
    bia_record = db.query(BIARecord).filter(
        BIARecord.id == bia_record_id
    ).first()

    if not bia_record:
        raise HTTPException(status_code=404, detail="BIA record not found")

    # Update fields that are provided
    update_data = bia_update.dict(exclude_unset=True)

    # Recalculate BMI if weight or height changed
    if 'weight_kg' in update_data or 'height_cm' in update_data:
        weight = update_data.get('weight_kg', bia_record.weight_kg)
        height = update_data.get('height_cm', bia_record.height_cm)

        if weight and height:
            height_m = height / 100
            bmi = weight / (height_m * height_m)
            update_data['bmi'] = bmi

            # Update BMI category
            scoring_service = ScoringService(db)
            update_data['bmi_category'] = scoring_service.get_bmi_category(bmi)

    for field, value in update_data.items():
        setattr(bia_record, field, value)

    db.commit()
    db.refresh(bia_record)

    return bia_record


@router.delete("/{bia_record_id}", response_model=MessageResponse)
def delete_bia_record(
    bia_record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin)
):
    """Delete BIA record (staff/admin only)"""
    bia_record = db.query(BIARecord).filter(
        BIARecord.id == bia_record_id
    ).first()

    if not bia_record:
        raise HTTPException(status_code=404, detail="BIA record not found")

    db.delete(bia_record)
    db.commit()

    return {"message": "BIA record deleted successfully"}


@router.get("/visit/{visit_id}/interpretation")
def get_bia_interpretation(
    visit_id: int,
    db: Session = Depends(get_db)
):
    """Get BIA interpretation and recommendations"""
    bia_record = db.query(BIARecord).filter(
        BIARecord.visit_id == visit_id
    ).first()

    if not bia_record:
        raise HTTPException(
            status_code=404,
            detail="BIA record not found for this visit"
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
        "body_fat_percentage": float(bia_record.body_fat_percentage) if bia_record.body_fat_percentage else None,
        "body_fat_interpretation": body_fat_interpretation,
        "visceral_fat_kg": float(bia_record.visceral_fat_kg) if bia_record.visceral_fat_kg else None,
        "visceral_fat_interpretation": visceral_fat_interpretation,
        "muscle_mass_kg": float(bia_record.muscle_mass_kg) if bia_record.muscle_mass_kg else None,
        "weight_management": bia_record.weight_management,
        "food_recommendation": bia_record.food_recommendation,
        "staff_signature": bia_record.staff_signature,
        "measurement_date": bia_record.measurement_date
    }
