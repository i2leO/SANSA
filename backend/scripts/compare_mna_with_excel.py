"""เปรียบเทียบข้อมูล MNA ระหว่าง Excel กับระบบ"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse, Visit

# ข้อมูลจาก Excel (ตาม screenshot)
excel_data = [
    # Row 1: ID=1
    {
        "id": 1,
        "s": [2, 2, 2, 1, 2, 1, 1],
        "screen_total": 7,  # มีสีแดงใน Excel แสดงว่าผิด แต่ควรเป็น 11
        "screen_cat": 2,
        "a": [0, 0, 1, 2, 0.5, 1, 1, 1, 1, 0.5, 1],
        "a12": 2,
        "ass_total": 13,
        "total": 20,
    },
    # Row 2: ID=2
    {
        "id": 2,
        "s": [2, 2, 1, 2, 1, 1, 1],
        "screen_total": 10,
        "screen_cat": 2,
        "a": [0, 0, 1, 2, 0.5, 1, 1, 1, 1, 0.5, 1],
        "a12": 2,
        "ass_total": 11,
        "total": 21,
    },
    # Row 3: ID=3
    {
        "id": 3,
        "s": [2, 2, 2, 2, 2, 2, 2],
        "screen_total": 14,
        "screen_cat": 1,
        "a": [1, 1, 1, 1, 0.5, 1, 0.5, 2, 2, 2, 0.5],
        "a12": 0,
        "ass_total": 10.5,
        "total": 24.5,
    },
    # Row 4: ID=4
    {
        "id": 4,
        "s": [0, 1, 0, 1, 0, 0, 0],
        "screen_total": 2,
        "screen_cat": 3,
        "a": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "a12": 0,
        "ass_total": 0,
        "total": 2,
    },
    # Row 5: ID=5
    {
        "id": 5,
        "s": [2, 2, 2, 2, 2, 2, 2],
        "screen_total": 14,
        "screen_cat": 1,
        "a": [1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        "a12": 2,
        "ass_total": 12,
        "total": 26,  # 14 + 12
    },
]

db = SessionLocal()
mnas = db.query(MNAResponse).join(Visit).order_by(Visit.id).all()

print("\n" + "=" * 150)
print("📊 เปรียบเทียบข้อมูล MNA: Excel vs ระบบปัจจุบัน")
print("=" * 150)

for idx, (excel, mna) in enumerate(zip(excel_data, mnas)):
    print(f"\n{'='*150}")
    print(f"Row {idx} | Visit #{mna.visit_id} | Excel ID={excel['id']}")
    print(f"{'='*150}")

    # Screening (s1-s7)
    print("\n🔍 SCREENING (s1-s7):")
    system_s = [
        mna.q1_score,
        mna.q2_score,
        mna.q3_score,
        mna.q4_score,
        mna.q5_score,
        mna.q6_score,
        mna.q7_score,
    ]

    for i, (ex, sys) in enumerate(zip(excel["s"], system_s), 1):
        match = "✅" if float(ex) == float(sys) else "❌"
        print(f"  s{i}: Excel={ex:4.1f} | System={float(sys):4.1f} {match}")

    match = "✅" if float(excel["screen_total"]) == float(mna.screening_total) else "❌"
    print(
        f"  Screen Total: Excel={excel['screen_total']:5.1f} | System={float(mna.screening_total):5.1f} {match}"
    )

    # Assessment (a1-a11)
    print("\n📝 ASSESSMENT (a1-a11):")
    system_a = [
        mna.q8_score,
        mna.q9_score,
        mna.q10_score,
        mna.q11_score,
        mna.q12_score,
        mna.q13_score,
        mna.q14_score,
        mna.q15_score,
        mna.q16_score,
        mna.q17_score,
        mna.q18_score,
    ]

    for i, (ex, sys) in enumerate(zip(excel["a"], system_a), 1):
        match = "✅" if float(ex) == float(sys) else "❌"
        print(f"  a{i}: Excel={ex:4.1f} | System={float(sys):4.1f} {match}")

    match = "✅" if float(excel["ass_total"]) == float(mna.assessment_total) else "❌"
    print(
        f"  Assessment Total: Excel={excel['ass_total']:5.1f} | System={float(mna.assessment_total):5.1f} {match}"
    )

    match = "✅" if float(excel["total"]) == float(mna.total_score) else "❌"
    print(
        f"  TOTAL Score: Excel={excel['total']:5.1f} | System={float(mna.total_score):5.1f} {match}"
    )

print("\n" + "=" * 150)
print("✅ = ตรงกัน | ❌ = ไม่ตรงกัน")
print("=" * 150 + "\n")

db.close()
