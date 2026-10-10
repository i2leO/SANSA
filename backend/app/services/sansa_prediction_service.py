"""Revised4 Model 3 prediction, independent of legacy threshold scoring."""

import math
from decimal import Decimal
from typing import Union

# Exact model identifier named by revised4 Data_Dictionary / Model_Logic.
# Changing the approved workbook must create a new identifier; stored results
# from another version are never overwritten under this key.
MODEL_VERSION = "Model3_Reduced_UnderRef_v1"
Number = Union[int, float, Decimal]


def predict_sansa_nutrition_status(
    d2_total: Number, d3_total: Number, waist_cm: Number, age_group01: int
) -> dict:
    """Accept Task 2 domain/age outputs and an explicitly selected waist in cm."""
    values = {}
    for name, value in (("d2_total", d2_total), ("d3_total", d3_total),
                        ("waist_cm", waist_cm)):
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise ValueError(f"{name} must be a finite number")
        try:
            number = float(value)
        except (OverflowError, ValueError):
            raise ValueError(f"{name} must be a finite number") from None
        if not math.isfinite(number):
            raise ValueError(f"{name} must be a finite number")
        values[name] = number
    if isinstance(age_group01, bool) or age_group01 not in (0, 1):
        raise ValueError("age_group01 must be 0 or 1")

    d2, d3, waist = (values[k] for k in ("d2_total", "d3_total", "waist_cm"))
    l_over = -23.625 + 0.019 * d2 - 0.377 * d3 + 0.349 * waist - 2.336 * age_group01
    l_normal = -9.655 + 0.039 * d2 - 0.507 * d3 + 0.189 * waist - 2.489 * age_group01
    if not all(math.isfinite(x) for x in (l_over, l_normal)):
        raise ValueError("Inputs produce non-finite logits")

    # Under is the zero-logit reference. Subtract the largest logit to avoid overflow.
    logits = {"UNDER": 0.0, "OVER": l_over, "NORMAL": l_normal}
    maximum = max(logits.values())
    weights = {group: math.exp(logit - maximum) for group, logit in logits.items()}
    denominator = math.fsum(weights.values())
    probabilities = {group: weight / denominator for group, weight in weights.items()}
    # Excel tie order: UNDER, then OVER, then NORMAL.
    return {
        **values, "age_group01": int(age_group01),
        "l_over": l_over, "l_normal": l_normal,
        "p_under": probabilities["UNDER"], "p_normal": probabilities["NORMAL"],
        "p_over": probabilities["OVER"],
        "predicted_group": max(probabilities, key=probabilities.get),
    }
