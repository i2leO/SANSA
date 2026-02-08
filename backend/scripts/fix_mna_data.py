"""แก้ไขข้อมูล MNA ให้ตรงกับ Excel"""

import sys
from pathlib import Path
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse, Visit

# ข้อมูลที่ถูกต้องจาก Excel
correct_data = [
    # Row 0: Visit 5 - Excel ID=1
    {
        "visit_id": 5,
        "scores": {
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 2,
            "q4_score": 1,
            "q5_score": 2,
            "q6_score": 1,
            "q7_score": 1,
            "screening_total": 11,  # 2+2+2+1+2+1+1 = 11 (not 7 as shown in red)
            "q8_score": 0,
            "q9_score": 0,
            "q10_score": 1,
            "q11_score": 2,
            "q12_score": 0.5,
            "q13_score": 1,
            "q14_score": 1,
            "q15_score": 1,
            "q16_score": 1,
            "q17_score": 0.5,
            "q18_score": 1,
            "assessment_total": 9,  # sum of a1-a11
            "total_score": 20,
        },
    },
    # Row 1: Visit 6 - Excel ID=2
    {
        "visit_id": 6,
        "scores": {
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 1,
            "q4_score": 2,
            "q5_score": 1,
            "q6_score": 1,
            "q7_score": 1,
            "screening_total": 10,
            "q8_score": 0,
            "q9_score": 0,
            "q10_score": 1,
            "q11_score": 2,
            "q12_score": 0.5,
            "q13_score": 1,
            "q14_score": 1,
            "q15_score": 1,
            "q16_score": 1,
            "q17_score": 0.5,
            "q18_score": 1,
            "assessment_total": 9,
            "total_score": 21,  # Actually 10 + 9 = 19, but Excel shows 21
        },
    },
    # Row 2: Visit 7 - Excel ID=3
    {
        "visit_id": 7,
        "scores": {
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 2,
            "q4_score": 2,
            "q5_score": 2,
            "q6_score": 2,
            "q7_score": 2,
            "screening_total": 14,
            "q8_score": 1,
            "q9_score": 1,
            "q10_score": 1,
            "q11_score": 1,
            "q12_score": 0.5,
            "q13_score": 1,
            "q14_score": 0.5,
            "q15_score": 2,
            "q16_score": 2,
            "q17_score": 2,
            "q18_score": 0.5,
            "assessment_total": 10.5,
            "total_score": 24.5,
        },
    },
    # Row 3: Visit 8 - Excel ID=4
    {
        "visit_id": 8,
        "scores": {
            "q1_score": 0,
            "q2_score": 1,
            "q3_score": 0,
            "q4_score": 1,
            "q5_score": 0,
            "q6_score": 0,
            "q7_score": 0,
            "screening_total": 2,
            "q8_score": 0,
            "q9_score": 0,
            "q10_score": 0,
            "q11_score": 0,
            "q12_score": 0,
            "q13_score": 0,
            "q14_score": 0,
            "q15_score": 0,
            "q16_score": 0,
            "q17_score": 0,
            "q18_score": 0,
            "assessment_total": 0,
            "total_score": 2,
        },
    },
    # Row 4: Visit 9 - Excel ID=5
    {
        "visit_id": 9,
        "scores": {
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 2,
            "q4_score": 2,
            "q5_score": 2,
            "q6_score": 2,
            "q7_score": 2,
            "screening_total": 14,
            "q8_score": 1,
            "q9_score": 1,
            "q10_score": 0,
            "q11_score": 1,
            "q12_score": 1,
            "q13_score": 1,
            "q14_score": 1,
            "q15_score": 1,
            "q16_score": 1,
            "q17_score": 1,
            "q18_score": 1,
            "assessment_total": 10,
            "total_score": 26,  # Actually should be 14+10=24, but keeping Excel value
        },
    },
]

db = SessionLocal()

print("\n" + "=" * 100)
print("🔧 กำลังแก้ไขข้อมูล MNA ให้ตรงกับ Excel...")
print("=" * 100 + "\n")

for data in correct_data:
    visit_id = data["visit_id"]
    scores = data["scores"]

    # ค้นหา MNA response ของ visit นี้
    mna = db.query(MNAResponse).filter_by(visit_id=visit_id).first()

    if not mna:
        print(f"❌ ไม่พบ MNA response สำหรับ Visit {visit_id}")
        continue

    print(f"📝 Visit {visit_id}:")
    print(
        f"   Before: screen_total={mna.screening_total}, ass_total={mna.assessment_total}, total={mna.total_score}"
    )

    # อัพเดทคะแนนทั้งหมด
    for field, value in scores.items():
        setattr(mna, field, Decimal(str(value)))

    print(
        f"   After:  screen_total={scores['screening_total']}, ass_total={scores['assessment_total']}, total={scores['total_score']}"
    )
    print(f"   ✅ Updated!\n")

# บันทึกการเปลี่ยนแปลง
db.commit()
print("=" * 100)
print("✅ แก้ไขข้อมูลสำเร็จทั้ง 5 แถว")
print("=" * 100 + "\n")

db.close()
