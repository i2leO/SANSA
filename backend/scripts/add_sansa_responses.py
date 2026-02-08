"""เพิ่ม SANSA Responses ให้ครบทุก visit"""

from app.database import SessionLocal
from app.models import *
from decimal import Decimal

db = SessionLocal()

try:
    print("=" * 80)
    print("เพิ่ม SANSA RESPONSES")
    print("=" * 80)

    # ดึง visits ทั้งหมด
    visits = db.query(Visit).all()
    print(f"พบ {len(visits)} visits\n")

    # ข้อมูลตัวอย่าง SANSA (หลากหลายระดับความเสี่ยง)
    sansa_samples = [
        # Visit 1 - ปกติ
        {
            "q1": "stable",
            "q1_score": 0,
            "q2": "normal",
            "q2_score": 0,
            "q3": "normal",
            "q3_score": 0,
            "q4": "no",
            "q4_score": 0,
            "q5": "3",
            "q5_score": 0,
            "q6": "normal",
            "q6_score": 0,
            "q7": "normal",
            "q7_score": 0,
            "q8": "daily",
            "q8_score": 1,
            "q9": "adequate",
            "q9_score": 1,
            "q10": "yes",
            "q10_score": 1,
            "q11": "daily",
            "q11_score": 1,
            "q12": "daily",
            "q12_score": 1,
            "q13": "6-8",
            "q13_score": 1,
            "q14": "none",
            "q14_score": 1,
            "q15": "boil_steam",
            "q15_score": 1,
            "q16": "no",
            "q16_score": 1,
            "screening_total": Decimal("0"),
            "diet_total": Decimal("9"),
            "total_score": Decimal("9"),
            "result_level": "normal",
        },
        # Visit 2 - เสี่ยงปานกลาง
        {
            "q1": "loss",
            "q1_score": 1,
            "q2": "decreased",
            "q2_score": 1,
            "q3": "reduced",
            "q3_score": 1,
            "q4": "yes",
            "q4_score": 1,
            "q5": "1-2",
            "q5_score": 1,
            "q6": "smaller",
            "q6_score": 1,
            "q7": "soft",
            "q7_score": 1,
            "q8": "sometimes",
            "q8_score": 0.5,
            "q9": "moderate",
            "q9_score": 0.5,
            "q10": "sometimes",
            "q10_score": 0.5,
            "q11": "sometimes",
            "q11_score": 0.5,
            "q12": "sometimes",
            "q12_score": 0.5,
            "q13": "3-5",
            "q13_score": 0.5,
            "q14": "sometimes",
            "q14_score": 0.5,
            "q15": "fry_stir",
            "q15_score": 0.5,
            "q16": "sometimes",
            "q16_score": 0.5,
            "screening_total": Decimal("7"),
            "diet_total": Decimal("4.5"),
            "total_score": Decimal("11.5"),
            "result_level": "moderate_risk",
        },
        # Visit 3 - เสี่ยงสูง
        {
            "q1": "loss",
            "q1_score": 1,
            "q2": "very_low",
            "q2_score": 2,
            "q3": "very_low",
            "q3_score": 2,
            "q4": "yes",
            "q4_score": 1,
            "q5": "0-1",
            "q5_score": 2,
            "q6": "much_smaller",
            "q6_score": 2,
            "q7": "liquid",
            "q7_score": 2,
            "q8": "rarely",
            "q8_score": 0,
            "q9": "inadequate",
            "q9_score": 0,
            "q10": "no",
            "q10_score": 0,
            "q11": "rarely",
            "q11_score": 0,
            "q12": "rarely",
            "q12_score": 0,
            "q13": "<3",
            "q13_score": 0,
            "q14": "often",
            "q14_score": 0,
            "q15": "fry_deep",
            "q15_score": 0,
            "q16": "yes",
            "q16_score": 0,
            "screening_total": Decimal("12"),
            "diet_total": Decimal("0"),
            "total_score": Decimal("12"),
            "result_level": "high_risk",
        },
        # Visit 4 - ปกติ
        {
            "q1": "gain",
            "q1_score": 0,
            "q2": "normal",
            "q2_score": 0,
            "q3": "normal",
            "q3_score": 0,
            "q4": "no",
            "q4_score": 0,
            "q5": "3",
            "q5_score": 0,
            "q6": "normal",
            "q6_score": 0,
            "q7": "normal",
            "q7_score": 0,
            "q8": "daily",
            "q8_score": 1,
            "q9": "adequate",
            "q9_score": 1,
            "q10": "yes",
            "q10_score": 1,
            "q11": "daily",
            "q11_score": 1,
            "q12": "sometimes",
            "q12_score": 0.5,
            "q13": "6-8",
            "q13_score": 1,
            "q14": "sometimes",
            "q14_score": 0.5,
            "q15": "boil_steam",
            "q15_score": 1,
            "q16": "no",
            "q16_score": 1,
            "screening_total": Decimal("0"),
            "diet_total": Decimal("8"),
            "total_score": Decimal("8"),
            "result_level": "normal",
        },
        # Visit 5 - เสี่ยงปานกลาง
        {
            "q1": "stable",
            "q1_score": 0,
            "q2": "decreased",
            "q2_score": 1,
            "q3": "reduced",
            "q3_score": 1,
            "q4": "yes",
            "q4_score": 1,
            "q5": "2",
            "q5_score": 0,
            "q6": "smaller",
            "q6_score": 1,
            "q7": "soft",
            "q7_score": 1,
            "q8": "sometimes",
            "q8_score": 0.5,
            "q9": "moderate",
            "q9_score": 0.5,
            "q10": "sometimes",
            "q10_score": 0.5,
            "q11": "sometimes",
            "q11_score": 0.5,
            "q12": "daily",
            "q12_score": 1,
            "q13": "3-5",
            "q13_score": 0.5,
            "q14": "none",
            "q14_score": 1,
            "q15": "fry_stir",
            "q15_score": 0.5,
            "q16": "sometimes",
            "q16_score": 0.5,
            "screening_total": Decimal("5"),
            "diet_total": Decimal("5.5"),
            "total_score": Decimal("10.5"),
            "result_level": "moderate_risk",
        },
    ]

    for i, visit in enumerate(visits):
        sample = sansa_samples[i % len(sansa_samples)]

        sansa = SANSAResponse(
            visit_id=visit.id,
            scoring_version_id=1,  # SANSA scoring version
            # Screening Q1-Q7
            q1_weight_change=sample["q1"],
            q1_score=Decimal(str(sample["q1_score"])),
            q2_food_intake=sample["q2"],
            q2_score=Decimal(str(sample["q2_score"])),
            q3_daily_activities=sample["q3"],
            q3_score=Decimal(str(sample["q3_score"])),
            q4_chronic_disease=sample["q4"],
            q4_score=Decimal(str(sample["q4_score"])),
            q5_meals_per_day=sample["q5"],
            q5_score=Decimal(str(sample["q5_score"])),
            q6_portion_size=sample["q6"],
            q6_score=Decimal(str(sample["q6_score"])),
            q7_food_texture=sample["q7"],
            q7_score=Decimal(str(sample["q7_score"])),
            screening_total=sample["screening_total"],
            # Diet Assessment Q8-Q16
            q8_rice_starch=sample["q8"],
            q8_score=Decimal(str(sample["q8_score"])),
            q9_protein=sample["q9"],
            q9_score=Decimal(str(sample["q9_score"])),
            q10_milk=sample["q10"],
            q10_score=Decimal(str(sample["q10_score"])),
            q11_fruits=sample["q11"],
            q11_score=Decimal(str(sample["q11_score"])),
            q12_vegetables=sample["q12"],
            q12_score=Decimal(str(sample["q12_score"])),
            q13_water=sample["q13"],
            q13_score=Decimal(str(sample["q13_score"])),
            q14_sweet_drinks=sample["q14"],
            q14_score=Decimal(str(sample["q14_score"])),
            q15_cooking_method=sample["q15"],
            q15_score=Decimal(str(sample["q15_score"])),
            q16_oil_coconut=sample["q16"],
            q16_score=Decimal(str(sample["q16_score"])),
            diet_total=sample["diet_total"],
            # Total
            total_score=sample["total_score"],
            result_level=sample["result_level"],
        )

        db.add(sansa)
        print(
            f'✓ Visit {visit.id}: Screening={float(sample["screening_total"]):4.1f}, Diet={float(sample["diet_total"]):4.1f}, Total={float(sample["total_score"]):5.1f} ({sample["result_level"]})'
        )

    db.commit()

    # สรุป
    print(f'\n{"=" * 80}')
    print(f"สร้าง SANSA Responses สำเร็จ: {len(visits)} records")
    print(f'{"=" * 80}')

    # นับข้อมูลทั้งหมด
    print(f"\nสรุปข้อมูลทั้งหมดในระบบ:")
    print(f"  - Respondents: {db.query(Respondent).count()}")
    print(f"  - Visits: {db.query(Visit).count()}")
    print(f"  - SANSA: {db.query(SANSAResponse).count()} ✓")
    print(f"  - MNA: {db.query(MNAResponse).count()}")
    print(f"  - BIA: {db.query(BIARecord).count()}")
    print(f"  - Satisfaction: {db.query(SatisfactionResponse).count()}")

finally:
    db.close()
