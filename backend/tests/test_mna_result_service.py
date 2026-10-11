from types import SimpleNamespace

from app.services.mna_result_service import build_mna_result_summary


def test_imported_scores_produce_current_at_risk_result_without_raw_answers():
    record = SimpleNamespace(
        **{f"mna_s{index}": value for index, value in enumerate([2, 3, 2, 2, 2, 3], 1)},
        **{f"mna_a{index}": value for index, value in enumerate([1, 1, 1, 2, .5, 1, 1, 1, 0, 0, 1, 0], 1)},
        mna_screen_total=14,
        mna_ass_total=9.5,
        mna_total=23.5,
        result_category="2",
        answer_capture_mode="score_only",
    )

    result = build_mna_result_summary(record)

    assert result["available"] is True
    assert result["source"] == "imported_scores"
    assert result["has_raw_answers"] is False
    assert result["total"] == 23.5
    assert result["category"] == "at_risk"
    assert result["category_code"] == "2"
    assert result["category_label"] == "กลุ่มเสี่ยงต่อภาวะขาดสารอาหาร"
    assert result["integrity_status"] == "verified"
    assert result["issues"] == []
