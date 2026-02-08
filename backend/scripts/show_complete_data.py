"""แสดงข้อมูลทั้งหมดครบทุก assessment"""

from app.database import SessionLocal
from app.models import *

db = SessionLocal()

try:
    print("=" * 90)
    print("SANSA NUTRITION ASSESSMENT SYSTEM - ข้อมูลทั้งหมด")
    print("=" * 90)

    # สรุปจำนวน
    respondents = db.query(Respondent).all()
    visits = db.query(Visit).all()
    sansas = db.query(SANSAResponse).all()
    mnas = db.query(MNAResponse).all()
    bias = db.query(BIARecord).all()
    sats = db.query(SatisfactionResponse).all()

    print(f"\n📊 สรุปจำนวนข้อมูล:")
    print(f"   • Respondents:  {len(respondents):2d} คน")
    print(f"   • Visits:       {len(visits):2d} ครั้ง")
    print(f"   • SANSA:        {len(sansas):2d} รายการ")
    print(f"   • MNA:          {len(mnas):2d} รายการ")
    print(f"   • BIA:          {len(bias):2d} รายการ")
    print(f"   • Satisfaction: {len(sats):2d} รายการ")

    print(f'\n{"=" * 90}')
    print("รายละเอียดแต่ละ VISIT")
    print("=" * 90)

    for visit in visits:
        resp = visit.respondent
        print(
            f"\n🏥 Visit #{visit.id} | Respondent: {resp.respondent_code} | {resp.age}y {resp.sex.value} | Date: {visit.visit_date}"
        )
        print("─" * 90)

        # SANSA
        sansa = db.query(SANSAResponse).filter_by(visit_id=visit.id).first()
        if sansa:
            print(
                f"   🍽️  SANSA: Screening={float(sansa.screening_total):4.1f}, Diet={float(sansa.diet_total):4.1f}, Total={float(sansa.total_score):5.1f} → {sansa.result_level}"
            )
        else:
            print("   🍽️  SANSA: ไม่มีข้อมูล")

        # MNA
        mna = db.query(MNAResponse).filter_by(visit_id=visit.id).first()
        if mna:
            print(
                f"   📋 MNA:   Screening={float(mna.screening_total):4.1f}, Assessment={float(mna.assessment_total):5.1f}, Total={float(mna.total_score):5.1f} → {mna.result_category}"
            )
        else:
            print("   📋 MNA:   ไม่มีข้อมูล")

        # BIA
        bia = db.query(BIARecord).filter_by(visit_id=visit.id).first()
        if bia:
            print(
                f"   ⚖️  BIA:   Weight={float(bia.weight_kg):5.1f}kg, BMI={float(bia.bmi):5.2f} ({bia.bmi_category}), Body Fat={float(bia.body_fat_percentage):5.1f}%"
            )
        else:
            print("   ⚖️  BIA:   ไม่มีข้อมูล")

        # Satisfaction
        sat = db.query(SatisfactionResponse).filter_by(visit_id=visit.id).first()
        if sat:
            avg = (
                sat.q1_clarity
                + sat.q2_ease_of_use
                + sat.q3_confidence
                + sat.q4_presentation
                + sat.q5_results_display
                + sat.q6_usefulness
                + sat.q7_overall_satisfaction
            ) / 7.0
            print(f"   ⭐ Satisfaction: Avg={avg:.2f}/5.00")
        else:
            print("   ⭐ Satisfaction: ไม่มีข้อมูล")

    print(f'\n{"=" * 90}')
    print("✅ ข้อมูลครบถ้วนทุก assessment แล้ว!")
    print("=" * 90)

finally:
    db.close()
