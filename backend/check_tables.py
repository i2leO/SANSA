"""
Check database table structure
"""

from sqlalchemy import create_engine, text, inspect
from app.config import get_settings


def check_table_columns():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)

    tables_to_check = [
        "respondents",
        "sansa_responses",
        "satisfaction_responses",
        "mna_responses",
        "bia_records",
    ]

    print("📋 Checking table structures...\n")

    for table_name in tables_to_check:
        if table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            print(f"✅ {table_name}: {len(columns)} columns")
            for col in columns:
                col_type = str(col["type"])
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                print(f"   - {col['name']}: {col_type} {nullable}")
            print()
        else:
            print(f"❌ {table_name}: Table not found")
            print()


if __name__ == "__main__":
    check_table_columns()
