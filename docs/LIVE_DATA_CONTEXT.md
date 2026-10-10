# SANSA — Live / SQL / Excel context

> อัปเดต 8 ต.ค. 2026: ข้อความเดิมด้านล่างเป็นหลักฐานการตรวจ ณ 11–12 ก.ย.
> การตัดสินใจปัจจุบันกำหนดให้ PDF ที่อนุมัติเป็นนิยามคะแนน SANSA 0/2/4
> เพียงชุดเดียว และไม่ใช้ total-score classification เดิมอีกต่อไป ดูหัวข้อวันที่
> 8 ต.ค. ใน `REWORK_CONTEXT.md` สำหรับสถานะการปรับระบบล่าสุด

ตรวจเว็บ 11 ก.ย. 2026; สรุปและตรวจไฟล์ซ้ำ 12 ก.ย. 2026 ใช้เอกสารนี้เป็นจุดเริ่มเพื่อประหยัดการอ่านซ้ำ รายละเอียด Git เดิมอยู่ใน [REWORK_CONTEXT.md](REWORK_CONTEXT.md)

## สถานะงานและข้อสรุปที่ต้องจำ

- ผู้ใช้เคย deploy และนำเข้าข้อมูลจนเกือบเสร็จแล้ว กำลังส่ง requirement หลายส่วน รอบนี้อนุญาตให้ตรวจเปรียบเทียบและเขียน MD ยังไม่ใช่งานแก้ระบบ/import
- **Git, SQL dump และ workbook เป็นคนละ baseline**: Git commit `8e034536cce40b00a3dee37af85d759dc2818ad5`; SQL มี 20 คอลัมน์ instrument ที่ model ใน Git ไม่มี; ยังไม่ยืนยัน commit ของ production
- revised4 มีข้อมูลผู้เข้าร่วมจริง **200 แถว (2–201)** และ template **100 แถว (202–301)** ที่มี record_id/สูตร/หน่วยเตรียมไว้ ห้ามนับ 300 เป็นข้อมูลพร้อม import
- revised4 ใช้ **Model3_Reduced_UnderRef_v1** ทำนาย Under/Normal/Over จาก D2, D3, รอบเอว และกลุ่มอายุ ต่างจาก SANSA total-score thresholds ใน Git
- **ห้าม upsert ด้วยลำดับ record_id โดยอนุมาน**: ทดลองจับคู่ record_id → `RES` + เลข 4 หลัก พบครบ 200 รหัส แต่ข้อมูลอายุต่าง 185 ราย และเพศต่าง 57 ราย เป็นเพียง candidate join ที่ไม่ผ่านการยืนยันตัวบุคคล
- Excel ไม่มี assessment_id/assessment_date สำหรับ 200 แถวจริง ต้องกำหนด identity crosswalk, visit และวันที่ก่อน import; ห้ามใส่วันที่วันนี้เป็นวันที่เก็บข้อมูลโดยอัตโนมัติ
- ตรวจอ่านเท่านั้น: ไม่เปลี่ยนเว็บ, ไม่สร้างผู้เข้าร่วม, ไม่ import SQL, ไม่แก้ workbook, ไม่ deploy/commit/push

## แหล่งข้อมูล

| แหล่ง | ตำแหน่ง/หลักฐาน |
| --- | --- |
| เว็บจริง | https://sansa-ntc.org/ |
| หลังบ้าน | https://sansa-ntc.org/admin/dashboard — เข้าสู่ระบบสำเร็จด้วยบัญชีที่ผู้ใช้ให้ |
| VPS | ผู้ใช้ให้ aaPanel endpoint ที่ IP `143.14.200.128`, port `33373`; รอบนี้ไม่ได้เข้าตรวจ panel/server files/process/config จึงยังไม่ทราบ deployment path และ production commit |
| SQL | `../sansa_db.sql`, 376,173 bytes; header: phpMyAdmin 5.2.3, MariaDB 10.11.10, database `sansa_db`; generation text `Sep 11, 2026 at 07:27 PM` ไม่ระบุ timezone ของข้อความนี้ |
| Excel เป้าหมาย | `../Use SANSA Integrated WebApp Data (revised4).xlsx`, 278,435 bytes |
| Excel เดิม | `../src/ปรับแก้ Test Data THESIS PHASE2 03022026.xlsx`; คนละ layout กับ revised4 ไม่ใช้แทนกัน |

เก็บข้อมูล login ไว้ในข้อความผู้ใช้เดิม ไม่คัดลอกรหัสผ่าน/token ลงเอกสารนี้ SQL dump เป็น snapshot ที่ผู้ใช้ส่ง ไม่ได้พิสูจน์ว่าเหมือน live DB ทุก record แม้ยอดผู้เข้าร่วมจะตรงกัน

SHA-256 ณ การตรวจ:

