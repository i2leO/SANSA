# Step-by-Step Import Instructions

## 📍 Step 1: วางไฟล์ Excel

**วางไฟล์** `ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx` ไว้ที่:

```
/Users/dev/SANSA/src/
```

ตรวจสอบว่าชื่อไฟล์ตรงทุกตัวอักษร (รวมภาษาไทย)

---

## 🔍 Step 2: Preview ข้อมูลจาก Excel

ดูข้อมูลจริงจาก Excel ก่อน import:

```bash
cd /Users/dev/SANSA/backend
source venv/bin/activate
python scripts/preview_excel_data.py
```

**Output ที่ได้:**
- แสดง sheets ทั้งหมดในไฟล์
- แสดง column names ของแต่ละ sheet
- แสดง 3 rows แรกของแต่ละ sheet
- **ตรวจสอบข้อมูลว่าถูกต้อง**

---

## ✅ Step 3: Validate Columns

ตรวจสอบว่า columns ใน Excel ครบถ้วนและถูกต้อง:

```bash
python scripts/validate_excel_columns.py
```

**จะตรวจสอบ:**
- ✅ Required columns (เช่น visit_id, respondent_code)
- ✅ Optional columns ที่มีอยู่
- ⚠️ Columns ที่ขาดหาย
- ℹ️ Columns พิเศษที่จะถูกข้าม

**ต้องผ่าน validation ก่อนถึง import ได้**

---

## 🚀 Step 4: Import ข้อมูลจริง

เมื่อตรวจสอบแล้วว่าข้อมูลถูกต้อง:

```bash
python scripts/import_all_excel_sheets.py
```

**Process:**
1. อ่านไฟล์จาก `/Users/dev/SANSA/src/`
2. Import แต่ละ sheet ตามลำดับ:
   - Demographic → respondents
   - Self Screen Assess → sansa_responses
   - Satisfaction → satisfaction_responses
   - MNA → mna_responses
   - BIA → bia_records

**Output ที่ได้:**
```
📊 Importing Demographic data: 5 rows
  ✅ Imported: 0, Updated: 5, Skipped: 0

📊 Importing SANSA data: 5 rows
  ✅ Imported: 0, Updated: 5, Skipped: 0

📊 Importing MNA data: 5 rows
  ✅ Imported: 5, Updated: 0, Skipped: 0

...

IMPORT SUMMARY
Total imported: 5
Total updated:  20
Total skipped:  0
✅ Import completed successfully
```

---

## 🔄 Step 5: ตรวจสอบข้อมูลใน Database

```bash
python scripts/show_mna_details.py
```

หรือเข้า phpMyAdmin ดูข้อมูลในตาราง

---

## ⚠️ Important Notes

### ข้อมูลที่ Import จะ:
- ✅ อ่านจาก Excel จริง 100%
- ✅ ไม่มีการ mock หรือสร้างข้อมูลปลอม
- ✅ ใช้ค่าจริงจาก columns ใน Excel
- ✅ แปลง data types อัตโนมัติ (Decimal, Integer, Enum)

### กรณี Duplicate:
- **Demographic**: ใช้ `respondent_code` เป็น key → อัพเดทข้อมูล
- **SANSA, Satisfaction, MNA, BIA**: ใช้ `visit_id` → อัพเดทข้อมูล
- ไม่มีการสร้าง duplicate records

### กรณี Error:
- Row ที่มีปัญหาจะถูกข้าม (skip)
- แสดง warning message พร้อมเลข row
- Import ต่อกับ rows ที่เหลือ
- Rows ที่สำเร็จจะถูกบันทึก (ไม่มี rollback)

---

## 📋 Required Columns Summary

### Demographic Sheet
- **Required**: `respondent_code`
- **Optional**: age, sex, education_level, marital_status, monthly_income, occupation, living_arrangement

### Self Screen Assess Sheet
- **Required**: `visit_id`
- **Optional**: q1_score to q16_score, screening_total, diet_total, total_score, result_level

### Satisfaction Sheet
- **Required**: `visit_id`
- **Optional**: q1 to q7, comments

### MNA Sheet ⭐
- **Required**: `visit_id`
- **Optional**: mna_s1 to mna_s7, mna_screen_total, mna_a1 to mna_a11, mna_ass_total, mna_total, result_category

### BIA Sheet
- **Required**: `visit_id`
- **Optional**: age, sex, weight_kg, height_cm, bmi, body composition fields

---

## 🆘 Troubleshooting

### ❌ File not found
```
Solution: ตรวจสอบ path และชื่อไฟล์
Expected: /Users/dev/SANSA/src/ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx
```

### ❌ Column not found
```
Solution: ตรวจสอบชื่อ columns ใน Excel ว่าถูกต้อง
Run: python scripts/validate_excel_columns.py
```

### ❌ Visit ID not found
```
Solution: visit_id ต้องมีในตาราง visits ก่อน
Check: mysql> SELECT * FROM visits;
```

### ⚠️ Data type mismatch
```
Solution: ตรวจสอบว่าค่าใน Excel เป็นตัวเลขหรือข้อความตามที่กำหนด
- Scores: ต้องเป็นตัวเลข (0, 0.5, 1, 2, 3)
- IDs: ต้องเป็นตัวเลข integer
- Text: สามารถเป็นข้อความได้
```

---

## ✨ Quick Commands

```bash
# 1. Preview data
python scripts/preview_excel_data.py

# 2. Validate columns
python scripts/validate_excel_columns.py

# 3. Import (if all OK)
python scripts/import_all_excel_sheets.py

# 4. Check results
python scripts/show_mna_details.py
```

---

**หมายเหตุ**: Script จะนำเข้าข้อมูลจริงจาก Excel เท่านั้น ไม่มีการสร้างหรือ mock ข้อมูลใดๆ
