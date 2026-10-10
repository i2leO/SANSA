import math

import pytest
from pydantic import ValidationError

from app.schemas import (
    RespondentProfileUpdate,
    BIAStaffSubmission,
    SANSAResponseCreate,
    SatisfactionResponseCreate,
)
from app.services.sansa_prediction_service import predict_sansa_nutrition_status


def complete_profile():
    return {
        "status": "elderly",
        "age": 72,
        "sex": "female",
        "education_level": "primary",
        "marital_status": "widowed",
        "monthly_income": "under_10k",
        "income_sources": [],
        "chronic_diseases": {"diseases": [], "other": ""},
        "living_arrangement": "with_family",
    }


def complete_sansa():
    return {
        "visit_id": 1,
        "q1_weight_change": "stable",
        "q2_food_intake": "normal",
        "q3_daily_activities": "normal",
        "q4_chronic_disease": "no",
        "q5_meals_per_day": "3",
        "q6_portion_size": "100",
        "q7_food_texture": "normal",
        "q8_rice_starch": "7-9",
        "q9_protein": "3-5",
        "q10_milk": "1",
        "q11_fruits": "1-2",
        "q12_vegetables": "2-3",
        "q13_water": "7-8",
        "q14_sweet_drinks": "rarely",
        "q15_cooking_method": "no_coconut",
        "q16_oil_coconut": "1-2",
    }


def test_revised4_profile_rejects_blank_and_legacy_options():
    profile = complete_profile()
    RespondentProfileUpdate(**profile)

    for field, value in (
        ("monthly_income", "over_20k"),
        ("living_arrangement", "with_children"),
        ("sex", "prefer_not_to_say"),
    ):
        invalid = {**profile, field: value}
        with pytest.raises(ValidationError):
            RespondentProfileUpdate(**invalid)

    missing = dict(profile)
    missing.pop("education_level")
    with pytest.raises(ValidationError):
        RespondentProfileUpdate(**missing)


def test_revised4_sansa_and_satisfaction_require_every_scored_answer():
    answers = complete_sansa()
    SANSAResponseCreate(**answers)
    answers.pop("q12_vegetables")
    with pytest.raises(ValidationError):
        SANSAResponseCreate(**answers)

    ratings = {"visit_id": 1, **{f"q{i}_{name}": 4 for i, name in enumerate([
        "clarity", "ease_of_use", "confidence", "presentation",
        "results_display", "usefulness", "overall_satisfaction",
    ], 1)}}
    SatisfactionResponseCreate(**ratings)
    ratings.pop("q7_overall_satisfaction")
    with pytest.raises(ValidationError):
        SatisfactionResponseCreate(**ratings)


def test_revised4_staff_bia_requires_complete_measurement_set():
    measurement = {
        "waist_circumference_cm": 84.0,
        "weight_kg": 61.2,
        "height_cm": 158.0,
        "fat_mass_kg": 18.2,
        "body_fat_percentage": 29.7,
        "visceral_fat_level": 8,
        "muscle_mass_kg": 39.1,
        "bone_mass_kg": 2.3,
        "water_percentage": 51.5,
        "metabolic_rate": 1210,
        "mac_cm": 26.0,
        "cc_cm": 33.0,
    }
    BIAStaffSubmission(**measurement)
    measurement.pop("body_fat_percentage")
    with pytest.raises(ValidationError):
        BIAStaffSubmission(**measurement)


def test_model3_uses_only_revised4_equations_and_probability_order():
    result = predict_sansa_nutrition_status(10, 6, 80, 1)
    l_over = -23.625 + 0.019 * 10 - 0.377 * 6 + 0.349 * 80 - 2.336
    l_normal = -9.655 + 0.039 * 10 - 0.507 * 6 + 0.189 * 80 - 2.489
    denominator = 1 + math.exp(l_over) + math.exp(l_normal)
    assert result["l_over"] == pytest.approx(l_over)
    assert result["l_normal"] == pytest.approx(l_normal)
    assert result["p_under"] == pytest.approx(1 / denominator)
    assert result["p_over"] == pytest.approx(math.exp(l_over) / denominator)
    assert result["p_normal"] == pytest.approx(math.exp(l_normal) / denominator)
    expected = max(
        {"UNDER": result["p_under"], "OVER": result["p_over"], "NORMAL": result["p_normal"]},
        key=lambda key: {"UNDER": result["p_under"], "OVER": result["p_over"], "NORMAL": result["p_normal"]}[key],
    )
    assert result["predicted_group"] == expected
