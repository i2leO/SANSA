# Excel Import Guide

## ไฟล์ที่ต้องการ

**ไฟล์ Excel**: `ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx`

วางไฟล์ไว้ที่: `/Users/dev/SANSA/backend/`

## Sheets ที่จะ Import

| # | Sheet Name | Target Table | Description |
|---|------------|--------------|-------------|
| 1 | **Demographic** | `respondents` | ข้อมูลประชากรศาสตร์ผู้ตอบแบบสอบถาม |
| 2 | **Self Screen Assess (3)** | `sansa_responses` | แบบประเมินตนเองด้านโภชนาการ (SANSA) |
| 3 | **Satisfaction** | `satisfaction_responses` | ข้อมูลความพึงพอใจ |
| 4 | **MNA** | `mna_responses` | Mini Nutritional Assessment |
| 5 | **BIA** | `bia_records` | Body Composition Analysis |

## Required Columns ในแต่ละ Sheet

### 1. Demographic Sheet
```
- respondent_code (required)
- age
- sex (ชาย/หญิง, male/female, m/f, 1/2)
- education_level
- marital_status
- monthly_income
- occupation
- living_arrangement
```

### 2. Self Screen Assess Sheet (SANSA)
```
- visit_id (required)
- q1_score, q2_score, ..., q16_score
- screening_total
- diet_total
- total_score
- result_level
```

### 3. Satisfaction Sheet
```
- visit_id (required)
- q1, q2, q3, q4, q5, q6, q7 (Likert scale 1-5)
- comments
```

### 4. MNA Sheet ⭐
```
- visit_id (required)
- mna_s1, mna_s2, mna_s3, mna_s4, mna_s5, mna_s6, mna_s7
- mna_screen_total
- mna_a1, mna_a2, mna_a3, mna_a4, mna_a5, mna_a6, mna_a7, mna_a8, mna_a9, mna_a10, mna_a11
- mna_ass_total
- mna_total
- result_category
```

### 5. BIA Sheet
```
- visit_id (required)
- age, sex
- weight_kg, height_cm, bmi
- waist_circumference_cm
- fat_mass_kg, body_fat_percentage
- visceral_fat_kg, muscle_mass_kg
- bone_mass_kg, water_percentage
- metabolic_rate
```

## วิธีการใช้งาน

### Step 1: วางไฟล์ Excel
```bash
# ย้ายไฟล์ไปยัง backend directory
cp "path/to/ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx" /Users/dev/SANSA/backend/
```

### Step 2: รัน Import Script
```bash
cd /Users/dev/SANSA/backend
source venv/bin/activate
python scripts/import_all_excel_sheets.py
```

### Step 3: ตรวจสอบผลลัพธ์
Script จะแสดงผลลัพธ์สำหรับแต่ละ sheet:
- ✅ Imported: จำนวน rows ที่เพิ่มใหม่
- ✅ Updated: จำนวน rows ที่อัพเดท
- ⚠️ Skipped: จำนวน rows ที่ข้าม (มีข้อผิดพลาด)

## Logic การ Import

### Demographic (respondents)
- **Key**: `respondent_code`
- **Logic**: หา respondent_code ที่มีอยู่ → อัพเดท / ไม่มี → สร้างใหม่

### SANSA, Satisfaction, MNA, BIA
- **Key**: `visit_id`
- **Logic**:
  1. ตรวจสอบว่า visit_id มีในตาราง visits หรือไม่
  2. หา record ที่มี visit_id นี้อยู่แล้ว → อัพเดท
  3. ไม่มี → สร้างใหม่
- **ข้อกำหนด**: visit_id ต้องมีในตาราง `visits` ก่อน

## Data Validation

Script จะตรวจสอบและแปลงข้อมูลอัตโนมัติ:

- **Decimal values**: คะแนน, measurements → DECIMAL(10,2)
- **Integer values**: อายุ, Likert scale → INTEGER
- **Sex mapping**:
  - ชาย/male/m/1 → Male
  - หญิง/female/f/2 → Female
- **NULL handling**: ช่องว่างจะเป็น NULL ใน database

## Error Handling

หาก row ใด import ไม่สำเร็จ:
- Script จะข้าม row นั้น
- แสดงข้อความ warning พร้อมเลข row
- ดำเนินการต่อกับ row ถัดไป
- **ไม่มี rollback** - rows ที่สำเร็จจะถูกบันทึก

## ตัวอย่าง Output

```
====================================================================================================
COMPREHENSIVE EXCEL IMPORT
====================================================================================================
Excel file: ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx
Timestamp: 2026-02-08 11:30:00

✅ Excel file loaded successfully
📋 Available sheets: ['Code_Demo', 'Demographic', 'Code_Self', 'Self Screen Assess (3)', ...]

📊 Importing Demographic data: 5 rows
  ✅ Imported: 0, Updated: 5, Skipped: 0

📊 Importing SANSA data: 5 rows
  ✅ Imported: 0, Updated: 5, Skipped: 0

📊 Importing Satisfaction data: 5 rows
  ✅ Imported: 0, Updated: 5, Skipped: 0

📊 Importing MNA data: 5 rows
  ✅ Imported: 5, Updated: 0, Skipped: 0

📊 Importing BIA data: 5 rows
  ✅ Imported: 0, Updated: 5, Skipped: 0

====================================================================================================
IMPORT SUMMARY
====================================================================================================
Total imported: 5
Total updated:  20
Total skipped:  0
====================================================================================================
✅ Import completed successfully
```

## หมายเหตุสำคัญ

1. **visit_id เป็น Foreign Key**:
   - ข้อมูล SANSA, Satisfaction, MNA, BIA ต้องอ้างอิง visit_id ที่มีอยู่ในตาราง `visits`
   - ถ้า visit_id ไม่มี row จะถูกข้าม

2. **Duplicate Handling**:
   - Demographic: อิงจาก `respondent_code`
   - ที่เหลือ: อิงจาก `visit_id` (unique constraint)

3. **NULL Values**:
   - ช่องว่างใน Excel จะถูกแปลงเป็น NULL
   - คอลัมน์ที่ไม่ required สามารถเป็น NULL ได้

4. **Column Name Matching**:
   - MNA Sheet ต้องใช้ชื่อ `mna_s1`, `mna_a1` (ตรงกับ database)
   - ถ้าชื่อไม่ตรงจะ import ค่าเป็น NULL

## Troubleshooting

### ❌ File not found
```
Solution: ตรวจสอบว่าไฟล์อยู่ใน /Users/dev/SANSA/backend/
```

### ❌ Visit ID xxx not found
```
Solution: ตรวจสอบว่า visit_id มีในตาราง visits หรือไม่
Query: SELECT * FROM visits WHERE id = xxx;
```

### ❌ Row skipped (duplicate)
```
Solution: เป็นเรื่องปกติถ้า visit_id ซ้ำ - row เก่าจะถูกอัพเดท
```

### ❌ Column not found in Excel
```
Solution: ตรวจสอบชื่อ columns ใน Excel ให้ตรงตามที่กำหนด
```

## ติดต่อ / สอบถาม

หากพบปัญหาในการ import:
1. ตรวจสอบ error message ที่แสดง
2. ดูรายละเอียดใน row ที่ skipped
3. ตรวจสอบ column names ใน Excel
4. ยืนยันว่า visit_id มีอยู่ในตาราง visits
