"""Compose verified visit results from the approved SANSA definition."""
from decimal import Decimal

from app.models import BIARecord
from app.services.sansa_definition import DB_SCORING_VERSION, SANSA_QUESTIONS, score_answer
from app.services.sansa_domain_service import calculate_sansa_domain_scores, age_group01
from app.services.sansa_prediction_service import MODEL_VERSION, predict_sansa_nutrition_status
from app.services.sansa_prediction_storage import save_sansa_prediction
from app.services.bia_reference_service import derive_nutrition_reference


_ITEM_FEEDBACK = {
    8: {0: ("UNDER", "กินข้าว-แป้งน้อยกว่าที่แนะนำ ลองเพิ่มข้าวอีกสักทัพพีในมื้อถัดไปนะคะ"), 2: ("NORMAL", "กินข้าว-แป้งพอดีตามเกณฑ์แล้วค่ะ รักษาแบบนี้ไว้นะคะ"), 4: ("OVER", "กินข้าว-แป้งมากกว่าที่แนะนำค่อนข้างมาก ลองลดลงเล็กน้อยในแต่ละมื้อนะคะ")},
    9: {0: ("UNDER", "กินเนื้อสัตว์หรือไข่น้อยกว่าที่แนะนำ ลองเพิ่มไข่หรือเนื้อสัตว์ไม่ติดมันในมื้อถัดไปนะคะ"), 2: ("NORMAL", "กินเนื้อสัตว์หรือไข่พอดีตามเกณฑ์แล้วค่ะ"), 4: ("OVER", "กินเนื้อสัตว์มากกว่าที่แนะนำ ลองลดปริมาณและเลือกเนื้อไม่ติดมันนะคะ")},
    10: {0: ("UNDER", "ดื่มนมน้อยกว่าที่แนะนำ ลองเพิ่มเป็นวันละ 1 แก้วนะคะ"), 2: ("NORMAL", "ดื่มนมพอดีตามเกณฑ์แล้วค่ะ"), 4: ("OVER", "ดื่มนมมากกว่าที่แนะนำ อาจได้รับพลังงานและไขมันมากเกินไป ลองลดลงเหลือวันละ 1–2 แก้วนะคะ")},
    11: {0: ("UNDER", "กินผลไม้น้อยกว่าที่แนะนำ ลองเพิ่มผลไม้เป็นของว่างนะคะ"), 2: ("NORMAL", "กินผลไม้พอดีตามเกณฑ์แล้วค่ะ"), 4: ("OVER", "กินผลไม้มากกว่าที่แนะนำ อาจได้รับน้ำตาลมากเกินไป โดยเฉพาะเมื่อมีภาวะเบาหวานร่วมด้วย ลองลดลงนะคะ")},
    12: {0: ("UNDER", "กินผักน้อยกว่าที่แนะนำ ลองเพิ่มผักในทุกมื้อนะคะ"), 2: ("NORMAL", "กินผักพอดีหรือมากกว่าเกณฑ์แล้ว ดีมากค่ะ")},
    13: {0: ("UNDER", "ดื่มน้ำน้อยกว่าที่แนะนำ ลองดื่มน้ำเปล่าเพิ่มขึ้นระหว่างวันนะคะ"), 2: ("NORMAL", "ดื่มน้ำเพียงพอตามเกณฑ์แล้วค่ะ")},
    14: {2: ("NORMAL", "ดื่มเครื่องดื่มหวานไม่บ่อย ดีแล้วค่ะ"), 4: ("OVER", "ดื่มเครื่องดื่มหวานบ่อยไป ลองลดลงนะคะ")},
    15: {2: ("NORMAL", "กินของทอดไม่บ่อย ดีแล้วค่ะ"), 4: ("OVER", "กินของทอดบ่อยไป ลองลดลงนะคะ")},
    16: {0: ("UNDER", "ใช้น้ำมันหรือกะทิน้อยเกินไปก็ไม่ดี ลองปรับให้พอดีนะคะ"), 2: ("NORMAL", "ใช้น้ำมันหรือกะทิพอดีแล้วค่ะ"), 4: ("OVER", "ใช้น้ำมันหรือกะทิมากไป ลองลดลงนะคะ")},
}


def participant_item_results(response):
    """Map D2/D3 answers to the approved page 12–14 participant messages."""
    items = []
    for question in SANSA_QUESTIONS:
        number = question["number"]
        if number not in _ITEM_FEEDBACK:
            continue
        raw = getattr(response, question["field"], None)
        score_value = getattr(response, f"q{number}_score", None)
        if score_value is None:
            continue
        score = int(Decimal(str(score_value)))
        feedback = _ITEM_FEEDBACK[number].get(score)
        if feedback is None:
            continue
        selected = next((option for option in question["options"] if option["value"] == raw), None)
        if selected is not None:
            answer_label = selected["label"]
            answer_source = "recorded_answer"
        else:
            labels = [option["label"] for option in question["options"] if option["score"] == score]
            answer_label = " / ".join(dict.fromkeys(labels))
            answer_source = "score_bucket"
        items.append({
            "number": number,
            "domain": question["domain"],
            "field": question["field"],
            "label": question["label"],
            "answer_label": answer_label,
            "answer_source": answer_source,
            "score": score,
            "status": feedback[0],
            "recommendation": feedback[1],
        })
    return items


