"""สร้างข้อมูล BIA ตัวอย่าง"""

from app.database import SessionLocal
from app.models import *
from datetime import date
from decimal import Decimal

db = SessionLocal()

try:
    # Check current data
    print("=== สถานะข้อมูลปัจจุบัน ===")
    print(f"✓ Users: {db.query(User).count()}")
    print(f"✓ Facilities: {db.query(Facility).count()}")
    print(f"✓ Scoring Versions: {db.query(ScoringRuleVersion).count()}")
    print(f"✓ Respondents: {db.query(Respondent).count()}")
    print(f"✓ Visits: {db.query(Visit).count()}")
    print(f"✓ SANSA Responses: {db.query(SANSAResponse).count()}")
    print(f"✓ MNA Responses: {db.query(MNAResponse).count()}")
    print(f"✓ BIA Records: {db.query(BIARecord).count()}")
    print(f"✓ Satisfaction: {db.query(SatisfactionResponse).count()}")

    # Get existing visit to add BIA record
    visit = db.query(Visit).first()
    if visit and db.query(BIARecord).filter_by(visit_id=visit.id).count() == 0:
        print(f"\n=== สร้างข้อมูล BIA ตัวอย่าง ===")
        bia = BIARecord(
            visit_id=visit.id,
            age=65,
            sex=Sex.FEMALE,
            waist_circumference_cm=Decimal("85.5"),
            weight_kg=Decimal("58.0"),
            height_cm=Decimal("155.0"),
            bmi=Decimal("24.1"),
            bmi_category="normal",
            fat_mass_kg=Decimal("18.5"),
            body_fat_percentage=Decimal("31.9"),
            visceral_fat_kg=Decimal("8.2"),
            muscle_mass_kg=Decimal("36.5"),
            bone_mass_kg=Decimal("2.3"),
            water_percentage=Decimal("48.5"),
            metabolic_rate=1250,
            hip_circumference_cm=Decimal("95.0"),
            waist_hip_ratio=Decimal("0.900"),
            weight_management="maintain",
            food_recommendation="balanced diet",
            measured_by=1,
            measurement_date=date.today(),
        )
        db.add(bia)
        db.commit()
        print(f"✓ เพิ่ม BIA record สำเร็จ (visit_id={visit.id})")
    else:
        print(f"\n✓ BIA record มีอยู่แล้ว หรือ ไม่มี visit")

    print(f"\n✓ Models ทั้งหมดใช้งานได้แล้ว!")

finally:
    db.close()
