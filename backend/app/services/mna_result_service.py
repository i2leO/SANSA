"""Read-only MNA current-result summary for imported and staff-entered records."""
from decimal import Decimal


MNA_SCORE_FIELDS = tuple(
    [f"mna_s{index}" for index in range(1, 7)]
    + [f"mna_a{index}" for index in range(1, 13)]
)

MNA_CATEGORY_LABELS = {
    "normal": "ภาวะโภชนาการปกติ",
    "at_risk": "กลุ่มเสี่ยงต่อภาวะขาดสารอาหาร",
    "malnourished": "ภาวะขาดสารอาหาร",
}

_CATEGORY_ALIASES = {
    "1": "normal",
    "2": "at_risk",
    "3": "malnourished",
    **{category: category for category in MNA_CATEGORY_LABELS},
}


def category_from_total(total: Decimal) -> str:
    if total >= Decimal("24"):
        return "normal"
    if total >= Decimal("17"):
        return "at_risk"
    return "malnourished"


def build_mna_result_summary(record) -> dict:
    """Expose the current result without inventing missing raw A-R answers."""
    scores = [getattr(record, field, None) for field in MNA_SCORE_FIELDS]
    has_item_scores = all(value is not None for value in scores)
    issues = []
    calculated_screen = calculated_assessment = calculated_total = None
    if has_item_scores:
        decimals = [Decimal(str(value)) for value in scores]
        calculated_screen = sum(decimals[:6], Decimal("0"))
        calculated_assessment = sum(decimals[6:], Decimal("0"))
        calculated_total = calculated_screen + calculated_assessment
        recorded_totals = (
            ("mna_screen_total", calculated_screen),
            ("mna_ass_total", calculated_assessment),
            ("mna_total", calculated_total),
        )
        for field, calculated in recorded_totals:
            recorded = getattr(record, field, None)
            if recorded is None or Decimal(str(recorded)) != calculated:
                issues.append(f"{field}_mismatch")

    recorded_total = getattr(record, "mna_total", None)
    effective_total = calculated_total if calculated_total is not None else (
        Decimal(str(recorded_total)) if recorded_total is not None else None
    )
    category = category_from_total(effective_total) if effective_total is not None else None
    stored_category = _CATEGORY_ALIASES.get(str(getattr(record, "result_category", "")))
    if category is not None and stored_category != category:
        issues.append("result_category_mismatch")

    return {
        "available": effective_total is not None,
        "source": (
            "imported_scores"
            if getattr(record, "answer_capture_mode", None) == "score_only"
            else "recorded_answers"
        ),
        "has_raw_answers": getattr(record, "answer_capture_mode", None) == "raw_answers",
        "has_item_scores": has_item_scores,
        "screening_total": calculated_screen if calculated_screen is not None else getattr(record, "mna_screen_total", None),
        "assessment_total": calculated_assessment if calculated_assessment is not None else getattr(record, "mna_ass_total", None),
        "total": effective_total,
        "category": category,
        "category_code": {"normal": "1", "at_risk": "2", "malnourished": "3"}.get(category),
        "category_label": MNA_CATEGORY_LABELS.get(category),
        "integrity_status": "verified" if not issues and has_item_scores else "partial" if effective_total is not None else "missing",
        "issues": issues,
    }
