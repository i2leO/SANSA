# SANSA: บริบทสำหรับการ Rework

## 2026-10-09 — Local MNA save feedback and per-item result display

- revised4 MNA rows contain recorded scores but not raw A–R option values. The staff form therefore must not reverse-map scores into invented answers; the stored historical score remains visible until staff completes and saves all 18 answers.
- The MNA form no longer fails silently when incomplete. Native browser validation is bypassed in favor of an explicit application message showing how many of 18 answers are complete; a full local PUT was verified successfully.
- The staff result page now loads the MNA definition and the saved MNA record independently and renders a dedicated A–R answer table with approved labels and `mna_s1..6` / `mna_a1..12` scores. Local verification showed all 18 answer rows after reload.
- This MNA result-table change is local only and was not deployed, per the user's instruction. Production cohort replacement also remains unapplied.

## 2026-10-09 — Single SANSA scoring definition and longitudinal history

- User confirmed that SANSA must use exactly one approved scoring definition: 0/2/4. Assessment revisions preserve changing observations and corrections; they do not select different scoring formulas.
- The cohort remains exactly 200 `respondents`. Repeated measurements are one-to-many child assessment occurrences under the same respondent (the current schema calls these `visits`); they must never create a new respondent or inflate participant counts. Corrections within one occurrence create append-only revisions while the current view selects the latest approved revision.
- Any legacy row not verifiably produced by 0/2/4 is `unverified` and excluded from comparisons; score-only revised4 rows retain explicit provenance and must not be reverse-mapped into invented raw answers.

## 2026-10-08 — Approved SANSA 0/2/4 is the only scoring definition

- ใช้ `EDIT SANSA ONLINE (revised).pdf` หน้า 5–9 เป็นนิยามที่อนุมัติสำหรับคำตอบและคะแนน 0/2/4 ทั้ง 16 ข้อ; `sansa_definition.py` เป็น executable definition กลางที่ backend, API definition และ frontend ใช้ร่วมกัน
- Workbook revised4 เป็นข้อมูลสังเกต ไม่ใช่ codebook; ตรวจ 200 แถวที่มีข้อมูลแล้วพบค่ารายข้อ D2/D3 อยู่ใน 0/2/4 และผลรวมตรงทุกแถว
- ยกเลิกการตีความผลจาก total SANSA แบบเดิม (`normal` / `at_risk` / `malnourished`) สำหรับรายการใหม่ ค่า aggregate ยังอยู่ใน schema เป็นผลรวมเพื่อ audit เท่านั้น ส่วนผลลัพธ์ใช้ Model 3 จาก D2, D3, รอบเอว และกลุ่มอายุ
- ผล 0/2/4 ถือว่า verified ได้เมื่อมีคำตอบดิบครบ 16 ข้อ คำตอบอยู่ในนิยาม คะแนนรายข้อตรงกับนิยาม และ `scoring_version` ตรงกับเวอร์ชันที่อนุมัติ หากข้อใดไม่ผ่าน API จะไม่คำนวณ/แสดง Model 3 จากคะแนนเก่าและจะส่ง issue code ให้หน้าแอดมินแจ้งเหตุ
- ข้อมูลเดิมที่ไม่มีคำตอบดิบห้าม reverse-map จากคะแนนหรือเดาคำตอบ ต้องแสดงว่าไม่สมบูรณ์และรอแหล่งข้อมูลที่ตรวจสอบย้อนกลับได้
- หน้าและ API จัดการ scoring version ไม่อนุญาตให้ activate SANSA เวอร์ชันเก่าหรือแก้ช่วงคะแนนรวม SANSA อีก; เวอร์ชันเก่าเป็นข้อมูล audit เท่านั้น
- Combined export ส่ง `sansa_total_024` เฉพาะรายการที่ผ่าน integrity gate และส่ง `sansa_scoring_status`; ไม่ส่ง legacy result level เป็นผลปัจจุบัน
- local DB ก่อนปรับมี SANSA 241 rows: ปรับคะแนนได้ 4 rows ที่คำตอบครบ และคง 237 rows ที่คำตอบดิบไม่ครบไว้โดยไม่แก้ไข; มี backup ก่อนดำเนินการที่ `backups/sansa_rework_local_before_024_20261008.sql`

## 2026-09-30 — SANSA research export contract

- Export ยึด 4 ชีตใน `Use SANSA Integrated WebApp Data (revised4).xlsx` เป็นสัญญาข้อมูล: `Participant_Data` 45 ฟิลด์, `Prediction` 16 ฟิลด์, `BIA_MNA_Staff` 42 ฟิลด์ และ `Satisfaction` 15 ฟิลด์ โดยชื่อและลำดับหัวคอลัมน์ตรงกับต้นแบบ.
- หน้า Export ดาวน์โหลด CSV แยกตามชุดข้อมูล หรือดาวน์โหลด XLSX รวมที่สร้าง 4 ชีตตามต้นแบบ; `predicted_group` ใช้ค่า `Under`, `Normal`, `Over` ตาม workbook.
- ค่าหมวดหมู่ใน `Participant_Data` ถูกแปลงเป็น research codes ด้วย: Role 1/2, sex 1/2, Education 1–6, Marital_status 1–4, Income 1–4 และ Living_with 1–4; ค่า enum ภายในเช่น `under_10k` ไม่ถูกส่งออก.
- หากยังไม่มีผลทำนายที่บันทึกไว้ Export จะเรียก result service เดิมเพื่อคำนวณแบบ read-only; ถ้าข้อมูล SANSA/BIA/อายุไม่ครบหรือ BIA กำกวม ช่อง Prediction จะว่างและไม่มีการเดาค่า.

> Tasks 5–6 are saved in [TASKS_5_6.md](TASKS_5_6.md). Status: requirements recorded only, pending implementation instruction. Task 5 is not yet completed; Task 6 must reuse it after completion.

