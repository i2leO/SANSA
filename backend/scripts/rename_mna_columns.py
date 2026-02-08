"""
Migration Script: เปลี่ยนชื่อคอลัมน์ MNA ให้ตรงกับ Excel format
From: q1_score, q2_score, ... -> To: mna_s1, mna_s2, ...
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from sqlalchemy import text

# Mapping: old_name -> new_name
COLUMN_RENAMES = {
    # Screening section (q1-q7 -> mna_s1-mna_s7)
    "q1_score": "mna_s1",
    "q2_score": "mna_s2",
    "q3_score": "mna_s3",
    "q4_score": "mna_s4",
    "q5_score": "mna_s5",
    "q6_score": "mna_s6",
    "q7_score": "mna_s7",
    "screening_total": "mna_screen_total",
    # Assessment section (q8-q18 -> mna_a1-mna_a11)
    "q8_score": "mna_a1",
    "q9_score": "mna_a2",
    "q10_score": "mna_a3",
    "q11_score": "mna_a4",
    "q12_score": "mna_a5",
    "q13_score": "mna_a6",
    "q14_score": "mna_a7",
    "q15_score": "mna_a8",
    "q16_score": "mna_a9",
    "q17_score": "mna_a10",
    "q18_score": "mna_a11",
    "assessment_total": "mna_ass_total",
    "total_score": "mna_total",
}


def rename_columns():
    db = SessionLocal()

    print("\n" + "=" * 100)
    print("🔄 RENAMING MNA COLUMNS IN DATABASE")
    print("=" * 100 + "\n")

    print("⚠️  WARNING: This will rename columns in mna_responses table")
    print("   This operation cannot be easily undone.\n")

    try:
        for old_name, new_name in COLUMN_RENAMES.items():
            sql = f"ALTER TABLE mna_responses CHANGE COLUMN `{old_name}` `{new_name}` DECIMAL(10,2)"

            print(f"Renaming: {old_name:20s} -> {new_name}")

            try:
                db.execute(text(sql))
                db.commit()
                print(f"  ✅ Success\n")
            except Exception as e:
                if "Unknown column" in str(e):
                    print(
                        f"  ⚠️  Column '{old_name}' does not exist (may already be renamed)\n"
                    )
                else:
                    print(f"  ❌ Error: {e}\n")
                    raise

        print("=" * 100)
        print("✅ COLUMN RENAMING COMPLETED")
        print("=" * 100 + "\n")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n⚠️  This will permanently rename columns in the database.")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() == "yes":
        rename_columns()
    else:
        print("Migration cancelled.")
