"""Audit or apply the approved SANSA 0/2/4 mapping to rows with raw answers.

Dry-run is the default. Rows with incomplete/unsupported raw answers are never
changed and are reported separately. Run only after a restorable DB backup.
"""

import argparse
from collections import Counter

from app.database import SessionLocal
from app.models import SANSAResponse, ScoringRuleVersion
from app.services.sansa_definition import DB_SCORING_VERSION, SANSA_QUESTIONS
from app.services.scoring_service import ScoringService
from app.services.sansa_result_service import revised_visit_result


def audit_row(row, scoring):
    missing = [
        question["field"]
        for question in SANSA_QUESTIONS
        if getattr(row, question["field"]) in (None, "")
    ]
    if missing:
        return "incomplete", missing
    try:
        return "ready", scoring.calculate_sansa_scores(row, version_id=-1)
    except ValueError as error:
        return "unsupported", str(error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="commit eligible rows")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        version = (
            db.query(ScoringRuleVersion)
            .filter(
                ScoringRuleVersion.instrument_name == "SANSA",
                ScoringRuleVersion.version_number == DB_SCORING_VERSION,
                ScoringRuleVersion.is_active == True,
            )
            .first()
        )
        if args.apply and version is None:
            raise RuntimeError(
                f"Active SANSA scoring version {DB_SCORING_VERSION} is required"
            )

        scoring = ScoringService(None)
        counts = Counter()
        ready = []
        details = []
        for row in db.query(SANSAResponse).order_by(SANSAResponse.id):
            state, result = audit_row(row, scoring)
            counts[state] += 1
            if state != "ready":
                details.append({
                    "response_id": row.id,
                    "visit_id": row.visit_id,
                    "state": state,
                    "detail": result,
                })
                continue
            ready.append((row, result))

        if args.apply:
            for row, scores in ready:
                for number in range(1, 17):
                    setattr(row, f"q{number}_score", scores[f"q{number}_score"])
                row.screening_total = scores["screening_total"]
                row.diet_total = scores["diet_total"]
                row.total_score = scores["total_score"]
                row.result_level = scores["result_level"]
                row.scoring_version_id = version.id
                db.flush()
                # Refresh Model 3 only when the visit has complete unambiguous inputs.
                revised_visit_result(db, row, persist=True)
            db.commit()
        else:
            db.rollback()

        print({
            "mode": "apply" if args.apply else "dry-run",
            "counts": dict(counts),
            "changed": len(ready) if args.apply else 0,
            "eligible": [row.visit_id for row, _ in ready],
            "unresolved_count": len(details),
            "unresolved_sample": details[:20],
        })
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
