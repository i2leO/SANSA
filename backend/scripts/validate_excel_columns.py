#!/usr/bin/env python3
"""
Validate Excel Columns Script
ตรวจสอบว่า columns ใน Excel ตรงกับที่ database ต้องการหรือไม่
"""

import pandas as pd
import sys
from pathlib import Path

# Excel file path
EXCEL_FILE = "/Users/dev/SANSA/src/ปรับแก้ Test Data THESIS PHASE2 03022026.xlsx"

# Required columns for each sheet
REQUIRED_COLUMNS = {
    "Demographic": {
        "required": ["respondent_code"],
        "optional": [
            "age",
            "sex",
            "education_level",
            "marital_status",
            "monthly_income",
            "occupation",
            "living_arrangement",
        ],
    },
    "Self Screen Assess (3)": {
        "required": ["visit_id"],
        "optional": [f"q{i}_score" for i in range(1, 17)]
        + ["screening_total", "diet_total", "total_score", "result_level"],
    },
    "Satisfaction": {
        "required": ["visit_id"],
        "optional": [f"q{i}" for i in range(1, 8)] + ["comments"],
    },
    "MNA": {
        "required": ["visit_id"],
        "optional": [f"mna_s{i}" for i in range(1, 8)]
        + ["mna_screen_total"]
        + [f"mna_a{i}" for i in range(1, 12)]
        + ["mna_ass_total", "mna_total", "result_category"],
    },
    "BIA": {
        "required": ["visit_id"],
        "optional": [
            "age",
            "sex",
            "weight_kg",
            "height_cm",
            "bmi",
            "waist_circumference_cm",
            "fat_mass_kg",
            "body_fat_percentage",
            "visceral_fat_kg",
            "muscle_mass_kg",
            "bone_mass_kg",
            "water_percentage",
            "metabolic_rate",
        ],
    },
}


def validate_columns(sheet_name, df):
    """ตรวจสอบ columns ของ sheet"""
    print(f"\n{'='*120}")
    print(f"🔍 VALIDATING: {sheet_name}")
    print(f"{'='*120}")

    if sheet_name not in REQUIRED_COLUMNS:
        print(f"⚠️  No validation rules defined for this sheet")
        return True

    rules = REQUIRED_COLUMNS[sheet_name]
    excel_columns = set(df.columns)
    required_cols = set(rules["required"])
    optional_cols = set(rules["optional"])
    expected_cols = required_cols | optional_cols

    # ตรวจสอบ required columns
    missing_required = required_cols - excel_columns
    if missing_required:
        print(f"❌ MISSING REQUIRED COLUMNS: {missing_required}")
        return False
    else:
        print(f"✅ All required columns present: {required_cols}")

    # ตรวจสอบ optional columns
    present_optional = optional_cols & excel_columns
    missing_optional = optional_cols - excel_columns

    print(f"\n📊 Optional columns:")
    print(f"  ✅ Present: {len(present_optional)}/{len(optional_cols)}")
    if present_optional:
        for col in sorted(present_optional):
            print(f"     - {col}")

    if missing_optional:
        print(f"\n  ⚠️  Missing (optional): {len(missing_optional)}")
        for col in sorted(missing_optional):
            print(f"     - {col}")

    # ตรวจสอบ extra columns
    extra_cols = excel_columns - expected_cols
    if extra_cols:
        print(f"\n  ℹ️  Extra columns (will be ignored): {len(extra_cols)}")
        for col in sorted(extra_cols):
            print(f"     - {col}")

    return True


def main():
    """Main validation function"""
    print("=" * 120)
    print("EXCEL COLUMNS VALIDATION")
    print("=" * 120)
    print(f"File: {EXCEL_FILE}")

    # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
    if not Path(EXCEL_FILE).exists():
        print(f"\n❌ ERROR: File not found!")
        print(f"Please place the Excel file at: {EXCEL_FILE}")
        return 1

    try:
        # Load Excel file
        excel_file = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
        print(f"\n✅ Excel file loaded successfully!")

        all_valid = True

        # Validate each sheet
        for sheet_name in REQUIRED_COLUMNS.keys():
            if sheet_name not in excel_file.sheet_names:
                print(f"\n⚠️  Sheet '{sheet_name}' not found in Excel file")
                all_valid = False
                continue

            # Read sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Validate
            is_valid = validate_columns(sheet_name, df)
            if not is_valid:
                all_valid = False

        print("\n" + "=" * 120)
        if all_valid:
            print("✅ ALL VALIDATIONS PASSED!")
            print("=" * 120)
            print("\n💡 You can now safely run the import:")
            print("   python scripts/import_all_excel_sheets.py")
        else:
            print("❌ VALIDATION FAILED!")
            print("=" * 120)
            print("\n⚠️  Please fix the issues above before importing")
        print("=" * 120)

        return 0 if all_valid else 1

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
