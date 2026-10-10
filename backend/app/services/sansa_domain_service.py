"""Derived SANSA domains using stored scores; no database writes or rescoring."""

from decimal import Decimal
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from app.models import Respondent, SANSAResponse


def calculate_sansa_domain_scores(response: "SANSAResponse", *, allow_missing=False) -> Dict[str, Optional[Decimal]]:
    """Sum existing dietary scores. Missing scores are errors, not zeroes."""
    domains = {
        "d1_total": ("q5_score", "q6_score", "q7_score"),
        "d2_total": (
            "q8_score", "q9_score", "q10_score",
            "q11_score", "q12_score", "q13_score",
        ),
        "d3_total": ("q14_score", "q15_score", "q16_score"),
    }
    totals = {}
    for domain, fields in domains.items():
        total = Decimal("0")
        for field in fields:
            value = getattr(response, field)
            if value is None:
                if allow_missing:
                    total = None
                    break
                raise ValueError(f"Missing SANSA score: {field}")
            total += Decimal(str(value))
        totals[domain] = total
    return totals


def age_group01(respondent: "Respondent") -> int:
    """Derive the age group from the existing respondent, without storing it."""
    if respondent.age is None:
        raise ValueError("Missing respondent age")
    return 0 if respondent.age < 70 else 1
