#!/usr/bin/env python3
"""
Custom Import Script for THESIS PHASE2 Excel Data
Map Excel columns to Database columns correctly
"""

import sys
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
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
EXCEL_FILE = "/Users/dev/SANSA/src/ปรับแก้ Test Data THESIS PHASE2 03022026.xlsx"

# Real sheet names from Excel (note: "Demographic " has trailing space!)
SHEET_NAMES = {
    "demographic": "Demographic ",  # Note the trailing space!
    "self_screen": "Self Screen Assess (3)",
    "satisfaction": "Satisfaction",
    "bia": "BIA",
    "mna": "MNA",
}

# ================================
# Column Mapping
# ================================

# MNA: Excel -> Database
MNA_COLUMN_MAP = {
    "ID": "visit_id",
    "mna_s1": "mna_s1",
    "mna_s2": "mna_s2",
    "mna_s3": "mna_s3",
    "mna_s4": "mna_s4",
    "mna_s5": "mna_s5",
    "mna_s6": "mna_s6",
    "mna_s7": "mna_s7",
    "mna_screen_total": "mna_screen_total",
    "mna_a1": "mna_a1",
    "mna_a2": "mna_a2",
    "mna_a3": "mna_a3",
    "mna_a4": "mna_a4",
    "mna_a5": "mna_a5",
    "mna_a6": "mna_a6",
    "mna_a7": "mna_a7",
    "mna_a8": "mna_a8",
    "mna_a9": "mna_a9",
    "mna_a10": "mna_a10",
    "mna_a11": "mna_a11",
    "mna_ass_total": "mna_ass_total",
    "mna_total": "mna_total",
    # Note: mna_a12 exists in Excel but not used in database
}

# SANSA/Self Screen: Excel -> Database
SANSA_COLUMN_MAP = {
    "ID": "visit_id",
    "scr_bw": "q1_score",  # weight change
    "scr_app": "q2_score",  # appetite/food intake
    "scr_act": "q3_score",  # daily activities
    "scr_dx": "q4_score",  # chronic disease
    "scr_total": "screening_total",
    "ass_meal": "q5_score",  # meals per day
    "ass_intake": "q6_score",  # portion size
    "ass_type": "q7_score",  # food texture
    "ass_rice_starch": "q8_score",
    "ass_meat_egg": "q9_score",
    "ass_milk": "q10_score",
    "ass_fruit": "q11_score",
    "ass_veget": "q12_score",
    "ass_water": "q13_score",
    "ass_sweetdrink": "q14_score",
    "ass_cook": "q15_score",
    "ass_oil": "q16_score",
    "ass_total": "diet_total",
}

# Satisfaction: Excel -> Database
SATISFACTION_COLUMN_MAP = {
    "ID": "visit_id",
    "sat_clarity": "q1_clarity",
    "sat_easy": "q2_ease_of_use",
    "sat_confident": "q3_confidence",
    "sat_design": "q4_presentation",
    "sat_result": "q5_results_display",
    "sat_benefit": "q6_usefulness",
    "sat_overall": "q7_overall_satisfaction",
    "sat_comment": "comments",
}

# BIA: Excel -> Database
BIA_COLUMN_MAP = {
    "ID": "visit_id",
    "age": "age",
    "sex": "sex",
    "wc_cm": "waist_circumference_cm",
    "weight_kg": "weight_kg",
    "height_cm": "height_cm",
    "bmi": "bmi",
    "fat_mass_kg": "fat_mass_kg",
    "pbf": "body_fat_percentage",
    "vfat_level": "visceral_fat_kg",  # Note: might need conversion
    "muscle_mass_kg": "muscle_mass_kg",
    "bone_mass_kg": "bone_mass_kg",
    "tbw": "water_percentage",
    "bmr_kcal": "metabolic_rate",
}

