"""Restore one local participant's current MNA values from revised4, preserving history.

Dry-run is the default. This is intentionally targeted and never recreates the cohort.
"""
import argparse
from decimal import Decimal

from openpyxl import load_workbook

from app.database import SessionLocal
from app.models import MNAResponse, Respondent, Visit
from app.services.assessment_revision_service import append_assessment_revision, ensure_assessment_baseline
from app.services.mna_definition import MNA_ITEMS
from scripts.replace_local_with_revised4 import BOOK, rows


def dec(value):
    return None if value is None else Decimal(str(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--respondent-code", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        record_id = int(args.respondent_code.removeprefix("R4-"))
    except ValueError as exc:
        raise RuntimeError("respondent code must use R4-####") from exc
    workbook = load_workbook(BOOK, data_only=True, read_only=True)
    source = next(row for row in rows(workbook["BIA_MNA_Staff"]) if int(row["record_id"]) == record_id)
    print({"mode": "apply" if args.apply else "dry-run", "respondent_code": args.respondent_code,
           "source_record_id": record_id, "source_total": source["mna_total"]})
    if not args.apply:
        return

    db = SessionLocal()
    try:
        respondent = db.query(Respondent).filter_by(respondent_code=args.respondent_code).one()
        visit = db.query(Visit).filter_by(respondent_id=respondent.id, visit_number=1).one()
        mna = db.query(MNAResponse).filter_by(visit_id=visit.id).one()
        ensure_assessment_baseline(db, "MNA", mna)
        for item in MNA_ITEMS:
            setattr(mna, item["field"], None)
        for field in [f"mna_s{i}" for i in range(1, 7)] + [f"mna_a{i}" for i in range(1, 13)]:
            setattr(mna, field, dec(source[field]))
        mna.mna_screen_total = dec(source["mna_screen_total"])
        mna.mna_ass_total = dec(source["mna_ass_total"])
        mna.mna_total = dec(source["mna_total"])
        mna.result_category = source["mna_total_cat"]
        mna.mac_cm = dec(source["MAC"])
        mna.cc_cm = dec(source["CC"])
        db.flush()
        append_assessment_revision(
            db, "MNA", mna, action_type="source_restore",
            change_reason="restore current values from approved revised4 source",
        )
        db.commit()
        print({"restored_visit_id": visit.id, "mna_id": mna.id, "mna_total": str(mna.mna_total)})
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