def revised_visit_result(db, response, persist=False):
    result = {"domain_scores": None, "prediction": None, "reference": None,
              "comparison": None, "bia_record_id": None, "issues": [], "saved": False,
              "verified_024": False, "missing_answer_fields": [],
              "invalid_answer_fields": [], "score_mismatch_fields": []}
    issues = result["issues"]
    visit = response.visit
    respondent = visit.respondent
    if visit.is_deleted or respondent.is_deleted:
        raise ValueError("Visit or respondent is deleted")
    missing_answers = [
        question["field"] for question in SANSA_QUESTIONS
        if getattr(response, question["field"], None) in (None, "")
    ]
    result["missing_answer_fields"] = missing_answers
    score_only_revised4 = (
        response.source_dataset == "revised4"
        and response.answer_capture_mode == "score_only"
    )
    if missing_answers and not score_only_revised4:
        issues.append("missing_raw_answers")

    invalid_answers = []
    score_mismatches = []
    if score_only_revised4:
        for question in SANSA_QUESTIONS:
            field = question["field"]
            recorded = getattr(response, f"q{question['number']}_score", None)
            allowed = {Decimal(str(option["score"])) for option in question["options"]}
            if recorded is None or Decimal(str(recorded)) not in allowed:
                score_mismatches.append(field)
    elif not missing_answers:
        for question in SANSA_QUESTIONS:
            field = question["field"]
            try:
                expected = Decimal(str(score_answer(question["number"], getattr(response, field))))
            except ValueError:
                invalid_answers.append(field)
                continue
            recorded = getattr(response, f"q{question['number']}_score", None)
            if recorded is None or Decimal(str(recorded)) != expected:
                score_mismatches.append(field)
    result["invalid_answer_fields"] = invalid_answers
    result["score_mismatch_fields"] = score_mismatches
    if invalid_answers:
        issues.append("invalid_raw_answers")
    if score_mismatches:
        issues.append("score_definition_mismatch")

    version = response.scoring_version
    if (version is None or version.instrument_name != "SANSA"
            or version.version_number != DB_SCORING_VERSION):
        issues.append("scoring_version_mismatch")

    result["verified_024"] = not any(code in issues for code in (
        "missing_raw_answers", "invalid_raw_answers", "score_definition_mismatch",
        "scoring_version_mismatch",
    ))
    if result["verified_024"]:
        result["domain_scores"] = calculate_sansa_domain_scores(response, allow_missing=False)
    records = db.query(BIARecord).filter(BIARecord.visit_id == visit.id).limit(2).all()
    if len(records) != 1:
        issues.append("missing_bia" if not records else "ambiguous_bia")
        return result
    bia = records[0]
    result["bia_record_id"] = bia.id
    # Task 2 requires respondent age. Use the same respondent demographics for reference.
    if respondent.age is None:
        issues.append("missing_age")
    if bia.waist_circumference_cm is None:
        issues.append("missing_waist")
    elif bia.waist_circumference_cm <= 0:
        issues.append("invalid_waist")
    if (result["domain_scores"] is not None
            and result["domain_scores"]["d2_total"] is not None
            and result["domain_scores"]["d3_total"] is not None
            and respondent.age is not None
            and bia.waist_circumference_cm is not None
            and bia.waist_circumference_cm > 0):
        inputs = dict(d2_total=result["domain_scores"]["d2_total"],
                      d3_total=result["domain_scores"]["d3_total"],
                      waist_cm=bia.waist_circumference_cm,
                      age_group01=age_group01(respondent))
        try:
            if persist:
                stored = save_sansa_prediction(db, visit.id, **inputs)
                prediction = {key: getattr(stored, key) for key in (
                    "d2_total", "d3_total", "waist_cm", "age_group01", "l_over", "l_normal",
                    "p_under", "p_normal", "p_over", "predicted_group", "model_version")}
                result["saved"] = True
            else:
                prediction = {**predict_sansa_nutrition_status(**inputs), "model_version": MODEL_VERSION}
            result["prediction"] = prediction
        except ValueError:
            issues.append("invalid_prediction_inputs")
    if respondent.age is None or bia.bmi is None or bia.body_fat_percentage is None:
        issues.append("missing_reference_inputs")
    else:
        try:
            result["reference"] = derive_nutrition_reference(
                respondent.age, respondent.sex, bia.bmi, bia.body_fat_percentage)
        except ValueError:
            issues.append("invalid_reference_inputs")
    if result["prediction"] and result["reference"]:
        predicted = result["prediction"]["predicted_group"]
        reference = result["reference"]["nutrition_reference"]
        result["comparison"] = {"predicted_group": predicted, "nutrition_reference": reference,
                                "matches": predicted == reference}
    return result
