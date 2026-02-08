#!/usr/bin/env python3
"""
Enhanced seed script to create comprehensive sample data including:
- Sample respondents with all 10 demographic fields
- Sample visits
- Sample SANSA responses with realistic answers
- Sample MNA responses
- Sample BIA records
- Sample satisfaction responses
"""

import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import (
    User,
    Facility,
    Respondent,
    Visit,
    SANSAResponse,
    MNAResponse,
    BIARecord,
    SatisfactionResponse,
    ScoringRuleVersion,
)


def seed_sample_data():
    """Create comprehensive sample data for testing"""
    db = SessionLocal()

    try:
        print("🌱 Seeding sample data...")

        # Get admin user
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("❌ Admin user not found. Please run seed.py first.")
            return

        # Get facility
        facility = db.query(Facility).first()
        if not facility:
            print("❌ No facilities found. Please run seed.py first.")
            return

        # Get scoring versions
        sansa_version = (
            db.query(ScoringRuleVersion)
            .filter(
                ScoringRuleVersion.instrument_name == "SANSA",
                ScoringRuleVersion.is_active == True,
            )
            .first()
        )

        mna_version = (
            db.query(ScoringRuleVersion)
            .filter(
                ScoringRuleVersion.instrument_name == "MNA",
                ScoringRuleVersion.is_active == True,
            )
            .first()
        )

        if not sansa_version or not mna_version:
            print("❌ Scoring versions not found. Please run seed.py first.")
            return

        # Sample data templates
        sample_respondents = [
            {
                "respondent_code": "RESP001",
                "status": "elderly",
                "age": 68,
                "sex": "female",
                "education_level": "มัธยมศึกษา",
                "marital_status": "หม้าย",
                "monthly_income": "5001-10000",
                "income_sources": ["บำนาญ", "ลูกหลานให้"],
                "chronic_diseases": {
                    "hypertension": True,
                    "diabetes": True,
                    "heart_disease": False,
                    "kidney_disease": False,
                    "cancer": False,
                    "other": "",
                },
                "living_arrangement": "อยู่กับลูก",
            },
            {
                "respondent_code": "RESP002",
                "status": "elderly",
                "age": 72,
                "sex": "male",
                "education_level": "ประถมศึกษา",
                "marital_status": "สมรส",
                "monthly_income": "10001-20000",
                "income_sources": ["บำนาญ", "ดอกเบี้ย/เงินฝาก"],
                "chronic_diseases": {
                    "hypertension": True,
                    "diabetes": False,
                    "heart_disease": False,
                    "kidney_disease": False,
                    "cancer": False,
                    "other": "",
                },
                "living_arrangement": "อยู่กับคู่สมรส",
            },
            {
                "respondent_code": "RESP003",
                "status": "caregiver",
                "age": 45,
                "sex": "female",
                "education_level": "ปริญญาตรี",
                "marital_status": "สมรส",
                "monthly_income": "20001-40000",
                "income_sources": ["เงินเดือน/ค่าจ้าง"],
                "chronic_diseases": {
                    "hypertension": False,
                    "diabetes": False,
                    "heart_disease": False,
                    "kidney_disease": False,
                    "cancer": False,
                    "other": "",
                },
                "living_arrangement": "อยู่กับครอบครัว",
            },
            {
                "respondent_code": "RESP004",
                "status": "elderly",
                "age": 75,
                "sex": "female",
                "education_level": "ไม่ได้เรียนหนังสือ",
                "marital_status": "หม้าย",
                "monthly_income": "ต่ำกว่า 5000",
                "income_sources": ["ลูกหลานให้", "เบี้ยยังชีพ"],
                "chronic_diseases": {
                    "hypertension": True,
                    "diabetes": True,
                    "heart_disease": True,
                    "kidney_disease": False,
                    "cancer": False,
                    "other": "โรคข้อเข่าเสื่อม",
                },
                "living_arrangement": "อยู่กับลูก",
            },
            {
                "respondent_code": "RESP005",
                "status": "elderly",
                "age": 65,
                "sex": "male",
                "education_level": "ปริญญาตรี",
                "marital_status": "สมรส",
                "monthly_income": "มากกว่า 40000",
                "income_sources": ["บำนาญ", "ดอกเบี้ย/เงินฝาก", "รายได้จากทรัพย์สิน"],
                "chronic_diseases": {
                    "hypertension": False,
                    "diabetes": False,
                    "heart_disease": False,
                    "kidney_disease": False,
                    "cancer": False,
                    "other": "",
                },
                "living_arrangement": "อยู่กับคู่สมรส",
            },
        ]

        # Create respondents with visits and assessments
        created_count = 0
        for resp_data in sample_respondents:
            # Check if respondent exists
            existing = (
                db.query(Respondent)
                .filter(Respondent.respondent_code == resp_data["respondent_code"])
                .first()
            )

            if existing:
                print(f"⏭️  Skipping {resp_data['respondent_code']} (already exists)")
                continue

            # Create respondent
            respondent = Respondent(
                respondent_code=resp_data["respondent_code"],
                status=resp_data["status"],
                age=resp_data["age"],
                sex=resp_data["sex"],
                education_level=resp_data["education_level"],
                marital_status=resp_data["marital_status"],
                monthly_income=resp_data["monthly_income"],
                income_sources=resp_data["income_sources"],
                chronic_diseases=resp_data["chronic_diseases"],
                living_arrangement=resp_data["living_arrangement"],
                created_by=admin.id,
            )
            db.add(respondent)
            db.flush()

            # Create visit
            visit = Visit(
                respondent_id=respondent.id,
                facility_id=facility.id,
                visit_number=1,
                visit_date=date.today() - timedelta(days=random.randint(1, 30)),
                visit_type="baseline",
                created_by=admin.id,
            )
            db.add(visit)
            db.flush()

            # Create SANSA response (realistic answers)
            sansa = create_sample_sansa_response(visit.id, sansa_version.id, resp_data)
            db.add(sansa)

            # Create MNA response for elderly only
            if resp_data["status"] == "elderly":
                mna = create_sample_mna_response(
                    visit.id, mna_version.id, resp_data, admin.id
                )
                db.add(mna)

                # Create BIA record for elderly
                bia = create_sample_bia_record(visit.id, resp_data, admin.id)
                db.add(bia)

            # Create satisfaction response
            satisfaction = create_sample_satisfaction_response(visit.id)
            db.add(satisfaction)

            created_count += 1
            print(
                f"✓ Created: {resp_data['respondent_code']} ({resp_data['status']}, {resp_data['age']} years)"
            )

        db.commit()
        print(
            f"\n✅ Created {created_count} sample respondents with complete assessments!"
        )

    except Exception as e:
        print(f"\n❌ Error seeding sample data: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_sansa_response(
    visit_id: int, version_id: int, resp_data: dict
) -> SANSAResponse:
    """Create realistic SANSA response based on respondent profile"""
    from app.services.scoring_service import calculate_sansa_scores

    # Adjust answers based on age and health status
    has_chronic = any(
        [
            resp_data["chronic_diseases"].get("hypertension"),
            resp_data["chronic_diseases"].get("diabetes"),
            resp_data["chronic_diseases"].get("heart_disease"),
        ]
    )

    is_old = resp_data["age"] >= 70

    # Screening questions (Q1-Q4)
    answers = {
        "q1_weight_change": (
            "คงเดิม" if resp_data["age"] < 70 else random.choice(["ลดลง", "คงเดิม"])
        ),
        "q2_food_intake": "ปกติ" if not has_chronic else random.choice(["น้อยลง", "ปกติ"]),
        "q3_daily_activities": "ปกติ" if resp_data["age"] < 70 else "ช้ากว่าปกติ",
        "q4_chronic_disease": "มี" if has_chronic else "ไม่มี",
        # Dietary questions (Q5-Q16)
        "q5_meals_per_day": "3",
        "q6_portion_size": "75%" if is_old else "100%",
        "q7_food_texture": "ปกติ",
        "q8_rice_starch": random.choice(["3-4", "5-6", "7-8"]),
        "q9_protein": random.choice(["3-4", "5-6"]),
        "q10_milk": random.choice(["1-2", "3-4"]),
        "q11_fruits": random.choice(["2-3", "4-5"]),
        "q12_vegetables": random.choice(["3-4", "5-6"]),
        "q13_water": random.choice(["6-8", "9-10"]),
        "q14_sweet_drinks": random.choice(["ไม่ดื่ม", "1-2"]),
        "q15_cooking_method": random.choice(["ต้ม/นึ่ง", "ผัด"]),
        "q16_oil_coconut": random.choice(["ไม่ใช้", "ใช้น้อย"]),
    }

    # Calculate scores
    scores = calculate_sansa_scores(answers)

    return SANSAResponse(
        visit_id=visit_id,
        scoring_version_id=version_id,
        **answers,
        q1_score=Decimal(str(scores["q1_score"])),
        q2_score=Decimal(str(scores["q2_score"])),
        q3_score=Decimal(str(scores["q3_score"])),
        q4_score=Decimal(str(scores["q4_score"])),
        q5_score=Decimal(str(scores["q5_score"])),
        q6_score=Decimal(str(scores["q6_score"])),
        q7_score=Decimal(str(scores["q7_score"])),
        q8_score=Decimal(str(scores["q8_score"])),
        q9_score=Decimal(str(scores["q9_score"])),
        q10_score=Decimal(str(scores["q10_score"])),
        q11_score=Decimal(str(scores["q11_score"])),
        q12_score=Decimal(str(scores["q12_score"])),
        q13_score=Decimal(str(scores["q13_score"])),
        q14_score=Decimal(str(scores["q14_score"])),
        q15_score=Decimal(str(scores["q15_score"])),
        q16_score=Decimal(str(scores["q16_score"])),
        screening_total=Decimal(str(scores["screening_total"])),
        diet_total=Decimal(str(scores["diet_total"])),
        total_score=Decimal(str(scores["total_score"])),
        result_level=scores["result_level"],
        completed_at=datetime.now(),
    )


