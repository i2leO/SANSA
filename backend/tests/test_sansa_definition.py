from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import SANSAResponseCreate
from app.services.sansa_definition import SANSA_QUESTIONS, public_definition
from app.services.scoring_service import ScoringService


def complete_answers() -> dict[str, object]:
    return {
        "visit_id": 1,
        "q1_weight_change": "stable",
        "q2_food_intake": "normal",
        "q3_daily_activities": "normal",
        "q4_chronic_disease": "yes",
        "q5_meals_per_day": "3",
        "q6_portion_size": "100",
        "q7_food_texture": "soft",
        "q8_rice_starch": "7-9",
        "q9_protein": "3-5",
        "q10_milk": "0",
        "q11_fruits": "3-5",
        "q12_vegetables": "2-3",
        "q13_water": "7-8",
        "q14_sweet_drinks": "rarely",
        "q15_cooking_method": "no_coconut",
        "q16_oil_coconut": "1-2",
    }


def test_codebook_has_16_unique_questions_and_public_options():
    assert [question["number"] for question in SANSA_QUESTIONS] == list(range(1, 17))
    assert len({question["field"] for question in SANSA_QUESTIONS}) == 16
    definition = public_definition()
    assert definition["definition_version"] == "SANSA_0_2_4_PDF_2026-10-08"
    assert all("legacy_aliases" not in option for question in definition["questions"] for option in question["options"])


@pytest.mark.parametrize(
    ("question", "answer", "expected"),
    [
        (1, "decrease", 0), (1, "stable", 2), (1, "increase", 4),
        (2, "decrease", 0), (2, "normal", 2), (2, "increase", 4),
        (3, "cannot", 0), (3, "slower", 0), (3, "normal", 2),
        (4, "no", 2), (4, "yes", 4),
        (5, "rarely", 0), (5, "1", 0), (5, "2", 2), (5, "3", 2), (5, ">3", 4),
        (6, "25", 0), (6, "50", 0), (6, "75", 0), (6, "100", 2), (6, ">100", 4),
        (7, "liquid", 0), (7, "soft", 0), (7, "normal", 2),
        (8, "0", 0), (8, "1-3", 0), (8, "4-6", 0), (8, "7-9", 2), (8, ">9", 4),
        (9, "0", 0), (9, "1-2", 0), (9, "3-5", 2), (9, "6-8", 4), (9, ">8", 4),
        (10, "0", 0), (10, "1", 2), (10, "2", 2), (10, "3", 4), (10, "4", 4),
        (11, "0", 0), (11, "1-2", 0), (11, "3-5", 2), (11, "6-8", 4), (11, ">8", 4),
        (12, "0", 0), (12, "0-1", 0), (12, "2-3", 2), (12, "4", 2), (12, ">4", 2),
        (13, "rarely", 0), (13, "1-3", 0), (13, "4-6", 0), (13, "7-8", 2), (13, ">8", 2),
        (14, "rarely", 2), (14, "1", 2), (14, "2", 4), (14, "3", 4), (14, ">3", 4),
        (15, "no_coconut", 2), (15, "stir_fry", 2), (15, "coconut_curry", 4), (15, "fried", 4),
        (16, "0", 0), (16, "1-2", 0), (16, "3-4", 0), (16, "5-6", 2), (16, ">6", 4),
    ],
)
def test_approved_pdf_scores(question, answer, expected):
    assert ScoringService(None).calculate_sansa_question_score(question, answer) == Decimal(expected)


def test_new_response_accepts_only_canonical_codebook_values():
    SANSAResponseCreate(**complete_answers())
    for field, invalid in (("q10_milk", "<1"), ("q15_cooking_method", "steam_boil"), ("q4_chronic_disease", "มี")):
        answers = complete_answers()
        answers[field] = invalid
        with pytest.raises(ValidationError):
            SANSAResponseCreate(**answers)


def test_legacy_values_remain_readable_but_are_not_new_write_options():
    service = ScoringService(None)
    assert service.calculate_sansa_question_score(10, "<1") == Decimal("0")
    assert service.calculate_sansa_question_score(15, "steam_boil") == Decimal("2")
    assert service.calculate_sansa_question_score(7, "อ่อน (โจ๊ก)") == Decimal("0")
    assert service.calculate_sansa_question_score(7, "ปกติ (ข้าวสวย)") == Decimal("2")
    public_values = {
        option["value"]
        for question in public_definition()["questions"]
        for option in question["options"]
    }
    assert "<1" not in public_values
    assert "steam_boil" not in public_values


def test_complete_score_uses_approved_pdf_definition():
    payload = SANSAResponseCreate(**complete_answers())
    result = ScoringService(None).calculate_sansa_scores(payload, version_id=99)
    assert result["q4_score"] == Decimal("4")
    assert result["q7_score"] == Decimal("0")
    assert result["q10_score"] == Decimal("0")
    assert result["q15_score"] == Decimal("2")
    assert result["screening_total"] == Decimal("10")
    assert result["diet_total"] == Decimal("18")
    assert result["result_level"] is None
