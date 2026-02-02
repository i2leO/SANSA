from decimal import Decimal
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models import ScoringRuleVersion, ScoringRuleValue, SANSAResponse, MNAResponse


class ScoringService:
    """Service for calculating scores and classifications"""

    def __init__(self, db: Session):
        self.db = db

    def get_active_scoring_version(
        self, instrument_name: str
    ) -> Optional[ScoringRuleVersion]:
        """Get the currently active scoring version for an instrument"""
        return (
            self.db.query(ScoringRuleVersion)
            .filter(
                ScoringRuleVersion.instrument_name == instrument_name,
                ScoringRuleVersion.is_active == True,
            )
            .order_by(ScoringRuleVersion.created_at.desc())
            .first()
        )

    def get_scoring_version(self, version_id: int) -> Optional[ScoringRuleVersion]:
        """Get a specific scoring version by ID"""
        return (
            self.db.query(ScoringRuleVersion)
            .filter(ScoringRuleVersion.id == version_id)
            .first()
        )

    def get_classification_level(
        self, version_id: int, total_score: Decimal
    ) -> Optional[str]:
        """Determine classification level based on score and thresholds"""
        rule_values = (
            self.db.query(ScoringRuleValue)
            .filter(ScoringRuleValue.version_id == version_id)
            .order_by(ScoringRuleValue.level_order)
            .all()
        )

        for rule_value in rule_values:
            # Handle different threshold configurations
            if rule_value.min_score is not None and rule_value.max_score is not None:
                if rule_value.min_score <= total_score <= rule_value.max_score:
                    return rule_value.level_code
            elif rule_value.min_score is not None:
                if total_score >= rule_value.min_score:
                    return rule_value.level_code
            elif rule_value.max_score is not None:
                if total_score <= rule_value.max_score:
                    return rule_value.level_code

        return None

    def get_advice_text(self, version_id: int, level_code: str) -> Optional[str]:
        """Get advice text for a classification level"""
        rule_value = (
            self.db.query(ScoringRuleValue)
            .filter(
                ScoringRuleValue.version_id == version_id,
                ScoringRuleValue.level_code == level_code,
            )
            .first()
        )

        return rule_value.advice_text if rule_value else None

    def calculate_sansa_question_score(
        self, question_num: int, answer_value: str
    ) -> Decimal:
        """
        Calculate score for a single SANSA question based on answer

        SANSA Scoring Rules (16 questions total):
        - Screening (Q1-Q4): 0-8 points
        - Dietary (Q5-Q16): 0-48 points
        - Total: 0-56 points

        Thresholds:
        - Normal: ≥38
        - At-risk: 25-37
        - Malnourished: 0-24
        """
        scoring_map = {
            # Screening Questions (Q1-Q4)
            1: {  # น้ำหนักตัว (Weight change)
                "decrease": 2,
                "ลดลง": 2,
                "stable": 0,
                "คงเดิม": 0,
                "increase": 2,
                "เพิ่มขึ้น": 2,
            },
            2: {  # การกินอาหาร (Food intake)
                "decrease": 2,
                "น้อยลง": 2,
                "normal": 0,
                "ปกติ": 0,
                "increase": 2,
                "มากขึ้น": 2,
            },
            3: {  # กิจวัตรประจำวัน (Daily activities)
                "cannot": 2,
                "ไม่ได้": 2,
                "slower": 1,
                "ช้ากว่าปกติ": 1,
                "normal": 0,
                "ปกติ": 0,
            },
            4: {"no": 0, "ไม่มี": 0, "yes": 2, "มี": 2},  # โรคประจำตัว (Chronic disease)
            # Dietary Questions (Q5-Q16)
            5: {  # มื้ออาหารต่อวัน (Meals per day)
                "rarely": 0,
                "แทบไม่ได้": 0,
                "1": 1,
                "1_meal": 1,
                "2": 2,
                "2_meals": 2,
                "3": 3,
                "3_meals": 3,
                "more_than_3": 4,
                ">3": 4,
            },
            6: {  # ปริมาณอาหารต่อมื้อ (Portion size)
                "25%": 0,
                "25": 0,
                "50%": 1,
                "50": 1,
                "75%": 2,
                "75": 2,
                "100%": 3,
                "100": 3,
                ">100%": 4,
                "more_than_100": 4,
            },
            7: {  # ลักษณะอาหาร (Food texture)
                "liquid": 0,
                "เหลว": 0,
                "soft": 2,
                "อ่อน": 2,
                "normal": 4,
                "ปกติ": 4,
            },
            8: {  # ข้าว/แป้ง (Rice/starch) - กำปั้น
                "0": 0,
                "1-3": 1,
                "1_to_3": 1,
                "4-6": 2,
                "4_to_6": 2,
                "7-9": 3,
                "7_to_9": 3,
                ">9": 4,
                "more_than_9": 4,
            },
            9: {  # เนื้อสัตว์ (Protein) - ฝ่ามือ
                "0": 0,
                "1-2": 1,
                "1_to_2": 1,
                "3-5": 2,
                "3_to_5": 2,
                "6-8": 3,
                "6_to_8": 3,
                ">8": 4,
                "more_than_8": 4,
            },
            10: {  # นม (Milk) - แก้ว
                "<1": 0,
                "less_than_1": 0,
                "1": 1,
                "2": 2,
                "3": 3,
                "4": 4,
            },
            11: {  # ผลไม้ (Fruits) - กำปั้น
                "0": 0,
                "1-2": 1,
                "1_to_2": 1,
                "3-5": 2,
                "3_to_5": 2,
                "6-8": 3,
                "6_to_8": 3,
                ">8": 4,
                "more_than_8": 4,
            },
            12: {  # ผัก (Vegetables) - อึงมือ
                "0": 0,
                "0-1": 1,
                "0_to_1": 1,
                "2-3": 2,
                "2_to_3": 2,
                "4": 3,
                ">4": 4,
                "more_than_4": 4,
            },
            13: {  # น้ำเปล่า (Water) - แก้ว
                "rarely": 0,
                "แทบไม่ได้": 0,
                "1-3": 1,
                "1_to_3": 1,
                "4-6": 2,
                "4_to_6": 2,
                "7-8": 3,
                "7_to_8": 3,
                ">8": 4,
                "more_than_8": 4,
            },
            14: {  # เครื่องดื่ม 3in1 (Sweet drinks)
                "0": 0,
                "1": 1,
                "2": 2,
                "3": 3,
                ">3": 4,
                "more_than_3": 4,
            },
            15: {  # วิธีปรุง (Cooking method)
                "steam_boil": 0,
                "ต้ม_นึ่ง": 0,
                "ต้ม/นึ่ง": 0,
                "no_coconut": 0,
                "stir_fry": 1,
                "ผัด": 1,
                "coconut_curry": 2,
                "แกงกะทิ": 2,
                "fried": 4,
                "ทอด": 4,
            },
            16: {  # น้ำมัน/กะทิ (Oil/coconut milk) - นิ้วหัวแม่มือ
                "0": 0,
                "1-2": 1,
                "1_to_2": 1,
                "3-4": 2,
                "3_to_4": 2,
                "5-6": 3,
                "5_to_6": 3,
                ">6": 4,
                "more_than_6": 4,
            },
        }

        if question_num not in scoring_map:
            return Decimal("0")

        score = scoring_map[question_num].get(answer_value, 0)
        return Decimal(str(score))

    def calculate_sansa_scores(
        self,
        sansa_response,  # Can be SANSAResponse model or SANSAResponseCreate schema
        version_id: Optional[int] = None,
    ) -> Dict:
        """
        Calculate SANSA screening, dietary, and total scores from question responses

        Args:
            sansa_response: SANSAResponse model instance or SANSAResponseCreate schema
            version_id: Optional scoring version ID (defaults to active version)

        Returns:
            Dict with individual question scores, screening_total, diet_total, total_score, result_level
        """
        if version_id is None:
            version_id = 1  # Default to version 1

        # Calculate scores for each question
        scores = {}

        # Screening questions (Q1-Q4)
        q1_score = self.calculate_sansa_question_score(
            1, sansa_response.q1_weight_change or ""
        )
        q2_score = self.calculate_sansa_question_score(
            2, sansa_response.q2_food_intake or ""
        )
        q3_score = self.calculate_sansa_question_score(
            3, sansa_response.q3_daily_activities or ""
        )
        q4_score = self.calculate_sansa_question_score(
            4, sansa_response.q4_chronic_disease or ""
        )

        scores["q1_score"] = q1_score
        scores["q2_score"] = q2_score
        scores["q3_score"] = q3_score
        scores["q4_score"] = q4_score

        screening_total = q1_score + q2_score + q3_score + q4_score

        # Dietary questions (Q5-Q16)
        diet_total = Decimal("0")
        for q_num in range(5, 17):
            q_field = f"q{q_num}_"
            # Get question answer based on field name
            question_field_map = {
                5: "meals_per_day",
                6: "portion_size",
                7: "food_texture",
                8: "rice_starch",
                9: "protein",
                10: "milk",
                11: "fruits",
                12: "vegetables",
                13: "water",
                14: "sweet_drinks",
                15: "cooking_method",
                16: "oil_coconut",
            }

            field_name = f"q{q_num}_{question_field_map[q_num]}"
            answer_value = getattr(sansa_response, field_name, None) or ""
            q_score = self.calculate_sansa_question_score(q_num, answer_value)
            scores[f"q{q_num}_score"] = q_score
            diet_total += q_score

        # Calculate overall total score
        total_score = screening_total + diet_total

        # Determine classification level
        # Thresholds: normal ≥38, at_risk 25-37, malnourished 0-24
        if total_score >= 38:
            result_level = "normal"
        elif total_score >= 25:
            result_level = "at_risk"
        else:
            result_level = "malnourished"

        return {
            **scores,  # Include all individual question scores
            "screening_total": screening_total,
            "diet_total": diet_total,
            "total_score": total_score,
            "result_level": result_level,
            "scoring_version_id": version_id,
        }

    def calculate_mna_question_score(
        self, question_num: int, answer_value: str
    ) -> Decimal:
        """
        Calculate score for a single MNA question based on answer

        MNA Scoring Rules (18 questions total):
        - Screening (Q1-Q7): Max 14 points
        - Full Assessment (Q8-Q18): Max 16 points
        - Total: Max 30 points

        Thresholds:
        - Normal: 24-30
        - At-risk: 17-23.5
        - Malnourished: <17
        """
        # Simplified scoring map - in production, this should be more comprehensive
        scoring_map = {
            1: {"0": 0, "1": 1, "2": 2},
            2: {"0": 0, "1": 1, "2": 2, "3": 3},
            3: {"0": 0, "1": 1, "2": 2},
            4: {"0": 0, "2": 2},
            5: {"0": 0, "1": 1, "2": 2},
            6: {"0": 0, "1": 1, "2": 2, "3": 3},
            7: {"0": 0, "3": 3},
            8: {"0": 0, "1": 1},
            9: {"0": 0, "1": 1},
            10: {"0": 0, "1": 1},
            11: {"0": 0, "1": 1, "2": 2},
            12: {"0": 0, "0.5": 0.5, "1": 1},
            13: {"0": 0, "1": 1},
            14: {"0": 0, "0.5": 0.5, "1": 1},
            15: {"0": 0, "1": 1, "2": 2},
            16: {"0": 0, "1": 1, "2": 2},
            17: {"0": 0, "0.5": 0.5, "1": 1, "2": 2},
            18: {"0": 0, "0.5": 0.5, "1": 1},
        }

        if question_num not in scoring_map:
            return Decimal("0")

        score = scoring_map[question_num].get(answer_value, 0)
        return Decimal(str(score))

    def calculate_mna_score(
        self,
        mna_response,  # Can be MNAResponse model or MNAResponseCreate schema
        version_id: Optional[int] = None,
    ) -> Dict:
        """
        Calculate MNA screening, assessment, and total score from question responses

        Args:
            mna_response: MNAResponse model instance or MNAResponseCreate schema
            version_id: Optional scoring version ID (defaults to 1)

        Returns:
            Dict with individual question scores, screening_total, assessment_total, total_score, result_category
        """
        if version_id is None:
            version_id = 1  # Default to version 1

        # Calculate scores for screening questions (Q1-Q7)
        scores = {}
        screening_total = Decimal("0")

        question_field_map = {
            1: "food_intake_decline",
            2: "weight_loss",
            3: "mobility",
            4: "psychological_stress",
            5: "neuropsychological_problems",
            6: "bmi_or_calf",
            7: "independent_living",
            8: "medications",
            9: "pressure_ulcers",
            10: "meals_per_day",
            11: "protein_markers",
            12: "fruits_vegetables",
            13: "fluid_intake",
            14: "feeding_ability",
            15: "self_nutrition_view",
            16: "health_comparison",
            17: "mid_arm_circumference",
            18: "calf_circumference",
        }

        # Calculate screening (Q1-Q7)
        for q_num in range(1, 8):
            field_name = f"q{q_num}_{question_field_map[q_num]}"
            answer_value = getattr(mna_response, field_name, None) or ""
            q_score = self.calculate_mna_question_score(q_num, answer_value)
            scores[f"q{q_num}_score"] = q_score
            screening_total += q_score

        # Calculate assessment (Q8-Q18) - only if screening ≤11
        assessment_total = Decimal("0")
        if screening_total <= 11:
            for q_num in range(8, 19):
                field_name = f"q{q_num}_{question_field_map[q_num]}"
                answer_value = getattr(mna_response, field_name, None) or ""
                q_score = self.calculate_mna_question_score(q_num, answer_value)
                scores[f"q{q_num}_score"] = q_score
                assessment_total += q_score
        else:
            # If screening > 11, skip assessment (normal nutritional status)
            for q_num in range(8, 19):
                scores[f"q{q_num}_score"] = Decimal("0")

        # Calculate total score
        total_score = screening_total + assessment_total

        # Determine category
        # Thresholds: normal 24-30, at_risk 17-23.5, malnourished <17
        if total_score >= 24:
            result_category = "normal"
        elif total_score >= 17:
            result_category = "at_risk"
        else:
            result_category = "malnourished"

        return {
            **scores,  # Include all individual question scores
            "screening_total": screening_total,
            "assessment_total": assessment_total,
            "total_score": total_score,
            "result_category": result_category,
            "scoring_version_id": version_id,
        }

    def calculate_bmi(self, weight_kg: Decimal, height_cm: Decimal) -> Decimal:
        """Calculate BMI from weight and height"""
        if weight_kg and height_cm and height_cm > 0:
            height_m = height_cm / 100
            bmi = weight_kg / (height_m * height_m)
            return round(bmi, 2)
        return None

    def get_bmi_category(self, bmi: Decimal) -> str:
        """
        Get BMI category based on Asian-Pacific thresholds

        Categories:
        - <18.5: ผอม (underweight)
        - 18.5-22.9: ปกติ (normal)
        - 23.0-24.9: เกิน (overweight)
        - 25.0-29.9: อ้วนระดับ 1 (obese I)
        - ≥30: อ้วนระดับ 2 (obese II)
        """
        if bmi < 18.5:
            return "underweight"
        elif bmi < 23:
            return "normal"
        elif bmi < 25:
            return "overweight"
        elif bmi < 30:
            return "obese_1"
        else:
            return "obese_2"

    def calculate_waist_hip_ratio(
        self, waist_cm: Decimal, hip_cm: Decimal
    ) -> Optional[Decimal]:
        """Calculate waist-to-hip ratio"""
        if waist_cm and hip_cm and hip_cm > 0:
            ratio = waist_cm / hip_cm
            return round(ratio, 3)
        return None