## Tasks 3–4 — Prediction engine and storage (completed 2026-09-12)

### Task 3: calculation only

- Added `backend/app/services/sansa_prediction_service.py` and `backend/tests/test_sansa_prediction_service.py`.
- Authoritative function: `predict_sansa_nutrition_status(d2_total, d3_total, waist_cm, age_group01)`; constant `MODEL_VERSION = "SANSA-PRED-1.0"`. Accepts Task 2 outputs; no duplicate domain or age calculation.
- Formula follows Excel revised4 as instructed; task-message operators were rendered as Markdown bullets: `L_OVER = -23.625 + .019*D2 - .377*D3 + .349*waist - 2.336*age_group01`; `L_NORMAL = -9.655 + .039*D2 - .507*D3 + .189*waist - 2.489*age_group01`.
- Under reference logit is 0. Probabilities use max-subtracted softmax to avoid exp overflow; result contains the four inputs, two logits, three probabilities and uppercase group. Tie order follows Excel: UNDER, OVER, NORMAL. Finite numeric inputs and group 0/1 required; engine does not invent clinical input ranges.
- Four focused tests passed, covering Task 2 compatibility, known logits/probabilities, all three winning groups, sums/ranges, age coefficients, numeric boundaries/extreme waist and invalid numbers. Existing SANSA threshold scoring is unchanged.

### Task 4: one-table persistence

- Added Alembic revision `backend/alembic/versions/20260912_01_sansa_prediction_results.py`, `revision=20260912_01`, `down_revision=None` because repository has no existing revision chain. Upgrade creates only `sansa_prediction_results`; downgrade drops only that table (and therefore its prediction data).
- This migration requires existing `visits`; it does not bootstrap the old schema. Inspect the target Alembic revision before deployment if it differs from the supplied dump's empty version table. No production migration was run.
- Modified `backend/app/models.py` only to add `SANSAPredictionResult`, its constraints and `Visit.prediction_results` relationship. Visit columns, existing instruments and scoring tables remain unchanged.
- Fields: id, visit_id, model_version, age_group01, d2_total, d3_total, waist_cm, l_over, l_normal, p_under, p_normal, p_over, predicted_group, created_at, updated_at.
- Types: inputs DECIMAL(12,4), logits DECIMAL(24,12), probabilities DECIMAL(18,16); category ENUM UNDER/NORMAL/OVER; timestamps have database creation defaults and storage/ORM update handling. Unique `(visit_id, model_version)`, FK to visits with delete cascade, checks for group 0/1 and probabilities within [0,1].
- Added `backend/app/services/sansa_prediction_storage.py::save_sansa_prediction(db, visit_id, *, d2_total, d3_total, waist_cm, age_group01)`. Calls Task 3 engine, locks existing parent visit and result via SELECT FOR UPDATE, inserts or updates current model version, flushes and refreshes. **Caller must commit on success or rollback on failure**. Does not accept arbitrary model version labels for this fixed engine. Rejects source inputs outside DECIMAL(12,4) precision rather than silently rounding.
- Added `backend/tests/test_sansa_prediction_storage.py`: six tests cover migrated-table persistence, ORM relationship, values/category roundtrip, upsert identity, unique key and independent versions, DB foreign key/category validation, missing visit/precision rejection, and scoped migration downgrade.
- Validation: from backend, `DATABASE_URL=sqlite:// DEBUG=False /private/tmp/sansa-task4-venv/bin/python -m unittest discover -s tests -p 'test_sansa_prediction*.py' -v`: **10 tests passed** (Task 3: 4; Task 4: 6). SQLite in-memory fixtures only. MySQL migration/ORM DDL compiled successfully without connection; git diff whitespace check passed.
- Test dependencies installed only in temporary venv using repository-pinned SQLAlchemy/Alembic/Pydantic/settings versions. No dependency manifest was changed or upgraded.
- Limitations: no live MariaDB roundtrip or concurrent-writer test; SQLite does not exercise MySQL row locks or fixed-point storage semantics. Probability roundtrips use tolerance, not exact sum equality after persistence. Existing BIA-record selection/authority remains unresolved; caller must supply the chosen waist. No API/UI integration, reporting or analytics was added.
- Rollback: remove new services/tests, reverse only the model relationship/class additions; if applied later, this revision's downgrade removes prediction storage only. Retain a backup before discarding stored predictions.

## Task 2 — SANSA domain score engine (completed 2026-09-12)

- Authorization: implement domain sums and derived respondent age group only; Excel revised4 is the reference. No questionnaire redesign, prediction, migrations, API/frontend changes or deployment.
- Added `backend/app/services/sansa_domain_service.py`: `calculate_sansa_domain_scores(response)` accepts the existing SANSAResponse and returns Decimal values under `d1_total`, `d2_total`, `d3_total`. This is the single domain-sum implementation; existing questionnaire rescoring remains unchanged.
- Mapping: meal/intake/type = `q5_score/q6_score/q7_score`; rice-starch/meat-egg/milk/fruit/vegetable/water = `q8_score/q9_score/q10_score/q11_score/q12_score/q13_score`; sweet-drink/cooking-method/oil = `q14_score/q15_score/q16_score`. All terms are added, not subtracted. Q1–Q4 screening scores are excluded.
- `age_group01(respondent)` reads existing `Respondent.age`: <70 returns 0; >=70 returns 1. No duplicated age or stored derived fields.
- Missing score/age raises ValueError rather than silently treating missing data as zero. Numeric zero remains valid. Functions do not mutate their inputs or access the database.
- Added `backend/tests/test_sansa_domain_service.py`. Run from backend: `python3 -m unittest discover -s tests -p test_sansa_domain_service.py -v`. Result: 7 tests passed, covering D1/D2/D3, screening exclusion, zero/Decimal arithmetic, input preservation, age 69/70/85 and missing values. Synthetic attribute-based records; no ORM/DB/API integration test or broad suite was run.
- Waist: existing source is `BIARecord.waist_circumference_cm`, but authority/selection among multiple BIA records per visit is not yet confirmed. No waist function/field was added and this does not block Task 2.
- Rollback: remove the two newly added Python files; no existing runtime caller or database state was changed. Consumers can import these functions in a later authorized task.
- Confirmed product decision retained for later tasks: admin-issued personal QR with a random secret, no device lock; users keep their own QR private. Not implemented in Task 2.


