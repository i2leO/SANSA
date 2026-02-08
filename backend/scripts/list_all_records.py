"""แสดงข้อมูลทั้งหมดในรูปแบบลิสต์"""

from app.database import SessionLocal
from app.models import *

db = SessionLocal()

try:
    print("=" * 80)
    print("RESPONDENTS (ผู้ตอบแบบสอบถาม)")
    print("=" * 80)
    respondents = db.query(Respondent).all()
    for r in respondents:
        print(
            f"ID={r.id:2d} | Code={r.respondent_code:10s} | Age={r.age:2d} | Sex={r.sex.value:6s} | Status={r.status.value}"
        )

    print("\n" + "=" * 80)
    print("VISITS (การมาพบ)")
    print("=" * 80)
    visits = db.query(Visit).all()
    for v in visits:
        print(
            f"ID={v.id:2d} | Respondent_ID={v.respondent_id:2d} | Date={v.visit_date} | Type={v.visit_type.value}"
        )

    print("\n" + "=" * 80)
    print("MNA RESPONSES (แบบประเมินภาวะโภชนาการ MNA)")
    print("=" * 80)
    mnas = db.query(MNAResponse).all()
    for m in mnas:
        print(
            f"ID={m.id:2d} | Visit_ID={m.visit_id:2d} | Screening={float(m.screening_total):5.1f} | Assessment={float(m.assessment_total):5.1f} | Total={float(m.total_score):5.1f} | Result={m.result_category}"
        )

    print("\n" + "=" * 80)
    print("BIA RECORDS (การวัดองค์ประกอบร่างกาย)")
    print("=" * 80)
    bias = db.query(BIARecord).all()
    for b in bias:
        print(
            f"ID={b.id:2d} | Visit_ID={b.visit_id:2d} | Age={b.age:2d} {b.sex.value:6s} | Weight={float(b.weight_kg):5.1f}kg | BMI={float(b.bmi):5.1f} ({b.bmi_category})"
        )

    print("\n" + "=" * 80)
    print("SATISFACTION RESPONSES (ความพึงพอใจ)")
    print("=" * 80)
    sats = db.query(SatisfactionResponse).all()
    for s in sats:
        avg = (
            s.q1_clarity
            + s.q2_ease_of_use
            + s.q3_confidence
            + s.q4_presentation
            + s.q5_results_display
            + s.q6_usefulness
            + s.q7_overall_satisfaction
        ) / 7.0
        print(
            f"ID={s.id:2d} | Visit_ID={s.visit_id:2d} | Q1-Q7=({s.q1_clarity},{s.q2_ease_of_use},{s.q3_confidence},{s.q4_presentation},{s.q5_results_display},{s.q6_usefulness},{s.q7_overall_satisfaction}) | Avg={avg:.2f}/5.00"
        )

    print("\n" + "=" * 80)
    print(
        f"รวมทั้งหมด: {len(respondents)} Respondents, {len(visits)} Visits, {len(mnas)} MNA, {len(bias)} BIA, {len(sats)} Satisfaction"
    )
    print("=" * 80)

finally:
    db.close()
