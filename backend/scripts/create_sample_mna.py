"""สร้างข้อมูล MNA ตัวอย่างตาม Excel structure"""

from app.database import SessionLocal
from app.models import *
from decimal import Decimal

db = SessionLocal()

try:
    # Check current MNA data
    mna_count = db.query(MNAResponse).count()
    print(f"MNA Responses currently: {mna_count}")

    # Get visit without MNA (visit_id=3)
    visit = db.query(Visit).filter(Visit.id == 3).first()

    if visit:
        # Check if already has MNA
        existing = db.query(MNAResponse).filter_by(visit_id=visit.id).first()
        if existing:
            print(f"Visit {visit.id} already has MNA")
        else:
            print(f"Creating MNA for visit_id={visit.id}")

            # Create sample MNA data matching Excel structure
            # mna_a1-a7 = Q1-Q7 (screening), mna_b1-b12 = Q8-Q18 (assessment)
            mna = MNAResponse(
                visit_id=visit.id,
                scoring_version_id=2,  # MNA version
                # Screening section (Q1-Q7) = mna_a1-a7
                q1_food_intake_decline="0",
                q1_score=Decimal("2"),
                q2_weight_loss="1-3kg",
                q2_score=Decimal("2"),
                q3_mobility="bed_chair",
                q3_score=Decimal("2"),
                q4_stress_illness="yes",
                q4_score=Decimal("2"),
                q5_neuropsychological="mild",
                q5_score=Decimal("1"),
                q6_bmi="21-23",
                q6_score=Decimal("2"),
                q7_calf_circumference="31cm",
                q7_score=Decimal("0"),
                screening_total=Decimal("14"),
                # Assessment section (Q8-Q18) = mna_b1-b12
                q8_independent_living="yes",
                q8_score=Decimal("1"),
                q9_medications="3+",
                q9_score=Decimal("0"),
                q10_pressure_sores="no",
                q10_score=Decimal("1"),
                q11_full_meals="2",
                q11_score=Decimal("1"),
                q12_protein_consumption="1",
                q12_score=Decimal("0.5"),
                q13_fruits_vegetables="1",
                q13_score=Decimal("0"),
                q14_fluid_intake="3-5",
                q14_score=Decimal("0.5"),
                q15_eating_independence="self",
                q15_score=Decimal("1"),
                q16_self_nutrition="good",
                q16_score=Decimal("1"),
                q17_health_comparison="better",
                q17_score=Decimal("2"),
                q18_mid_arm_circumference="22cm",
                q18_score=Decimal("0.5"),
                assessment_total=Decimal("10.5"),
                total_score=Decimal("24.5"),
                result_category="normal",
                entry_mode=EntryMode.STAFF,
                created_by=1,
            )
            db.add(mna)
            db.commit()
            print("✓ เพิ่ม MNA response สำเร็จ!")
    else:
        print("ไม่พบ visit_id=2")

finally:
    db.close()