# Demographic: Excel -> Database
DEMOGRAPHIC_COLUMN_MAP = {
    "ID": "respondent_code",  # Will use as R{ID:03d}
    "Age": "age",
    "Sex": "sex",
    "Education": "education_level",
    "Marital_status": "marital_status",
    "Income": "monthly_income",
    "Living_with": "living_arrangement",
}

# ================================
# Helper Functions
# ================================


def safe_decimal(value, default=None):
    """Convert value to Decimal safely"""
    if pd.isna(value) or value == "" or value == "–":
        return default
    try:
        return Decimal(str(value))
    except:
        return default


def safe_int(value, default=None):
    """Convert value to int safely"""
    if pd.isna(value) or value == "" or value == "–":
        return default
    try:
        return int(float(value))
    except:
        return default


def safe_str(value, default=None):
    """Convert value to string safely"""
    if pd.isna(value) or value == "" or value == "–":
        return default
    return str(value).strip()


def map_sex(value):
    """Map sex value to enum"""
    if pd.isna(value):
        return None
    try:
        val = int(float(value))
        if val == 1:
            return Sex.MALE
        elif val == 2:
            return Sex.FEMALE
    except:
        pass
    return None


# ================================
# Import Functions
# ================================


def ensure_visits_exist(df, db):
    """Ensure visits exist for all IDs in dataframe"""
    print("\n🔍 Checking/Creating visits...")

    ids_in_data = df["ID"].dropna().unique()
    created = 0
    existing = 0

    for visit_id in ids_in_data:
        visit_id = int(visit_id)

        # Check if visit exists
        visit = db.query(Visit).filter(Visit.id == visit_id).first()
        if visit:
            existing += 1
            continue

        # Create visit with respondent
        # First ensure respondent exists
        respondent_code = f"R{visit_id:03d}"
        respondent = (
            db.query(Respondent)
            .filter(Respondent.respondent_code == respondent_code)
            .first()
        )

        if not respondent:
            respondent = Respondent(
                respondent_code=respondent_code,
                status=RespondentStatus.ELDERLY,
                created_by=1,
            )
            db.add(respondent)
            db.flush()

        # Create visit
        visit = Visit(
            id=visit_id,
            respondent_id=respondent.id,
            visit_number=1,
            visit_date=date.today(),
            visit_type=VisitType.BASELINE,
            created_by=1,
        )
        db.add(visit)
        created += 1

    db.commit()
    print(f"  ✅ Visits: {existing} existing, {created} created")


