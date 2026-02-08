from typing import Optional, List
from datetime import datetime, date
import csv
import io
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    Respondent,
    Visit,
    SANSAResponse,
    SatisfactionResponse,
    MNAResponse,
    BIARecord,
)


class ExportService:
    """Service for exporting data to SPSS-compatible CSV format"""

    def __init__(self, db: Session):
        self.db = db

    def export_sansa_csv(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        facility_id: Optional[int] = None,
    ) -> str:
        """Export SANSA data to CSV"""

        # Build query
        query = (
            self.db.query(Respondent, Visit, SANSAResponse)
            .join(Visit, Visit.respondent_id == Respondent.id)
            .join(SANSAResponse, SANSAResponse.visit_id == Visit.id)
        )

        # Apply filters
        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)
        if facility_id:
            query = query.filter(Visit.facility_id == facility_id)

        query = query.filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        results = query.all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        header = [
            # Respondent demographics (expanded)
            "respondent_code",
            "respondent_id",
            "status",
            "age",
            "sex",
            "education_level",
            "marital_status",
            "monthly_income",
            "income_sources",
            "chronic_diseases",
            "living_arrangement",
            # Visit information
            "visit_id",
            "visit_number",
            "visit_date",
            # SANSA screening questions & scores (Q1-Q4)
            "sansa_q1_answer",
            "sansa_q1_score",
            "sansa_q2_answer",
            "sansa_q2_score",
            "sansa_q3_answer",
            "sansa_q3_score",
            "sansa_q4_answer",
            "sansa_q4_score",
            # SANSA dietary questions & scores (Q5-Q16)
            "sansa_q5_answer",
            "sansa_q5_score",
            "sansa_q6_answer",
            "sansa_q6_score",
            "sansa_q7_answer",
            "sansa_q7_score",
            "sansa_q8_answer",
            "sansa_q8_score",
            "sansa_q9_answer",
            "sansa_q9_score",
            "sansa_q10_answer",
            "sansa_q10_score",
            "sansa_q11_answer",
            "sansa_q11_score",
            "sansa_q12_answer",
            "sansa_q12_score",
            "sansa_q13_answer",
            "sansa_q13_score",
            "sansa_q14_answer",
            "sansa_q14_score",
            "sansa_q15_answer",
            "sansa_q15_score",
            "sansa_q16_answer",
            "sansa_q16_score",
            # SANSA totals
            "sansa_screening_total",
            "sansa_diet_total",
            "sansa_total",
            "sansa_level",
            "sansa_version",
            "sansa_completed_at",
        ]
        writer.writerow(header)

        # Write data rows
        for respondent, visit, sansa_response in results:
            # Prepare JSON fields
            import json

            income_sources = (
                json.dumps(respondent.income_sources)
                if respondent.income_sources
                else ""
            )
            chronic_diseases = (
                json.dumps(respondent.chronic_diseases)
                if respondent.chronic_diseases
                else ""
            )

            row = [
                # Respondent demographics (expanded)
                respondent.respondent_code,
                respondent.id,
                respondent.status or "",
                respondent.age or "",
                self._encode_sex(respondent.sex),
                respondent.education_level or "",
                respondent.marital_status or "",
                respondent.monthly_income or "",
                income_sources,
                chronic_diseases,
                respondent.living_arrangement or "",
                # Visit information
                visit.id,
                visit.visit_number,
                visit.visit_date.isoformat() if visit.visit_date else "",
                # SANSA screening questions & scores (Q1-Q4)
                sansa_response.q1_weight_change or "",
                float(sansa_response.q1_score) if sansa_response.q1_score else "",
                sansa_response.q2_food_intake or "",
                float(sansa_response.q2_score) if sansa_response.q2_score else "",
                sansa_response.q3_daily_activities or "",
                float(sansa_response.q3_score) if sansa_response.q3_score else "",
                sansa_response.q4_chronic_disease or "",
                float(sansa_response.q4_score) if sansa_response.q4_score else "",
                # SANSA dietary questions & scores (Q5-Q16)
                sansa_response.q5_meals_per_day or "",
                float(sansa_response.q5_score) if sansa_response.q5_score else "",
                sansa_response.q6_portion_size or "",
                float(sansa_response.q6_score) if sansa_response.q6_score else "",
                sansa_response.q7_food_texture or "",
                float(sansa_response.q7_score) if sansa_response.q7_score else "",
                sansa_response.q8_rice_starch or "",
                float(sansa_response.q8_score) if sansa_response.q8_score else "",
                sansa_response.q9_protein or "",
                float(sansa_response.q9_score) if sansa_response.q9_score else "",
                sansa_response.q10_milk or "",
                float(sansa_response.q10_score) if sansa_response.q10_score else "",
                sansa_response.q11_fruits or "",
                float(sansa_response.q11_score) if sansa_response.q11_score else "",
                sansa_response.q12_vegetables or "",
                float(sansa_response.q12_score) if sansa_response.q12_score else "",
                sansa_response.q13_water or "",
                float(sansa_response.q13_score) if sansa_response.q13_score else "",
                sansa_response.q14_sweet_drinks or "",
                float(sansa_response.q14_score) if sansa_response.q14_score else "",
                sansa_response.q15_cooking_method or "",
                float(sansa_response.q15_score) if sansa_response.q15_score else "",
                sansa_response.q16_oil_coconut or "",
                float(sansa_response.q16_score) if sansa_response.q16_score else "",
                # SANSA totals
                (
                    float(sansa_response.screening_total)
                    if sansa_response.screening_total
                    else ""
                ),
                float(sansa_response.diet_total) if sansa_response.diet_total else "",
                float(sansa_response.total_score) if sansa_response.total_score else "",
                self._encode_sansa_level(sansa_response.result_level),
                sansa_response.scoring_version_id,
                (
                    sansa_response.completed_at.isoformat()
                    if sansa_response.completed_at
                    else ""
                ),
            ]
            writer.writerow(row)

        return output.getvalue()

    def export_mna_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """Export MNA data to CSV"""

        query = (
            self.db.query(Respondent, Visit, MNAResponse)
            .join(Visit, Visit.respondent_id == Respondent.id)
            .join(MNAResponse, MNAResponse.visit_id == Visit.id)
        )

        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)

        query = query.filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        results = query.all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header with MNA items (18 questions with answers and scores)
        header = [
            "respondent_code",
            "visit_id",
            "visit_date",
            # Screening section (Q1-Q7)
            "mna_q1_answer",
            "mna_q1_score",
            "mna_q2_answer",
            "mna_q2_score",
            "mna_q3_answer",
            "mna_q3_score",
            "mna_q4_answer",
            "mna_q4_score",
            "mna_q5_answer",
            "mna_q5_score",
            "mna_q6_answer",
            "mna_q6_score",
            "mna_q7_answer",
            "mna_q7_score",
            "mna_screening_total",
            # Assessment section (Q8-Q18)
            "mna_q8_answer",
            "mna_q8_score",
            "mna_q9_answer",
            "mna_q9_score",
            "mna_q10_answer",
            "mna_q10_score",
            "mna_q11_answer",
            "mna_q11_score",
            "mna_q12_answer",
            "mna_q12_score",
            "mna_q13_answer",
            "mna_q13_score",
            "mna_q14_answer",
            "mna_q14_score",
            "mna_q15_answer",
            "mna_q15_score",
            "mna_q16_answer",
            "mna_q16_score",
            "mna_q17_answer",
            "mna_q17_score",
            "mna_q18_answer",
            "mna_q18_score",
            "mna_assessment_total",
            # Totals
            "mna_total",
            "mna_category",
            "entry_mode",
            "completed_at",
        ]
        writer.writerow(header)

        for respondent, visit, mna_response in results:
            row = [
                respondent.respondent_code,
                visit.id,
                visit.visit_date.isoformat() if visit.visit_date else "",
                # Screening section (Q1-Q7)
                mna_response.q1_food_intake_decline or "",
                float(mna_response.mna_s1) if mna_response.mna_s1 else "",
                mna_response.q2_weight_loss or "",
                float(mna_response.mna_s2) if mna_response.mna_s2 else "",
                mna_response.q3_mobility or "",
                float(mna_response.mna_s3) if mna_response.mna_s3 else "",
                mna_response.q4_stress_illness or "",
                float(mna_response.mna_s4) if mna_response.mna_s4 else "",
                mna_response.q5_neuropsychological or "",
                float(mna_response.mna_s5) if mna_response.mna_s5 else "",
                mna_response.q6_bmi or "",
                float(mna_response.mna_s6) if mna_response.mna_s6 else "",
                mna_response.q7_calf_circumference or "",
                float(mna_response.mna_s7) if mna_response.mna_s7 else "",
                (
                    float(mna_response.mna_screen_total)
                    if mna_response.mna_screen_total
                    else ""
                ),
                # Assessment section (Q8-Q18)
                mna_response.q8_independent_living or "",
                float(mna_response.mna_a1) if mna_response.mna_a1 else "",
                mna_response.q9_medications or "",
                float(mna_response.mna_a2) if mna_response.mna_a2 else "",
                mna_response.q10_pressure_sores or "",
                float(mna_response.mna_a3) if mna_response.mna_a3 else "",
                mna_response.q11_full_meals or "",
                float(mna_response.mna_a4) if mna_response.mna_a4 else "",
                mna_response.q12_protein_consumption or "",
                float(mna_response.mna_a5) if mna_response.mna_a5 else "",
                mna_response.q13_fruits_vegetables or "",
                float(mna_response.mna_a6) if mna_response.mna_a6 else "",
                mna_response.q14_fluid_intake or "",
                float(mna_response.mna_a7) if mna_response.mna_a7 else "",
                mna_response.q15_eating_independence or "",
                float(mna_response.mna_a8) if mna_response.mna_a8 else "",
                mna_response.q16_self_nutrition or "",
                float(mna_response.mna_a9) if mna_response.mna_a9 else "",
                mna_response.q17_health_comparison or "",
                float(mna_response.mna_a10) if mna_response.mna_a10 else "",
                mna_response.q18_mid_arm_circumference or "",
                float(mna_response.mna_a11) if mna_response.mna_a11 else "",
                (
                    float(mna_response.mna_ass_total)
                    if mna_response.mna_ass_total
                    else ""
                ),
                # Totals
                float(mna_response.mna_total) if mna_response.mna_total else "",
                self._encode_mna_category(mna_response.result_category),
                mna_response.entry_mode or "",
                (
                    mna_response.completed_at.isoformat()
                    if mna_response.completed_at
                    else ""
                ),
            ]
            writer.writerow(row)

        return output.getvalue()

    def export_bia_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """Export BIA/anthropometry data to CSV"""

        query = (
            self.db.query(Respondent, Visit, BIARecord)
            .join(Visit, Visit.respondent_id == Respondent.id)
            .join(BIARecord, BIARecord.visit_id == Visit.id)
        )

        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)

        query = query.filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        results = query.all()

        output = io.StringIO()
        writer = csv.writer(output)

        header = [
            "respondent_code",
            "visit_id",
            "visit_date",
            # Basic info
            "bia_age",
            "bia_sex",
            # Basic measurements
            "bia_weight_kg",
            "bia_height_cm",
            "bia_bmi",
            "bia_bmi_category",
            "bia_waist_cm",
            "bia_hip_cm",
            "bia_waist_hip_ratio",
            # Body composition
            "bia_fat_mass_kg",
            "bia_body_fat_pct",
            "bia_visceral_fat_kg",
            "bia_muscle_mass_kg",
            "bia_bone_mass_kg",
            "bia_water_pct",
            "bia_metabolic_rate",
            # Recommendations
            "bia_weight_management",
            "bia_food_recommendation",
            "staff_signature",
            "measurement_date",
            "notes",
        ]
        writer.writerow(header)

        for respondent, visit, bia in results:
            row = [
                respondent.respondent_code,
                visit.id,
                visit.visit_date.isoformat() if visit.visit_date else "",
                # Basic info
                bia.age or "",
                self._encode_sex(bia.sex),
                # Basic measurements
                float(bia.weight_kg) if bia.weight_kg else "",
                float(bia.height_cm) if bia.height_cm else "",
                float(bia.bmi) if bia.bmi else "",
                bia.bmi_category or "",
                float(bia.waist_circumference_cm) if bia.waist_circumference_cm else "",
                float(bia.hip_circumference_cm) if bia.hip_circumference_cm else "",
                float(bia.waist_hip_ratio) if bia.waist_hip_ratio else "",
                # Body composition
                float(bia.fat_mass_kg) if bia.fat_mass_kg else "",
                float(bia.body_fat_percentage) if bia.body_fat_percentage else "",
                float(bia.visceral_fat_kg) if bia.visceral_fat_kg else "",
                float(bia.muscle_mass_kg) if bia.muscle_mass_kg else "",
                float(bia.bone_mass_kg) if bia.bone_mass_kg else "",
                float(bia.water_percentage) if bia.water_percentage else "",
                bia.metabolic_rate or "",
                # Recommendations
                bia.weight_management or "",
                bia.food_recommendation or "",
                bia.staff_signature or "",
                bia.measurement_date.isoformat() if bia.measurement_date else "",
                bia.notes or "",
            ]
            writer.writerow(row)

        return output.getvalue()

    def export_satisfaction_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """Export Satisfaction survey data to CSV"""

        query = (
            self.db.query(Respondent, Visit, SatisfactionResponse)
            .join(Visit, Visit.respondent_id == Respondent.id)
            .join(SatisfactionResponse, SatisfactionResponse.visit_id == Visit.id)
        )

        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)

        query = query.filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        results = query.all()

        output = io.StringIO()
        writer = csv.writer(output)

        header = [
            "respondent_code",
            "visit_id",
            "visit_date",
            "sat_q1_clarity",
            "sat_q2_ease_of_use",
            "sat_q3_confidence",
            "sat_q4_presentation",
            "sat_q5_results_display",
            "sat_q6_usefulness",
            "sat_q7_overall_satisfaction",
            "sat_comments",
            "completed_at",
        ]
        writer.writerow(header)

        for respondent, visit, satisfaction in results:
            row = [
                respondent.respondent_code,
                visit.id,
                visit.visit_date.isoformat() if visit.visit_date else "",
                satisfaction.q1_clarity or "",
                satisfaction.q2_ease_of_use or "",
                satisfaction.q3_confidence or "",
                satisfaction.q4_presentation or "",
                satisfaction.q5_results_display or "",
                satisfaction.q6_usefulness or "",
                satisfaction.q7_overall_satisfaction or "",
                satisfaction.comments or "",
                (
                    satisfaction.completed_at.isoformat()
                    if satisfaction.completed_at
                    else ""
                ),
            ]
            writer.writerow(row)

        return output.getvalue()

    def export_combined_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """Export combined dataset with all instruments"""

        query = self.db.query(Respondent, Visit).join(
            Visit, Visit.respondent_id == Respondent.id
        )

        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)

        query = query.filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        results = query.all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Combined header
        header = [
            # Respondent info
            "respondent_code",
            "respondent_status",
            "age",
            "sex",
            "education_level",
            "marital_status",
            "monthly_income",
            "living_arrangement",
            # Visit info
            "visit_id",
            "visit_number",
            "visit_date",
            "visit_type",
            # SANSA
            "has_sansa",
            "sansa_total",
            "sansa_level",
            # MNA
            "has_mna",
            "mna_total",
            "mna_category",
            # BIA
            "has_bia",
            "bia_bmi",
            "bia_bmi_category",
            "bia_body_fat_pct",
            "bia_muscle_mass_kg",
            # Satisfaction
            "has_satisfaction",
            "sat_avg_score",
            "sat_overall",
        ]
        writer.writerow(header)

        for respondent, visit in results:
            # Check for related data
            sansa = (
                self.db.query(SANSAResponse)
                .filter(SANSAResponse.visit_id == visit.id)
                .first()
            )

            mna = (
                self.db.query(MNAResponse)
                .filter(MNAResponse.visit_id == visit.id)
                .first()
            )

            bia = (
                self.db.query(BIARecord).filter(BIARecord.visit_id == visit.id).first()
            )

            satisfaction = (
                self.db.query(SatisfactionResponse)
                .filter(SatisfactionResponse.visit_id == visit.id)
                .first()
            )

            # Calculate satisfaction average
            sat_avg = ""
            sat_overall = ""
            if satisfaction:
                scores = [
                    satisfaction.q1_clarity,
                    satisfaction.q2_ease_of_use,
                    satisfaction.q3_confidence,
                    satisfaction.q4_presentation,
                    satisfaction.q5_results_display,
                    satisfaction.q6_usefulness,
                    satisfaction.q7_overall_satisfaction,
                ]
                valid_scores = [s for s in scores if s is not None]
                if valid_scores:
                    sat_avg = round(sum(valid_scores) / len(valid_scores), 2)
                    sat_overall = satisfaction.q7_overall_satisfaction or ""

            row = [
                # Respondent info
                respondent.respondent_code,
                respondent.status or "",
                respondent.age or "",
                self._encode_sex(respondent.sex),
                respondent.education_level or "",
                respondent.marital_status or "",
                respondent.monthly_income or "",
                respondent.living_arrangement or "",
                # Visit info
                visit.id,
                visit.visit_number,
                visit.visit_date.isoformat() if visit.visit_date else "",
                visit.visit_type or "",
                # SANSA
                1 if sansa else 0,
                float(sansa.total_score) if sansa and sansa.total_score else "",
                self._encode_sansa_level(sansa.result_level) if sansa else "",
                # MNA
                1 if mna else 0,
                float(mna.mna_total) if mna and mna.mna_total else "",
                self._encode_mna_category(mna.result_category) if mna else "",
                # BIA
                1 if bia else 0,
                float(bia.bmi) if bia and bia.bmi else "",
                bia.bmi_category if bia else "",
                (
                    float(bia.body_fat_percentage)
                    if bia and bia.body_fat_percentage
                    else ""
                ),
                float(bia.muscle_mass_kg) if bia and bia.muscle_mass_kg else "",
                # Satisfaction
                1 if satisfaction else 0,
                sat_avg,
                sat_overall,
            ]
            writer.writerow(row)

        return output.getvalue()

    def _encode_sex(self, sex: Optional[str]) -> str:
        """Encode sex for SPSS (1=male, 2=female, 3=other, 9=prefer not to say)"""
        if not sex:
            return ""
        mapping = {"male": "1", "female": "2", "other": "3", "prefer_not_to_say": "9"}
        return mapping.get(sex, "")

    def _encode_sansa_level(self, level: Optional[str]) -> str:
        """Encode SANSA level (1=normal, 2=at-risk, 3=malnourished)"""
        if not level:
            return ""
        mapping = {"normal": "1", "at_risk": "2", "malnourished": "3"}
        return mapping.get(level, level)

    def _encode_mna_category(self, category: Optional[str]) -> str:
        """Encode MNA category"""
        if not category:
            return ""
        mapping = {"normal": "1", "at_risk": "2", "malnourished": "3"}
        return mapping.get(category, category)
