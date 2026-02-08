"""แสดงข้อมูล MNA แบบละเอียดทุกคำถาม"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse, Visit, Respondent

db = SessionLocal()

print("=" * 100)
print("📋 MNA RESPONSES - ข้อมูลทั้งหมด")
print("=" * 100)

mnas = db.query(MNAResponse).join(Visit).order_by(Visit.id).all()

print(f"\nพบ MNA ทั้งหมด: {len(mnas)} รายการ\n")

for idx, mna in enumerate(mnas, 1):
    visit = mna.visit
    resp = visit.respondent

    print(f"{'='*100}")
    print(f"Row {idx} | Visit #{visit.id} | Respondent: {resp.respondent_code}")
    print(f"{'='*100}")

    # Screening Questions (Q1-Q7)
    print("\n🔍 SCREENING (Q1-Q7):")
    print(
        f"  Q1 (Food intake decline):     {mna.q1_food_intake_decline}  [Score: {mna.mna_s1}]"
    )
    print(
        f"  Q2 (Weight loss):             {mna.q2_weight_loss}  [Score: {mna.mna_s2}]"
    )
    print(f"  Q3 (Mobility):                {mna.q3_mobility}  [Score: {mna.mna_s3}]")
    print(
        f"  Q4 (Stress/Illness):          {mna.q4_stress_illness}  [Score: {mna.mna_s4}]"
    )
    print(
        f"  Q5 (Neuropsychological):      {mna.q5_neuropsychological}  [Score: {mna.mna_s5}]"
    )
    print(f"  Q6 (BMI):                     {mna.q6_bmi}  [Score: {mna.mna_s6}]")
    print(
        f"  Q7 (Calf circumference):      {mna.q7_calf_circumference}  [Score: {mna.mna_s7}]"
    )
    print(f"  ➜ Screening Total: {mna.mna_screen_total}")

    # Assessment Questions (Q8-Q18)
    print("\n📝 ASSESSMENT (Q8-Q18):")
    print(
        f"  Q8  (Independent living):     {mna.q8_independent_living}  [Score: {mna.mna_a1}]"
    )
    print(
        f"  Q9  (Medications >3):         {mna.q9_medications}  [Score: {mna.mna_a2}]"
    )
    print(
        f"  Q10 (Pressure sores):         {mna.q10_pressure_sores}  [Score: {mna.mna_a3}]"
    )
    print(
        f"  Q11 (Full meals):             {mna.q11_full_meals}  [Score: {mna.mna_a4}]"
    )
    print(
        f"  Q12 (Protein consumption):    {mna.q12_protein_consumption}  [Score: {mna.mna_a5}]"
    )
    print(
        f"  Q13 (Fruits/veg):             {mna.q13_fruits_vegetables}  [Score: {mna.mna_a6}]"
    )
    print(
        f"  Q14 (Fluid intake):           {mna.q14_fluid_intake}  [Score: {mna.mna_a7}]"
    )
    print(
        f"  Q15 (Eating independence):    {mna.q15_eating_independence}  [Score: {mna.mna_a8}]"
    )
    print(
        f"  Q16 (Self nutrition):         {mna.q16_self_nutrition}  [Score: {mna.mna_a9}]"
    )
    print(
        f"  Q17 (Health comparison):      {mna.q17_health_comparison}  [Score: {mna.mna_a10}]"
    )
    print(
        f"  Q18 (Mid-arm circumference):  {mna.q18_mid_arm_circumference}  [Score: {mna.mna_a11}]"
    )
    print(f"  ➜ Assessment Total: {mna.mna_ass_total}")

    # Overall
    print(f"\n📊 TOTAL SCORE: {mna.mna_total}")
    print(f"🏷️  CATEGORY: {mna.result_category}\n")
