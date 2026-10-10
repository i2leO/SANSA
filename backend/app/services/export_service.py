from typing import Optional, List
from datetime import datetime, date
import csv
import io
import json
from decimal import Decimal
from openpyxl import Workbook
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    Respondent,
    Visit,
    SANSAResponse,
    SatisfactionResponse,
    MNAResponse,
    BIARecord,
    AssessmentRevision,
)
from app.services.sansa_domain_service import calculate_sansa_domain_scores
from app.services.sansa_result_service import revised_visit_result
from app.services.bia_reference_service import derive_nutrition_reference


class ExportService:
    """Service for exporting data to SPSS-compatible CSV format"""

    def __init__(self, db: Session):
        self.db = db

    def export_revised4_xlsx(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> bytes:
        """Build the four-sheet workbook defined by the revised4 template."""
        datasets = [
            ("Participant_Data", self.export_sansa_csv(start_date, end_date)),
            ("Prediction", self.export_prediction_csv(start_date, end_date)),
            ("BIA_MNA_Staff", self.export_bia_mna_csv(start_date, end_date)),
            ("Satisfaction", self.export_satisfaction_csv(start_date, end_date)),
        ]
        workbook = Workbook()
        workbook.remove(workbook.active)
        for sheet_name, content in datasets:
            sheet = workbook.create_sheet(sheet_name)
            for row in csv.reader(io.StringIO(content)):
                sheet.append(row)
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    def export_assessment_history_csv(self) -> str:
        """Export immutable MNA/BIA revisions in long form without confusing zero and missing."""
        rows = (
            self.db.query(AssessmentRevision, Respondent.respondent_code, Visit.visit_number)
            .join(Respondent, Respondent.id == AssessmentRevision.respondent_id)
            .join(Visit, Visit.id == AssessmentRevision.visit_id)
            .order_by(
                Respondent.respondent_code,
                Visit.visit_number,
                AssessmentRevision.instrument,
                AssessmentRevision.revision_number,
            )
            .all()
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "respondent_code", "assessment_id", "assessment_round", "instrument",
            "record_id", "revision_number", "action_type", "is_current",
            "recorded_at", "changed_by", "change_reason", "field", "value_json",
        ])
        for revision, respondent_code, visit_number in rows:
            for field, value in sorted((revision.snapshot or {}).items()):
                writer.writerow([
                    respondent_code,
                    revision.visit_id,
                    visit_number,
                    revision.instrument,
                    revision.record_id,
                    revision.revision_number,
                    revision.action_type,
                    1 if revision.is_current else 0,
                    revision.recorded_at.isoformat() if revision.recorded_at else "",
                    revision.changed_by if revision.changed_by is not None else "",
                    revision.change_reason or "",
                    field,
                    json.dumps(value, ensure_ascii=False),
                ])
        return output.getvalue()

    def export_sansa_csv(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        facility_id: Optional[int] = None,
    ) -> str:
        """Export SANSA using the revised4 research field contract."""
        query = (
            self.db.query(Respondent, Visit, SANSAResponse)
            .join(Visit, Visit.respondent_id == Respondent.id)
            .join(SANSAResponse, SANSAResponse.visit_id == Visit.id)
        )
        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)
        if facility_id:
            query = query.filter(Visit.facility_id == facility_id)
        query = query.filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        results = query.all()

        output = io.StringIO()
        writer = csv.writer(output)
        header = [
            "record_id",
            "assessment_id",
            "assessment_date",
            "Role",
            "age",
            "age_group01",
            "sex",
            "Education",
            "Marital_status",
            "Income",
            "Income_oldage",
            "Income_Pension",
            "Income_spouse",
            "Income_children",
            "Income_work",
            "DM", "HT", "DLP", "CKD", "CA", "Other", "Other_text",
            "Living_with",
            "scr_bw", "scr_app", "scr_act", "scr_dx",
            "ass_meal", "ass_intake", "ass_type",
            "ass_rice_starch", "ass_meat_egg", "ass_milk", "ass_fruit",
            "ass_veget", "ass_water", "ass_sweetdrink", "ass_cook", "ass_oil",
            "D1_total", "D2_total", "D3_total",
            "wc_input", "wc_unit", "wc_cm",
        ]
        writer.writerow(header)

        for respondent, visit, sansa_response in results:
            domains = calculate_sansa_domain_scores(sansa_response, allow_missing=True)
            prediction = self._get_sansa_prediction(visit.id, sansa_response)
            income = respondent.income_sources
            diseases = respondent.chronic_diseases
            waist = prediction["waist_cm"] if prediction else self._unique_waist(visit.id)
            row = [
                self._record_id(respondent),
                self._assessment_id(respondent, visit),
                visit.visit_date.isoformat() if visit.visit_date else "",
                self._encode_respondent_role(respondent.status),
                respondent.age if respondent.age is not None else "",
                (0 if respondent.age < 70 else 1) if respondent.age is not None else "",
                self._encode_sex(respondent.sex),
                self._encode_education(respondent.education_level),
                self._encode_marital_status(respondent.marital_status),
                self._encode_income(respondent.monthly_income),
                self._list_flag(income, "เบี้ยยังชีพ", "oldage", "old_age"),
                self._list_flag(income, "บำนาญ", "pension"),
                self._list_flag(income, "คู่สมรส", "spouse"),
                self._list_flag(income, "บุตร", "ลูกหลาน", "children"),
                self._list_flag(income, "ทำงาน", "ค่าจ้าง", "work"),
                self._disease_flag(diseases, "dm", "diabetes", "เบาหวาน"),
                self._disease_flag(diseases, "ht", "hypertension", "ความดัน"),
                self._disease_flag(diseases, "dlp", "ไขมัน"),
                self._disease_flag(diseases, "ckd", "ไต"),
                self._disease_flag(diseases, "ca", "cancer", "มะเร็ง"),
                self._other_disease_flag(diseases),
                self._other_disease_text(diseases),
                self._encode_living_arrangement(respondent.living_arrangement),
                *[self._decimal_or_blank(getattr(sansa_response, f"q{i}_score")) for i in range(1, 17)],
                self._decimal_or_blank(domains["d1_total"]),
                self._decimal_or_blank(domains["d2_total"]),
                self._decimal_or_blank(domains["d3_total"]),
                self._decimal_or_blank(waist),
                "cm" if waist is not None else "",
                self._decimal_or_blank(waist),
            ]
            writer.writerow(row)

        return output.getvalue()

    def export_prediction_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """Export exactly the revised4 Prediction sheet fields."""
        query = (
            self.db.query(Respondent, Visit, SANSAResponse)
            .join(Visit, Visit.respondent_id == Respondent.id)
            .join(SANSAResponse, SANSAResponse.visit_id == Visit.id)
            .filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        )
        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "record_id", "assessment_id", "assessment_date", "age_group01",
            "D2_total", "D3_total", "wc_cm", "L_Over", "L_Normal",
            "EXP_over", "EXP_normal", "Denom", "P_Under", "P_Over",
            "P_Normal", "predicted_group",
        ])
        for respondent, visit, response in query.all():
            prediction = self._get_sansa_prediction(visit.id, response)
            exp_over, exp_normal, denom = self._prediction_intermediates(prediction)
            writer.writerow([
                self._record_id(respondent),
                self._assessment_id(respondent, visit),
                visit.visit_date.isoformat() if visit.visit_date else "",
                prediction["age_group01"] if prediction else "",
                self._decimal_or_blank(prediction["d2_total"]) if prediction else "",
                self._decimal_or_blank(prediction["d3_total"]) if prediction else "",
                self._decimal_or_blank(prediction["waist_cm"]) if prediction else "",
                self._decimal_or_blank(prediction["l_over"]) if prediction else "",
                self._decimal_or_blank(prediction["l_normal"]) if prediction else "",
                exp_over, exp_normal, denom,
                self._decimal_or_blank(prediction["p_under"]) if prediction else "",
                self._decimal_or_blank(prediction["p_over"]) if prediction else "",
                self._decimal_or_blank(prediction["p_normal"]) if prediction else "",
                self._title_prediction_group(prediction["predicted_group"]) if prediction else "",
            ])
        return output.getvalue()

    def export_mna_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        return self.export_bia_mna_csv(start_date, end_date)

    def export_bia_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        return self.export_bia_mna_csv(start_date, end_date)

    def export_bia_mna_csv(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> str:
        """Export exactly the revised4 BIA_MNA_Staff sheet fields."""
        query = self.db.query(Respondent, Visit).join(
            Visit, Visit.respondent_id == Respondent.id
        ).filter(Respondent.is_deleted == False, Visit.is_deleted == False)
        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "record_id", "assessment_id", "assessment_date", "staff_id",
            "height_cm", "weight_kg", "bmi", "fat_mass_kg", "pbf",
            "vfat_level", "muscle_mass_kg", "bone_mass_kg", "tbw", "bmr_kcal",
            "mna_s1", "mna_s2", "mna_s3", "mna_s4", "mna_s5", "mna_s6",
            "mna_screen_total", "mna_screen_cat",
            "mna_a1", "mna_a2", "mna_a3", "mna_a4", "mna_a5", "mna_a6",
            "mna_a7", "mna_a8", "mna_a9", "mna_a10", "mna_a11", "mna_a12",
            "mna_ass_total", "mna_total", "mna_total_cat", "MAC", "CC",
            "bmi_class_glim", "pbf_class", "nutri_ref_class",
        ])
        for respondent, visit in query.all():
            bia_records = self.db.query(BIARecord).filter(BIARecord.visit_id == visit.id).limit(2).all()
            bia = bia_records[0] if len(bia_records) == 1 else None
            mna = self.db.query(MNAResponse).filter(MNAResponse.visit_id == visit.id).first()
            if not bia and not mna:
                continue
            reference = None
            if bia and respondent.age is not None and bia.bmi is not None and bia.body_fat_percentage is not None:
                try:
                    reference = derive_nutrition_reference(
                        respondent.age, respondent.sex, bia.bmi, bia.body_fat_percentage
                    )
                except ValueError:
                    pass
            screen_total = mna.mna_screen_total if mna else None
            total = mna.mna_total if mna else None
            writer.writerow([
                self._record_id(respondent), self._assessment_id(respondent, visit),
                visit.visit_date.isoformat() if visit.visit_date else "",
                self._staff_id(respondent, bia, mna),
                self._decimal_or_blank(bia.height_cm) if bia else "",
                self._decimal_or_blank(bia.weight_kg) if bia else "",
                self._decimal_or_blank(bia.bmi) if bia else "",
                self._decimal_or_blank(bia.fat_mass_kg) if bia else "",
                self._decimal_or_blank(bia.body_fat_percentage) if bia else "",
                self._decimal_or_blank(bia.visceral_fat_level) if bia else "",
                self._decimal_or_blank(bia.muscle_mass_kg) if bia else "",
                self._decimal_or_blank(bia.bone_mass_kg) if bia else "",
                self._decimal_or_blank(bia.water_percentage) if bia else "",
                bia.metabolic_rate if bia and bia.metabolic_rate is not None else "",
                *[self._decimal_or_blank(getattr(mna, f"mna_s{i}")) if mna else "" for i in range(1, 7)],
                self._decimal_or_blank(screen_total), self._mna_category_code(screen_total, screening=True),
                *[self._decimal_or_blank(getattr(mna, f"mna_a{i}")) if mna else "" for i in range(1, 13)],
                self._decimal_or_blank(mna.mna_ass_total) if mna else "",
                self._decimal_or_blank(total), self._mna_category_code(total),
                self._decimal_or_blank(mna.mac_cm if mna and mna.mac_cm is not None else bia.mac_cm if bia else None),
                self._decimal_or_blank(mna.cc_cm if mna and mna.cc_cm is not None else bia.cc_cm if bia else None),
                self._translate_reference(reference["bmi_class"]) if reference else "",
                self._translate_reference(reference["pbf_class"]) if reference else "",
                self._translate_reference(reference["nutrition_reference"]) if reference else "",
            ])
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
            "record_id", "assessment_id", "assessment_date", "respondent_role",
            "sat_clarity", "sat_easy", "sat_confident", "sat_design",
            "sat_result", "sat_benefit", "sat_overall", "sat_comment",
            "sat_total", "sat_mean", "sat_level",
        ]
        writer.writerow(header)

        for respondent, visit, satisfaction in results:
            scores = [
                satisfaction.q1_clarity, satisfaction.q2_ease_of_use,
                satisfaction.q3_confidence, satisfaction.q4_presentation,
                satisfaction.q5_results_display, satisfaction.q6_usefulness,
                satisfaction.q7_overall_satisfaction,
            ]
            valid = [score for score in scores if score is not None]
            total = sum(valid) if valid else None
            mean = total / len(valid) if valid else None
            row = [
                self._record_id(respondent),
                self._assessment_id(respondent, visit),
                visit.visit_date.isoformat() if visit.visit_date else "",
                self._encode_respondent_role(respondent.status),
                *[score if score is not None else "" for score in scores],
                satisfaction.comments or "",
                total if total is not None else "",
                round(mean, 2) if mean is not None else "",
                self._satisfaction_level(mean),
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
            "sansa_total_024",
            "sansa_scoring_status",
            "sansa_prediction_group",
            "sansa_level",
            "sansa_p_under",
            "sansa_p_normal",
            "sansa_p_over",
            "sansa_prediction_model_version",
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
            sansa_result = revised_visit_result(self.db, sansa, persist=False) if sansa else None
            prediction = sansa_result["prediction"] if sansa_result else None

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
                respondent.age if respondent.age is not None else "",
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
                self._decimal_or_blank(sansa.total_score) if sansa_result and sansa_result["verified_024"] else "",
                "verified_024" if sansa_result and sansa_result["verified_024"] else (
                    "incomplete_or_unverified" if sansa else ""
                ),
                prediction["predicted_group"] if prediction else "",
                self._translate_prediction_group(prediction["predicted_group"]) if prediction else "",
                self._decimal_or_blank(prediction["p_under"]) if prediction else "",
                self._decimal_or_blank(prediction["p_normal"]) if prediction else "",
                self._decimal_or_blank(prediction["p_over"]) if prediction else "",
                prediction["model_version"] if prediction else "",
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

    def _get_sansa_prediction(self, visit_id: int, response: SANSAResponse) -> Optional[dict]:
        """Derive a read-only prediction only after the 0/2/4 integrity gate."""
        fields = (
            "age_group01", "d2_total", "d3_total", "waist_cm",
            "l_over", "l_normal", "p_under", "p_normal", "p_over",
            "predicted_group", "model_version",
        )
        prediction = revised_visit_result(self.db, response, persist=False)["prediction"]
        if not prediction:
            return None
        return {field: prediction[field] for field in fields}

    @staticmethod
    def _translate_prediction_group(group: Optional[str]) -> str:
        """Thai research labels confirmed for the three prediction outcomes."""
        if not group:
            return ""
        mapping = {
            "UNDER": "เสี่ยงขาด/ขาด",
            "NORMAL": "ปกติ",
            "OVER": "เสี่ยงเกิน/เกิน",
        }
        return mapping.get(group, group)

    @staticmethod
    def _decimal_or_blank(value) -> object:
        return float(value) if value is not None else ""

    @staticmethod
    def _record_id(respondent) -> object:
        """Use the stable research-source ID; DB primary keys are never export IDs."""
        return respondent.source_record_id if respondent.source_record_id is not None else respondent.id

    @staticmethod
    def _assessment_id(respondent, visit) -> object:
        """Preserve a missing source assessment ID instead of inventing one on import."""
        if respondent.source_dataset:
            return visit.source_assessment_id or ""
        return visit.source_assessment_id or visit.id

    @staticmethod
    def _staff_id(respondent, bia, mna) -> object:
        """Preserve source staff identity separately from later system actors."""
        if respondent.source_dataset:
            return (bia.source_staff_id if bia else None) or ""
        return (bia.measured_by if bia else None) or (mna.created_by if mna else None) or ""

    @staticmethod
    def _title_prediction_group(group: Optional[str]) -> str:
        return group.title() if group else ""

    @staticmethod
    def _prediction_intermediates(prediction: Optional[dict]):
        if not prediction:
            return "", "", ""
        p_under = float(prediction["p_under"])
        if p_under <= 0:
            return "", "", ""
        exp_over = float(prediction["p_over"]) / p_under
        exp_normal = float(prediction["p_normal"]) / p_under
        return exp_over, exp_normal, 1.0 / p_under

    def _unique_waist(self, visit_id: int):
        records = self.db.query(BIARecord).filter(BIARecord.visit_id == visit_id).limit(2).all()
        if len(records) != 1:
            return None
        return records[0].waist_circumference_cm

    @staticmethod
    def _encode_respondent_role(status) -> object:
        value = getattr(status, "value", status)
        return {"elderly": "1", "caregiver": "2"}.get(value, "")

    @staticmethod
    def _encode_category(value, mapping: dict) -> object:
        if value is None or value == "":
            return ""
        normalized = str(getattr(value, "value", value)).strip().lower()
        if normalized in mapping:
            return mapping[normalized]
        if normalized.isdigit() and int(normalized) in mapping.values():
            return int(normalized)
        return ""

    @classmethod
    def _encode_education(cls, value) -> object:
        return cls._encode_category(value, {
            "no_education": 1, "ไม่ได้เรียน": 1, "ไม่ได้เรียนหนังสือ": 1,
            "primary": 2, "ประถมศึกษา": 2,
            "secondary": 3, "มัธยมศึกษา": 3,
            "vocational": 4, "ปวช.-ปวส.": 4, "ปวช./ปวส.": 4,
            "bachelor": 5, "ปริญญาตรี": 5,
            "graduate": 6, "สูงกว่าปริญญาตรี": 6,
        })

    @classmethod
    def _encode_marital_status(cls, value) -> object:
        return cls._encode_category(value, {
            "single": 1, "โสด": 1,
            "married": 2, "สมรส": 2,
            "widowed": 3, "หม้าย": 3,
            "divorced": 4, "หย่าร้าง": 4,
        })

    @classmethod
    def _encode_income(cls, value) -> object:
        return cls._encode_category(value, {
            "under_10k": 1, "under_5k": 1, "5k_10k": 1,
            "ต่ำกว่า 5000": 1, "5001-10000": 1,
            "น้อยกว่า 10,000 บาท": 1,
            "10k_20k": 2,
            "10,000-20,000 บาท": 2, "10001-20000": 2,
            "20k_30k": 3, "20,001-30,000 บาท": 3,
            "over_30k": 4, "มากกว่า 30,000 บาท": 4, "มากกว่า 40000": 4,
        })

    @classmethod
    def _encode_living_arrangement(cls, value) -> object:
        return cls._encode_category(value, {
            "alone": 1, "อยู่คนเดียว": 1,
            "with_spouse": 2, "อยู่กับคู่สมรส": 2,
            "with_friends": 3, "อยู่กับเพื่อน": 3,
            "with_family": 4, "with_children": 4, "with_relatives": 4,
            "อยู่กับครอบครัว": 4, "อยู่กับลูก": 4, "อยู่กับลูกหลาน": 4,
            "อยู่กับญาติ": 4,
        })

    @staticmethod
    def _list_flag(values, *aliases: str):
        if values is None:
            return ""
        if not isinstance(values, (list, tuple, set)):
            return 0
        text = "|".join(str(value).lower() for value in values)
        return int(any(alias.lower() in text for alias in aliases))

    @staticmethod
    def _disease_flag(data, *aliases: str):
        if data is None:
            return ""
        if not isinstance(data, dict):
            return 0
        for alias in aliases:
            if data.get(alias) is True or data.get(alias) == 1:
                return 1
        diseases = data.get("diseases")
        if isinstance(diseases, (list, tuple, set)):
            text = "|".join(str(value).lower() for value in diseases)
            return int(any(alias.lower() in text for alias in aliases))
        return 0

    @classmethod
    def _other_disease_text(cls, data) -> str:
        if not isinstance(data, dict):
            return ""
        value = data.get("source_other_text")
        if value is None:
            value = data.get("other") or data.get("other_text") or ""
        return value if isinstance(value, str) else ""

    @classmethod
    def _other_disease_flag(cls, data):
        if data is None:
            return ""
        if isinstance(data, dict) and data.get("other_flag") in (0, 1):
            return data["other_flag"]
        return int(bool(cls._other_disease_text(data)))

    @staticmethod
    def _mna_category_code(value, screening=False) -> object:
        if value is None:
            return ""
        score = float(value)
        if screening:
            return 1 if score >= 12 else 2 if score >= 8 else 3
        return 1 if score >= 24 else 2 if score >= 17 else 3

    @staticmethod
    def _translate_reference(group: Optional[str]) -> str:
        return {
            "UNDER": "ขาด/เสี่ยงขาด",
            "NORMAL": "ปกติ",
            "OVER": "เสี่ยงเกิน/เกิน",
        }.get(group, group or "")

    @staticmethod
    def _satisfaction_level(mean) -> str:
        if mean is None:
            return ""
        if mean >= 4.5:
            return "มากที่สุด"
        if mean >= 3.5:
            return "มาก"
        if mean >= 2.5:
            return "ปานกลาง"
        if mean >= 1.5:
            return "น้อย"
        return "น้อยที่สุด"

    def _encode_mna_category(self, category: Optional[str]) -> str:
        """Encode MNA category"""
        if not category:
            return ""
        mapping = {"normal": "1", "at_risk": "2", "malnourished": "3"}
        return mapping.get(category, category)
