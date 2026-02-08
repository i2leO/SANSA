"""
แสดง Mapping ระหว่างชื่อคอลัมน์ Excel และ Database

EXCEL COLUMNS -> DATABASE COLUMNS:

📊 SCREENING SECTION (Questions 1-7):
  mna_s1            -> q1_score
  mna_s2            -> q2_score
  mna_s3            -> q3_score
  mna_s4            -> q4_score
  mna_s5            -> q5_score
  mna_s6            -> q6_score
  mna_s7            -> q7_score
  mna_screen_total  -> screening_total
  mna_scr_cat       -> (ไม่มีในระบบ - อาจเป็น screening_category หรือ derived field)

📝 ASSESSMENT SECTION (Questions 8-18):
  mna_a1            -> q8_score
  mna_a2            -> q9_score
  mna_a3            -> q10_score
  mna_a4            -> q11_score
  mna_a5            -> q12_score
  mna_a6            -> q13_score
  mna_a7            -> q14_score
  mna_a8            -> q15_score
  mna_a9            -> q16_score
  mna_a10           -> q17_score
  mna_a11           -> q18_score
  mna_a12           -> (ไม่มีในระบบ - MNA standard มีแค่ Q1-Q18)
  mna_ass_total     -> assessment_total
  mna_total         -> total_score

⚠️ คำถาม:
1. คุณต้องการให้เปลี่ยนชื่อคอลัมน์ใน Database จาก q1_score -> mna_s1 หรือไม่?
2. หรือคุณต้องการให้ import ข้อมูลจาก Excel ที่มีชื่อคอลัมน์แบบ mna_s1?
3. mna_a12 คืออะไร? (MNA standard มีแค่ 18 questions)

กรุณาบอกผมว่าต้องการอะไร แล้วผมจะทำให้ครับ
"""

print(__doc__)
