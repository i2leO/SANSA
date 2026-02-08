"""แสดง structure ปัจจุบันของตาราง mna_responses"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

print("=" * 80)
print("📋 โครงสร้างตาราง mna_responses ปัจจุบัน")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("SHOW COLUMNS FROM mna_responses"))

    print("\n🔍 Score Columns (columns ที่เก็บคะแนน):")
    print("-" * 80)

    for row in result:
        col_name = row[0]
        col_type = row[1]
        col_null = row[2]
        col_key = row[3]
        col_default = row[4]
        col_extra = row[5]

        # แสดงเฉพาะ columns ที่เกี่ยวข้องกับ MNA scores
        if (
            col_name.startswith("mna_")
            or col_name.startswith("q")
            and not col_name.endswith("_score")
            or "total" in col_name
        ):
            print(f"{col_name:30} {col_type:20} NULL={col_null}")

print("\n" + "=" * 80)
print("✨ ชื่อ columns ตอนนี้ควรเป็น:")
print("   - Screening: mna_s1, mna_s2, ..., mna_s7, mna_screen_total")
print("   - Assessment: mna_a1, mna_a2, ..., mna_a11, mna_ass_total")
print("   - Total: mna_total")
print("=" * 80)