> อัปเดต 12 กันยายน 2026: อ่าน [LIVE_DATA_CONTEXT.md](LIVE_DATA_CONTEXT.md) ก่อนสำหรับผลเทียบเว็บจริง, SQL และ Excel revised4 ข้อความด้านล่างเป็นผลตรวจ Git รอบแรก ไม่ใช่การยืนยันว่า production ใช้โค้ดเดียวกัน สถานะ “ยังไม่ได้ตรวจ workbook/browser” ในส่วน 7 หมายถึงรอบแรกเท่านั้น

วันที่ตรวจ: 11 กันยายน 2026  
Repository: https://github.com/i2leO/SANSA  
Branch: `main`  
Commit: `8e034536cce40b00a3dee37af85d759dc2818ad5` (`Last Update`)

## 1. เป้าหมายและขอบเขต

ผู้ใช้ต้องการให้ตรวจและทำความเข้าใจ repository ก่อนเริ่ม rework และสร้างเอกสารอ้างอิงสำหรับ agent รอบถัดไป ขณะนี้ยังไม่ได้ระบุว่าต้องการเปลี่ยน UX, business logic, schema หรือ deployment มากน้อยเพียงใด

Workspace เดิมว่าง จึง clone repository ที่ระบุลง `/Users/dev/Documents/SANSA` การตรวจรอบนี้อ่าน source/config/documentation และตรวจ logic บางส่วนด้วยข้อมูลจำลอง ไม่ได้แก้ application code, เชื่อมฐานข้อมูล, import ข้อมูล, commit หรือ push

นี่คือ implementation review ไม่ใช่การรับรองความถูกต้องทางคลินิกของแบบประเมิน และไม่ใช่ผลทดสอบระบบ production

## 2. ภาพรวมระบบ

SANSA เป็นระบบเก็บข้อมูลวิจัยด้านโภชนาการภาษาไทย รองรับผู้สูงอายุ/ผู้ดูแลและเจ้าหน้าที่ มีรหัสผู้เข้าร่วม ข้อมูลทั่วไป การประเมินหลายเครื่องมือ บันทึกอาหาร เนื้อหาความรู้ สถานบริการ และ CSV สำหรับงานวิเคราะห์

| ชั้นระบบ | เทคโนโลยี/ตำแหน่ง |
| --- | --- |
| UI | React 18, TypeScript, Vite 5, Tailwind CSS; `frontend/src/pages/` |
| Form/state | React Hook Form, Zod, Zustand; `frontend/src/stores/` |
| API client | Axios และ token refresh interceptor; `frontend/src/lib/api.ts` |
| API | FastAPI 0.109, Pydantic 2.5; `backend/app/main.py` |
| Persistence | SQLAlchemy 2.0, PyMySQL, MySQL; `backend/app/database.py` |
| Authentication | JWT access/refresh และ bcrypt; `backend/app/auth.py` |
| Schema migration | มี Alembic config แต่ไม่มี revision ที่ tracked |
| Export | Python CSV writer; `backend/app/services/export_service.py` |
| Upload | local filesystem เปิดผ่าน `/uploads` |

ไม่พบ `.openai/hosting.json` หรือ GitHub Actions workflow ใน checkout ที่ตรวจ เอกสารอ้าง SQLModel แต่ implementation หลักใช้ SQLAlchemy declarative models

## 3. เส้นทางใช้งานจริง

ผู้เข้าร่วม: `/` → `/start` → `/general-info/:respondentCode` → `/sansa/:respondentCode` → `/mna/:visitId` → `/bia/:visitId` → `/satisfaction/:visitId` → `/result/:visitId`

- `/start` สร้างรหัสใหม่ ตรวจรหัสเดิม และมี QR flow
- GeneralInfo บันทึก demographics และตรวจ/สร้าง visit; SANSA ตรวจ/สร้าง visit อีกจุดหนึ่ง จึงต้องทบทวนการเลือก visit และการส่งซ้ำเมื่อ rework
- หน้า Result อ่าน SANSA ผ่าน `/sansa/visit/{visitId}`
- `/visit/:visitId/result` redirect ไป `/result/:visitId`
- เส้นทางเสริม: `/food-diary/:respondentCode`, `/knowledge`, `/facilities`
- ผู้ดูแลเข้าสู่ `/admin/login`; ส่วน admin มี dashboard, respondents/detail, results, exports, knowledge, facilities, scoring, users
- Role ฝั่ง backend คือ admin และ staff; ผู้เข้าร่วมไม่ได้มี account role ใน User model

หลักฐาน: `frontend/src/App.tsx`, `frontend/src/pages/admin/AdminRoutes.tsx` และ submit handlers ในแต่ละหน้า Flow ปัจจุบันผ่าน MNA/BIA ก่อนผลลัพธ์ ต่างจากคำอธิบายบางส่วนใน README

## 4. โครงสร้างข้อมูล

`Respondent` → `Visit` → responses/records เป็นแกนหลัก โดย visit มีชนิด baseline/follow_up/final และอ้าง facility กับผู้สร้าง

