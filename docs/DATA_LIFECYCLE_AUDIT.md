# SANSA data lifecycle audit — MNA and BIA

ตรวจจาก active source และฐานข้อมูล local วันที่ 9 ต.ค. 2026 เอกสารนี้อธิบายพฤติกรรมปัจจุบัน ไม่ใช่ข้อกำหนดทางคลินิก และยังไม่ได้ deploy การแก้ไขในรอบนี้

## หน่วยข้อมูลหลัก

- `respondents`: ผู้เข้าร่วมหนึ่งราย ระบุด้วย `respondent_code`
- `assessment_occurrences` (ปัจจุบัน source ใช้ชื่อตาราง `visits`): รอบการเก็บข้อมูลที่เป็นรายการลูกของผู้เข้าร่วมคนเดิม ไม่ใช่ผู้เข้าร่วมใหม่
- `mna_responses`: MNA หนึ่งรายการต่อ visit
- `bia_records`: BIA หนึ่งรายการต่อ visit โดยฐานข้อมูลบังคับ unique
- `assessment_revisions`: snapshot แบบ append-only ของ MNA/BIA ทุกครั้งที่บันทึกสำเร็จ

จำนวน cohort นับจาก `respondents` เท่านั้นและต้องคงเป็น 200 คน ส่วนรอบการประเมินเป็น child records แบบ one-to-many และอาจมากกว่า 200 แถวได้โดยไม่ทำให้จำนวนผู้เข้าร่วมเพิ่ม การแก้ค่าภายในรอบเดิมต้องสร้าง revision ไม่เขียนทับ

## พฤติกรรมเมื่อบันทึก

| เครื่องมือ | ครั้งแรกใน visit | ครั้งต่อไปใน visit เดิม | การบังคับใน DB | ผู้บันทึก |
| --- | --- | --- | --- | --- |
| MNA | `POST /mna` สร้างหนึ่งแถวและ revision | `PUT /mna/{id}` อัปเดต current พร้อม append revision | `visit_id` unique | เก็บ actor ใน `created_by`/revision |
| BIA ฝั่ง staff | `PUT /bia/visit/{visit_id}/staff` สร้างเมื่อยังไม่มี | อัปเดต current พร้อม append revision | `visit_id` unique | เก็บ actor ใน `measured_by`/revision |
| รอบเอวฝั่งผู้เข้าร่วม | สร้าง BIA แบบบางส่วนถ้ายังไม่มี | อัปเดตเฉพาะ `waist_circumference_cm` พร้อม append revision | `visit_id` unique | revision ระบุ participant action |

## MNA fields ที่ใช้งานจริง

### คำตอบดิบ

`q1_food_intake_decline`, `q2_weight_loss`, `q3_mobility`, `q4_stress_illness`, `q5_neuropsychological`, `q6_bmi`, `q8_independent_living`, `q9_medications`, `q10_pressure_sores`, `q11_full_meals`, `q12_protein_consumption`, `q13_fruits_vegetables`, `q14_fluid_intake`, `q15_eating_independence`, `q16_self_nutrition`, `q17_health_comparison`, `q18_mid_arm_circumference`, `q19_calf_circumference_assess`

`q7_calf_circumference` เป็นช่อง historical แยกต่างหากและไม่ได้อยู่ใน A–R ที่หน้า staff ใช้ปัจจุบัน

### คะแนนและผล

- A–F: `mna_s1` ถึง `mna_s6`
- G–R: `mna_a1` ถึง `mna_a12`
- รวม: `mna_screen_total`, `mna_ass_total`, `mna_total`, `result_category`
- provenance: `scoring_version_id`, `entry_mode`, `completed_at`, `created_at`, `updated_at`
- measurement support: `mac_cm`, `cc_cm`

## BIA fields ที่หน้า staff บังคับกรอก

`waist_circumference_cm`, `weight_kg`, `height_cm`, `fat_mass_kg`, `body_fat_percentage`, `visceral_fat_level`, `muscle_mass_kg`, `bone_mass_kg`, `water_percentage`, `metabolic_rate`, `mac_cm`, `cc_cm`

ระบบคำนวณ `bmi` และ `bmi_category` ใหม่จากน้ำหนัก/ส่วนสูง แล้วเก็บ `measured_by`, `created_at`, `updated_at` และ `measurement_date` (เมื่อสร้างใหม่)

ตารางยังมี field ที่หน้า staff นี้ไม่ได้ส่ง ได้แก่ `age`, `sex`, `visceral_fat_kg`, `hip_circumference_cm`, `waist_hip_ratio`, `weight_management`, `food_recommendation`, `staff_signature`, `notes`

## สถานะการปิดช่องว่างใน local

