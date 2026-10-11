"""Attach stable revised4 source IDs and a six-sheet import manifest.

Dry-run is default. Missing source fields stay NULL; no value is invented.
"""
import argparse
from decimal import Decimal

from openpyxl import load_workbook

from app.database import SessionLocal
from app.models import BIARecord, MNAResponse, Respondent, SourceImportBatch, SourceImportSheet, Visit
from app.services.assessment_revision_service import append_assessment_revision
from app.services.mna_definition import MNA_ITEMS
from app.services.source_provenance_service import (
    REVISED4_DATASET,
    REVISED4_SCHEMA_VERSION,
    workbook_manifest,
    workbook_sheet_snapshots,
    workbook_sha256,
)
from scripts.replace_local_with_revised4 import BOOK, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    digest = workbook_sha256(BOOK)
    manifest = workbook_manifest(BOOK)
    workbook = load_workbook(BOOK, data_only=True, read_only=True)
    participant_rows = {
        int(row["record_id"]): row for row in rows(workbook["Participant_Data"])
    }
    staff_rows = {
        int(row["record_id"]): row for row in rows(workbook["BIA_MNA_Staff"])
    }
    db = SessionLocal()
    try:
        respondents = db.query(Respondent).filter(Respondent.respondent_code.like("R4-%")).all()
        mapping = {}
        for respondent in respondents:
            try:
                source_id = int(respondent.respondent_code.removeprefix("R4-"))
            except ValueError as exc:
                raise RuntimeError(f"invalid revised4 respondent code: {respondent.respondent_code}") from exc
            if source_id not in range(1, 201) or source_id in mapping:
                raise RuntimeError(f"invalid or duplicate revised4 source ID: {source_id}")
            mapping[source_id] = respondent
        if set(mapping) != set(range(1, 201)):
            raise RuntimeError("local cohort does not map exactly to revised4 record_id 1..200")
        print({"mode": "apply" if args.apply else "dry-run", "mapped": len(mapping),
               "sha256": digest, "sheets": list(manifest)})
        if not args.apply:
            return
        batch = db.query(SourceImportBatch).filter_by(source_sha256=digest).first()
        if batch is None:
            batch = SourceImportBatch(
                source_dataset=REVISED4_DATASET,
                source_filename=BOOK.name,
                source_sha256=digest,
                schema_version=REVISED4_SCHEMA_VERSION,
                populated_rows=200,
                sheet_manifest=manifest,
            )
            db.add(batch)
            db.flush()
        if db.query(SourceImportSheet).filter_by(import_batch_id=batch.id).count() == 0:
            for snapshot in workbook_sheet_snapshots(BOOK):
                db.add(SourceImportSheet(import_batch_id=batch.id, **snapshot))
        sex_map = {1: "male", 2: "female"}
        education_map = {
            1: "no_education", 2: "primary", 3: "secondary",
            4: "vocational", 5: "bachelor", 6: "graduate",
        }
        marital_map = {1: "single", 2: "married", 3: "widowed", 4: "divorced"}
        income_map = {1: "under_10k", 2: "10k_20k", 3: "20k_30k", 4: "over_30k"}
        living_map = {1: "alone", 2: "with_spouse", 3: "with_friends", 4: "with_family"}
        for source_id, respondent in mapping.items():
            respondent.source_dataset = REVISED4_DATASET
            respondent.source_record_id = source_id
            respondent.source_import_batch_id = batch.id
            # Preserve source semantics exactly; do not derive Other from text.
            source = participant_rows[source_id]
            respondent.age = source["age"]
            respondent.sex = sex_map[source["sex"]]
            respondent.education_level = education_map[source["Education"]]
            respondent.marital_status = marital_map[source["Marital_status"]]
            respondent.monthly_income = income_map[source["Income"]]
            respondent.living_arrangement = living_map[source["Living_with"]]
            respondent.income_sources = [
                name for column, name in (
                    ("Income_oldage", "old_age"), ("Income_Pension", "pension"),
                    ("Income_spouse", "spouse"), ("Income_children", "children"),
                    ("Income_work", "work"),
                ) if source[column] == 1
            ]
            respondent.chronic_diseases = {
                "diseases": [
                    code.lower() for code in ("DM", "HT", "DLP", "CKD", "CA")
                    if source[code] == 1
                ],
                "other": source["Other_text"] if source["Other"] == 1 else "",
                "other_flag": int(source["Other"]),
                "source_other_text": source["Other_text"] or "",
            }
            visit = db.query(Visit).filter_by(respondent_id=respondent.id, visit_number=1).one()
            visit.source_assessment_id = None
            bia = db.query(BIARecord).filter_by(visit_id=visit.id).one()
            bia.source_staff_id = None
            mna = db.query(MNAResponse).filter_by(visit_id=visit.id).one()
            changed = (
                mna.source_dataset != REVISED4_DATASET
                or mna.answer_capture_mode != "score_only"
            )
            mna.source_dataset = REVISED4_DATASET
            mna.answer_capture_mode = "score_only"
            for item in MNA_ITEMS:
                # revised4 contains MNA scores, not A-R raw option codes.
                # Clear operational claims only; prior values remain in revisions.
                if getattr(mna, item["field"]) is not None:
                    changed = True
                setattr(mna, item["field"], None)
            staff = staff_rows[source_id]
            mna_fields = [f"mna_s{i}" for i in range(1, 7)] + [
                "mna_screen_total"
            ] + [f"mna_a{i}" for i in range(1, 13)] + [
                "mna_ass_total", "mna_total"
            ]
            for field in mna_fields:
                source_value = None if staff[field] is None else Decimal(str(staff[field]))
                if getattr(mna, field) != source_value:
                    setattr(mna, field, source_value)
                    changed = True
            total = Decimal(str(staff["mna_total"]))
            operational_category = "1" if total >= 24 else "2" if total >= 17 else "3"
            if mna.result_category != operational_category:
                mna.result_category = operational_category
                changed = True
            if changed:
                db.flush()
                append_assessment_revision(
                    db, "MNA", mna, action_type="reconcile",
                    change_reason="Reconcile current values to revised4; prior value retained in revision history",
                )
        db.commit()
        print({"batch_id": batch.id, "updated_respondents": len(mapping)})
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