| กลุ่ม | ตาราง/รายละเอียด |
| --- | --- |
| ผู้ใช้ | `users`: admin/staff, active status, password hash |
| ผู้เข้าร่วม | `respondents`: unique code, demographics, JSON income/disease fields, optional phone/email, legacy fields, soft delete |
| รอบเก็บข้อมูล | `visits`: respondent, visit number/date/type, facility |
| SANSA | `sansa_responses`: 16 คำตอบและคะแนนรายข้อ รวม screening/diet/total, result level, scoring version |
| MNA | `mna_responses`: 18 ช่องคำตอบ, `mna_s1..s7`, `mna_a1..a11`, totals, category, scoring version |
| BIA | `bia_records`: anthropometry/body composition และค่าที่คำนวณ |
| ความพึงพอใจ | `satisfaction_responses`: 7 ข้อและ comments |
| อาหาร | `food_diary_entries` → `food_diary_photos` |
| เนื้อหา | `knowledge_posts`, `facilities` |
| เกณฑ์คะแนน | `scoring_rule_versions`, `scoring_rules`, `scoring_rule_values` |
| Audit | `audit_log` มี model แต่ไม่พบการใช้ `AuditLog` ใน active routers/services |

SANSA/MNA/satisfaction ใช้คอลัมน์คำตอบโดยตรง ไม่ใช่ response + item tables ตามเอกสารเดิมบางหน้า ต้องใช้ `backend/app/models.py` และ `schemas.py` เป็นฐาน แล้วเทียบกับฐานข้อมูลจริงก่อน migration

ข้อมูลผู้เข้าร่วมมีช่องติดต่อได้ จึงไม่ควรถือว่าทุก record เป็น anonymous โดยสมบูรณ์ และไม่ควรนำข้อมูลจริงมาใส่เอกสารนี้

## 5. แผนที่ API

Router ที่ mount จริงอยู่ใน `backend/app/main.py`:

- `/auth`: login, refresh, me, register, user management
- `/respondents`, `/visits`: ผู้เข้าร่วมและรอบประเมิน
- `/sansa`, `/mna`, `/bia`, `/satisfaction`: instruments
- `/food-diary`: entries/photos
- `/knowledge`, `/facilities`: เนื้อหาและสถานบริการ
- `/scoring`: อ่าน/แก้ threshold values และ activate versions
- `/exports`: `sansa.csv`, `mna.csv`, `bia.csv`, `satisfaction.csv`, `combined.csv` โดย staff/admin

Authentication แตกต่างกันตาม endpoint; ไม่ควรสรุปว่า endpoint ใต้ instrument ทั้งหมดถูกป้องกันเพราะบาง operation ต้อง login

## 6. ข้อค้นพบที่ควรจัดลำดับก่อน Rework

### สูง: ความถูกต้องของคะแนนและข้อมูลวิจัย

1. **MNA field mapping ไม่ตรง schema** — `calculate_mna_score()` ใน `backend/app/services/scoring_service.py` ใช้ชื่อ เช่น `q4_psychological_stress`, `q5_neuropsychological_problems`, `q6_bmi_or_calf`, `q7_independent_living` แต่ schema/router/model ใช้ `q4_stress_illness`, `q5_neuropsychological`, `q6_bmi`, `q7_calf_circumference` และมีความต่างต่อเนื่องใน assessment fields การใช้ `getattr(..., None)` ทำให้ข้อมูลที่ชื่อไม่ตรงกลายเป็นคะแนน 0 เงียบ ๆ
2. **MNA screening/category ขัดกันภายในโค้ด** — เมื่อ screening > 11 จะข้าม assessment แต่ยังใช้ threshold total 24/17 ในการจัดกลุ่ม อีกทั้ง comment ระบุ screening max 14 แต่ map Q1–Q7 รวมค่าสูงสุดได้ 17 ต้องตกลง specification ของแบบประเมินก่อนแก้ ไม่ควรเลือกเกณฑ์เอง
3. **Scoring configuration ไม่ได้ควบคุม calculation ปัจจุบันเต็มรูปแบบ** — SANSA/MNA calculation ใช้ maps/thresholds ในโค้ดและ default version 1; MNA create ส่ง version 1 โดยตรง แม้มี helper อ่าน active version และ admin API แก้ thresholds ต้องเชื่อม version กับสูตร/เกณฑ์จริงและรักษาผลย้อนหลัง
4. **CSV ทำคะแนน 0 หาย** — `export_service.py` มีรูปแบบ `float(value) if value else ""` ในคะแนน MNA และ combined totals ทำให้ศูนย์กลายเป็น missing ต้องใช้การแยก `None` ออกจาก 0 พร้อม regression case
5. **Combined export เลือก BIA ด้วย `.first()`** — model รองรับหลาย records ต่อ visit จึงควรกำหนดว่าจะใช้ครั้งแรก ล่าสุด หรือทุกครั้ง และกำหนดลำดับให้แน่นอน

### สูง: Authentication และสิทธิ์ข้อมูล

6. **JWT secret ถูก print ใน debug log** — `backend/app/auth.py::decode_token` print signing secret, token บางส่วนและ payload ควรถอดออกก่อนใช้งานจริง และประเมินการเปลี่ยน secret หาก deployment เคยใช้โค้ดนี้ ไม่ได้ตรวจ production logs ในรอบนี้
7. **Refresh request contract ไม่ตรงกัน** — Axios ส่ง JSON `{refresh_token: ...}` แต่ `backend/app/routers/auth.py` รับ scalar `refresh_token: str` ซึ่งเป็น query parameter ตาม signature ปัจจุบัน ต้องปรับ contract ให้ตรงและทดสอบ token expiry
8. **ไม่ตรวจ token type ตอน decode** — token creator ใส่ `type` แต่ `decode_token` ไม่บังคับ access/refresh ตาม operation
9. **ขาด ownership check ในบาง endpoint** — ตัวอย่าง `PUT /respondents/{id}` ใช้ optional auth แล้วแก้ record ตาม ID; instrument reads และ food diary หลาย operation เปิดให้เรียกโดยไม่มีผู้ใช้ยืนยันตัวตน ต้องออกแบบ respondent session/สิทธิ์ต่อ visit ที่รองรับ self-service ได้จริง
10. **Food photo upload ไม่ใช้ข้อจำกัดที่ประกาศไว้** — `food_diary.py` อ่านไฟล์ทั้งก้อนและใช้ extension ที่ส่งมา โดยไม่มี size/type validation ก่อน write ใน handler ที่ตรวจ และใช้ path `uploads/food_diary` ตายตัวแทน `UPLOAD_DIR`

