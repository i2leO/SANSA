"""สร้างข้อมูล Satisfaction ตัวอย่าง"""

from app.database import SessionLocal
from app.models import *

db = SessionLocal()

try:
    # Check current data
    sat_count = db.query(SatisfactionResponse).count()
    print(f"Satisfaction Responses currently: {sat_count}")

    # Get visit without Satisfaction (we can use visit_id=1 since it has SANSA and BIA)
    visit = db.query(Visit).filter(Visit.id == 1).first()

    if visit:
        existing = db.query(SatisfactionResponse).filter_by(visit_id=visit.id).first()
        if existing:
            print(f"Visit {visit.id} already has Satisfaction")
        else:
            print(f"Creating Satisfaction for visit_id={visit.id}")

            # Create Satisfaction response (7 Likert questions, scores 1-5)
            sat = SatisfactionResponse(
                visit_id=visit.id,
                q1_clarity=5,  # ความชัดเจนของคำถาม
                q2_ease_of_use=4,  # ความสะดวกในการใช้งาน
                q3_confidence=4,  # ความมั่นใจในการกรอก
                q4_presentation=5,  # รูปแบบการนำเสนอ
                q5_results_display=4,  # การแสดงผลลัพธ์
                q6_usefulness=5,  # ประโยชน์ที่ได้รับ
                q7_overall_satisfaction=5,  # ความพึงพอใจโดยรวม
                comments="ระบบใช้งานสะดวก ชัดเจน และให้ข้อมูลที่เป็นประโยชน์",
            )
            db.add(sat)
            db.commit()
            print("✓ เพิ่ม Satisfaction response สำเร็จ!")
    else:
        print("ไม่พบ visit_id=1")

finally:
    db.close()
