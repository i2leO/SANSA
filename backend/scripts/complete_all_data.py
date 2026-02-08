"""เติมข้อมูลให้ครบทุก visit"""

from app.database import SessionLocal
from app.models import *
from decimal import Decimal
from datetime import date

db = SessionLocal()

try:
    print("=" * 80)
    print("เติมข้อมูลให้ครบทุก VISIT")
    print("=" * 80)

    # หา visit ที่ยังไม่มี MNA
    visits_without_mna = (
        db.query(Visit).filter(~Visit.id.in_(db.query(MNAResponse.visit_id))).all()
    )

    print(f"\nVisits ที่ยังไม่มี MNA: {len(visits_without_mna)}")
    for v in visits_without_mna:
        mna = MNAResponse(
            visit_id=v.id,
            scoring_version_id=2,
            # Screening
            q1_food_intake_decline="2",
            q1_score=Decimal("2"),
            q2_weight_loss="no",
            q2_score=Decimal("2"),
            q3_mobility="walks",
            q3_score=Decimal("2"),
            q4_stress_illness="no",
            q4_score=Decimal("2"),
            q5_neuropsychological="none",
            q5_score=Decimal("2"),
            q6_bmi="23-24.9",
            q6_score=Decimal("3"),
            q7_calf_circumference="33cm",
            q7_score=Decimal("3"),
            screening_total=Decimal("14"),
            # Assessment
            q8_independent_living="yes",
            q8_score=Decimal("1"),
            q9_medications="<3",
            q9_score=Decimal("1"),
            q10_pressure_sores="no",
            q10_score=Decimal("1"),
            q11_full_meals="3",
            q11_score=Decimal("1"),
            q12_protein_consumption="2",
            q12_score=Decimal("1"),
            q13_fruits_vegetables="2",
            q13_score=Decimal("0.5"),
            q14_fluid_intake="5-7",
            q14_score=Decimal("1"),
            q15_eating_independence="self",
            q15_score=Decimal("1"),
            q16_self_nutrition="good",
            q16_score=Decimal("1"),
            q17_health_comparison="same",
            q17_score=Decimal("1"),
            q18_mid_arm_circumference="24cm",
            q18_score=Decimal("1"),
            assessment_total=Decimal("11.5"),
            total_score=Decimal("25.5"),
            result_category="normal",
            entry_mode=EntryMode.STAFF,
            created_by=1,
        )
        db.add(mna)
        print(f"  ✓ Visit {v.id}: MNA added (total=25.5, normal)")

    # หา visit ที่ยังไม่มี BIA
    visits_without_bia = (
        db.query(Visit).filter(~Visit.id.in_(db.query(BIARecord.visit_id))).all()
    )

    print(f"\nVisits ที่ยังไม่มี BIA: {len(visits_without_bia)}")
    for v in visits_without_bia:
        bia = BIARecord(
            visit_id=v.id,
            age=70,
            sex=Sex.MALE,
            waist_circumference_cm=Decimal("90"),
            weight_kg=Decimal("70"),
            height_cm=Decimal("160"),
            bmi=Decimal("27.3"),
            bmi_category="overweight",
            fat_mass_kg=Decimal("25"),
            body_fat_percentage=Decimal("35.7"),
            visceral_fat_kg=Decimal("12"),
            muscle_mass_kg=Decimal("40"),
            bone_mass_kg=Decimal("2.8"),
            water_percentage=Decimal("45"),
            metabolic_rate=1450,
            hip_circumference_cm=Decimal("102"),
            waist_hip_ratio=Decimal("0.88"),
            weight_management="reduce",
            food_recommendation="low fat, high protein",
            measured_by=1,
            measurement_date=date.today(),
        )
        db.add(bia)
        print(f"  ✓ Visit {v.id}: BIA added (BMI=27.3, overweight)")

    # หา visit ที่ยังไม่มี Satisfaction
    visits_without_sat = (
        db.query(Visit)
        .filter(~Visit.id.in_(db.query(SatisfactionResponse.visit_id)))
        .all()
    )

    print(f"\nVisits ที่ยังไม่มี Satisfaction: {len(visits_without_sat)}")
    for v in visits_without_sat:
        sat = SatisfactionResponse(
            visit_id=v.id,
            q1_clarity=4,
            q2_ease_of_use=5,
            q3_confidence=4,
            q4_presentation=4,
            q5_results_display=5,
            q6_usefulness=5,
            q7_overall_satisfaction=4,
            comments="ดีมากครับ",
        )
        db.add(sat)
        avg = (4 + 5 + 4 + 4 + 5 + 5 + 4) / 7.0
        print(f"  ✓ Visit {v.id}: Satisfaction added (avg={avg:.2f}/5.00)")

    db.commit()

    print(f'\n{"=" * 80}')
    print("สรุปข้อมูลทั้งหมด:")
    print(f'{"=" * 80}')
    print(f"  Respondents:  {db.query(Respondent).count()}")
    print(f"  Visits:       {db.query(Visit).count()}")
    print(f"  SANSA:        {db.query(SANSAResponse).count()}")
    print(f"  MNA:          {db.query(MNAResponse).count()}")
    print(f"  BIA:          {db.query(BIARecord).count()}")
    print(f"  Satisfaction: {db.query(SatisfactionResponse).count()}")
    print(f'{"=" * 80}')
    print("ครบทุก assessment แล้ว! ✓")

finally:
    db.close()