### กลาง: ความพร้อมในการพัฒนาและบำรุงรักษา

11. **Migration baseline หาย** — tracked `backend/alembic/` มีเพียง `env.py` และ `script.py.mako`; คำสั่ง setup ที่อ้าง `alembic upgrade head` จึงไม่เพียงพอสร้าง schema ใหม่
12. **Frontend TypeScript config น่าสงสัย** — lockfile ระบุ TypeScript 5.9.3 แต่ `tsconfig.json` ตั้ง `ignoreDeprecations: "6.0"`; ต้องยืนยันด้วย build หลังติดตั้ง dependencies ยังไม่ได้รัน build รอบนี้
13. **Legacy files ยังอยู่ใต้ source** — `*_old.py`, `*_old.tsx` รวมถึง old pages ที่อยู่ใต้ TypeScript `include: ["src"]` อาจยังถูกตรวจโดย compiler แม้ router ไม่ import
14. **Audit trail ยังไม่ครบตาม README** — พบ table model แต่ไม่พบ code เขียน `AuditLog` ใน active app จากการค้น source
15. **Testing baseline จำกัด** — มี manual checklist/API requests และ DB connection script แต่ไม่พบชุด automated regression tests ของ scoring/API/UI ที่ครอบคลุม; frontend ไม่มี test script
16. **ค่า config ผูกกับเครื่องพัฒนาเดิม** — default DB URL เป็น MAMP socket บน macOS และมี development credentials/secret defaults ต้องใช้ environment ของเครื่องเป้าหมาย

รายการนี้เป็นข้อค้นพบจาก source ไม่ใช่ผล penetration test หรือการยืนยันว่าข้อมูล production ได้รับผลกระทบแล้ว

## 7. สถานะการตรวจสอบ

ทำแล้ว:

- ตรวจ branch/commit และ active entry points ทั้ง frontend/backend
- อ่าน models, schemas, routers หลัก, auth, scoring, export, config และ setup scripts
- ตรวจ Python syntax ด้วย `ast.parse` ครบ 61 ไฟล์: ผ่านทั้งหมด โดยไม่ import app หรือเปิด DB connection
- ทดลองแยกเฉพาะสอง method ของ MNA scoring จาก AST ด้วย synthetic object ที่ใช้ชื่อ field จาก `MNAResponseCreate`: ตั้งค่า field จำลองเป็น string `2` พบ `mna_s4..mna_s7 = 0` และ total = 6 ยืนยันอาการ mapping fallback ใน logic ที่แยกทดสอบ

ยังไม่ได้ทำ:

- ติดตั้ง dependencies หรือรัน frontend build/lint
- รัน backend API, pytest integration, MySQL, browser flow หรือทดสอบ deployment
- ตรวจเนื้อหาข้อมูลรายบุคคลใน workbook/JSON backup หรือเทียบกับฐานข้อมูลจริง
- ยืนยัน scoring ตามต้นฉบับเครื่องมือวิจัย

การทดลอง MNA ไม่ใช่การ validate Pydantic/API end-to-end และค่า synthetic ไม่ได้อ้างว่าเป็นคำตอบที่ถูกต้องตามเครื่องมือทุกข้อ

## 8. แนวทางเริ่มพัฒนารอบถัดไป

1. ระบุเป้าหมาย rework และ acceptance criteria ของ flow ที่ต้องการเปลี่ยน
2. เตรียมฐานข้อมูลทดสอบแยกและยืนยัน schema baseline ก่อน seed/import; ตรวจ script ก่อนใช้ โดยเฉพาะ recreate/cleanup/reset
3. ยืนยันข้อคำถาม mapping สูตร scoring และ expected results จาก specification ที่เจ้าของงานอนุมัติ
4. เพิ่ม regression cases สำหรับ mapping, score boundaries, unknown/missing answers, score 0 ใน CSV และ token refresh/ownership
5. แก้ data correctness และ authentication ที่เกี่ยวข้องก่อน refactor โครงสร้างใหญ่
6. ค่อยปรับ UI/components, แยก API/domain logic และจัดการ legacy source ตามขอบเขตงาน
7. เทียบ raw answers, totals, categories, versions, respondent/visit IDs และ CSV ก่อน/หลังด้วยข้อมูลจำลองหรือข้อมูลทดสอบที่ได้รับอนุญาต

คำสั่งอ้างอิงสำหรับสภาพแวดล้อมทดสอบ เมื่อเตรียม config/database แล้ว:

```bash
# frontend
cd frontend
npm ci
npm run build
npm run lint
npm run dev
```

```bash
# backend จาก repository root
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# ตั้งค่า .env และ schema ของฐานข้อมูลทดสอบก่อนเริ่มระบบ
uvicorn app.main:app --reload
```

Frontend ใช้ `VITE_API_URL` (default `http://localhost:8000`); Vite มี `/api` proxy แต่ค่า default ของ client เรียก backend โดยตรง Backend ใช้ `DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_URL`, `UPLOAD_DIR` ผ่าน settings และเปิด `/docs` สำหรับ API docs ส่วน `/health` คืน static status ไม่ได้ทดสอบ DB

