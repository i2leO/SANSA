from pathlib import Path

from openpyxl import Workbook

from app.services.source_provenance_service import (
    REVISED4_SHEETS,
    workbook_manifest,
    workbook_sheet_snapshots,
)


def test_provenance_dimensions_are_derived_from_streamed_cells(tmp_path: Path):
    workbook = Workbook()
    workbook.remove(workbook.active)
    for sheet_name in REVISED4_SHEETS:
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(["record_id", "value"])
        sheet.append([1, 2])
        sheet["B3"] = "=B2*2"
    path = tmp_path / "revised4.xlsx"
    workbook.save(path)

    manifest = workbook_manifest(path)
    snapshots = workbook_sheet_snapshots(path)

    assert all(item["rows"] == 3 for item in manifest.values())
    assert all(item["columns"] == 2 for item in manifest.values())
    assert all(item["row_count"] == 3 for item in snapshots)
    assert all(item["column_count"] == 2 for item in snapshots)
