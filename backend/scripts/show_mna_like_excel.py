"""แสดงข้อมูล MNA ในรูปแบบเหมือน Excel เป๊ะ"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse, Visit

db = SessionLocal()
mnas = db.query(MNAResponse).join(Visit).order_by(Visit.id).all()

print("\n" + "=" * 180)
print("📋 ข้อมูล MNA ในระบบปัจจุบัน (รูปแบบเหมือน Excel)")
print("=" * 180)

# Header row (like Excel)
print(
    "\nID | mna_s1 | mna_s2 | mna_s3 | mna_s4 | mna_s5 | mna_s6 | mna_s7 | mna_screen_total | mna_scr_cat | mna_a1 | mna_a2 | mna_a3 | mna_a4 | mna_a5 | mna_a6 | mna_a7 | mna_a8 | mna_a9 | mna_a10 | mna_a11 | mna_a12 | mna_ass_total | mna_total"
)
print("-" * 180)

# Data rows
for idx, mna in enumerate(mnas, 1):
    # Screening (s1-s7 = q1-q7)
    s1, s2, s3, s4, s5, s6, s7 = (
        mna.q1_score,
        mna.q2_score,
        mna.q3_score,
        mna.q4_score,
        mna.q5_score,
        mna.q6_score,
        mna.q7_score,
    )
    screen_total = mna.screening_total
    scr_cat = "?"  # ไม่มีในระบบ

    # Assessment (a1-a11 = q8-q18)
    a1, a2, a3, a4, a5, a6 = (
        mna.q8_score,
        mna.q9_score,
        mna.q10_score,
        mna.q11_score,
        mna.q12_score,
        mna.q13_score,
    )
    a7, a8, a9, a10, a11 = (
        mna.q14_score,
        mna.q15_score,
        mna.q16_score,
        mna.q17_score,
        mna.q18_score,
    )
    a12 = "?"  # ไม่มีในระบบ (Excel มี column นี้)
    ass_total = mna.assessment_total
    total = mna.total_score

    print(
        f" {idx} | {s1:6.1f} | {s2:6.1f} | {s3:6.1f} | {s4:6.1f} | {s5:6.1f} | {s6:6.1f} | {s7:6.1f} | {screen_total:16.1f} | {scr_cat:>11} | {a1:6.1f} | {a2:6.1f} | {a3:6.1f} | {a4:6.1f} | {a5:6.1f} | {a6:6.1f} | {a7:6.1f} | {a8:6.1f} | {a9:6.1f} | {a10:7.1f} | {a11:7.1f} | {a12:>7} | {ass_total:13.1f} | {total:9.1f}"
    )

print("\n" + "=" * 180)
print("📝 กรุณาเปรียบเทียบกับ Excel แล้วบอกผม:")
print("   1. แถวไหนไม่ตรง?")
print("   2. ค่าที่ถูกต้องควรเป็นเท่าไหร่?")
print("   หรือ copy ข้อมูลจาก Excel มาให้ผมได้เลยครับ")
print("=" * 180 + "\n")

db.close()