## 9. เรื่องที่ต้องทราบเมื่อเริ่มงานจริง

- ต้องการ rework ส่วนใด และมีหน้าตาหรือ flow เป้าหมายหรือไม่
- มีข้อมูลเดิมที่ต้องย้าย/รักษาหรือไม่ และ production ใช้ schema/commit ใด
- specification SANSA/MNA ฉบับที่อนุมัติ และ expected score examples อยู่ที่ไหน
- ผู้เข้าร่วมควรเข้าถึง/แก้ข้อมูลเดิมด้วยรหัสอย่างเดียวหรือมี session เพิ่มเติม
- ปลายทาง deployment และรูปแบบ CSV/codebook ที่ทีมวิจัยต้องใช้งาน

หัวข้อเหล่านี้ยังไม่ใช่ข้อสรุปที่ได้รับอนุมัติ และไม่ขัดขวางการใช้เอกสารนี้เป็นบริบทเริ่มต้น

## 10. เอกสารและไฟล์สำคัญ

- `../AGENTS.md`: จุดเริ่มอ่านและแนวปฏิบัติสำหรับ agent
- `../README.md`, `ARCHITECTURE.md`, `DATABASE_SCHEMA.md`: เอกสารเดิม ต้องเทียบ source ปัจจุบัน
- `../TESTING_CHECKLIST.md`, `../QUICK_START_TESTING.md`, `../api-tests.http`: ตัวช่วย manual verification
- `../backend/docs/`: เอกสาร import และ mapping เดิม ต้องตรวจให้ตรง schema ก่อนใช้
- `../src/`: มี workbook อ้างอิงที่ยังไม่ได้เปิดตรวจข้อมูลในรอบนี้

ปรับปรุงเอกสารนี้เมื่อมีการตัดสินใจ rework หรือแก้ประเด็นแล้ว โดยบันทึก commit/วันที่และหลักฐานการตรวจใหม่


## 2026-09-13 — Tasks 5–6 and local MAMP validation
User authorized implementation and isolated local SQL import/migration. Tasks 5–6 integrated and validated locally: 30 backend tests, 200 cached Excel reference cases, frontend build/lint, synthetic browser save and MySQL upsert passed. Full change log/source decisions/limitations: `TASKS_5_6.md`; local database and startup notes: `LOCAL_TESTING.md`. No VPS changes/deployment.

## 2026-09-13 — Local theme alignment
User authorized frontend visual changes based on the deployed public/admin screenshots and live pages. The first pass updated the homepage, shared admin layout/dashboard, palette and Thai font locally. It did not yet change backend/auth behavior. File log: `THEME_LOCAL_REWORK.md`.

## 2026-09-14 — Menu completion and personal QR access

User clarified that all menu pages and backend behavior must be completed and explicitly chose to include QR in this task. Public knowledge/facilities now use existing database APIs; dashboard has live aggregates; admin listings have pagination/search; participant access uses admin-issued, revocable random QR secrets with ownership checks. The scoring relationship/schema mismatch that caused its menu to return 500 was corrected. Local migration head is `20260913_02`. Validation: 37 backend tests, frontend build, lint with zero errors, local MySQL API checks and browser review of all menus. No VPS deployment. Full details: `THEME_LOCAL_REWORK.md`.
# Customer UI alignment — 2026-09-29

- Food diary now follows the approved daily-meal prototype: date navigation, three-meal progress, meal/snack sections, edit/delete, and copy-from-yesterday.
- Participant results now select existing MISSION and nutrition-media records by revised prediction group (`UNDER`, `NORMAL`, `OVER`). The selection reuses the imported knowledge bundle and does not add a second content store.
- Production deployment remains paused until the customer reviews the local UI.

## 2026-10-02 — Staff workspace and participant visibility requirements

Customer supplied `ฝั่งเจ้าหน้าที่.pdf` (6 pages) as the staff-side target and two annotated participant screenshots. These are UI/authorization requirements, not evidence that the current source already enforces them.

### Staff/admin view

- The PDF is the staff workspace for one participant/visit. It may expose the operational and research detail needed for staff work: participant identity/visit summary, Model 3 result and probabilities, D1/D2/D3, waist and age-group inputs, model intermediates, BIA/reference comparison, general information, and per-question SANSA answers/scores.
- Staff can record the full BIA/body-composition dataset: weight, height, BMI, staff-measured waist, fat mass, body-fat percentage, visceral-fat level, muscle mass, bone mass, body-water percentage, metabolic rate, MAC, and CC.
- Staff can record the complete MNA A-R form, see screening/total progress and scores, and populate F/Q/R from BIA values. The PDF is a layout/permission reference only; approved MNA scoring rules and field mappings remain the authority for calculation and must not be inferred from screenshots.
- These staff capabilities apply to authorized `staff` and `admin` sessions. The backend must enforce them; hiding controls in React alone is not sufficient.

### Participant view

- Hide the complete MNA assessment from participants.
- In the body-composition section, expose only the waist-circumference input required for Model 3; do not expose the staff BIA fields listed above.
- Remove the entire legacy SANSA-score card (screening score, behavior score, total score, and legacy nutrition status).
- Do not display D1, D2, D3, prediction probabilities, model version/intermediates, or the BMI/body-fat reference comparison. Show only the final Model 3 prediction label.
- The customer requested optional per-item explanatory text/recommendations after the prediction. The exact approved message/rule set is still required before implementation; do not invent clinical advice or derive it silently from the PDF.
- Use the requested Thai ordering for the over group: `เสี่ยงเกิน/เกิน` (instead of `เกิน/เสี่ยงเกิน`). Other final labels remain subject to the approved wording list.

