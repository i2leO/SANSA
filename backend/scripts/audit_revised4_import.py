"""Fail-fast audit of all six revised4 sheets against normalized local data."""
import csv
import io
import math
from collections import Counter

from openpyxl import load_workbook

from app.database import SessionLocal
from app.models import (
    BIARecord, MNAResponse, Respondent, SatisfactionResponse, SANSAResponse,
    SANSAPredictionResult, SourceImportBatch, SourceImportSheet, Visit,
)
from app.services.export_service import ExportService
from app.services.source_provenance_service import (
    REVISED4_SHEETS, workbook_sha256,
)
from scripts.replace_local_with_revised4 import BOOK


def workbook_rows(workbook, sheet_name):
    sheet = workbook[sheet_name]
    data = list(sheet.iter_rows(min_row=1, max_row=201, values_only=True))
    headers = list(data[0])
    return headers, [dict(zip(headers, row)) for row in data[1:]]


def csv_rows(content):
    reader = csv.DictReader(io.StringIO(content))
    return reader.fieldnames, list(reader)


def blank(value):
    return value is None or value == ""


def equal_value(source, exported, field=None):
    if blank(source) and blank(exported):
        return True
    try:
        if field == "bmi":
            return math.isclose(round(float(source), 2), float(exported), abs_tol=1e-9)
        return math.isclose(float(source), float(exported), rel_tol=1e-9, abs_tol=1e-9)
    except (TypeError, ValueError):
        return str(source).strip().lower() == str(exported).strip().lower()


def compare_sheet(name, source_headers, source_rows, export_headers, export_rows, excluded=()):
    if source_headers != export_headers:
        raise RuntimeError(f"{name}: export headers differ from workbook")
    source_by_id = {int(row["record_id"]): row for row in source_rows}
    export_by_id = {int(row["record_id"]): row for row in export_rows}
    if set(source_by_id) != set(range(1, 201)) or set(export_by_id) != set(range(1, 201)):
        raise RuntimeError(f"{name}: record_id coverage must be exactly 1..200")
    mismatches = []
    for record_id in range(1, 201):
        for field in source_headers:
            if field in excluded:
                continue
            # The source contains one documented out-of-domain value (4 in a
            # field defined as a 0/1 flag). The exact value remains in the
            # immutable sheet snapshot; operational normalization cannot turn
            # it into a boolean without inventing meaning.
            if name == "Participant_Data" and record_id == 52 and field == "Income_work":
                if source_by_id[record_id][field] != 4:
                    mismatches.append((record_id, field))
                continue
            # revised4 row 138 stores category 1 although its total 23.5 maps
            # to category 2 under the workbook's own Data_Dictionary rule.
            # Keep the source cell in the immutable snapshot and keep the
            # operational value derived from the approved threshold.
            if name == "BIA_MNA_Staff" and record_id == 138 and field == "mna_total_cat":
                if source_by_id[record_id][field] != 1 or export_by_id[record_id][field] != "2":
                    mismatches.append((record_id, field))
                continue
            if not equal_value(
                source_by_id[record_id][field], export_by_id[record_id][field], field
            ):
                mismatches.append((record_id, field))
    return len(source_headers) - len(excluded), mismatches


def main():
    workbook = load_workbook(BOOK, data_only=True, read_only=True)
    if tuple(workbook.sheetnames) != REVISED4_SHEETS:
        raise RuntimeError(f"unexpected sheets: {workbook.sheetnames}")
    source = {name: workbook_rows(workbook, name) for name in REVISED4_SHEETS[:4]}
    for name, (_, rows) in source.items():
        ids = [row["record_id"] for row in rows]
        if ids != list(range(1, 201)):
            raise RuntimeError(f"{name}: populated rows are not record_id 1..200")

    db = SessionLocal()
    try:
        counts = {
            "respondents": db.query(Respondent).filter_by(is_deleted=False).count(),
            "visits": db.query(Visit).filter_by(is_deleted=False).count(),
            "sansa": db.query(SANSAResponse).count(),
            "prediction": db.query(SANSAPredictionResult).count(),
            "bia": db.query(BIARecord).count(),
            "mna": db.query(MNAResponse).count(),
            "satisfaction": db.query(SatisfactionResponse).count(),
        }
        if any(value != 200 for value in counts.values()):
            raise RuntimeError(f"normalized table counts differ from 200: {counts}")
        ids = [value for (value,) in db.query(Respondent.source_record_id).order_by(Respondent.source_record_id)]
        if ids != list(range(1, 201)):
            raise RuntimeError("respondent source_record_id coverage must be exactly 1..200")
        batch = db.query(SourceImportBatch).filter_by(source_sha256=workbook_sha256(BOOK)).one()
        snapshots = db.query(SourceImportSheet).filter_by(import_batch_id=batch.id).all()
        if {row.sheet_name for row in snapshots} != set(REVISED4_SHEETS):
            raise RuntimeError("six-sheet source snapshot is incomplete")

        exporter = ExportService(db)
        exported = {
            "Participant_Data": csv_rows(exporter.export_sansa_csv()),
            "Prediction": csv_rows(exporter.export_prediction_csv()),
            "BIA_MNA_Staff": csv_rows(exporter.export_bia_mna_csv()),
            "Satisfaction": csv_rows(exporter.export_satisfaction_csv()),
        }
        compared = {}
        mismatches = {}
        for name in ("Participant_Data", "Prediction", "BIA_MNA_Staff"):
            compared[name], mismatches[name] = compare_sheet(
                name, *source[name], *exported[name]
            )
        compared["Satisfaction"], mismatches["Satisfaction"] = compare_sheet(
            "Satisfaction", *source["Satisfaction"], *exported["Satisfaction"],
            excluded=("respondent_role", "sat_mean", "sat_level"),
        )
        mismatches = {name: values for name, values in mismatches.items() if values}
        if mismatches:
            summary = {
                name: {
                    "count": len(values),
                    "by_field": dict(Counter(field for _, field in values)),
                    "first": values[:10],
                }
                for name, values in mismatches.items()
            }
            raise RuntimeError(f"workbook/export mismatches: {summary}")
        missing = {}
        for name, (headers, rows) in source.items():
            missing[name] = {
                field: sum(blank(row[field]) for row in rows)
                for field in headers if any(blank(row[field]) for row in rows)
            }
        print({
            "status": "PASS",
            "workbook_sha256": batch.source_sha256,
            "sheets_snapshotted": len(snapshots),
            "normalized_counts": counts,
            "compared_columns": compared,
            "source_missing_counts": missing,
            "source_validation_issues": [
                {"sheet": "Participant_Data", "record_id": 52,
                 "field": "Income_work", "value": 4, "expected_domain": [0, 1]},
                {"sheet": "BIA_MNA_Staff", "record_id": 138,
                 "field": "mna_total_cat", "value": 1,
                 "expected_from_total_23_5": 2},
            ],
        })
    finally:
        db.close()


if __name__ == "__main__":
    main()