def create_sample_mna_response(
    visit_id: int, version_id: int, resp_data: dict, created_by: int
) -> MNAResponse:
    """Create realistic MNA response"""
    from app.services.scoring_service import calculate_mna_score

    has_disease = any(
        [
            resp_data["chronic_diseases"].get("hypertension"),
            resp_data["chronic_diseases"].get("diabetes"),
            resp_data["chronic_diseases"].get("heart_disease"),
        ]
    )

    # Screening section
    answers = {
        "q1_food_intake_decline": "moderate" if resp_data["age"] > 70 else "no",
        "q2_weight_loss": "1_3kg" if has_disease else "no",
        "q3_mobility": "goes_out" if resp_data["age"] < 75 else "bed_chair",
        "q4_stress_illness": "yes" if has_disease else "no",
        "q5_neuropsychological": "no" if resp_data["age"] < 75 else "mild_dementia",
        "q6_bmi": "21_23" if resp_data["sex"] == "female" else "23_25",
        "q7_calf_circumference": "31_34",
    }

    # Calculate screening score
    partial_scores = calculate_mna_score(answers)

    # Add assessment if needed
    if partial_scores["screening_total"] <= 11:
        answers.update(
            {
                "q8_independent_living": "yes",
                "q9_medications": "3",
                "q10_pressure_sores": "no",
                "q11_full_meals": "3",
                "q12_protein_consumption": "2",
                "q13_fruits_vegetables": "2",
                "q14_fluid_intake": "5_cups",
                "q15_eating_independence": "self",
                "q16_self_nutrition": "ok",
                "q17_health_comparison": "better",
                "q18_mid_arm_circumference": "22_26",
            }
        )
        final_scores = calculate_mna_score(answers)
    else:
        final_scores = partial_scores

    mna_data = {
        "visit_id": visit_id,
        "scoring_version_id": version_id,
        "entry_mode": "staff",
        "created_by": created_by,
        "completed_at": datetime.now(),
    }

    # Add all answers and scores
    for key, value in answers.items():
        mna_data[key] = value
        score_key = key.replace("q", "q") + "_score"
        if score_key in final_scores:
            mna_data[score_key] = Decimal(str(final_scores[score_key]))

    mna_data["screening_total"] = Decimal(str(final_scores["screening_total"]))
    if "assessment_total" in final_scores:
        mna_data["assessment_total"] = Decimal(str(final_scores["assessment_total"]))
    mna_data["total_score"] = Decimal(str(final_scores["total_score"]))
    mna_data["result_category"] = final_scores["result_category"]

    return MNAResponse(**mna_data)


