"""
สร้างตาราง mna_responses ใหม่เลย (Clean - ไม่มีข้อมูลเก่า)
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

print("=" * 100)
print("🔨 สร้างตาราง mna_responses ใหม่ (Clean)")
print("=" * 100)

# Drop table เก่า
print("\n🗑️  Step 1: Drop table เก่า...")
confirmation = input("\n⚠️  ต้องการ DROP table mna_responses และสร้างใหม่? (yes/no): ")

if confirmation.lower() != "yes":
    print("\n❌ ยกเลิกการทำงาน")
    sys.exit(0)

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS mna_responses"))
    conn.commit()
    print("✅ Drop table สำเร็จ")

# สร้าง table ใหม่
print("\n🔨 Step 2: สร้าง table ใหม่...")

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

# ตรวจสอบผล
print("\n✅ Step 3: ตรวจสอบผล...")
with engine.connect() as conn:
    # แสดง columns
    result = conn.execute(text("DESCRIBE mna_responses"))
    print(f"\n📋 โครงสร้างตาราง:")
    print(f"{'Field':<30} {'Type':<20} {'Null':<5} {'Key':<5}")
    print("-" * 70)
    for row in result:
        print(f"{row[0]:<30} {row[1]:<20} {row[2]:<5} {row[3]:<5}")

print("\n" + "=" * 100)
print("✨ สร้างตารางใหม่เสร็จสมบูรณ์!")
print("💡 ตารางว่างเปล่า พร้อมเพิ่มข้อมูลใหม่")
print("=" * 100)