def import_demographic_data(df, db):
    """Import Demographic sheet"""
    print(f"\n📊 Importing Demographic data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            respondent_id = safe_int(row.get("ID"))
            if not respondent_id:
                skipped += 1
                continue

            respondent_code = f"R{respondent_id:03d}"

            respondent = (
                db.query(Respondent)
                .filter(Respondent.respondent_code == respondent_code)
                .first()
            )

            if respondent:
                # Update existing
                respondent.age = safe_int(row.get("Age"))
                respondent.sex = map_sex(row.get("Sex"))
                respondent.education_level = safe_str(row.get("Education"))
                respondent.marital_status = safe_str(row.get("Marital_status"))
                respondent.monthly_income = safe_str(row.get("Income"))
                respondent.living_arrangement = safe_str(row.get("Living_with"))

                # Store chronic diseases as JSON
                chronic_diseases = {
                    "dm": bool(safe_int(row.get("DM"), 0)),
                    "ht": bool(safe_int(row.get("HT"), 0)),
                    "dlp": bool(safe_int(row.get("DLP"), 0)),
                    "ckd": bool(safe_int(row.get("CKD"), 0)),
                    "ca": bool(safe_int(row.get("CA"), 0)),
                    "other": safe_str(row.get("Other_text")),
                }
                respondent.chronic_diseases = chronic_diseases
                updated += 1
            else:
                # Create new
                chronic_diseases = {
                    "dm": bool(safe_int(row.get("DM"), 0)),
                    "ht": bool(safe_int(row.get("HT"), 0)),
                    "dlp": bool(safe_int(row.get("DLP"), 0)),
                    "ckd": bool(safe_int(row.get("CKD"), 0)),
                    "ca": bool(safe_int(row.get("CA"), 0)),
                    "other": safe_str(row.get("Other_text")),
                }

                respondent = Respondent(
                    respondent_code=respondent_code,
                    age=safe_int(row.get("Age")),
                    sex=map_sex(row.get("Sex")),
                    education_level=safe_str(row.get("Education")),
                    marital_status=safe_str(row.get("Marital_status")),
                    monthly_income=safe_str(row.get("Income")),
                    living_arrangement=safe_str(row.get("Living_with")),
                    chronic_diseases=chronic_diseases,
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
    """Import SANSA/Self Screen sheet"""
    print(f"\n📊 Importing SANSA data: {len(df)} rows")

    imported = 0
    updated = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            visit_id = safe_int(row.get("ID"))
            if not visit_id:
                skipped += 1
                continue

            # Check if SANSA response exists
            sansa = (
                db.query(SANSAResponse)
                .filter(SANSAResponse.visit_id == visit_id)
                .first()
            )

            # Calculate total score
            screening_total = safe_decimal(row.get("scr_total"))
            diet_total = safe_decimal(row.get("ass_total"))
            total_score = None
            if screening_total is not None and diet_total is not None:
                total_score = screening_total + diet_total

            if sansa:
                # Update existing
                for excel_col, db_col in SANSA_COLUMN_MAP.items():
                    if excel_col != "ID" and excel_col in row:
                        if "score" in db_col or "total" in db_col:
                            setattr(sansa, db_col, safe_decimal(row.get(excel_col)))
                sansa.total_score = total_score
                updated += 1
            else:
                # Create new
                sansa = SANSAResponse(
                    visit_id=visit_id,
                    scoring_version_id=1,
                    screening_total=screening_total,
                    diet_total=diet_total,
                    total_score=total_score,
                )

                # Set individual scores
                for excel_col, db_col in SANSA_COLUMN_MAP.items():
                    if excel_col != "ID" and excel_col in row:
                        if "score" in db_col:
                            setattr(sansa, db_col, safe_decimal(row.get(excel_col)))

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
            visit_id = safe_int(row.get("ID"))
            if not visit_id:
                skipped += 1
                continue

            satisfaction = (
                db.query(SatisfactionResponse)
                .filter(SatisfactionResponse.visit_id == visit_id)
                .first()
            )

            if satisfaction:
                # Update existing
                for excel_col, db_col in SATISFACTION_COLUMN_MAP.items():
                    if excel_col != "ID" and excel_col in row:
                        if db_col == "comments":
                            setattr(satisfaction, db_col, safe_str(row.get(excel_col)))
                        else:
                            setattr(satisfaction, db_col, safe_int(row.get(excel_col)))
                updated += 1
            else:
                # Create new
                satisfaction = SatisfactionResponse(
                    visit_id=visit_id,
                    q1_clarity=safe_int(row.get("sat_clarity")),
                    q2_ease_of_use=safe_int(row.get("sat_easy")),
                    q3_confidence=safe_int(row.get("sat_confident")),
                    q4_presentation=safe_int(row.get("sat_design")),
                    q5_results_display=safe_int(row.get("sat_result")),
                    q6_usefulness=safe_int(row.get("sat_benefit")),
                    q7_overall_satisfaction=safe_int(row.get("sat_overall")),
                    comments=safe_str(row.get("sat_comment")),
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

    for idx, row in df.iterrows():
        try:
            visit_id = safe_int(row.get("ID"))
            if not visit_id:
                skipped += 1
                continue

            mna = db.query(MNAResponse).filter(MNAResponse.visit_id == visit_id).first()

            if mna:
                # Update existing
                for excel_col, db_col in MNA_COLUMN_MAP.items():
                    if excel_col != "ID" and excel_col in row:
                        setattr(mna, db_col, safe_decimal(row.get(excel_col)))
                updated += 1
            else:
                # Create new
                mna = MNAResponse(
                    visit_id=visit_id,
                    scoring_version_id=1,
                    entry_mode=EntryMode.STAFF,
                    created_by=1,
                )

                # Set all score columns
                for excel_col, db_col in MNA_COLUMN_MAP.items():
                    if excel_col != "ID" and excel_col in row:
                        setattr(mna, db_col, safe_decimal(row.get(excel_col)))

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
            visit_id = safe_int(row.get("ID"))
            if not visit_id:
                skipped += 1
                continue

            bia = db.query(BIARecord).filter(BIARecord.visit_id == visit_id).first()

            if bia:
                # Update existing
                for excel_col, db_col in BIA_COLUMN_MAP.items():
                    if excel_col != "ID" and excel_col in row:
                        if db_col == "sex":
                            setattr(bia, db_col, map_sex(row.get(excel_col)))
                        elif db_col in ["age", "metabolic_rate"]:
                            setattr(bia, db_col, safe_int(row.get(excel_col)))
                        else:
                            setattr(bia, db_col, safe_decimal(row.get(excel_col)))
                updated += 1
            else:
                # Create new
                bia = BIARecord(
                    visit_id=visit_id,
                    age=safe_int(row.get("age")),
                    sex=map_sex(row.get("sex")),
                    waist_circumference_cm=safe_decimal(row.get("wc_cm")),
                    weight_kg=safe_decimal(row.get("weight_kg")),
                    height_cm=safe_decimal(row.get("height_cm")),
                    bmi=safe_decimal(row.get("bmi")),
                    fat_mass_kg=safe_decimal(row.get("fat_mass_kg")),
                    body_fat_percentage=safe_decimal(row.get("pbf")),
                    visceral_fat_kg=safe_decimal(row.get("vfat_level")),
                    muscle_mass_kg=safe_decimal(row.get("muscle_mass_kg")),
                    bone_mass_kg=safe_decimal(row.get("bone_mass_kg")),
                    water_percentage=safe_decimal(row.get("tbw")),
                    metabolic_rate=safe_int(row.get("bmr_kcal")),
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
    print("=" * 120)
    print("THESIS PHASE2 DATA IMPORT")
    print("=" * 120)
    print(f"Excel file: {EXCEL_FILE}")
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # Check if file exists
    try:
        excel_file = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
        print(f"\n✅ Excel file loaded successfully")
        print(f"📋 Available sheets: {len(excel_file.sheet_names)} sheets")
    except FileNotFoundError:
        print(f"\n❌ Error: File not found at {EXCEL_FILE}")
        return 1
    except Exception as e:
        print(f"\n❌ Error loading Excel file: {str(e)}")
        return 1

    # Initialize database
    db = SessionLocal()

    try:
        # Track overall statistics
        total_stats = {"imported": 0, "updated": 0, "skipped": 0}

        # First, ensure visits exist (read from any sheet that has ID column)
        df_first = pd.read_excel(excel_file, sheet_name="MNA")
        ensure_visits_exist(df_first, db)

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
                # Check if sheet exists
                if sheet_name not in excel_file.sheet_names:
                    print(f'\n⚠️  Sheet "{sheet_name}" not found')
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
                import traceback

                traceback.print_exc()
                continue

        # Print summary
        print("\n" + "=" * 120)
        print("IMPORT SUMMARY")
        print("=" * 120)
        print(f'Total imported: {total_stats["imported"]}')
        print(f'Total updated:  {total_stats["updated"]}')
        print(f'Total skipped:  {total_stats["skipped"]}')
        print("=" * 120)
        print("✅ Import completed successfully")

    except Exception as e:
        print(f"\n❌ Fatal error during import: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