- SQL: `0a14c3f1f57a50f8552b3d87946ac98cfc189efab1575f99009ba2a195ad0dca`
- revised4: `a7b86eafbdd6ebab4bd6c580def86b216731d1900d592fc50390159dc1b15edc`

## สิ่งที่เห็นบนเว็บจริง

| หน้า | ผลตรวจอ่าน |
| --- | --- |
| Home | ภาษาไทย; flow ข้อมูลทั่วไป → SANSA → MNA → BIA → พึงพอใจ → ผลลัพธ์; มีบันทึกอาหาร ความรู้ สถานบริการ |
| Admin dashboard | 244 ผู้เข้าร่วม, 0 การประเมินวันนี้ ณ เวลาที่เปิด, 1 บทความ, 3 ศูนย์บริการ |
| ผู้เข้าร่วม | 244 รายการ; คอลัมน์รหัส อายุ เพศ ช่องติดต่อ และเปิดรายละเอียด; pagination 10/25/50 ต่อหน้า |
| รายละเอียดผู้เข้าร่วม | เปิด route ได้และเห็น heading/รหัส; ยังไม่ได้ตรวจเนื้อหาหลังโหลดครบหรือผลประเมินรายบุคคลทุกเครื่องมือ |
| ส่งออกข้อมูล | มี SANSA, MNA, BIA, Satisfaction, Combined CSV; ตรวจปุ่ม/endpoint ที่แสดง ไม่ได้ดาวน์โหลดทดสอบ CSV จริง |
| กฎคะแนน | แสดง “ไม่สามารถโหลดกฎการให้คะแนนได้” และ “ไม่พบข้อมูล”; ไม่ได้กดแก้/activate; ยังไม่ทราบสาเหตุจาก server logs |

หน้า Home และ admin navigation สอดคล้องโครงสร้าง Git ในระดับ UI เท่านั้น ไม่ยืนยันว่า backend/scoring เหมือน Git และไม่ได้ submit แบบประเมินเพื่อทดสอบการคำนวณบน production

## SQL: จำนวนและความต่างจาก Git

อ่าน dump แบบ text และ parse VALUES literals โดยไม่ execute SQL ตรวจครบ 16 CREATE TABLE, 15 INSERT statements, รวม 1,360 rows

| ตาราง | rows | คอลัมน์เพิ่มจาก Git model |
| --- | ---: | --- |
| respondents | 244 | ไม่มี |
| visits | 242 | ไม่มี |
| sansa_responses | 240 | `screening_status`, `assessment_result` |
| mna_responses | 208 | `mna_screen_category`, `mna_total_category`, `q19_calf_circumference_assess`, `mna_a12`, `mac_cm`, `cc_cm`, `ref_risk24`, `ref_mal17` |
| bia_records | 207 | `waist_status`, `pbf_cat`, `visceral_fat_level`, `visceral_fat_cat`, `muscle_mass_cat`, `bone_mass_cat`, `water_status` |
| satisfaction_responses | 206 | `total_score`, `mean_score`, `satisfaction_level` |
| scoring_rule_versions / scoring_rule_values | 2 / 6 | ไม่มี |
| facilities / knowledge_posts / users | 3 / 1 / 1 | ไม่มี |
| alembic_version / audit_log / scoring_rules | 0 / 0 / 0 | alembic_version เป็นตาราง migration metadata |
| food_diary_entries / food_diary_photos | 0 / 0 | ไม่มี |

- ไม่พบคอลัมน์ใน Git models ที่หายจาก dump จากการเทียบ **ชื่อคอลัมน์**; ยังไม่ได้ตรวจ type/default/index/constraint equivalence ครบทุกช่อง
- 242 visits ผูกกับ 242 respondents คนละหนึ่ง visit; respondents/visits ไม่มี soft-delete ใน snapshot
- SANSA/MNA/BIA/satisfaction มี visit_id ไม่ซ้ำในแต่ละตาราง และไม่พบ orphan visit_id ในตารางเหล่านี้
- กลุ่มรหัส: `RES` ตามด้วยเลข 4 หลัก 206 คน, `PILOT` ตามด้วยเลข 3 หลัก 30 คน, รูปแบบอื่น 8 คน ไม่ใช่ cohort revised4 200 คนอย่างเดียว
- MNA มี `mna_s1` ครบ 208 rows แต่ `q1_food_intake_decline` มีเพียง 2 rows; `mna_a12` ครบ 208 แต่ `q19_calf_circumference_assess` มี 2 แถว แสดงว่าคะแนนที่นำเข้าไม่ได้มี raw-answer string ครบเสมอ ห้าม recalculation ทับจากช่องคำตอบว่าง
- version id 1 เป็น SANSA และ id 2 เป็น MNA ทั้งคู่ active ใน dump; Git MNA create ส่ง id 1 จึงเป็นจุดต้องตรวจ code บน server ก่อนสรุปผลกระทบ
- มี extra columns ที่ยังว่างทั้งหมด เช่น BIA `bone_mass_cat`, `muscle_mass_cat`, `visceral_fat_cat`, `water_status`; การมี schema ไม่ได้แปลว่า feature มีข้อมูลแล้ว

