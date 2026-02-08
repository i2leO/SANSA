"""ตรวจสอบ columns ในฐานข้อมูลจริงๆ โดยตรง"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

print("=" * 100)
print("🔍 ตรวจสอบ Database และ Table Structure")
print("=" * 100)

with engine.connect() as conn:
    # ตรวจสอบว่าเชื่อมต่อกับ database ไหน
    result = conn.execute(text("SELECT DATABASE()"))
    current_db = result.fetchone()[0]
    print(f"\n✅ เชื่อมต่อกับ Database: {current_db}")

    # นับจำนวน columns ทั้งหมด
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = :db AND table_name = 'mna_responses'"
        ),
        {"db": current_db},
    )
    total_columns = result.fetchone()[0]
    print(f"\n📊 จำนวน columns ทั้งหมดในตาราง mna_responses: {total_columns}")

    # แสดง columns ทั้งหมดที่มีคำว่า score หรือ total
    print("\n" + "=" * 100)
    print("📋 รายชื่อ Columns ทั้งหมดที่เกี่ยวข้องกับ Score/Total:")
    print("=" * 100)

    result = conn.execute(
        text(
            """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM information_schema.columns
        WHERE table_schema = :db
        AND table_name = 'mna_responses'
        AND (COLUMN_NAME LIKE '%score%' OR COLUMN_NAME LIKE '%total%' OR COLUMN_NAME LIKE 'mna_%')
        ORDER BY ORDINAL_POSITION
    """
        ),
        {"db": current_db},
    )

    old_columns_found = []
    new_columns_found = []

    for row in result:
        col_name = row[0]
        col_type = row[1]
        col_nullable = row[2]
        col_default = row[3]

        # ตรวจสอบว่าเป็น column เก่าหรือใหม่
        if col_name in [
            "q1_score",
            "q2_score",
            "q3_score",
            "q4_score",
            "q5_score",
            "q6_score",
            "q7_score",
            "q8_score",
            "q9_score",
            "q10_score",
            "q11_score",
            "q12_score",
            "q13_score",
            "q14_score",
            "q15_score",
            "q16_score",
            "q17_score",
            "q18_score",
            "screening_total",
            "assessment_total",
            "total_score",
        ]:
            old_columns_found.append(col_name)
            print(f"❌ COLUMN เก่า: {col_name:30} ({col_type})")
        elif col_name.startswith("mna_"):
            new_columns_found.append(col_name)
            print(f"✅ COLUMN ใหม่: {col_name:30} ({col_type})")

    print("\n" + "=" * 100)
    print("📊 สรุปผลการตรวจสอบ:")
    print("=" * 100)
    print(f"✅ Columns ใหม่ที่พบ: {len(new_columns_found)} columns")
    for col in new_columns_found:
        print(f"   - {col}")

    if old_columns_found:
        print(f"\n❌ Columns เก่าที่ยังพบ: {len(old_columns_found)} columns")
        for col in old_columns_found:
            print(f"   - {col}")
        print("\n⚠️  ต้องลบ columns เก่าเหล่านี้ออก!")
    else:
        print(f"\n✅ ไม่พบ columns เก่า - โครงสร้างตารางสะอาดแล้ว!")
