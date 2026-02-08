"""แสดงสรุปข้อมูลทั้งหมดในระบบ"""

from app.database import SessionLocal
from app.models import *

db = SessionLocal()

try:
    print("=== สรุปข้อมูลในระบบ SANSA ===\n")
    print(f"Users: {db.query(User).count()}")
    print(f"Facilities: {db.query(Facility).count()}")
    print(f"Scoring Versions: {db.query(ScoringRuleVersion).count()}")
    print(f"Respondents: {db.query(Respondent).count()}")
    print(f"Visits: {db.query(Visit).count()}")
    print(f"SANSA Responses: {db.query(SANSAResponse).count()}")
    print(f"MNA Responses: {db.query(MNAResponse).count()}")
    print(f"BIA Records: {db.query(BIARecord).count()}")
    print(f"Satisfaction: {db.query(SatisfactionResponse).count()}")

    print("\n=== รายละเอียดข้อมูล ===")

    # Show MNA data
    mna = db.query(MNAResponse).first()
    if mna:
        print(f"\nMNA (visit_id={mna.visit_id}):")
        print(f"  Screening (Q1-Q7): total={mna.screening_total}")
        print(
            f"    Q1={mna.q1_food_intake_decline}({mna.q1_score}), Q2={mna.q2_weight_loss}({mna.q2_score})"
        )
        print(
            f"    Q3={mna.q3_mobility}({mna.q3_score}), Q4={mna.q4_stress_illness}({mna.q4_score})"
        )
        print(f"  Assessment (Q8-Q18): total={mna.assessment_total}")
        print(f"  Total Score: {mna.total_score} -> {mna.result_category}")

    # Show BIA data
    bia = db.query(BIARecord).first()
    if bia:
        print(f"\nBIA (visit_id={bia.visit_id}):")
        print(f"  Age={bia.age}, Sex={bia.sex}")
        print(
            f"  Weight={bia.weight_kg}kg, Height={bia.height_cm}cm, BMI={bia.bmi} ({bia.bmi_category})"
        )
        print(f"  Body Fat={bia.body_fat_percentage}%, Muscle={bia.muscle_mass_kg}kg")
        print(
            f"  Waist={bia.waist_circumference_cm}cm, Hip={bia.hip_circumference_cm}cm, WHR={bia.waist_hip_ratio}"
        )

    # Show Satisfaction
    sat = db.query(SatisfactionResponse).first()
    if sat:
        print(f"\nSatisfaction (visit_id={sat.visit_id}):")
        print(f"  Q1={sat.q1_clarity}, Q2={sat.q2_ease_of_use}, Q3={sat.q3_confidence}")
        print(f"  Q4={sat.q4_presentation}, Q5={sat.q5_results_display}")
        print(f"  Q6={sat.q6_usefulness}, Q7={sat.q7_overall_satisfaction}")
        avg = (
            sat.q1_clarity
            + sat.q2_ease_of_use
            + sat.q3_confidence
            + sat.q4_presentation
            + sat.q5_results_display
            + sat.q6_usefulness
            + sat.q7_overall_satisfaction
        ) / 7.0
        print(f"  Average: {avg:.2f}/5.00")

    print("\n*** ข้อมูลครบถ้วนแล้ว! ***")

finally:
    db.close()
