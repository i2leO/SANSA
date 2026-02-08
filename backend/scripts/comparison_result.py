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

# Columns ในตาราง Database (เฉพาะที่ใช้เก็บข้อมูล MNA)
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

# วิเคราะห์
excel_scores = [c for c in excel_columns if c.startswith("mna_")]
db_scores = [c for c in db_columns if c.startswith("mna_")]
excel_only = [c for c in excel_scores if c not in db_scores]
db_only = [c for c in db_scores if c not in excel_scores]
matching = len([c for c in db_scores if c in excel_scores])

# เขียนผลลงไฟล์
with open("comparison_result.txt", "w", encoding="utf-8") as f:
    f.write("=" * 100 + "\n")
    f.write("COMPARISON RESULT: Excel vs Database\n")
    f.write("=" * 100 + "\n\n")

    f.write(f"Excel score columns ({len(excel_scores)}):\n")
    f.write("  " + ", ".join(excel_scores) + "\n\n")

    f.write(f"Database score columns ({len(db_scores)}):\n")
    f.write("  " + ", ".join(db_scores) + "\n\n")

    f.write("=" * 100 + "\n")
    f.write("ANALYSIS:\n")
    f.write("=" * 100 + "\n\n")

    if excel_only:
        f.write(f"Columns in Excel but NOT in Database ({len(excel_only)}):\n")
        for c in excel_only:
            f.write(f"  - {c}\n")
        f.write("\n")
    else:
        f.write("All Excel columns exist in Database\n\n")

    if db_only:
        f.write(f"Columns in Database but NOT in Excel ({len(db_only)}):\n")
        for c in db_only:
            f.write(f"  - {c}\n")
        f.write("\n")
    else:
        f.write("No extra columns in Database\n\n")

    f.write("=" * 100 + "\n")
    f.write("SUMMARY:\n")
    f.write("=" * 100 + "\n")
    f.write(f"Excel score columns:    {len(excel_scores)}\n")
    f.write(f"Database score columns: {len(db_scores)}\n")
    f.write(f"Matching columns:       {matching}\n")
    f.write(
        f"Match rate:             {matching}/{len(db_scores)} = {matching*100//len(db_scores)}%\n\n"
    )

    if matching == len(db_scores):
        f.write("STATUS: PERFECT MATCH - Database ready for import\n")
    else:
        f.write(f"STATUS: {matching}/{len(db_scores)} columns match\n")

    if "mna_a12" in excel_only:
        f.write("\nNOTE: mna_a12 exists in Excel but not used in MNA calculation\n")
        f.write("      (Not required in Database)\n")

    f.write("\n" + "=" * 100 + "\n")
    f.write("DATABASE SPECIAL COLUMNS:\n")
    f.write("=" * 100 + "\n\n")

    question_cols = [c for c in db_columns if c.startswith("q")]
    f.write(f"Question text columns ({len(question_cols)}):\n")
    f.write('  Store answer choices like "severe decrease", "no weight loss"\n')
    for i, c in enumerate(question_cols, 1):
        f.write(f"  {i:2d}. {c}\n")

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
    f.write(f"\nMetadata columns ({len(metadata_cols)}):\n")
    for i, c in enumerate(metadata_cols, 1):
        f.write(f"  {i}. {c}\n")

    f.write("\n" + "=" * 100 + "\n")
    f.write("TOTAL DATABASE STRUCTURE:\n")
    f.write("=" * 100 + "\n")
    f.write(f"Total columns: {len(db_columns)}\n")
    f.write(f"  - Score columns:    {len(db_scores)} (mna_s*, mna_a*, totals)\n")
    f.write(f"  - Question columns: {len(question_cols)} (q*_*)\n")
    f.write(f"  - Metadata columns: {len(metadata_cols)} (id, timestamps, etc.)\n")
    f.write("=" * 100 + "\n")

print("Comparison complete. Results written to: comparison_result.txt")