## Excel revised4: layout และ import mapping

| ชีต/ช่วง | ความหมาย | ปลายทาง/ช่องว่าง |
| --- | --- | --- |
| Participant_Data!A1:AS301 | 45 คอลัมน์; demographics, screening 4, dietary 12, D1–D3, waist | respondents + visits + sansa; รอบเอวปัจจุบันอยู่ BIA ต้องกำหนดแหล่งของ participant waist |
| Prediction!A1:P301 | 16 คอลัมน์; links/สูตร probabilities และ predicted_group | ไม่พบ prediction table หรือ probability/model-input columns ใน SQL/Git ที่ตรวจ |
| BIA_MNA_Staff!A1:AP301 | 42 คอลัมน์; BIA, MNA screening 6 + assessment 12, reference classes | bia_records + mna_responses; `mna_a12` มีใน SQL แต่ไม่มีใน Git |
| Satisfaction!A1:O301 | 15 คอลัมน์; 7 ข้อ, role/comment, total/mean/level | satisfaction_responses; respondent_role ยังไม่มีช่องตรงใน SQL |
| Data_Dictionary !A1:H119 | ชื่อชีตมี **space ท้ายชื่อ**; definitions/codings | ใช้เป็น specification ประกอบ mapping |
| Model_Logic!A1:B14 | สมการ Model 3 และ exclusions | แยกจากคะแนน/เกณฑ์เดิมและผล reference |

Mapping ที่ต้องรักษาความหมาย:

- `Role/age/sex/Education/Marital_status/Income/Living_with` → `status/age/sex/education_level/marital_status/monthly_income/living_arrangement`; numeric codes ต้องแปลงโดย codebook ไม่ cast เป็น enum ตรง ๆ
- `Income_*` → `income_sources` JSON; `DM/HT/DLP/CKD/CA/Other/Other_text` → `chronic_diseases` JSON หลังยืนยัน key conventions
- `scr_bw/scr_app/scr_act/scr_dx` → SANSA Q1–Q4; `ass_meal..ass_oil` → Q5–Q16 ตามลำดับ แต่ Excel เก็บค่าตัวเลข ส่วน Git ใช้ answer strings/maps ต้องยืนยันว่า numeric value เป็นรหัสตัวเลือกหรือคะแนน ห้าม reverse-map เดา
- D1 = `ass_meal + ass_intake + ass_type`; D2 = `ass_rice_starch + ass_meat_egg + ass_milk + ass_fruit + ass_veget + ass_water`; D3 = `ass_sweetdrink + ass_cook + ass_oil`
- `pbf` → `body_fat_percentage`; `vfat_level` → `visceral_fat_level` (SQL เท่านั้น อย่าสลับกับ `visceral_fat_kg`); `tbw` → `water_percentage`; `bmr_kcal` → `metabolic_rate`; `MAC/CC` → `mac_cm/cc_cm`
- `sat_clarity/easy/confident/design/result/benefit/overall` → satisfaction Q1–Q7 ตามลำดับ; `sat_comment` → comments
- `bmi_class_glim`, `pbf_class`, `nutri_ref_class` ต้องคงแยกจาก Prediction และจาก category เดิม แม้มี `bmi_category`/`pbf_cat` ก็ยังไม่พิสูจน์ว่าใช้เกณฑ์เดียวกัน
- import scripts เดิมชี้ workbook THESIS layout เช่น Demographic/Self Screen/BIA/MNA และ hardcoded path จึงไม่รองรับ revised4 โดยอัตโนมัติ

## Model 3 ตาม workbook (ยังไม่ได้นำไปใช้กับเว็บ)

อ้างอิง `Model_Logic!A2:B12`, `Participant_Data!AN1:AS201`, `Prediction!D1:P201`:

```text
AgeGroup01 = 0 สำหรับ 60–69 ปี; 1 สำหรับ >=70 ปี
L_Over   = -23.625 + 0.019*D2 - 0.377*D3 + 0.349*wc_cm - 2.336*AgeGroup01
L_Normal =  -9.655 + 0.039*D2 - 0.507*D3 + 0.189*wc_cm - 2.489*AgeGroup01
denom = 1 + exp(L_Over) + exp(L_Normal)
P_Under = 1/denom; P_Over = exp(L_Over)/denom; P_Normal = exp(L_Normal)/denom
predicted_group = กลุ่มที่มี probability สูงสุด
```

