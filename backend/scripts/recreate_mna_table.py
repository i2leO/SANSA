"""
สร้างตาราง mna_responses ใหม่เลยด้วย schema ที่ถูกต้อง
1. Backup ข้อมูลเก่า
2. Drop table เก่า
3. Create table ใหม่
4. Restore ข้อมูล
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text
import json
from datetime import datetime

print("=" * 100)
print("🔄 สร้างตาราง mna_responses ใหม่")
print("=" * 100)

# 1. Backup ข้อมูลเก่า
print("\n📦 Step 1: Backup ข้อมูล MNA...")
with engine.connect() as conn:
    result = conn.execute(
        text(
            """
        SELECT * FROM mna_responses
    """
        )
    )

    backup_data = []
    for row in result:
        backup_data.append(dict(row._mapping))

    print(f"✅ Backup เรียบร้อย: {len(backup_data)} records")

    # Save to JSON file
    backup_file = Path(__file__).parent / "mna_backup.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"✅ บันทึกไว้ที่: {backup_file}")

# 2. Drop table เก่า
print("\n🗑️  Step 2: Drop table เก่า...")
confirmation = input("\n⚠️  ต้องการ DROP table mna_responses และสร้างใหม่? (yes/no): ")

if confirmation.lower() != "yes":
    print("\n❌ ยกเลิกการทำงาน")
    sys.exit(0)

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS mna_responses"))
    conn.commit()
    print("✅ Drop table สำเร็จ")

# 3. สร้าง table ใหม่
print("\n🔨 Step 3: สร้าง table ใหม่...")

create_table_sql = """
CREATE TABLE mna_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    scoring_version_id INT NOT NULL,

    -- Screening Questions (Q1-Q7) + Scores
    q1_food_intake_decline VARCHAR(50),
    mna_s1 DECIMAL(10,2),

    q2_weight_loss VARCHAR(50),
    mna_s2 DECIMAL(10,2),

    q3_mobility VARCHAR(50),
    mna_s3 DECIMAL(10,2),

    q4_stress_illness VARCHAR(50),
    mna_s4 DECIMAL(10,2),

    q5_neuropsychological VARCHAR(50),
    mna_s5 DECIMAL(10,2),

    q6_bmi VARCHAR(50),
    mna_s6 DECIMAL(10,2),

    q7_calf_circumference VARCHAR(50),
    mna_s7 DECIMAL(10,2),

    mna_screen_total DECIMAL(10,2),

    -- Assessment Questions (Q8-Q18) + Scores
    q8_independent_living VARCHAR(50),
    mna_a1 DECIMAL(10,2),

    q9_medications VARCHAR(50),
    mna_a2 DECIMAL(10,2),

    q10_pressure_sores VARCHAR(50),
    mna_a3 DECIMAL(10,2),

    q11_full_meals VARCHAR(50),
    mna_a4 DECIMAL(10,2),

    q12_protein_consumption VARCHAR(50),
    mna_a5 DECIMAL(10,2),

    q13_fruits_vegetables VARCHAR(50),
    mna_a6 DECIMAL(10,2),

    q14_fluid_intake VARCHAR(50),
    mna_a7 DECIMAL(10,2),

    q15_eating_independence VARCHAR(50),
    mna_a8 DECIMAL(10,2),

    q16_self_nutrition VARCHAR(50),
    mna_a9 DECIMAL(10,2),

    q17_health_comparison VARCHAR(50),
    mna_a10 DECIMAL(10,2),

    q18_mid_arm_circumference VARCHAR(50),
    mna_a11 DECIMAL(10,2),

    mna_ass_total DECIMAL(10,2),
    mna_total DECIMAL(10,2),

    -- Metadata
    result_category VARCHAR(50),
    completed_at TIMESTAMP NULL,
    entry_mode ENUM('STAFF', 'SELF'),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes
    UNIQUE KEY uk_visit_id (visit_id),
    KEY idx_result_category (result_category),
    KEY idx_created_by (created_by),

    -- Foreign Keys
    CONSTRAINT fk_mna_visit FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE,
    CONSTRAINT fk_mna_scoring_version FOREIGN KEY (scoring_version_id) REFERENCES scoring_rule_versions(id),
    CONSTRAINT fk_mna_created_by FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

