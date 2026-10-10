from decimal import Decimal
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models import ScoringRuleVersion, ScoringRuleValue, SANSAResponse, MNAResponse
from app.services.sansa_definition import DB_SCORING_VERSION, score_answer


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

    def get_active_sansa_definition_version(self) -> Optional[ScoringRuleVersion]:
        """Resolve the database provenance row for the executable SANSA definition."""
        if self.db is None:
            return None
        return (
            self.db.query(ScoringRuleVersion)
            .filter(
                ScoringRuleVersion.instrument_name == "SANSA",
                ScoringRuleVersion.version_number == DB_SCORING_VERSION,
                ScoringRuleVersion.is_active == True,
            )
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

        The score is resolved exclusively by the approved, versioned SANSA
        definition.  Clients never submit or calculate item scores.
        """
        return Decimal(str(score_answer(question_num, answer_value)))

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
            version = self.get_active_scoring_version("SANSA") if self.db is not None else None
            if version is None:
                raise ValueError("ไม่พบเวอร์ชัน SANSA ที่เปิดใช้งาน")
            version_id = version.id

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

        # There is no approved classification based on the 16-item sum.  Keep
        # the aggregate columns only as auditable sums; Model 3 is the sole
        # outcome and is calculated from D2, D3, waist and age group.
        result_level = None

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
        - Screening (A-F): Max 14 points
        - Full Assessment (G-R): Max 16 points
        - Total: Max 30 points

        Thresholds:
        - Normal: 24-30
        - At-risk: 17-23.5
        - Malnourished: <17
        """
        # Accept the semantic values submitted by the MNA form. Numeric strings are
        # retained for backwards compatibility with older imports.
        scoring_map = {
            1: {"severe": 0, "moderate": 1, "none": 2, "0": 0, "1": 1, "2": 2},
            2: {">3kg": 0, "unknown": 1, "1-3kg": 2, "none": 3, "0": 0, "1": 1, "2": 2, "3": 3},
            3: {"bed_chair": 0, "home_only": 1, "goes_out": 2, "0": 0, "1": 1, "2": 2},
            4: {"yes": 0, "no": 2, "0": 0, "2": 2},
            5: {"severe": 0, "mild": 1, "none": 2, "0": 0, "1": 1, "2": 2},
            6: {"<19": 0, "19-21": 1, "21-23": 2, ">23": 3, "0": 0, "1": 1, "2": 2, "3": 3},
            7: {"no": 0, "yes": 1, "0": 0, "1": 1},
            8: {">3": 0, "2-3": 1, "<2": 1, "yes": 0, "no": 1, "0": 0, "1": 1},
            9: {"yes": 0, "no": 1, "0": 0, "1": 1},
            10: {"1": 0, "2": 1, "3": 2, "0": 0},
            11: {"0-1": 0, "2": 0.5, "3": 1, "0": 0, "0.5": 0.5, "1": 1},
            12: {"no": 0, "yes": 1, "0": 0, "1": 1},
            13: {"<3": 0, "3-5": 0.5, ">5": 1, "0": 0, "0.5": 0.5, "1": 1},
            14: {"need_help": 0, "self_difficulties": 1, "self_no_problem": 2, "0": 0, "1": 1, "2": 2},
            15: {"malnourished": 0, "uncertain": 1, "well_nourished": 2, "0": 0, "1": 1, "2": 2},
            16: {"worse": 0, "unknown": 0.5, "same": 1, "better": 2, "0": 0, "0.5": 0.5, "1": 1, "2": 2},
            17: {"<21": 0, "21-22": 0.5, ">22": 1, "0": 0, "0.5": 0.5, "1": 1},
            18: {"<31": 0, ">31": 1, ">=31": 1, "0": 0, "1": 1},
        }

        if question_num not in scoring_map or answer_value not in scoring_map[question_num]:
            raise ValueError(f"MNA item {question_num}: missing or unsupported answer")

        score = scoring_map[question_num][answer_value]
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
            version_id: Instrument version resolved by the write endpoint

        Returns:
            Dict with individual question scores, screening_total, assessment_total, total_score, result_category
        """
        # The approved MNA layout is A-F screening (6 items) and G-R
        # assessment (12 items). R uses q19/mna_a12, never screening q7.
        scores = {}
        screening_total = Decimal("0")
        screening_fields = [
            "q1_food_intake_decline", "q2_weight_loss", "q3_mobility",
            "q4_stress_illness", "q5_neuropsychological", "q6_bmi",
        ]
        for q_num, field_name in enumerate(screening_fields, 1):
            answer_value = getattr(mna_response, field_name, None) or ""
            q_score = self.calculate_mna_question_score(q_num, answer_value)
            scores[f"mna_s{q_num}"] = q_score
            screening_total += q_score

        assessment_fields = [
            "q8_independent_living", "q9_medications", "q10_pressure_sores",
            "q11_full_meals", "q12_protein_consumption", "q13_fruits_vegetables",
            "q14_fluid_intake", "q15_eating_independence", "q16_self_nutrition",
            "q17_health_comparison", "q18_mid_arm_circumference",
            "q19_calf_circumference_assess",
        ]
        assessment_total = Decimal("0")
        # A full result requires every G-R answer, regardless of the screening
        # subtotal. Missing answers must never become zero-point observations.
        for logical_num, field_name in enumerate(assessment_fields, 7):
            answer_value = getattr(mna_response, field_name, None) or ""
            q_score = self.calculate_mna_question_score(logical_num, answer_value)
            scores[f"mna_a{logical_num - 6}"] = q_score
            assessment_total += q_score

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
            "mna_screen_total": screening_total,
            "mna_ass_total": assessment_total,
            "mna_total": total_score,
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
