"""Staff PDF A-R answer vocabulary; explicit values, never inferred from scores.

Assessment R uses q19/mna_a12. Historical screening calf fields remain untouched.
"""
from decimal import Decimal


def answers_from_bia(bia):
    """Suggest F/Q/R from saved measurements only; never fill missing data or save."""
    answers = {}
    for field, measurement, boundaries, values in [
        ("q6_bmi", bia.bmi, (19, 21, 23), ("<19", "19-21", "21-23", ">23")),
        ("q19_calf_circumference_assess", bia.cc_cm, (31,), ("<31", ">=31")),
    ]:
        if measurement is not None and Decimal(str(measurement)) > 0:
            index = sum(Decimal(str(measurement)) >= limit for limit in boundaries)
            answers[field] = values[index]
    if bia.mac_cm is not None and Decimal(str(bia.mac_cm)) > 0:
        value = Decimal(str(bia.mac_cm))
        answers["q18_mid_arm_circumference"] = "<21" if value < 21 else "21-22" if value <= 22 else ">22"
    return answers

def item(letter, field, label, options):
    return {"letter": letter, "field": field, "label": label,
            "options": [{"value": value, "label": text} for value, text in options]}


MNA_ITEMS = [
    item("A", "q1_food_intake_decline", "ความอยากอาหาร/ปริมาณการกินลดลงใน 3 เดือนที่ผ่านมา", [("severe", "ลดลงอย่างมาก"), ("moderate", "ลดลงปานกลาง"), ("none", "ไม่ลดลง")]),
    item("B", "q2_weight_loss", "น้ำหนักลดลงใน 3 เดือนที่ผ่านมา", [(">3kg", "ลดลงมากกว่า 3 กก."), ("unknown", "ไม่ทราบ"), ("1-3kg", "ลดลง 1–3 กก."), ("none", "ไม่ลดลง")]),
    item("C", "q3_mobility", "การเคลื่อนไหว", [("bed_chair", "นอนติดเตียง/นั่งรถเข็นตลอด"), ("home_only", "ลุกได้แต่ไม่ออกนอกบ้าน"), ("goes_out", "ออกนอกบ้านได้")]),
    item("D", "q4_stress_illness", "มีความเครียดรุนแรงหรือเจ็บป่วยเฉียบพลันใน 3 เดือนที่ผ่านมา", [("yes", "มี"), ("no", "ไม่มี")]),
    item("E", "q5_neuropsychological", "ปัญหาทางจิตประสาท", [("severe", "สมองเสื่อม/ซึมเศร้ารุนแรง"), ("mild", "สมองเสื่อมเล็กน้อย"), ("none", "ไม่มีปัญหา")]),
    item("F", "q6_bmi", "ดัชนีมวลกาย (กก./ม²)", [("<19", "น้อยกว่า 19"), ("19-21", "19 ถึงน้อยกว่า 21"), ("21-23", "21 ถึงน้อยกว่า 23"), (">23", "23 ขึ้นไป")]),
    item("G", "q8_independent_living", "อาศัยอยู่ได้ด้วยตนเอง (ไม่อยู่สถานดูแลหรือโรงพยาบาล)", [("no", "ไม่ใช่"), ("yes", "ใช่")]),
    item("H", "q9_medications", "ใช้ยาที่แพทย์สั่งมากกว่า 3 ชนิดต่อวัน", [("yes", "ใช่"), ("no", "ไม่ใช่")]),
    item("I", "q10_pressure_sores", "มีแผลกดทับหรือแผลที่ผิวหนัง", [("yes", "มี"), ("no", "ไม่มี")]),
    item("J", "q11_full_meals", "จำนวนมื้ออาหารหลักที่กินได้เต็มมื้อต่อวัน", [("1", "1 มื้อ"), ("2", "2 มื้อ"), ("3", "3 มื้อ")]),
    item("K", "q12_protein_consumption", "ตัวบ่งชี้โปรตีน: นม ≥1 ส่วน/วัน ถั่วหรือไข่ ≥2 ส่วน/สัปดาห์ และเนื้อสัตว์/ปลา/สัตว์ปีกทุกวัน", [("0-1", "ใช่ 0–1 ข้อ"), ("2", "ใช่ 2 ข้อ"), ("3", "ใช่ 3 ข้อ")]),
    item("L", "q13_fruits_vegetables", "กินผักหรือผลไม้อย่างน้อย 2 ส่วนต่อวัน", [("no", "ไม่ใช่"), ("yes", "ใช่")]),
    item("M", "q14_fluid_intake", "ดื่มน้ำหรือเครื่องดื่มต่อวัน", [("<3", "น้อยกว่า 3 แก้ว"), ("3-5", "3–5 แก้ว"), (">5", "มากกว่า 5 แก้ว")]),
    item("N", "q15_eating_independence", "วิธีการกินอาหาร", [("need_help", "ต้องมีผู้ป้อน"), ("self_difficulties", "กินเองได้แต่ลำบาก"), ("self_no_problem", "กินเองได้ ไม่มีปัญหา")]),
    item("O", "q16_self_nutrition", "การรับรู้ภาวะโภชนาการของตนเอง", [("malnourished", "คิดว่าขาดสารอาหาร"), ("uncertain", "ไม่แน่ใจ"), ("well_nourished", "คิดว่าไม่มีปัญหา")]),
    item("P", "q17_health_comparison", "เปรียบเทียบสุขภาพกับคนวัยเดียวกัน", [("worse", "แย่กว่า"), ("unknown", "ไม่ทราบ"), ("same", "เท่ากัน"), ("better", "ดีกว่า")]),
    item("Q", "q18_mid_arm_circumference", "เส้นรอบวงแขน (MAC)", [("<21", "น้อยกว่า 21 ซม."), ("21-22", "21–22 ซม."), (">22", "มากกว่า 22 ซม.")]),
    item("R", "q19_calf_circumference_assess", "เส้นรอบวงน่อง (CC)", [("<31", "น้อยกว่า 31 ซม."), (">=31", "31 ซม. ขึ้นไป")]),
]