with engine.connect() as conn:
    conn.execute(text(create_table_sql))
    conn.commit()
    print("✅ สร้าง table ใหม่สำเร็จ")

# 4. Restore ข้อมูล
print("\n📥 Step 4: Restore ข้อมูลกลับ...")

if backup_data:
    with engine.connect() as conn:
        for record in backup_data:
            # Map old column names to new names
            insert_sql = """
                INSERT INTO mna_responses (
                    id, visit_id, scoring_version_id,
                    q1_food_intake_decline, mna_s1,
                    q2_weight_loss, mna_s2,
                    q3_mobility, mna_s3,
                    q4_stress_illness, mna_s4,
                    q5_neuropsychological, mna_s5,
                    q6_bmi, mna_s6,
                    q7_calf_circumference, mna_s7,
                    mna_screen_total,
                    q8_independent_living, mna_a1,
                    q9_medications, mna_a2,
                    q10_pressure_sores, mna_a3,
                    q11_full_meals, mna_a4,
                    q12_protein_consumption, mna_a5,
                    q13_fruits_vegetables, mna_a6,
                    q14_fluid_intake, mna_a7,
                    q15_eating_independence, mna_a8,
                    q16_self_nutrition, mna_a9,
                    q17_health_comparison, mna_a10,
                    q18_mid_arm_circumference, mna_a11,
                    mna_ass_total, mna_total,
                    result_category, completed_at, entry_mode, created_by, created_at, updated_at
                ) VALUES (
                    :id, :visit_id, :scoring_version_id,
                    :q1_food_intake_decline, :mna_s1,
                    :q2_weight_loss, :mna_s2,
                    :q3_mobility, :mna_s3,
                    :q4_stress_illness, :mna_s4,
                    :q5_neuropsychological, :mna_s5,
                    :q6_bmi, :mna_s6,
                    :q7_calf_circumference, :mna_s7,
                    :mna_screen_total,
                    :q8_independent_living, :mna_a1,
                    :q9_medications, :mna_a2,
                    :q10_pressure_sores, :mna_a3,
                    :q11_full_meals, :mna_a4,
                    :q12_protein_consumption, :mna_a5,
                    :q13_fruits_vegetables, :mna_a6,
                    :q14_fluid_intake, :mna_a7,
                    :q15_eating_independence, :mna_a8,
                    :q16_self_nutrition, :mna_a9,
                    :q17_health_comparison, :mna_a10,
                    :q18_mid_arm_circumference, :mna_a11,
                    :mna_ass_total, :mna_total,
                    :result_category, :completed_at, :entry_mode, :created_by, :created_at, :updated_at
                )
            """

            conn.execute(text(insert_sql), record)

        conn.commit()
        print(f"✅ Restore สำเร็จ: {len(backup_data)} records")
else:
    print("⚠️  ไม่มีข้อมูลต้อง restore")

# 5. ตรวจสอบผล
print("\n✅ Step 5: ตรวจสอบผล...")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) as count FROM mna_responses"))
    count = result.fetchone()[0]
    print(f"✅ จำนวน records: {count}")

    # แสดง columns
    result = conn.execute(
        text("SHOW COLUMNS FROM mna_responses WHERE Field LIKE 'mna_%'")
    )
    print(f"\n✅ Columns ใหม่:")
    for row in result:
        print(f"   - {row[0]} ({row[1]})")

print("\n" + "=" * 100)
print("✨ สร้างตารางใหม่เสร็จสมบูรณ์!")
print("=" * 100)
