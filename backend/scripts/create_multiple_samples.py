"""สร้างข้อมูลตัวอย่างหลาย rows ตามภาพ Excel"""

from app.database import SessionLocal
from app.models import *
from decimal import Decimal
from datetime import date, timedelta

db = SessionLocal()

try:
    # ลบข้อมูลเก่า (ถ้ามี)
    db.query(SatisfactionResponse).delete()
    db.query(BIARecord).delete()
    db.query(MNAResponse).delete()
    db.query(SANSAResponse).delete()
    db.query(Visit).delete()
    db.query(Respondent).delete()
    db.commit()

    print("=== สร้างข้อมูลตัวอย่าง 4-5 records ===\n")

    # สร้าง Respondents 5 คน
    respondents = []
    for i in range(1, 6):
        resp = Respondent(
            respondent_code=f"R{2026000 + i}",
            status=RespondentStatus.ELDERLY if i <= 4 else RespondentStatus.CAREGIVER,
            age=65 + i,
            sex=Sex.FEMALE if i % 2 == 0 else Sex.MALE,
            education_level="primary" if i <= 2 else "secondary",
            marital_status="married" if i <= 3 else "single",
            monthly_income="5000-10000",
            income_sources='["pension"]',
            chronic_diseases='{"diabetes": false, "hypertension": true}',
            living_arrangement="with_family",
            created_by=1,
        )
        db.add(resp)
        respondents.append(resp)

    db.commit()
    print(f"✓ สร้าง Respondents: {len(respondents)} records")

    # สร้าง Visits
    visits = []
    for i, resp in enumerate(respondents, 1):
        visit = Visit(
            respondent_id=resp.id,
            visit_number=1,
            visit_date=date.today() - timedelta(days=i),
            facility_id=1,
            visit_type=VisitType.BASELINE,
            created_by=1,
        )
        db.add(visit)
        visits.append(visit)

    db.commit()
    print(f"✓ สร้าง Visits: {len(visits)} records")

    # สร้าง MNA Responses (ตามภาพ Excel rows 2-5)
    mna_data = [
        # Row 2
        {
            "screening_total": Decimal("13"),
            "assessment_total": Decimal("0"),
            "total": Decimal("13"),
        },
        # Row 3
        {
            "screening_total": Decimal("24.5"),
            "assessment_total": Decimal("0"),
            "total": Decimal("24.5"),
        },
        # Row 4
        {
            "screening_total": Decimal("0"),
            "assessment_total": Decimal("10.5"),
            "total": Decimal("10.5"),
        },
        # Row 5
        {
            "screening_total": Decimal("12"),
            "assessment_total": Decimal("20"),
            "total": Decimal("20"),
        },
    ]

    for i, (visit, data) in enumerate(zip(visits[:4], mna_data), 1):
        mna = MNAResponse(
            visit_id=visit.id,
            scoring_version_id=2,
            # Screening Q1-Q7
            q1_food_intake_decline=str(i % 3),
            q1_score=Decimal("2"),
            q2_weight_loss="1-3kg" if i % 2 == 0 else "0",
            q2_score=Decimal("2"),
            q3_mobility="walks" if i <= 2 else "bed_chair",
            q3_score=Decimal("2") if i <= 2 else Decimal("0"),
            q4_stress_illness="yes" if i % 2 == 1 else "no",
            q4_score=Decimal("2") if i % 2 == 1 else Decimal("0"),
            q5_neuropsychological="none" if i <= 2 else "mild",
            q5_score=Decimal("2") if i <= 2 else Decimal("1"),
            q6_bmi="21-23" if i <= 3 else "<19",
            q6_score=Decimal("2") if i <= 3 else Decimal("0"),
            q7_calf_circumference="31cm" if i % 2 == 0 else "29cm",
            q7_score=Decimal("0.5") if i % 2 == 0 else Decimal("0"),
            screening_total=data["screening_total"],
            # Assessment Q8-Q18
            q8_independent_living="yes",
            q8_score=Decimal("1"),
            q9_medications="3+" if i % 2 == 0 else "<3",
            q9_score=Decimal("0") if i % 2 == 0 else Decimal("1"),
            q10_pressure_sores="no",
            q10_score=Decimal("1"),
            q11_full_meals=str(2 + i % 2),
            q11_score=Decimal("1"),
            q12_protein_consumption=str(i % 3),
            q12_score=Decimal("0.5"),
            q13_fruits_vegetables=str(1 + i % 2),
            q13_score=Decimal("0") if i % 2 == 0 else Decimal("0.5"),
            q14_fluid_intake="3-5",
            q14_score=Decimal("0.5"),
            q15_eating_independence="self" if i <= 3 else "assisted",
            q15_score=Decimal("1") if i <= 3 else Decimal("0"),
            q16_self_nutrition="good" if i <= 2 else "fair",
            q16_score=Decimal("1") if i <= 2 else Decimal("0.5"),
            q17_health_comparison="better" if i % 2 == 0 else "same",
            q17_score=Decimal("2") if i % 2 == 0 else Decimal("1"),
            q18_mid_arm_circumference="22cm" if i <= 2 else "20cm",
            q18_score=Decimal("0.5"),
            assessment_total=data["assessment_total"],
            total_score=data["total"],
            result_category="normal" if data["total"] >= Decimal("24") else "at_risk",
            entry_mode=EntryMode.STAFF,
            created_by=1,
        )
        db.add(mna)

    db.commit()
    print(f"✓ สร้าง MNA Responses: 4 records")

    # สร้าง BIA Records (4 records)
    for i, visit in enumerate(visits[:4], 1):
        bia = BIARecord(
            visit_id=visit.id,
            age=65 + i,
            sex=Sex.FEMALE if i % 2 == 0 else Sex.MALE,
            waist_circumference_cm=Decimal(80 + i * 2),
            weight_kg=Decimal(55 + i * 3),
            height_cm=Decimal(155 + i),
            bmi=Decimal(23.0 + i * 0.5),
            bmi_category="normal" if i <= 2 else "overweight",
            fat_mass_kg=Decimal(15 + i * 2),
            body_fat_percentage=Decimal(28 + i * 2),
            visceral_fat_kg=Decimal(7 + i),
            muscle_mass_kg=Decimal(35 + i),
            bone_mass_kg=Decimal(2.2 + i * 0.1),
            water_percentage=Decimal(50 - i),
            metabolic_rate=1200 + i * 50,
            hip_circumference_cm=Decimal(92 + i * 2),
            waist_hip_ratio=Decimal(0.85 + i * 0.02),
            weight_management="maintain" if i <= 2 else "reduce",
            food_recommendation="balanced diet",
            measured_by=1,
            measurement_date=date.today() - timedelta(days=i),
        )
        db.add(bia)

    db.commit()
    print(f"✓ สร้าง BIA Records: 4 records")

    # สร้าง Satisfaction Responses (4 records)
    for i, visit in enumerate(visits[:4], 1):
        sat = SatisfactionResponse(
            visit_id=visit.id,
            q1_clarity=5 if i <= 2 else 4,
            q2_ease_of_use=4 + (i % 2),
            q3_confidence=4,
            q4_presentation=5 if i % 2 == 0 else 4,
            q5_results_display=4,
            q6_usefulness=5 if i <= 3 else 4,
            q7_overall_satisfaction=5 if i <= 2 else 4,
            comments=f"ทดสอบครั้งที่ {i}" if i <= 2 else None,
        )
        db.add(sat)

    db.commit()
    print(f"✓ สร้าง Satisfaction Responses: 4 records")

    # สรุป
    print(f"\n=== สรุปข้อมูลที่สร้าง ===")
    print(f"Respondents: {db.query(Respondent).count()}")
    print(f"Visits: {db.query(Visit).count()}")
    print(f"SANSA Responses: {db.query(SANSAResponse).count()}")
    print(f"MNA Responses: {db.query(MNAResponse).count()}")
    print(f"BIA Records: {db.query(BIARecord).count()}")
    print(f"Satisfaction: {db.query(SatisfactionResponse).count()}")

    print(f"\n✓ สร้างข้อมูลตัวอย่างหลาย rows สำเร็จ!")

finally:
    db.close()
