"""Canonical SANSA 16-item instrument definition.

The approved 0/2/4 scoring contract is transcribed from pages 5-9 of
``EDIT SANSA ONLINE (revised).pdf``.  Validation, server-side scoring and the
participant form all consume this module.  Observation workbooks must never
be used as an executable codebook.
"""

from typing import Any


DEFINITION_VERSION = "SANSA_0_2_4_PDF_2026-10-08"
DEFINITION_SOURCE = "EDIT SANSA ONLINE (revised).pdf#pages=5-9"
DB_SCORING_VERSION = "0.2.4-20261008"


def _option(value: str, label: str, score: int, *legacy_aliases: str) -> dict[str, Any]:
    return {
        "value": value,
        "label": label,
        "score": score,
        "legacy_aliases": list(legacy_aliases),
    }


SANSA_QUESTIONS: tuple[dict[str, Any], ...] = (
    {"number": 1, "field": "q1_weight_change", "label": "ท่านมีการเปลี่ยนแปลงของน้ำหนักตัวโดยไม่ได้ตั้งใจในช่วง 3 เดือนที่ผ่านมาอย่างไร", "domain": "screening", "included_in_model": False, "options": (_option("decrease", "ลดลง", 0, "ลดลง"), _option("stable", "คงเดิม", 2, "คงเดิม"), _option("increase", "เพิ่มขึ้น", 4, "เพิ่มขึ้น"))},
    {"number": 2, "field": "q2_food_intake", "label": "ท่านมีความเปลี่ยนแปลงของการกินอาหาร ในช่วง 3 เดือนที่ผ่านมาอย่างไร", "domain": "screening", "included_in_model": False, "options": (_option("decrease", "เบื่ออาหาร กินได้น้อยลง", 0, "น้อยลง"), _option("normal", "ความอยากอาหารเป็นปกติ กินได้เท่า ๆ เดิม", 2, "ปกติ"), _option("increase", "ความอยากอาหารมากขึ้น กินได้มากกว่าปกติ", 4, "มากขึ้น"))},
    {"number": 3, "field": "q3_daily_activities", "label": "ท่านสามารถทำกิจวัตรประจำวัน เช่น การเดินไปจ่ายตลาด ซื้ออาหาร การทำอาหาร การตักอาหารกินได้หรือไม่", "domain": "screening", "included_in_model": False, "options": (_option("cannot", "ไม่สามารถทำได้ ต้องได้รับความช่วยเหลือ", 0, "ไม่ได้"), _option("slower", "ทำได้ด้วยตนเอง แต่ต้องใช้เวลามากกว่าปกติ", 0, "ช้ากว่าปกติ"), _option("normal", "ทำได้ด้วยตนเองเป็นปกติ", 2, "ปกติ"))},
    {"number": 4, "field": "q4_chronic_disease", "label": "ท่านมีโรคประจำตัวหรือไม่ เช่น โรคอ้วน โรคเบาหวาน โรคไขมันในเลือดสูง โรคความดันโลหิตสูง โรคหัวใจ โรคไตเรื้อรัง โรคเก๊าท์ โรคสมองเสื่อม โรคซึมเศร้า หรือโรคมะเร็งที่ได้รับการรักษาด้วยเคมีบำบัด", "domain": "screening", "included_in_model": False, "options": (_option("no", "ไม่มี", 2, "ไม่มี"), _option("yes", "มี", 4, "มี"))},
    {"number": 5, "field": "q5_meals_per_day", "label": "ในช่วง 1 สัปดาห์ที่ผ่านมา ท่านกินอาหารมื้อหลักวันละกี่มื้อ (ไม่รวมมื้อของว่างเล็ก ๆ น้อย ๆ เช่น ขนม ผลไม้ หรือเครื่องดื่ม)", "domain": "d1", "included_in_model": False, "options": (_option("rarely", "แทบไม่ได้กิน", 0, "แทบไม่ได้"), _option("1", "1 มื้อ", 0, "1_meal"), _option("2", "2 มื้อ", 2, "2_meals"), _option("3", "3 มื้อ", 2, "3_meals"), _option(">3", "มากกว่า 3 มื้อ", 4, "more_than_3"))},
    {"number": 6, "field": "q6_portion_size", "label": "ในช่วง 1 สัปดาห์ที่ผ่านมา ท่านกินอาหารในแต่ละมื้อได้ปริมาณเท่าใด เมื่อเทียบกับที่เคยกิน", "domain": "d1", "included_in_model": False, "options": (_option("25", "25%", 0, "25%"), _option("50", "50%", 0, "50%"), _option("75", "75%", 0, "75%"), _option("100", "หมดจาน (100%)", 2, "100%"), _option(">100", "มากกว่า 1 จาน", 4, ">100%", "more_than_100"))},
    {"number": 7, "field": "q7_food_texture", "label": "ลักษณะอาหารที่ท่านกินเป็นประจำ", "domain": "d1", "included_in_model": False, "options": (_option("liquid", "อาหารเหลว", 0, "เหลว"), _option("soft", "อาหารอ่อนนิ่ม", 0, "อ่อน", "อ่อน (โจ๊ก)"), _option("normal", "อาหารปกติ (ข้าวสวย + กับข้าว)", 2, "ปกติ", "ปกติ (ข้าวสวย)"))},
    {"number": 8, "field": "q8_rice_starch", "label": "ในแต่ละวัน ท่านกินอาหารประเภทข้าวแป้ง เช่น ข้าวสวย เส้นก๋วยเตี๋ยว ขนมปัง ข้าวโพด เผือก มัน รวมกันได้ประมาณเท่ากับกี่กำปั้นมือของท่านเอง (1 กำปั้นมือ = ประมาณ 1 ทัพพี)", "domain": "d2", "included_in_model": True, "options": (_option("0", "แทบไม่ได้กิน", 0), _option("1-3", "1–3 กำปั้นมือ", 0, "1_to_3"), _option("4-6", "4–6 กำปั้นมือ", 0, "4_to_6"), _option("7-9", "7–9 กำปั้นมือ", 2, "7_to_9"), _option(">9", "มากกว่า 9 กำปั้นมือ", 4, "more_than_9"))},
    {"number": 9, "field": "q9_protein", "label": "ในแต่ละวัน ท่านกินไข่ เต้าหู้ ไก่ ปลา กุ้ง รวมกันได้ปริมาณเท่ากับกี่ฝ่ามือของท่านเอง (1 ฝ่ามือ = ประมาณ 2 ช้อนกินข้าว หรือไข่ 1 ฟอง)", "domain": "d2", "included_in_model": True, "options": (_option("0", "แทบไม่ได้กิน", 0), _option("1-2", "1–2 ฝ่ามือ", 0, "1_to_2"), _option("3-5", "3–5 ฝ่ามือ", 2, "3_to_5"), _option("6-8", "6–8 ฝ่ามือ", 4, "6_to_8"), _option(">8", "มากกว่า 8 ฝ่ามือ", 4, "more_than_8"))},
    {"number": 10, "field": "q10_milk", "label": "ในแต่ละวัน ท่านดื่มนมวัว โยเกิร์ต หรือนมถั่วเหลืองเสริมแคลเซียม รวมกันได้ประมาณกี่แก้ว (1 แก้ว = ประมาณ 240 มิลลิลิตร หรือโยเกิร์ต 1 ถ้วย)", "domain": "d2", "included_in_model": True, "options": (_option("0", "ไม่ได้ดื่มหรือน้อยกว่า 1 แก้ว", 0, "<1", "less_than_1"), _option("1", "1 แก้ว", 2), _option("2", "2 แก้ว", 2), _option("3", "3 แก้ว", 4), _option("4", "4 แก้ว", 4))},
    {"number": 11, "field": "q11_fruits", "label": "ในแต่ละวัน ท่านกินผลไม้ เช่น กล้วย ส้มเขียวหวาน มะละกอ สับปะรด มะม่วง แตงโม รวมกันได้ปริมาณเท่ากับกี่กำปั้นมือของท่านเอง (1 กำปั้นมือ = ผลไม้ที่พอดีกับมือของท่านเอง เช่น ส้ม 1 ลูกเล็ก มะละกอ 6 ชิ้นคำ)", "domain": "d2", "included_in_model": True, "options": (_option("0", "แทบไม่ได้กิน", 0), _option("1-2", "1–2 กำปั้นมือ", 0, "1_to_2"), _option("3-5", "3–5 กำปั้นมือ", 2, "3_to_5"), _option("6-8", "6–8 กำปั้นมือ", 4, "6_to_8"), _option(">8", "มากกว่า 8 กำปั้นมือ", 4, "more_than_8"))},
    {"number": 12, "field": "q12_vegetables", "label": "ในแต่ละวัน ท่านกินผัก (ผักใบ เช่น ผักบุ้ง ตำลึง คะน้า ผักกาดขาว ผักหัว เช่น แครอท บล็อกโคลี่) รวมกันได้ปริมาณเท่ากับกี่อุ้งมือต่อกันของท่านเอง (1 อุ้งมือต่อกัน = ประมาณ 1 ทัพพี)", "domain": "d2", "included_in_model": True, "options": (_option("0", "แทบไม่ได้กิน", 0), _option("0-1", "0–1 อุ้งมือ", 0, "0_to_1"), _option("2-3", "2–3 อุ้งมือ", 2, "2_to_3"), _option("4", "4 อุ้งมือ", 2), _option(">4", "มากกว่า 4 อุ้งมือ", 2, "more_than_4"))},
    {"number": 13, "field": "q13_water", "label": "ในแต่ละวัน ท่านดื่มน้ำเปล่า รวมกันได้ประมาณกี่แก้ว (1 แก้ว = ประมาณ 200 มิลลิลิตร)", "domain": "d2", "included_in_model": True, "options": (_option("rarely", "แทบไม่ได้ดื่ม", 0, "แทบไม่ได้"), _option("1-3", "1–3 แก้ว", 0, "1_to_3"), _option("4-6", "4–6 แก้ว", 0, "4_to_6"), _option("7-8", "7–8 แก้ว", 2, "7_to_8"), _option(">8", "มากกว่า 8 แก้ว", 2, "more_than_8"))},
    {"number": 14, "field": "q14_sweet_drinks", "label": "ในแต่ละวัน ท่านดื่มเครื่องดื่ม เช่น เครื่องดื่ม 3 in 1 (ชาเขียว ชาเย็น โกโก้ กาแฟ) น้ำหวาน น้ำอัดลม รวมกันได้ประมาณกี่แก้ว (1 แก้ว = ประมาณ 240 มิลลิลิตร)", "domain": "d3", "included_in_model": True, "options": (_option("rarely", "แทบไม่ได้ดื่ม", 2, "0", "ไม่ดื่ม"), _option("1", "1 แก้ว", 2), _option("2", "2 แก้ว", 4), _option("3", "3 แก้ว", 4), _option(">3", "มากกว่า 3 แก้ว", 4, "more_than_3"))},
    {"number": 15, "field": "q15_cooking_method", "label": "ประเภทการปรุงประกอบอาหารที่ท่านกินบ่อยที่สุด", "domain": "d3", "included_in_model": True, "options": (_option("no_coconut", "ต้ม ตุ๋น นึ่ง อบ ยำ ย่าง", 2, "steam_boil", "ต้ม_นึ่ง", "ต้ม/นึ่ง"), _option("stir_fry", "ผัด", 2, "ผัด"), _option("coconut_curry", "แกงกะทิ", 4, "แกงกะทิ"), _option("fried", "ทอดน้ำมันท่วม", 4, "ทอด"))},
    {"number": 16, "field": "q16_oil_coconut", "label": "ในแต่ละวัน ท่านกินน้ำมัน กะทิ หรือน้ำสลัดน้ำข้น รวมกันได้ประมาณเท่ากับกี่นิ้วหัวแม่มือของท่านเอง (1 นิ้วหัวแม่มือ = น้ำมันประมาณ 1 ช้อนชา หรือกะทิ/น้ำสลัดน้ำข้น 1 ช้อนโต๊ะ)", "domain": "d3", "included_in_model": True, "options": (_option("0", "แทบไม่ได้กิน", 0), _option("1-2", "1–2 นิ้วหัวแม่มือ", 0, "1_to_2"), _option("3-4", "3–4 นิ้วหัวแม่มือ", 0, "3_to_4"), _option("5-6", "5–6 นิ้วหัวแม่มือ", 2, "5_to_6"), _option(">6", "มากกว่า 6 นิ้วหัวแม่มือ", 4, "more_than_6"))},
)