1. ปิดแล้ว: MNA/BIA ทุก write เก็บ immutable snapshot ใน `assessment_revisions`; current table ยังคงให้ระบบอ่านค่าล่าสุดได้ง่าย
2. ปิดแล้ว: revision เก็บ actor, เวลา, action และช่องเหตุผล; MNA create เก็บ `created_by`, BIA เก็บ `measured_by`
3. ปิดแล้ว: migration `20261009_10` บังคับ unique `bia_records.visit_id` และตรวจ duplicate ก่อนสร้าง constraint
4. ปิดแล้ว: ไม่สามารถสร้าง BIA รายการที่สองใน occurrence เดียว; regression test ยืนยันที่ชั้นฐานข้อมูล
5. revised4 มี MNA scores แต่ไม่มี raw A–R answers ห้าม reverse-map คะแนนเป็นคำตอบเพราะหลายคำตอบอาจให้คะแนนเดียวกัน
6. ปิดแล้วใน local: หน้า staff แสดง MNA A–R หลังบันทึก; revised4 แบบ score-only แสดงคะแนนโดยไม่สร้างคำตอบดิบปลอม
7. ปิดแล้วสำหรับ MNA/BIA ด้วย `assessment_revisions`; `AuditLog` เดิมยังใช้กับงาน audit ทั่วไปแยกกัน
8. ปิดบางส่วน: หน้า staff เปิด snapshot ทุก field และ metadata ได้ และส่งออก CSV แบบ long-form ได้; data dictionary รวม unit/source ยังเป็นงานเอกสารต่อยอด ไม่กระทบการรักษาประวัติ

## กติกาที่ใช้ใน implementation local

1. คง `respondents` ที่ 200 คน และเก็บรอบการประเมินเป็น child records แบบ one-to-many ใต้ `respondent_id` เดิม; UI และรายงานจำนวนผู้เข้าร่วมต้องไม่นับ child records เป็นคนใหม่
2. บังคับ unique constraint ให้ BIA `visit_id`
3. ทุก update เก็บ history แบบ append-only: instrument, record id, visit id, snapshot, actor, timestamp, reason และ scoring versionที่อยู่ใน snapshot
4. MNA/BIA current table เก็บสถานะล่าสุด ส่วน history table ใช้ตรวจสอบย้อนหลังและไม่ถูกเขียนทับ
5. หน้า admin แสดงประวัติ revision และมี export `assessment-history.csv`; ค่าเก็บเป็น JSON จึงแยก `null` ออกจาก `0`
6. import score-only ต้องติด provenance และแสดงชัดว่าไม่มี raw answer; ห้ามแสดงว่าเป็นคำตอบที่เจ้าหน้าที่กรอก

## ข้อกำหนดคะแนน SANSA ที่ยืนยัน 9 ต.ค. 2026

- SANSA ใช้นิยามคะแนนที่อนุมัติเพียงชุดเดียวคือ **0/2/4**
- ไม่เปิดให้เลือก สร้าง แก้ หรือ activate นิยามคะแนนหลายเวอร์ชันจากหน้า admin
- revision ของ assessment มีไว้เก็บประวัติคำตอบ/การวัดที่เปลี่ยน ไม่ใช่เก็บสูตรคะแนนหลายชุด
- ทุกคำตอบใหม่ต้องคำนวณจากนิยามกลาง 0/2/4 เดียวกันทั้ง frontend, API, export และการเปรียบเทียบ
- ข้อมูลเก่าที่ไม่มี raw answer จะคงคะแนน 0/2/4 ที่ตรวจสอบได้พร้อม provenance `score_only`; ห้ามเดาคำตอบย้อนจากคะแนน
- ข้อมูลใดที่พิสูจน์ไม่ได้ว่าเป็น 0/2/4 ต้องแยกเป็น `unverified` และไม่นำเข้า comparison จนกว่าจะตรวจสอบได้

## Provenance ของ revised4 ที่ปิดงาน 10 ต.ค. 2026

- `source_import_batches` ระบุชื่อชุดข้อมูล ชื่อไฟล์ hash เวอร์ชัน schema จำนวนแถว และ manifest ของ workbook
- `source_import_sheets` เก็บค่าต้นทางและสูตรของทั้ง 6 ชีตแยกกัน พร้อม hash ต่อชีต
- `respondents.source_record_id` คือรหัส 1–200 จาก Excel; ห้ามใช้ primary key ภายในแทนรหัสต้นทาง
- `visits.source_assessment_id` และ `bia_records.source_staff_id` คงเป็น null เพราะ workbook ไม่มีค่า ห้ามสร้างค่าทดแทน
- ข้อมูล normalized ใช้สำหรับระบบปัจจุบัน ส่วน snapshot และ `assessment_revisions` ใช้ตรวจสอบต้นทาง/ประวัติย้อนหลัง โดยแยก null ออกจากเลขศูนย์
- `scripts/audit_revised4_import.py` เป็น fail-fast audit สำหรับ coverage, counts, snapshots และ field-level export fidelity รวมทั้งตรวจ binary domain และความสัมพันธ์ MNA total/category ทุก record โดยไม่มี record-specific bypass
- วันที่ 10 ต.ค. ลูกค้ายืนยันแก้ revised4 สองจุด: record 52 `Income_work` จาก 4 เป็น 1 และ record 138 `mna_total_cat` จาก 1 เป็น 2; เก็บ workbook/import batch ก่อนแก้ไว้สำหรับ audit และสร้าง provenance batch ใหม่จากไฟล์ที่แก้แล้ว
