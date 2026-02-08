#!/usr/bin/env python3
"""
Preview Excel Data Script
แสดงข้อมูลจริงจาก Excel ก่อน import เพื่อยืนยันความถูกต้อง
"""

import pandas as pd
import sys
from pathlib import Path

# Excel file path
EXCEL_FILE = "/Users/dev/SANSA/src/ปรับแก้ Test Data THESIS PHASE2 03022026.xlsx"

SHEET_NAMES = {
    "demographic": "Demographic",
    "self_screen": "Self Screen Assess (3)",
    "satisfaction": "Satisfaction",
    "bia": "BIA",
    "mna": "MNA",
}


def preview_sheet(sheet_name, df, max_rows=10):
    """แสดง preview ของ sheet"""
    print(f"\n{'='*120}")
    print(f"📋 SHEET: {sheet_name}")
    print(f"{'='*120}")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"\nColumn names ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\n🔍 First {min(max_rows, len(df))} rows of data:")
    print("-" * 120)

    # แสดง data แบบ row-by-row เพื่อความชัดเจน
    for idx in range(min(max_rows, len(df))):
        row = df.iloc[idx]
        print(f"\nRow {idx + 1}:")
        for col in df.columns:
            value = row[col]
            if pd.notna(value):
                print(f"  {col:30s} = {value}")
        print("-" * 120)

    if len(df) > max_rows:
        print(f"\n... และอีก {len(df) - max_rows} rows")


def main():
    """Main preview function"""
    print("=" * 120)
    print("EXCEL DATA PREVIEW")
    print("=" * 120)
    print(f"File: {EXCEL_FILE}")

    # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
    if not Path(EXCEL_FILE).exists():
        print(f"\n❌ ERROR: File not found!")
        print(f"Please place the Excel file at: {EXCEL_FILE}")
        print(f"\nExpected location: /Users/dev/SANSA/src/")
        print(f"Expected filename: ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx")
        return 1

    try:
        # Load Excel file
        excel_file = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
        print(f"\n✅ Excel file loaded successfully!")
        print(f"📋 Available sheets: {excel_file.sheet_names}")

        # Preview each sheet
        for sheet_key, sheet_name in SHEET_NAMES.items():
            if sheet_name not in excel_file.sheet_names:
                print(f"\n⚠️  Sheet '{sheet_name}' not found in Excel file")
                continue

            # Read sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Preview
            preview_sheet(sheet_name, df, max_rows=3)

        print("\n" + "=" * 120)
        print("✅ Preview completed")
        print("=" * 120)
        print("\n💡 Next step: Run import script if data looks correct:")
        print("   python scripts/import_all_excel_sheets.py")
        print("=" * 120)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
