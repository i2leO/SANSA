#!/usr/bin/env python3
"""
Comprehensive Excel Import Script
Import all sheets from "ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx" into database
"""

import sys
import pandas as pd
from decimal import Decimal
from datetime import datetime
from app.database import SessionLocal
from app.models import (
    Respondent,
    Visit,
    SANSAResponse,
    SatisfactionResponse,
    MNAResponse,
    BIARecord,
    RespondentStatus,
    Sex,
    VisitType,
    EntryMode,
)

# ================================
# Configuration
# ================================
import os

EXCEL_FILE = "/Users/dev/SANSA/src/ปรับแก้ Test Data THESIS PHASE2 03022026.xlsx"

SHEET_NAMES = {
    "demographic": "Demographic",
    "self_screen": "Self Screen Assess (3)",
    "satisfaction": "Satisfaction",
    "bia": "BIA",
    "mna": "MNA",
}

# ================================
# Helper Functions
# ================================


def safe_decimal(value, default=None):
    """Convert value to Decimal safely"""
    if pd.isna(value) or value == "":
        return default
    try:
        return Decimal(str(value))
    except:
        return default


def safe_int(value, default=None):
    """Convert value to int safely"""
    if pd.isna(value) or value == "":
        return default
    try:
        return int(value)
    except:
        return default


def safe_str(value, default=None):
    """Convert value to string safely"""
    if pd.isna(value) or value == "":
        return default
    return str(value).strip()


def map_sex(value):
    """Map sex value to enum"""
    if pd.isna(value):
        return None
    value_lower = str(value).lower()
    if value_lower in ["ชาย", "male", "m", "1"]:
        return Sex.MALE
    elif value_lower in ["หญิง", "female", "f", "2"]:
        return Sex.FEMALE
    return None


# ================================
# Import Functions
# ================================


