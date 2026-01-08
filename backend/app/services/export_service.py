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
            "respondent_code",
            "respondent_id",
            "visit_id",
            "visit_number",
            "visit_date",
            "age",
            "sex",
            "education_level",
            "income_range",
            "sansa_q1",
            "sansa_q2",
            "sansa_q3",
            "sansa_q4",
            "sansa_d01",
            "sansa_d02",
            "sansa_d03",
            "sansa_d04",
            "sansa_d05",
            "sansa_d06",
            "sansa_d07",
            "sansa_d08",
            "sansa_d09",
            "sansa_d10",
            "sansa_d11",
            "sansa_d12",
            "sansa_screening_total",
            "sansa_diet_total",
            "sansa_total",
            "sansa_level",
            "sansa_version",
            "completed_at",
            "created_at",
        ]
        writer.writerow(header)

        # Write data rows
        for respondent, visit, sansa_response in results:
            # Use columns from SANSAResponse directly
            row = [
                respondent.respondent_code,
                respondent.id,
                visit.id,
                visit.visit_number,
                visit.visit_date.isoformat() if visit.visit_date else "",
                respondent.age,
                self._encode_sex(respondent.sex),
                respondent.education_level or "",
                respondent.income_range or "",
                # Screening items (q1-q4 scores)
                float(sansa_response.q1_score) if sansa_response.q1_score else "",
                float(sansa_response.q2_score) if sansa_response.q2_score else "",
                float(sansa_response.q3_score) if sansa_response.q3_score else "",
                float(sansa_response.q4_score) if sansa_response.q4_score else "",
                # Dietary items (q5-q16 scores)
                float(sansa_response.q5_score) if sansa_response.q5_score else "",
                float(sansa_response.q6_score) if sansa_response.q6_score else "",
                float(sansa_response.q7_score) if sansa_response.q7_score else "",
                float(sansa_response.q8_score) if sansa_response.q8_score else "",
                float(sansa_response.q9_score) if sansa_response.q9_score else "",
                float(sansa_response.q10_score) if sansa_response.q10_score else "",
                float(sansa_response.q11_score) if sansa_response.q11_score else "",
                float(sansa_response.q12_score) if sansa_response.q12_score else "",
                float(sansa_response.q13_score) if sansa_response.q13_score else "",
                float(sansa_response.q14_score) if sansa_response.q14_score else "",
                float(sansa_response.q15_score) if sansa_response.q15_score else "",
                float(sansa_response.q16_score) if sansa_response.q16_score else "",
                # Totals
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
                (
                    sansa_response.created_at.isoformat()
                    if sansa_response.created_at
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

        # Header with MNA items (assuming 18 items)
        header = (
            ["respondent_code", "visit_id", "visit_date"]
            + [f"mna_q{i:02d}" for i in range(1, 19)]
            + ["mna_total", "mna_category", "entry_mode", "completed_at"]
        )
        writer.writerow(header)

        for respondent, visit, mna_response in results:
            # Use columns from MNAResponse directly (q1-q18 scores)
            row = (
                [
                    respondent.respondent_code,
                    visit.id,
                    visit.visit_date.isoformat() if visit.visit_date else "",
                ]
                + [
                    (
                        float(getattr(mna_response, f"q{i}_score"))
                        if getattr(mna_response, f"q{i}_score")
                        else ""
                    )
                    for i in range(1, 19)
                ]
                + [
                    float(mna_response.total_score) if mna_response.total_score else "",
                    self._encode_mna_category(mna_response.result_category),
                    mna_response.entry_mode or "",
                    (
                        mna_response.completed_at.isoformat()
                        if mna_response.completed_at
                        else ""
                    ),
                ]
            )
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
            "bia_weight",
            "bia_height",
            "bia_bmi",
            "bia_body_fat_pct",
            "bia_muscle_kg",
            "bia_bone_kg",
            "bia_water_pct",
            "bia_visceral_fat",
            "bia_waist_cm",
            "bia_hip_cm",
            "bia_waist_hip_ratio",
            "measured_at",
        ]
        writer.writerow(header)

        for respondent, visit, bia in results:
            row = [
                respondent.respondent_code,
                visit.id,
                visit.visit_date.isoformat() if visit.visit_date else "",
                float(bia.weight_kg) if bia.weight_kg else "",
                float(bia.height_cm) if bia.height_cm else "",
                float(bia.bmi) if bia.bmi else "",
                float(bia.body_fat_percentage) if bia.body_fat_percentage else "",
                float(bia.muscle_mass_kg) if bia.muscle_mass_kg else "",
                float(bia.bone_mass_kg) if bia.bone_mass_kg else "",
                float(bia.water_percentage) if bia.water_percentage else "",
                bia.visceral_fat_level or "",
                float(bia.waist_circumference_cm) if bia.waist_circumference_cm else "",
                float(bia.hip_circumference_cm) if bia.hip_circumference_cm else "",
                float(bia.waist_hip_ratio) if bia.waist_hip_ratio else "",
                bia.created_at.isoformat() if bia.created_at else "",
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
            "respondent_code",
            "visit_id",
            "visit_number",
            "visit_date",
            "visit_type",
            "age",
            "sex",
            "education_level",
            "has_sansa",
            "sansa_total",
            "sansa_level",
            "has_mna",
            "mna_total",
            "mna_category",
            "has_bia",
            "bia_bmi",
            "bia_waist_cm",
            "has_satisfaction",
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

            row = [
                respondent.respondent_code,
                visit.id,
                visit.visit_number,
                visit.visit_date.isoformat() if visit.visit_date else "",
                visit.visit_type or "",
                respondent.age or "",
                self._encode_sex(respondent.sex),
                respondent.education_level or "",
                1 if sansa else 0,
                float(sansa.total_score) if sansa and sansa.total_score else "",
                self._encode_sansa_level(sansa.result_level) if sansa else "",
                1 if mna else 0,
                float(mna.total_score) if mna and mna.total_score else "",
                self._encode_mna_category(mna.result_category) if mna else "",
                1 if bia else 0,
                float(bia.bmi) if bia and bia.bmi else "",
                (
                    float(bia.waist_circumference_cm)
                    if bia and bia.waist_circumference_cm
                    else ""
                ),
                1 if satisfaction else 0,
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
