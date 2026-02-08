"""แสดงข้อมูล MNA ในรูปแบบ Excel เพื่อเปรียบเทียบ"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse, Visit

db = SessionLocal()

# ดึงข้อมูล MNA ทั้งหมดจากน้อยไปมาก according to visit_id
mnas = db.query(MNAResponse).join(Visit).order_by(Visit.id).all()

print("\n" + "=" * 120)
print("📋 MNA DATA - Excel Format Comparison")
print("=" * 120)

# Header
print(
    "\nRow | Visit | mna_s1 | mna_s2 | mna_s3 | mna_s4 | mna_s5 | mna_s6 | mna_s7 | screen_total | scr_cat"
)
print("-" * 120)

for idx, mna in enumerate(mnas):
    # แสดงเฉพาะ scores (คะแนนที่ได้)
    print(
        f" {idx}  |   {mna.visit_id}   |  {mna.q1_score:4.1f}  |  {mna.q2_score:4.1f}  |  {mna.q3_score:4.1f}  |  {mna.q4_score:4.1f}  |  {mna.q5_score:4.1f}  |  {mna.q6_score:4.1f}  |  {mna.q7_score:4.1f}  |    {mna.screening_total:5.1f}     | {mna.result_category}"
    )

print("\n" + "=" * 120)
print(
    "\nRow | mna_a1 | mna_a2 | mna_a3 | mna_a4 | mna_a5 | mna_a6 | mna_a7 | mna_a8 | mna_a9 | mna_a10 | mna_a11 | ass_total | mna_total"
)
print("-" * 120)

for idx, mna in enumerate(mnas):
    # Q8-Q18 คือ assessment questions (11 questions)
    # mna_a1 = Q8, mna_a2 = Q9, ... mna_a11 = Q18
    print(
        f" {idx}  |  {mna.q8_score:4.1f}  |  {mna.q9_score:4.1f}  |  {mna.q10_score:4.1f}  |  {mna.q11_score:4.1f}  |  {mna.q12_score:4.1f}  |  {mna.q13_score:4.1f}  |  {mna.q14_score:4.1f}  |  {mna.q15_score:4.1f}  |  {mna.q16_score:4.1f}  |   {mna.q17_score:4.1f}  |   {mna.q18_score:4.1f}  |   {mna.assessment_total:6.1f}    |   {mna.total_score:5.1f}"
    )

print("\n" + "=" * 120)
print("\n✅ กรุณาเปรียบเทียบกับข้อมูลใน Excel และบอกผมว่าแถวไหนไม่ตรงครับ")
print("   แล้วผมจะแก้ไขให้ตรงกับข้อมูลที่ถูกต้อง\n")

db.close()