QUESTIONS_BY_NUMBER = {question["number"]: question for question in SANSA_QUESTIONS}
QUESTIONS_BY_FIELD = {question["field"]: question for question in SANSA_QUESTIONS}


def canonical_values(field: str) -> set[str]:
    return {option["value"] for option in QUESTIONS_BY_FIELD[field]["options"]}


def score_answer(question_number: int, answer: str, *, allow_legacy: bool = True) -> int:
    question = QUESTIONS_BY_NUMBER.get(question_number)
    if question is None:
        raise ValueError(f"ไม่พบข้อคำถาม SANSA ข้อ {question_number}")
    for option in question["options"]:
        if answer == option["value"] or (allow_legacy and answer in option["legacy_aliases"]):
            return option["score"]
    raise ValueError(
        f"กรุณาตรวจคำตอบ SANSA ข้อ {question_number}: ยังไม่ได้ตอบหรือรูปแบบคำตอบไม่รองรับ"
    )


def public_definition() -> dict[str, Any]:
    """Return the participant-safe definition without legacy write aliases."""
    questions = []
    for question in SANSA_QUESTIONS:
        questions.append({
            key: value for key, value in question.items() if key != "options"
        } | {
            "options": [
                {key: value for key, value in option.items() if key != "legacy_aliases"}
                for option in question["options"]
            ]
        })
    return {
        "definition_version": DEFINITION_VERSION,
        "source": DEFINITION_SOURCE,
        "questions": questions,
    }
