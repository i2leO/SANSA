"""แก้ไขข้อมูล MNA ให้ตรงกับ Excel (อ่านใหม่จากภาพที่ชัดเจน)"""

import sys
from pathlib import Path
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse

# ข้อมูลที่ถูกต้องจาก Excel (อ่านจากภาพใหม่)
# Row numbering: Excel row 3 = ID 1, row 4 = ID 2, etc.
# Visit mapping: ต้องเช็คว่า Excel ID 1-5 map กับ Visit ID ไหน

correct_data = [
    # Excel Row 3 (ID=1) -> Visit 5
    {
        "visit_id": 5,
        "excel_id": 1,
        "scores": {
            # Screening (s1-s7)
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 1,
            "q4_score": 2,
            "q5_score": 1,
            "q6_score": 1,
            "q7_score": 1,
            "screening_total": 10,  # sum = 10 (Excel shows 10 in red, likely wrong sum display)
            # Assessment (a1-a11 -> q8-q18)
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
            "assessment_total": 9,  # a1-a11 sum (not including a12)
            "total_score": 21,  # Excel shows 21 but 10+9=19 (keeping Excel value)
        },
    },
    # Excel Row 4 (ID=2) -> Visit 6
    {
        "visit_id": 6,
        "excel_id": 2,
        "scores": {
            # Screening: 2,2,1,0,1,2,2 (from Excel visible cells)
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 1,
            "q4_score": 0,
            "q5_score": 1,
            "q6_score": 2,
            "q7_score": 2,
            "screening_total": 10,
            # Assessment
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
            "total_score": 21,
        },
    },
    # Excel Row 5 (ID=3) -> Visit 7
    {
        "visit_id": 7,
        "excel_id": 3,
        "scores": {
            # Screening: 2,2,2,2,2,2,2 (from Excel)
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 2,
            "q4_score": 2,
            "q5_score": 2,
            "q6_score": 2,
            "q7_score": 2,
            "screening_total": 14,
            # Assessment: 1,1,1,1,0.5,1,0.5,2,2,2,0.5
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
            "assessment_total": 12,  # from Excel (but sum = 13)
            "total_score": 24.5,  # Excel shows 24.5
        },
    },
    # Excel Row 6 (ID=4) -> Visit 8
    {
        "visit_id": 8,
        "excel_id": 4,
        "scores": {
            # Screening: 1,0,2,1,0,0,0 (from Excel)
            "q1_score": 1,
            "q2_score": 0,
            "q3_score": 2,
            "q4_score": 1,
            "q5_score": 0,
            "q6_score": 0,
            "q7_score": 0,
            "screening_total": 4,
            # Assessment: all zeros
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
            "total_score": 2,  # Excel shows 2 (but screening sum = 4)
        },
    },
    # Excel Row 7 (ID=5) -> Visit 9
    {
        "visit_id": 9,
        "excel_id": 5,
        "scores": {
            # Screening: 2,2,2,2,2,2,2
            "q1_score": 2,
            "q2_score": 2,
            "q3_score": 2,
            "q4_score": 2,
            "q5_score": 2,
            "q6_score": 2,
            "q7_score": 2,
            "screening_total": 14,
            # Assessment: 1,1,0,1,1,1,1,1,1,1,1
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
            "total_score": 26,  # Excel shows 26 (but 14+10=24)
        },
    },
]

db = SessionLocal()

print("\n" + "=" * 120)
print("🔧 แก้ไขข้อมูล MNA ให้ตรงกับ Excel (อ่านใหม่จากภาพที่ชัดเจน)")
print("=" * 120 + "\n")

for data in correct_data:
    visit_id = data["visit_id"]
    excel_id = data["excel_id"]
    scores = data["scores"]

    mna = db.query(MNAResponse).filter_by(visit_id=visit_id).first()

    if not mna:
        print(f"❌ ไม่พบ MNA response สำหรับ Visit {visit_id}")
        continue

    print(f"📝 Visit {visit_id} (Excel ID={excel_id}):")
    print(
        f"   Before: s1-s7=[{mna.q1_score},{mna.q2_score},{mna.q3_score},{mna.q4_score},{mna.q5_score},{mna.q6_score},{mna.q7_score}]"
    )
    print(f"           screen_total={mna.screening_total}, total={mna.total_score}")

    # อัพเดทคะแนนทั้งหมด
    for field, value in scores.items():
        setattr(mna, field, Decimal(str(value)))

    print(
        f"   After:  s1-s7=[{scores['q1_score']},{scores['q2_score']},{scores['q3_score']},{scores['q4_score']},{scores['q5_score']},{scores['q6_score']},{scores['q7_score']}]"
    )
    print(
        f"           screen_total={scores['screening_total']}, total={scores['total_score']}"
    )
    print(f"   ✅ Updated!\n")

# บันทึกการเปลี่ยนแปลง
db.commit()
print("=" * 120)
print("✅ แก้ไขข้อมูลสำเร็จทั้ง 5 แถว (อ่านจากภาพใหม่)")
print("=" * 120 + "\n")

print("📊 กรุณาตรวจสอบว่าข้อมูลตรงกับ Excel แล้ว โดยเปิด phpMyAdmin ดู:")
print("   http://localhost/phpMyAdmin หรือรันสคริปต์เปรียบเทียบอีกครั้ง\n")

db.close()
