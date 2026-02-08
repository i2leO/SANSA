#!/usr/bin/env python3
"""
เปรียบเทียบโครงสร้าง columns ระหว่าง Excel และ Database
"""

# Columns ตาม Excel ที่ผู้ใช้ส่งภาพมา
excel_columns = [
    "visit_id",
    "mna_s1",
    "mna_s2",
    "mna_s3",
    "mna_s4",
    "mna_s5",
    "mna_s6",
    "mna_s7",
    "mna_screen_total",
    "mna_a1",
    "mna_a2",
    "mna_a3",
    "mna_a4",
    "mna_a5",
    "mna_a6",
    "mna_a7",
    "mna_a8",
    "mna_a9",
    "mna_a10",
    "mna_a11",
    "mna_a12",  # Column พิเศษใน Excel
    "mna_ass_total",
    "mna_total",
]

# Columns ในตาราง Database (เฉพาะที่ใช้เก็บข้อมูล MNA จริงๆ)
db_columns = [
    "id",
    "visit_id",
    "scoring_version_id",
    "q1_food_intake_decline",
    "mna_s1",
    "q2_weight_loss",
    "mna_s2",
    "q3_mobility",
    "mna_s3",
    "q4_stress_illness",
    "mna_s4",
    "q5_neuropsychological",
    "mna_s5",
    "q6_bmi",
    "mna_s6",
    "q7_calf_circumference",
    "mna_s7",
    "mna_screen_total",
    "q8_independent_living",
    "mna_a1",
    "q9_medications",
    "mna_a2",
    "q10_pressure_sores",
    "mna_a3",
    "q11_full_meals",
    "mna_a4",
    "q12_protein_consumption",
    "mna_a5",
    "q13_fruits_vegetables",
    "mna_a6",
    "q14_fluid_intake",
    "mna_a7",
    "q15_eating_independence",
    "mna_a8",
    "q16_self_nutrition",
    "mna_a9",
    "q17_health_comparison",
    "mna_a10",
    "q18_mid_arm_circumference",
    "mna_a11",
    "mna_ass_total",
    "mna_total",
    "result_category",
    "completed_at",
    "entry_mode",
    "created_by",
    "created_at",
    "updated_at",
]

print("=" * 100)
print("📊 เปรียบเทียบ Columns: Excel vs Database")
print("=" * 100)

# Score columns ที่ต้องตรงกัน
excel_scores = [c for c in excel_columns if c.startswith("mna_")]
db_scores = [c for c in db_columns if c.startswith("mna_")]

print(f"\n✅ Score Columns ใน Excel: {len(excel_scores)} columns")
print("   " + ", ".join(excel_scores))

print(f"\n✅ Score Columns ใน Database: {len(db_scores)} columns")
print("   " + ", ".join(db_scores))

# หา columns ที่ไม่ตรงกัน
print("\n" + "=" * 100)
print("🔍 การวิเคราะห์:")
print("=" * 100)

excel_only = [c for c in excel_scores if c not in db_scores]
db_only = [c for c in db_scores if c not in excel_scores]

if excel_only:
    print(f"\n⚠️  Columns ใน Excel แต่ไม่มีใน Database: {len(excel_only)}")
    for c in excel_only:
        print(f"   - {c}")
else:
    print("\n✅ ไม่มี columns ใน Excel ที่ขาดใน Database")

if db_only:
    print(f"\n❌ Columns ใน Database แต่ไม่มีใน Excel: {len(db_only)}")
    for c in db_only:
        print(f"   - {c}")
else:
    print("\n✅ ไม่มี columns เกินใน Database")

# ตรวจสอบ mapping
print("\n" + "=" * 100)
print("✅ สรุปผลการเปรียบเทียบ:")
print("=" * 100)
print(f"Score columns ทั้งหมดใน Excel:    {len(excel_scores)}")
print(f"Score columns ทั้งหมดใน Database: {len(db_scores)}")

matching = len([c for c in db_scores if c in excel_scores])
print(f"Score columns ที่ตรงกัน:           {matching} columns")

if matching == len(db_scores):
    print("\n✅ ตรงกัน 100% - Database พร้อมสำหรับ import ข้อมูลจาก Excel")
else:
    print(f"\n⚠️  ตรงกัน {matching}/{len(db_scores)} columns")

if "mna_a12" in excel_only:
    print("\n💡 หมายเหตุ: mna_a12 อยู่ใน Excel แต่ไม่ใช้ในการคำนวณคะแนน MNA")
    print("   (ไม่จำเป็นต้องเก็บใน Database)")

# แสดง columns พิเศษ
print("\n" + "=" * 100)
print("📋 Columns พิเศษใน Database:")
print("=" * 100)

question_cols = [c for c in db_columns if c.startswith("q")]
print(f"\n✅ Question text columns (เก็บคำตอบ): {len(question_cols)} columns")
print('   ใช้เก็บข้อความที่ผู้ใช้เลือกตอบ เช่น "severe decrease", "no weight loss"')
for i, c in enumerate(question_cols, 1):
    print(f"   {i:2d}. {c}")

metadata_cols = [
    "id",
    "visit_id",
    "scoring_version_id",
    "result_category",
    "completed_at",
    "entry_mode",
    "created_by",
    "created_at",
    "updated_at",
]
print(f"\n✅ Metadata columns (ข้อมูลระบบ): {len(metadata_cols)} columns")
for i, c in enumerate(metadata_cols, 1):
    print(f"   {i}. {c}")

print("\n" + "=" * 100)
print("📊 สรุปรวม Database Structure:")
print("=" * 100)
print(f"Total columns: {len(db_columns)}")
print(f"  - Score columns:    {len(db_scores)} (mna_s*, mna_a*, totals)")
print(f"  - Question columns: {len(question_cols)} (q*_*)")
print(f"  - Metadata columns: {len(metadata_cols)} (id, timestamps, etc.)")
print("=" * 100)
