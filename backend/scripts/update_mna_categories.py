"""Update MNA result_category for existing records"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from decimal import Decimal
from app.database import SessionLocal
from app.models import MNAResponse


def calculate_result_category(mna_total: Decimal) -> str:
    """Calculate result category based on MNA total score

    Thresholds:
    - normal: 24-30
    - at_risk: 17-23.5
    - malnourished: <17
    """
    if mna_total >= 24:
        return "normal"
    elif mna_total >= 17:
        return "at_risk"
    else:
        return "malnourished"


def main():
    db = SessionLocal()

    try:
        # Get all MNA responses
        mna_responses = db.query(MNAResponse).all()

        print(f"Found {len(mna_responses)} MNA responses")
        print("-" * 60)

        updated_count = 0

        for mna in mna_responses:
            if mna.mna_total is not None:
                old_category = mna.result_category
                new_category = calculate_result_category(mna.mna_total)

                if old_category != new_category:
                    mna.result_category = new_category
                    updated_count += 1

                    print(
                        f"ID {mna.id}: Total={mna.mna_total}, "
                        f"Category: {old_category} → {new_category}"
                    )
                else:
                    print(
                        f"ID {mna.id}: Total={mna.mna_total}, "
                        f"Category: {new_category} (unchanged)"
                    )
            else:
                print(f"ID {mna.id}: No mna_total - skipped")

        if updated_count > 0:
            db.commit()
            print("-" * 60)
            print(f"✅ Updated {updated_count} records")
        else:
            print("-" * 60)
            print("No updates needed")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