### Current-source gaps to address during implementation

- `ResultPage.tsx` currently exposes D1/D2/D3, probabilities, model version, reference results, and the legacy score card to participants, so it does not satisfy the new participant visibility rule.
- `AdminResultPage.tsx` currently presents only a subset of the staff PDF and does not yet provide the consolidated BIA/MNA/general-information/per-answer workspace shown in the reference.
- Public routes currently include `/mna/:visitId` and `/bia/:visitId`; access and navigation must be split so participant sessions cannot read or mutate staff-only MNA/full-BIA data, while waist submission remains scoped to the participant's own visit.
- Instrument routers are mounted behind `require_participant_access`, which verifies ownership but presently treats a valid participant session as sufficient for routes under those routers. Staff-only operations/data therefore need explicit role-aware endpoint separation or dependencies in addition to ownership checks.
- Preserve respondent/visit associations, raw answers, recorded scores, scoring versions, and zero-versus-missing semantics while changing visibility and workflow.

No implementation, schema migration, production change, or historical recalculation was performed when recording this requirement.

## 2026-10-02 — Local implementation of role-separated assessment flow

- Added one QR entry page at `/login` for participants, staff, and admins. Participant QR continues to create a respondent-scoped session; staff/admin QR creates the existing role-bearing access/refresh session and redirects to the admin workspace. Password login remains available at `/admin/login` as an emergency recovery path.
- Added revocable QR credentials for `users`, an admin-only issue/rotate endpoint, and QR generation/download controls on the user-management page. Rotating a staff/admin QR invalidates access and refresh tokens issued from the old QR.
- Participant flow now goes from SANSA to a waist-only page, then to a participant-safe result endpoint. The participant result contract returns only `predicted_group` and readiness; the UI no longer displays legacy SANSA totals/status, D1/D2/D3, probabilities, model version/intermediates, BIA reference, or MNA.
- Full MNA and full BIA APIs now require staff/admin authorization in addition to participant/visit ownership middleware. Admin results link to protected staff MNA and BIA entry pages.
- Added BIA model/schema/form support for `visceral_fat_level`, `mac_cm`, and `cc_cm`. Migrations `20261002_05` and `20261002_06` add missing staff-BIA and user-QR columns conditionally because the reviewed SQL snapshot already contains some research columns absent from earlier Git models.
- Updated the over-group Thai label to `เสี่ยงเกิน/เกิน` in the participant result.
- Validation completed locally: 50 backend tests passed using isolated synthetic SQLite data; frontend lint passed with zero warnings; frontend production build passed. No production database, participant data, deployment, historical score, or import was changed.
## 2026-10-03 - Staff assessment workspace layout

Current repair status and outstanding research-integrity issues are tracked in
[RESEARCH_REPAIR.md](RESEARCH_REPAIR.md). Earlier build-only completion statements
do not establish end-to-end correctness. MNA now rejects missing/unknown answers,
requires all A-R items for a full result, and supplies form options/scores from
an authenticated API definition. Existing history is not automatically rescored.

- The staff/admin visit result page now follows the supplied staff PDF structure: participant summary, Model 3 prediction, five section tabs, equation variables, BIA, MNA, general information, and item-level SANSA answers.
- Staff lookup of respondent demographics for a visit uses the authenticated read-only endpoint `GET /respondents/id/{respondent_id}`.
- Existing participant-facing result restrictions remain unchanged.
- Staff-facing prediction codes are translated as `UNDER` = `เสี่ยงขาด`, `NORMAL` = `ปกติ`, and `OVER` = `เสี่ยงเกิน/เกิน`.
- MNA scoring now consumes the semantic answer codes submitted by the active form. Screening is A-F (maximum 14), while G-R is the assessment portion; the legacy database columns remain unchanged. Existing stored MNA totals are not silently rewritten, and inconsistent historical rows are flagged for staff review/resave.

## 2026-10-04 — Research-integrity repair closure for local review

- The staff workspace now displays participant codes rather than names, translates known stored demographic/SANSA codes through field-specific shared definitions, and marks unsupported historical codes for review instead of inventing labels.
- Full MNA uses A–R with canonical R fields `q19_calf_circumference_assess` and `mna_a12`. New writes resolve an active MNA scoring version; records with missing or non-MNA provenance remain visible as history but read-only and flagged. No historical answers or scores were inferred or recalculated.
- SANSA submissions now require all 16 supported answers and reject missing/unknown values instead of silently scoring them as zero. Duplicate assessment attempts return an explicit failure rather than navigating as though a save succeeded.
- BIA editing reloads and updates the existing visit record. Derived BMI/category come from the backend; clearing weight or height clears the derived values. Visceral-fat export uses its level field, and missing export flags remain blank rather than becoming false zeroes.
- Authentication refresh is single-flight and store-synchronized, including protection against an older refresh overwriting a newer login. Production configuration rejects sample/short JWT secrets, a local MAMP database, or debug mode.
- Validation on 2026-10-04: 59 isolated backend tests passed; frontend production build and lint passed; frontend auth-refresh regressions passed; Python compilation and whitespace checks passed. Browser acceptance is reserved for the user's local review. Deployment remains paused.
- Still requires owner-approved specifications: clinical recommendation text, correction/crosswalk for ambiguous historical provenance, and the exact revised export mapping for legacy `over20k` income values.

## 2026-10-05 — revised4 is the workflow/model authority