def import_demographic_data(df, db):
    """Import Demographic sheet"""
    print(f"\n📊 Importing Demographic data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            # Get or create respondent by code
            respondent_code = safe_str(row.get("respondent_code", f"R{idx+1:03d}"))

            respondent = (
                db.query(Respondent)
                .filter(Respondent.respondent_code == respondent_code)
                .first()
            )

            if respondent:
                # Update existing
                respondent.age = safe_int(row.get("age"))
                respondent.sex = map_sex(row.get("sex"))
                respondent.education_level = safe_str(row.get("education_level"))
                respondent.marital_status = safe_str(row.get("marital_status"))
                respondent.monthly_income = safe_str(row.get("monthly_income"))
                respondent.occupation = safe_str(row.get("occupation"))
                respondent.living_arrangement = safe_str(row.get("living_arrangement"))
                updated += 1
            else:
                # Create new
                respondent = Respondent(
                    respondent_code=respondent_code,
                    age=safe_int(row.get("age")),
                    sex=map_sex(row.get("sex")),
                    education_level=safe_str(row.get("education_level")),
                    marital_status=safe_str(row.get("marital_status")),
                    monthly_income=safe_str(row.get("monthly_income")),
                    occupation=safe_str(row.get("occupation")),
                    living_arrangement=safe_str(row.get("living_arrangement")),
                    status=RespondentStatus.ELDERLY,
                    created_by=1,
                )
                db.add(respondent)
                imported += 1

        except Exception as e:
            print(f"  ⚠️  Row {idx+1}: {str(e)}")
            skipped += 1
            continue

    db.commit()
    print(f"  ✅ Imported: {imported}, Updated: {updated}, Skipped: {skipped}")
    return imported, updated, skipped


def import_sansa_data(df, db):
    """Import Self Screen Assessment (SANSA) sheet"""
    print(f"\n📊 Importing SANSA data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            visit_id = safe_int(row.get("visit_id"))
            if not visit_id:
                print(f"  ⚠️  Row {idx+1}: Missing visit_id")
                skipped += 1
                continue

            # Check if visit exists
            visit = db.query(Visit).filter(Visit.id == visit_id).first()
            if not visit:
                print(f"  ⚠️  Row {idx+1}: Visit ID {visit_id} not found")
                skipped += 1
                continue

            # Check if SANSA response exists
            sansa = (
                db.query(SANSAResponse)
                .filter(SANSAResponse.visit_id == visit_id)
                .first()
            )

            if sansa:
                # Update existing
                for i in range(1, 17):
                    setattr(sansa, f"q{i}_score", safe_decimal(row.get(f"q{i}_score")))
                sansa.screening_total = safe_decimal(row.get("screening_total"))
                sansa.diet_total = safe_decimal(row.get("diet_total"))
                sansa.total_score = safe_decimal(row.get("total_score"))
                sansa.result_level = safe_str(row.get("result_level"))
                updated += 1
            else:
                # Create new
                sansa = SANSAResponse(
                    visit_id=visit_id,
                    scoring_version_id=1,
                    screening_total=safe_decimal(row.get("screening_total")),
                    diet_total=safe_decimal(row.get("diet_total")),
                    total_score=safe_decimal(row.get("total_score")),
                    result_level=safe_str(row.get("result_level")),
                )
                # Set individual scores
                for i in range(1, 17):
                    setattr(sansa, f"q{i}_score", safe_decimal(row.get(f"q{i}_score")))

                db.add(sansa)
                imported += 1

        except Exception as e:
            print(f"  ⚠️  Row {idx+1}: {str(e)}")
            skipped += 1
            continue

    db.commit()
    print(f"  ✅ Imported: {imported}, Updated: {updated}, Skipped: {skipped}")
    return imported, updated, skipped


def import_satisfaction_data(df, db):
    """Import Satisfaction sheet"""
    print(f"\n📊 Importing Satisfaction data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            visit_id = safe_int(row.get("visit_id"))
            if not visit_id:
                skipped += 1
                continue

            # Check if satisfaction response exists
            satisfaction = (
                db.query(SatisfactionResponse)
                .filter(SatisfactionResponse.visit_id == visit_id)
                .first()
            )

            if satisfaction:
                # Update existing
                for i in range(1, 8):
                    setattr(
                        satisfaction,
                        f"q{i}_clarity" if i == 1 else f"q{i}_score",
                        safe_int(row.get(f"q{i}")),
                    )
                satisfaction.comments = safe_str(row.get("comments"))
                updated += 1
            else:
                # Create new
                satisfaction = SatisfactionResponse(
                    visit_id=visit_id,
                    q1_clarity=safe_int(row.get("q1")),
                    q2_ease_of_use=safe_int(row.get("q2")),
                    q3_confidence=safe_int(row.get("q3")),
                    q4_presentation=safe_int(row.get("q4")),
                    q5_results_display=safe_int(row.get("q5")),
                    q6_usefulness=safe_int(row.get("q6")),
                    q7_overall_satisfaction=safe_int(row.get("q7")),
                    comments=safe_str(row.get("comments")),
                )
                db.add(satisfaction)
                imported += 1

        except Exception as e:
            print(f"  ⚠️  Row {idx+1}: {str(e)}")
            skipped += 1
            continue

    db.commit()
    print(f"  ✅ Imported: {imported}, Updated: {updated}, Skipped: {skipped}")
    return imported, updated, skipped


def import_mna_data(df, db):
    """Import MNA sheet"""
    print(f"\n📊 Importing MNA data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    # Screening questions mapping
    screening_cols = [
        "mna_s1",
        "mna_s2",
        "mna_s3",
        "mna_s4",
        "mna_s5",
        "mna_s6",
        "mna_s7",
    ]
    # Assessment questions mapping
    assessment_cols = [
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
    ]

    for idx, row in df.iterrows():
        try:
            visit_id = safe_int(row.get("visit_id"))
            if not visit_id:
                print(f"  ⚠️  Row {idx+1}: Missing visit_id")
                skipped += 1
                continue

            # Check if visit exists
            visit = db.query(Visit).filter(Visit.id == visit_id).first()
            if not visit:
                print(f"  ⚠️  Row {idx+1}: Visit ID {visit_id} not found")
                skipped += 1
                continue

            # Check if MNA response exists
            mna = db.query(MNAResponse).filter(MNAResponse.visit_id == visit_id).first()

            if mna:
                # Update existing
                for col in screening_cols:
                    setattr(mna, col, safe_decimal(row.get(col)))
                for col in assessment_cols:
                    setattr(mna, col, safe_decimal(row.get(col)))
                mna.mna_screen_total = safe_decimal(row.get("mna_screen_total"))
                mna.mna_ass_total = safe_decimal(row.get("mna_ass_total"))
                mna.mna_total = safe_decimal(row.get("mna_total"))
                mna.result_category = safe_str(row.get("result_category"))
                updated += 1
            else:
                # Create new
                mna = MNAResponse(
                    visit_id=visit_id,
                    scoring_version_id=1,
                    mna_screen_total=safe_decimal(row.get("mna_screen_total")),
                    mna_ass_total=safe_decimal(row.get("mna_ass_total")),
                    mna_total=safe_decimal(row.get("mna_total")),
                    result_category=safe_str(row.get("result_category")),
                    entry_mode=EntryMode.STAFF,
                    created_by=1,
                )
                # Set individual scores
                for col in screening_cols:
                    setattr(mna, col, safe_decimal(row.get(col)))
                for col in assessment_cols:
                    setattr(mna, col, safe_decimal(row.get(col)))

                db.add(mna)
                imported += 1

        except Exception as e:
            print(f"  ⚠️  Row {idx+1}: {str(e)}")
            skipped += 1
            continue

    db.commit()
    print(f"  ✅ Imported: {imported}, Updated: {updated}, Skipped: {skipped}")
    return imported, updated, skipped


def import_bia_data(df, db):
    """Import BIA sheet"""
    print(f"\n📊 Importing BIA data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            visit_id = safe_int(row.get("visit_id"))
            if not visit_id:
                skipped += 1
                continue

            # Check if BIA record exists
            bia = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).first()

            if bia:
                # Update existing
                bia.age = safe_int(row.get("age"))
                bia.sex = map_sex(row.get("sex"))
                bia.weight_kg = safe_decimal(row.get("weight_kg"))
                bia.height_cm = safe_decimal(row.get("height_cm"))
                bia.bmi = safe_decimal(row.get("bmi"))
                bia.waist_circumference_cm = safe_decimal(
                    row.get("waist_circumference_cm")
                )
                bia.fat_mass_kg = safe_decimal(row.get("fat_mass_kg"))
                bia.body_fat_percentage = safe_decimal(row.get("body_fat_percentage"))
                bia.visceral_fat_kg = safe_decimal(row.get("visceral_fat_kg"))
                bia.muscle_mass_kg = safe_decimal(row.get("muscle_mass_kg"))
                bia.bone_mass_kg = safe_decimal(row.get("bone_mass_kg"))
                bia.water_percentage = safe_decimal(row.get("water_percentage"))
                bia.metabolic_rate = safe_int(row.get("metabolic_rate"))
                updated += 1
            else:
                # Create new
                bia = BIARecord(
                    visit_id=visit_id,
                    age=safe_int(row.get("age")),
                    sex=map_sex(row.get("sex")),
                    weight_kg=safe_decimal(row.get("weight_kg")),
                    height_cm=safe_decimal(row.get("height_cm")),
                    bmi=safe_decimal(row.get("bmi")),
                    waist_circumference_cm=safe_decimal(
                        row.get("waist_circumference_cm")
                    ),
                    fat_mass_kg=safe_decimal(row.get("fat_mass_kg")),
                    body_fat_percentage=safe_decimal(row.get("body_fat_percentage")),
                    visceral_fat_kg=safe_decimal(row.get("visceral_fat_kg")),
                    muscle_mass_kg=safe_decimal(row.get("muscle_mass_kg")),
                    bone_mass_kg=safe_decimal(row.get("bone_mass_kg")),
                    water_percentage=safe_decimal(row.get("water_percentage")),
                    metabolic_rate=safe_int(row.get("metabolic_rate")),
                    measured_by=1,
                )
                db.add(bia)
                imported += 1

        except Exception as e:
            print(f"  ⚠️  Row {idx+1}: {str(e)}")
            skipped += 1
            continue

    db.commit()
    print(f"  ✅ Imported: {imported}, Updated: {updated}, Skipped: {skipped}")
    return imported, updated, skipped


# ================================
# Main Import Function
# ================================


def main():
    """Main import orchestrator"""
    print("=" * 100)
    print("COMPREHENSIVE EXCEL IMPORT")
    print("=" * 100)
    print(f"Excel file: {EXCEL_FILE}")
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # Check if file exists
    try:
        excel_file = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
        print(f"\n✅ Excel file loaded successfully")
        print(f"📋 Available sheets: {excel_file.sheet_names}")
    except FileNotFoundError:
        print(f'\n❌ Error: File "{EXCEL_FILE}" not found')
        print("Please provide the Excel file path or place it in the current directory")
        return 1
    except Exception as e:
        print(f"\n❌ Error loading Excel file: {str(e)}")
        return 1

    # Initialize database
    db = SessionLocal()

    try:
        # Track overall statistics
        total_stats = {"imported": 0, "updated": 0, "skipped": 0}

        # Import each sheet
        sheets_to_import = [
            ("demographic", import_demographic_data),
            ("self_screen", import_sansa_data),
            ("satisfaction", import_satisfaction_data),
            ("mna", import_mna_data),
            ("bia", import_bia_data),
        ]

        for sheet_key, import_func in sheets_to_import:
            sheet_name = SHEET_NAMES.get(sheet_key)
            if not sheet_name:
                continue

            try:
                # Check if sheet exists in Excel
                if sheet_name not in excel_file.sheet_names:
                    print(f'\n⚠️  Sheet "{sheet_name}" not found in Excel file')
                    continue

                # Read sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                # Import data
                imported, updated, skipped = import_func(df, db)
                total_stats["imported"] += imported
                total_stats["updated"] += updated
                total_stats["skipped"] += skipped

            except Exception as e:
                print(f"\n❌ Error importing {sheet_name}: {str(e)}")
                continue

        # Print summary
        print("\n" + "=" * 100)
        print("IMPORT SUMMARY")
        print("=" * 100)
        print(f'Total imported: {total_stats["imported"]}')
        print(f'Total updated:  {total_stats["updated"]}')
        print(f'Total skipped:  {total_stats["skipped"]}')
        print("=" * 100)
        print("✅ Import completed successfully")

    except Exception as e:
        print(f"\n❌ Fatal error during import: {str(e)}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
