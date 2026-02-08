"""
Import MNA data จาก Excel format (ใช้ชื่อคอลัมน์แบบ mna_s1, mna_a1, etc.)
แล้วแปลงเป็นชื่อคอลัมน์ใน Database (q1_score, q8_score, etc.)
"""

import sys
from pathlib import Path
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MNAResponse

# Mapping: Excel column name -> Database field name
EXCEL_TO_DB_MAPPING = {
    # Screening (s1-s7 -> q1-q7)
    "mna_s1": "q1_score",
    "mna_s2": "q2_score",
    "mna_s3": "q3_score",
    "mna_s4": "q4_score",
    "mna_s5": "q5_score",
    "mna_s6": "q6_score",
    "mna_s7": "q7_score",
    "mna_screen_total": "screening_total",
    # Assessment (a1-a11 -> q8-q18)
    "mna_a1": "q8_score",
    "mna_a2": "q9_score",
    "mna_a3": "q10_score",
    "mna_a4": "q11_score",
    "mna_a5": "q12_score",
    "mna_a6": "q13_score",
    "mna_a7": "q14_score",
    "mna_a8": "q15_score",
    "mna_a9": "q16_score",
    "mna_a10": "q17_score",
    "mna_a11": "q18_score",
    "mna_ass_total": "assessment_total",
    "mna_total": "total_score",
}

# ข้อมูลจาก Excel (ใช้ชื่อคอลัมน์แบบ Excel)
# คุณสามารถแก้ไขข้อมูลตรงนี้ให้ตรงกับ Excel ของคุณ
excel_data = [
    {
        "visit_id": 5,
        "mna_s1": 2,
        "mna_s2": 2,
        "mna_s3": 2,
        "mna_s4": 1,
        "mna_s5": 2,
        "mna_s6": 1,
        "mna_s7": 1,
        "mna_screen_total": 11,
        "mna_a1": 0,
        "mna_a2": 0,
        "mna_a3": 1,
        "mna_a4": 2,
        "mna_a5": 0.5,
        "mna_a6": 1,
        "mna_a7": 1,
        "mna_a8": 1,
        "mna_a9": 1,
        "mna_a10": 0.5,
        "mna_a11": 1,
        "mna_ass_total": 9,
        "mna_total": 20,
    },
    {
        "visit_id": 6,
        "mna_s1": 2,
        "mna_s2": 2,
        "mna_s3": 1,
        "mna_s4": 2,
        "mna_s5": 1,
        "mna_s6": 1,
        "mna_s7": 1,
        "mna_screen_total": 10,
        "mna_a1": 0,
        "mna_a2": 0,
        "mna_a3": 1,
        "mna_a4": 2,
        "mna_a5": 0.5,
        "mna_a6": 1,
        "mna_a7": 1,
        "mna_a8": 1,
        "mna_a9": 1,
        "mna_a10": 0.5,
        "mna_a11": 1,
        "mna_ass_total": 9,
        "mna_total": 21,
    },
    {
        "visit_id": 7,
        "mna_s1": 2,
        "mna_s2": 2,
        "mna_s3": 2,
        "mna_s4": 2,
        "mna_s5": 2,
        "mna_s6": 2,
        "mna_s7": 2,
        "mna_screen_total": 14,
        "mna_a1": 1,
        "mna_a2": 1,
        "mna_a3": 1,
        "mna_a4": 1,
        "mna_a5": 0.5,
        "mna_a6": 1,
        "mna_a7": 0.5,
        "mna_a8": 2,
        "mna_a9": 2,
        "mna_a10": 2,
        "mna_a11": 0.5,
        "mna_ass_total": 12,
        "mna_total": 24.5,
    },
    {
        "visit_id": 8,
        "mna_s1": 0,
        "mna_s2": 1,
        "mna_s3": 0,
        "mna_s4": 1,
        "mna_s5": 0,
        "mna_s6": 0,
        "mna_s7": 0,
        "mna_screen_total": 2,
        "mna_a1": 0,
        "mna_a2": 0,
        "mna_a3": 0,
        "mna_a4": 0,
        "mna_a5": 0,
        "mna_a6": 0,
        "mna_a7": 0,
        "mna_a8": 0,
        "mna_a9": 0,
        "mna_a10": 0,
        "mna_a11": 0,
        "mna_ass_total": 0,
        "mna_total": 2,
    },
    {
        "visit_id": 9,
        "mna_s1": 2,
        "mna_s2": 2,
        "mna_s3": 2,
        "mna_s4": 2,
        "mna_s5": 2,
        "mna_s6": 2,
        "mna_s7": 2,
        "mna_screen_total": 14,
        "mna_a1": 1,
        "mna_a2": 1,
        "mna_a3": 0,
        "mna_a4": 1,
        "mna_a5": 1,
        "mna_a6": 1,
        "mna_a7": 1,
        "mna_a8": 1,
        "mna_a9": 1,
        "mna_a10": 1,
        "mna_a11": 1,
        "mna_ass_total": 10,
        "mna_total": 26,
    },
]


def import_mna_data(data_list):
    """Import MNA data โดยแปลงชื่อคอลัมน์จาก Excel format เป็น Database format"""
    db = SessionLocal()

    print("\n" + "=" * 100)
    print("📥 IMPORT MNA DATA จาก Excel Format")
    print("=" * 100 + "\n")

    updated_count = 0

    for data in data_list:
        visit_id = data.pop("visit_id")

        # หา MNA response ของ visit นี้
        mna = db.query(MNAResponse).filter_by(visit_id=visit_id).first()

        if not mna:
            print(f"❌ ไม่พบ MNA response สำหรับ Visit {visit_id}")
            continue

        print(f"📝 Visit {visit_id}:")

        # แปลงชื่อคอลัมน์จาก Excel -> Database
        db_data = {}
        for excel_col, value in data.items():
            if excel_col in EXCEL_TO_DB_MAPPING:
                db_field = EXCEL_TO_DB_MAPPING[excel_col]
                db_data[db_field] = value
            else:
                print(f"   ⚠️  Unknown column: {excel_col} (skipped)")

        # แสดงข้อมูลก่อนอัพเดท
        print(f"   Before: total={mna.total_score}")

        # อัพเดทข้อมูล
        for field, value in db_data.items():
            setattr(mna, field, Decimal(str(value)))

        print(f"   After:  total={db_data.get('total_score', '?')}")
        print(f"   ✅ Updated {len(db_data)} fields\n")

        updated_count += 1

    # บันทึกการเปลี่ยนแปลง
    db.commit()
    db.close()

    print("=" * 100)
    print(f"✅ Import สำเร็จ: อัพเดท {updated_count} records")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    import_mna_data(excel_data)

    print("💡 TIP: ถ้าต้องการ import ข้อมูลใหม่")
    print("   1. แก้ไขข้อมูลใน excel_data list ด้านบน")
    print("   2. รันสคริปต์นี้อีกครั้ง")
    print("   3. หรือสร้างฟังก์ชั่นอ่านจาก CSV/Excel file\n")