- User confirmed that `Use SANSA Integrated WebApp Data (revised4).xlsx` is the sole current authority for workflow and algorithm design. Older application options may remain readable for historical records, but cannot be offered or accepted in a newly completed participant profile.
- Completed profiles now require status, age (60–150), binary sex as defined in revised4, education, marital status, revised four-band monthly income, an explicit income-source response, an explicit disease response, and revised living arrangement. The UI options match the workbook Data Dictionary; removed legacy choices include the old 5,000-baht bands, `over20k`, child/relative-only living categories, salary/deposit-interest income choices, and heart disease.
- Empty income-source and disease lists remain valid because revised4 contains explicit all-zero indicator rows. The UI requires the participant to choose the visible “none” answer so an untouched question cannot be mistaken for an intentional empty list.
- New SANSA submissions require all 16 fields. Satisfaction submissions require all seven Likert answers; the free-text comment remains optional. Model 3 uses only D2, D3, waist circumference in centimetres and AgeGroup01, with the exact workbook equations and model identifier `Model3_Reduced_UnderRef_v1`.
- Staff BIA submission requires the complete measurement set present in revised4. Participant waist remains a separate limited submission. Fields absent from revised4 are no longer shown in the current staff workflow, while their historical database columns remain untouched.
- No historical participant row was deleted, imported, rewritten or rescored. Existing non-revised4 option values are not silently translated into a revised category.

### 2026-10-07 clarification

The owner clarified that revised4 is the collected-data workbook. Its observed item values must not be treated as the questionnaire option/scoring codebook. `Model_Logic` remains evidence for reproducing and checking the supplied Model 3 calculations, while Q1–Q16 answer labels and scoring require the actual instrument specification. Earlier wording that treated observed 0/2/4 values as the complete allowed option set is superseded by this clarification.

The earlier `Code_Self` implementation decision was superseded on 2026-10-08 by the user's explicit approval of the 0/2/4 contract in `EDIT SANSA ONLINE (revised).pdf`, pages 5-9. The field-level comparison is recorded in `SANSA_SCORING_AUDIT.md`.
## 2026-10-07 — SANSA instrument definition decision

- `revised4` is observed research data and Model 3 logic; it is not the 16-item answer codebook.
- The canonical answer choices and per-item scores for new submissions come from `backend/app/services/sansa_definition.py`, version `SANSA_0_2_4_PDF_2026-10-08`, transcribed from `EDIT SANSA ONLINE (revised).pdf`, pages 5-9. Backend validation, backend scoring and the participant form consume this same definition. Historical rows are not automatically rescored or overwritten.
- `backend/app/services/sansa_definition.py` is now the single machine-readable definition used by new-write validation, scoring, and the participant form API.
- Historical answer aliases remain readable for display/scoring compatibility, but new submissions accept canonical codes only. No historical row was recalculated or modified.

## 2026-10-09 — Longitudinal assessment and immutable history

- Cohort identity is `respondents`; the revised4 cohort remains exactly 200 participants. A follow-up creates a new `visits` child row under the same respondent and never creates another participant.
- MNA and BIA current rows represent the latest state for one assessment occurrence. Every successful create/update also appends an immutable snapshot to `assessment_revisions`; delete endpoints reject deletion of research measurements.
- Migration `20261009_10` enforces one BIA row per occurrence and adds revision history. Local pre-migration backup: `backups/sansa_rework_local_before_history_20261009_202520.sql`.
- The local 200-row database was backfilled with 400 baseline snapshots (200 MNA + 200 BIA). The synthetic MNA form test on visit 443 was restored from revised4 record 200; its temporary state remains visible only as the prior revision, while current MNA total is 19 and raw answers remain absent as required by the score-only source.
- Staff UI now provides a longitudinal comparison by occurrence, explicit increased/decreased/unchanged states, full revision snapshots, a controlled “add assessment round” action, and revision-history CSV export.
- SANSA exposes only the approved canonical 0/2/4 scoring definition; legacy SANSA versions cannot be activated from API/UI and are retained only as historical provenance.
- Local verification: 139 isolated backend tests passed, Python compilation passed, frontend production build passed, MySQL local database reports 200 respondents/200 visits/200 BIA/200 MNA, migration head `20261009_10`, 401 revisions total and 400 current snapshots. No VPS deployment was performed.

## 2026-10-10 — revised4 six-sheet provenance and field audit

- Migration `20261009_11` adds immutable import-batch and per-sheet snapshots, stable `source_record_id`, nullable source assessment/staff identifiers, and the workbook SHA-256. Internal database IDs are no longer exported as if they were Excel `record_id`/`assessment_id` values.
- All six workbook sheets are retained: the four populated data sheets plus `Data_Dictionary ` and `Model_Logic`, including cached values and formulas. The 100 template rows remain source evidence and are not imported as participants.
- The local cohort maps exactly from workbook `record_id` 1–200 to respondent codes `R4-0001`–`R4-0200`. Normalized counts are 200 for respondents, visits, SANSA, prediction, BIA, MNA, and satisfaction.
- Corrected the import mapping for marital values 3/4 to `widowed`/`divorced`. `Other` and `Other_text` are preserved independently because revised4 contains text even when its flag is zero.
- A field audit passes for 45 Participant, 16 Prediction, 42 BIA/MNA, and 12 source-authored Satisfaction columns. Formula BMI is compared to the two-decimal operational storage while its original formula/value remains in the snapshot.
- Two source validation exceptions are retained rather than silently coerced: Participant row 52 has `Income_work=4` although the dictionary domain is 0/1; BIA/MNA row 138 has category 1 at total 23.5 although its dictionary rule yields category 2. Operational data follows the approved dictionary, while exact source cells remain auditable.
- Source-empty assessment IDs/dates/staff IDs stay null/blank. No identifier or date was invented. Current record 200 MNA was reconciled to revised4 total 19; the prior value remains in append-only revision history.
- Verification: 141 isolated backend tests passed, frontend production build passed, six-sheet/database/export audit passed, and the provenance backfill was confirmed idempotent at 604 total assessment revisions. Local backup before the migration: `backups/sansa_rework_local_before_history_20261010_072457.sql`. No VPS deployment was performed.
