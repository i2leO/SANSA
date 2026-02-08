"""ลบ columns เก่าของ MNA ที่ซ้ำซ้อนออก (q1_score, q2_score, ...)"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

# Columns เก่าที่ต้องลบออก
OLD_COLUMNS_TO_DROP = [
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
]

print("=" * 80)
print("🗑️  ลบ MNA Columns เก่าที่ซ้ำซ้อน")
print("=" * 80)

# ตรวจสอบ columns ที่มีอยู่ในตาราง
print("\n📋 ตรวจสอบ columns ที่มีอยู่ในตาราง mna_responses...")
with engine.connect() as conn:
    result = conn.execute(text("SHOW COLUMNS FROM mna_responses"))
    existing_columns = [row[0] for row in result]

print(f"จำนวน columns ทั้งหมด: {len(existing_columns)}")

# หา columns เก่าที่ยังมีอยู่
columns_to_drop = [col for col in OLD_COLUMNS_TO_DROP if col in existing_columns]

if not columns_to_drop:
    print("\n✅ ไม่พบ columns เก่าที่ต้องลบ - ตารางสะอาดแล้ว!")
    sys.exit(0)

print(f"\n⚠️  พบ columns เก่าที่ต้องลบ: {len(columns_to_drop)} columns")
for col in columns_to_drop:
    print(f"   - {col}")

# ยืนยันก่อนลบ
print("\n⚠️  คำเตือน: การลบ columns นี้ไม่สามารถย้อนกลับได้!")
print("หาก columns เก่ายังมีข้อมูลสำคัญ ควร backup ก่อน")
confirmation = input("\nต้องการลบ columns เก่าหรือไม่? (yes/no): ")

if confirmation.lower() != "yes":
    print("\n❌ ยกเลิกการลบ columns")
    sys.exit(0)

# ลบ columns ทีละอัน
print("\n🔄 เริ่มลบ columns...")
with engine.connect() as conn:
    for col_name in columns_to_drop:
        try:
            sql = f"ALTER TABLE mna_responses DROP COLUMN {col_name}"
            conn.execute(text(sql))
            conn.commit()
            print(f"  ✅ ลบ {col_name} สำเร็จ")
        except Exception as e:
            print(f"  ❌ ลบ {col_name} ล้มเหลว: {e}")
            conn.rollback()

print("\n" + "=" * 80)
print("✅ เสร็จสิ้นการลบ columns เก่า")
print("=" * 80)

# แสดง columns ที่เหลืออยู่
print("\n📊 Columns ที่เหลืออยู่ในตาราง:")
with engine.connect() as conn:
    result = conn.execute(text("SHOW COLUMNS FROM mna_responses"))
    for row in result:
        col_name = row[0]
        col_type = row[1]
        if col_name.startswith("mna_") or col_name.startswith("q"):
            print(f"   - {col_name} ({col_type})")

print("\n✨ ตารางพร้อมใช้งานแล้ว!")