สูตร worksheet ใช้ age<70 เป็น 0; specification ระบุ 60–69 ต้องกำหนด validation อายุ<60 เมื่อนำไปทำระบบ ไม่พบอายุ<60 ใน 200 แถวที่มีข้อมูล หน่วย waist มี cm/inch โดย inch × 2.54; ไฟล์นี้กรอก cm ทั้งหมด เมื่อ probabilities เท่ากันสูตรเลือก Under ก่อน Over ก่อน Normal

Model_Logic ระบุ screening 4 ข้อ, dietary 3 ข้อแรก (D1), BIA/MNA และ satisfaction **ไม่เข้า Model 3** แต่ยังเก็บข้อมูล ดังนั้นจะเปลี่ยน total-score result ของระบบเดิมเป็น predicted_group โดยตรงไม่ได้โดยไม่มีแผน version/history

Reference class ตาม `BIA_MNA_Staff!AN2:AP201` ใช้ BMI ตามอายุ + %fat ตามเพศ ปัดหนึ่งตำแหน่งก่อนตัดเกณฑ์: อายุ<70 BMI<18.5 หรืออายุ>=70 BMI<20 เป็นกลุ่มขาด; BMI>=25 เป็นกลุ่มเกิน; %fat ชาย<15/>25, หญิง<20/>35 เป็นขาด/เกิน ถ้าข้อใดเป็นขาดให้ขาดก่อน มิฉะนั้นถ้าข้อใดเกินให้เกิน ที่เหลือปกติ นี่คือกฎ **ที่อ่านจาก workbook** ไม่ใช่ข้อสรุปทางคลินิกเพิ่มเติม

## ความครบถ้วนและข้อจำกัดของ workbook

- 200 แถวจริงมี input สำหรับ Prediction ครบ; D2/D3 ที่เก็บเป็นค่าคงที่เท่ากับผลรวมรายข้อครบ 200 แถว
- แยกคำนวณ probabilities ใน Python ตามสมการเทียบ cached Excel values ครบ 200 แถว × 3 probabilities: ไม่พบต่างเกิน `1e-10` (maximum delta 0 ในการตรวจนี้) ไม่ใช่การทดสอบ production scoring
- ไม่พบ Excel error cells ใน cached values; ไม่ได้เปิด Excel เพื่อ recalculate/บันทึกใหม่
- assessment_id/date ว่างทั้งหมด; staff_id และ satisfaction respondent_role ว่าง ไม่ควรเดาผู้วัด/ผู้ตอบ
- Satisfaction `sat_mean` และ `sat_level` ว่างทั้ง 300 แถว; `sat_total` มีสูตร SUM ที่ให้ 0 ใน 100 แถว template อย่านำไปสร้าง response ว่าเป็นคะแนน 0 จริง
- พบ `Satisfaction!J202:J301` (sat_benefit) เป็นสูตรรวม E:I ในแถว template ต่างจาก 200 แถวจริงที่เป็น input ต้องแก้ specification/template เมื่อได้รับงานส่วนนี้ ไม่ใช่นำสูตรนั้นมาใช้เป็นคะแนนข้อที่ 6
- Dictionary ใช้ชื่อ `Prob_Normal` แต่ header จริงคือ `P_Normal`; import ควรยึดชื่อที่ตรวจแล้วและมี alias ชัดเจน
- แม้ record_id ไม่ซ้ำทั้ง 300 slots แต่ไม่ได้ทำให้เป็น key ของ DB เดิมได้ และการมี cached IDs ในชีตอื่นไม่ใช่หลักฐานว่ามี observations ครบ 300

## ขั้นถัดไปเมื่อผู้ใช้ส่ง requirement ครบ

1. ยืนยันว่าจะเพิ่ม cohort ใหม่หรือ reconcile cohort เดิม และขอ/กำหนด identity crosswalk ที่ตรวจสอบได้
2. ตรวจ production source/schema/config แบบ read-only เพื่อทราบความต่างจาก Git โดยรักษา existing data; aaPanel ยังไม่ได้ตรวจในรอบนี้
3. สรุป target schema และ mapping สำหรับ Model 3, raw answers/scores, reference classes และ historical versions
4. ทำ dry-run import ในฐานข้อมูลแยก พร้อมรายงาน create/update/skip/conflict ไม่เขียน production จนขอบเขตงานนั้นได้รับอนุญาต
5. ทดสอบสูตร ขอบเขตค่า missing/zero, idempotency, visits และ export ก่อนนำไปใช้งาน

รอบนี้ยังไม่ได้ตรวจ server files, API payload ที่ deploy, exports จริง, database constraints ครบถ้วน หรือทุกหน้าฟอร์ม สิ่งที่ยืนยันแล้วคือหน้าเว็บที่ระบุ, โครงสร้าง/จำนวนใน dump, workbook headers/formulas/cached aggregates และความต่างของชื่อคอลัมน์กับ Git
