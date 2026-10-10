"""Create one immutable baseline snapshot for legacy MNA/BIA rows.

Dry-run is default. Existing revision history is never replaced.
"""
import argparse

from app.database import SessionLocal
from app.models import AssessmentRevision, BIARecord, MNAResponse
from app.services.assessment_revision_service import append_assessment_revision


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        existing = {(row.instrument, row.record_id) for row in db.query(AssessmentRevision).all()}
        pending = [
            ("BIA", row) for row in db.query(BIARecord).all() if ("BIA", row.id) not in existing
        ] + [
            ("MNA", row) for row in db.query(MNAResponse).all() if ("MNA", row.id) not in existing
        ]
        print({"mode": "apply" if args.apply else "dry-run", "pending": len(pending),
               "bia": sum(kind == "BIA" for kind, _ in pending),
               "mna": sum(kind == "MNA" for kind, _ in pending)})
        if args.apply:
            for instrument, record in pending:
                append_assessment_revision(db, instrument, record, action_type="baseline")
            db.commit()
            print({"created": len(pending), "total": db.query(AssessmentRevision).count()})
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
