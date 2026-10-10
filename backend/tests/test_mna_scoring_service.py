from app.schemas import MNAResponseCreate
from app.services.scoring_service import ScoringService
from app.services.mna_definition import MNA_ITEMS
import pytest


def test_mna_semantic_answers_are_scored_and_calf_is_assessment():
    response = MNAResponseCreate(
        visit_id=1,
        q1_food_intake_decline="none",
        q2_weight_loss="unknown",
        q3_mobility="goes_out",
        q4_stress_illness="no",
        q5_neuropsychological="none",
        q6_bmi="19-21",
        q19_calf_circumference_assess=">=31",
        q8_independent_living="yes",
        q9_medications="<2",
        q10_pressure_sores="no",
        q11_full_meals="2",
        q12_protein_consumption="2",
        q13_fruits_vegetables="yes",
        q14_fluid_intake="3-5",
        q15_eating_independence="self_no_problem",
        q16_self_nutrition="well_nourished",
        q17_health_comparison="same",
        q18_mid_arm_circumference=">22",
    )

    result = ScoringService(None).calculate_mna_score(response)

    assert result["mna_screen_total"] == 10
    assert result["mna_ass_total"] == 13
    assert result["mna_total"] == 23
    assert result["result_category"] == "at_risk"
    assert result["mna_a12"] == 1
    assert "mna_s7" not in result


def test_missing_answers_do_not_become_zero_or_diagnosis():
    with pytest.raises(ValueError, match="missing or unsupported"):
        ScoringService(None).calculate_mna_score(MNAResponseCreate(visit_id=1))


def test_complete_maximum_answers_score_thirty_even_with_high_screening():
    service = ScoringService(None)
    answers = {
        item["field"]: max(item["options"], key=lambda option: service.calculate_mna_question_score(index, option["value"]))["value"]
        for index, item in enumerate(MNA_ITEMS, 1)
    }
    result = service.calculate_mna_score(MNAResponseCreate(visit_id=1, **answers))
    assert result["mna_screen_total"] == 14
    assert result["mna_ass_total"] == 16
    assert result["mna_total"] == 30
    assert result["result_category"] == "normal"


def test_valid_zero_answers_remain_valid_zero():
    service = ScoringService(None)
    answers = {
        item["field"]: min(item["options"], key=lambda option: service.calculate_mna_question_score(index, option["value"]))["value"]
        for index, item in enumerate(MNA_ITEMS, 1)
    }
    result = service.calculate_mna_score(MNAResponseCreate(visit_id=1, **answers))
    assert result["mna_total"] == 0


def test_unknown_answer_is_rejected():
    with pytest.raises(ValueError):
        ScoringService(None).calculate_mna_question_score(1, "unsupported")