def create_sample_bia_record(
    visit_id: int, resp_data: dict, measured_by: int
) -> BIARecord:
    """Create realistic BIA record"""
    # Generate realistic measurements
    sex = resp_data["sex"]
    age = resp_data["age"]

    if sex == "female":
        weight = round(random.uniform(50, 65), 1)
        height = round(random.uniform(150, 160), 1)
        body_fat = round(random.uniform(28, 35), 1)
        muscle = round(random.uniform(35, 42), 1)
    else:
        weight = round(random.uniform(60, 75), 1)
        height = round(random.uniform(160, 172), 1)
        body_fat = round(random.uniform(18, 25), 1)
        muscle = round(random.uniform(45, 55), 1)

    bmi = round(weight / ((height / 100) ** 2), 1)

    # Determine BMI category (Asian-Pacific)
    if bmi < 18.5:
        bmi_category = "underweight"
    elif bmi < 23:
        bmi_category = "normal"
    elif bmi < 25:
        bmi_category = "overweight"
    elif bmi < 30:
        bmi_category = "obese_i"
    else:
        bmi_category = "obese_ii"

    return BIARecord(
        visit_id=visit_id,
        age=age,
        sex=sex,
        weight_kg=Decimal(str(weight)),
        height_cm=Decimal(str(height)),
        bmi=Decimal(str(bmi)),
        bmi_category=bmi_category,
        waist_circumference_cm=Decimal(str(round(random.uniform(75, 95), 1))),
        hip_circumference_cm=Decimal(str(round(random.uniform(90, 105), 1))),
        waist_hip_ratio=Decimal(str(round(random.uniform(0.8, 0.95), 2))),
        fat_mass_kg=Decimal(str(round(weight * body_fat / 100, 1))),
        body_fat_percentage=Decimal(str(body_fat)),
        visceral_fat_kg=Decimal(str(round(random.uniform(2, 5), 1))),
        muscle_mass_kg=Decimal(str(muscle)),
        bone_mass_kg=Decimal(str(round(random.uniform(2.5, 3.5), 1))),
        water_percentage=Decimal(str(round(random.uniform(50, 60), 1))),
        metabolic_rate=int(random.randint(1200, 1600)),
        weight_management="maintain" if bmi_category == "normal" else "decrease",
        food_recommendation="รับประทานอาหารครบ 5 หมู่ เน้นผัก ผลไม้ ลดของทอด ของหวาน",
        staff_signature="นางสาวสมหมาย ใจดี",
        measurement_date=date.today(),
        measured_by=measured_by,
    )


def create_sample_satisfaction_response(visit_id: int) -> SatisfactionResponse:
    """Create realistic satisfaction response"""
    # Most responses should be positive (4-5)
    return SatisfactionResponse(
        visit_id=visit_id,
        q1_clarity=random.choice([4, 5, 5]),
        q2_ease_of_use=random.choice([4, 5, 5]),
        q3_confidence=random.choice([4, 4, 5]),
        q4_presentation=random.choice([4, 5, 5]),
        q5_results_display=random.choice([4, 4, 5]),
        q6_usefulness=random.choice([4, 5, 5]),
        q7_overall_satisfaction=random.choice([4, 5, 5]),
        comments=random.choice(
            [
                "ระบบใช้งานง่าย เข้าใจได้ดี",
                "ดีมาก ชอบการแสดงผลที่ชัดเจน",
                "สะดวก รวดเร็ว",
                "",  # Some blank
            ]
        ),
        completed_at=datetime.now(),
    )


if __name__ == "__main__":
    seed_sample_data()
