# SANSA Frontend Integration Testing Checklist

**Date:** February 8, 2026
**Servers Running:**
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:5173

---

## 🔐 Authentication & Admin

### Admin Login (`/admin/login`)
- [ ] เข้าหน้า login ได้
- [ ] Login ด้วย username: `admin` / password: `admin123`
- [ ] ได้ JWT token และเก็บใน localStorage
- [ ] Redirect ไปหน้า Admin Dashboard

### Admin Dashboard (`/admin/*`)
- [ ] แสดงรายการ Respondents (5 records)
- [ ] แสดง navigation menu
- [ ] แสดงสถิติ/ข้อมูลภาพรวม

---

## 👤 Respondent Management

### Create New Respondent
- [ ] สร้าง respondent ใหม่ได้
- [ ] Validation ทำงานถูกต้อง
- [ ] บันทึกข้อมูลลง database
- [ ] ได้ respondent_code สำหรับใช้งาน

### View Respondents List
- [ ] แสดงรายการ 5 respondents ที่ import มา (R001-R005)
- [ ] แสดงข้อมูล: code, age, sex, status
- [ ] คลิกเพื่อดูรายละเอียด
- [ ] Update ข้อมูลได้
- [ ] Delete ได้ (soft delete)

---

## 📝 SANSA Assessment Flow

### Start Assessment (`/start`)
- [ ] หน้า Start แสดงฟอร์มกรอก respondent_code
- [ ] กรอก code ที่มีอยู่แล้ว (เช่น R001)
- [ ] Navigate ไปหน้า General Info

### General Information (`/general-info/:respondentCode`)
- [ ] แสดงข้อมูลผู้สูงอายุที่มีอยู่
- [ ] แก้ไขข้อมูลได้
- [ ] บันทึกและไปหน้าถัดไป

### SANSA Form (`/sansa/:respondentCode`)
- [ ] แสดงคำถาม 16 ข้อ
- [ ] Screening questions (Q1-Q4)
- [ ] Diet questions (Q5-Q16)
- [ ] คำนวณคะแนนอัตโนมัติ
- [ ] บันทึกคำตอบ

### MNA Assessment
- [ ] แสดงคำถาม MNA
- [ ] Screening section (7 questions)
- [ ] Assessment section (11 questions, ถ้าจำเป็น)
- [ ] คำนวณคะแนนทั้งหมด

### BIA Measurement (`/bia/:respondentCode`)
- [ ] กรอกข้อมูล body composition
- [ ] Weight, Height, BMI
- [ ] Fat mass, Muscle mass
- [ ] บันทึกข้อมูล

---

## 📊 Results & Reports

### Result Page (`/result/:visitId`)
- [ ] แสดงผลการประเมิน SANSA
  - Screening total
  - Diet total
  - Total score
  - Risk level (สีเขียว/เหลือง/แดง)
- [ ] แสดงผล MNA
  - Screening total
  - Assessment total
  - Total score
  - Result category (normal/at_risk/malnourished)
  - Advice text (ภาษาไทย)
- [ ] แสดงผล BIA
  - BMI, Body fat %
  - Muscle mass, Visceral fat
- [ ] กราฟ/แผนภูมิแสดงผล
- [ ] คำแนะนำตามผลการประเมิน

### Satisfaction Survey (`/satisfaction/:visitId`)
- [ ] แสดงแบบสอบถามความพึงพอใจ
- [ ] 7 คำถาม (1-5 scale)
- [ ] ช่องใส่ comments
- [ ] บันทึกได้
- [ ] Thai text แสดงถูกต้อง

---

## 🍽️ Food Diary (`/food-diary/:respondentCode`)
- [ ] แสดงรายการมื้ออาหาร
- [ ] เพิ่มรายการอาหารใหม่
- [ ] ระบุมื้อ: เช้า/กลางวัน/เย็น/ว่าง
- [ ] ระบุเวลา
- [ ] บันทึกได้

---

## 📥 Export Functions

### SANSA Export
- [ ] กดปุ่ม Export SANSA CSV
- [ ] ดาวน์โหลดไฟล์ได้
- [ ] ไฟล์มีข้อมูลครบ (5 records)
- [ ] Format ถูกต้อง

### MNA Export
- [ ] กดปุ่ม Export MNA CSV
- [ ] ดาวน์โหลดไฟล์ได้
- [ ] ข้อมูล 48 columns ครบ
- [ ] result_category แสดงถูกต้อง

### BIA Export
- [ ] กดปุ่ม Export BIA CSV
- [ ] ดาวน์โหลดไฟล์ได้
- [ ] ข้อมูล body composition ครบ

### Combined Export
- [ ] กดปุ่ม Export Combined CSV
- [ ] ได้ไฟล์รวมข้อมูลทุกตาราง
- [ ] Foreign keys เชื่อมถูกต้อง

---

## 🌐 UI/UX Testing

### Visual Design
- [ ] Tailwind CSS โหลดถูกต้อง
- [ ] สีสัน layout สวยงาม
- [ ] Responsive บน mobile/tablet
- [ ] Font แสดงภาษาไทยได้

### Navigation
- [ ] Menu/navbar ทำงานได้
- [ ] Back button ทำงาน
- [ ] Breadcrumbs แสดงถูกต้อง

### Loading States
- [ ] แสดง loading indicator เวลาดึงข้อมูล
- [ ] แสดง error messages ถ้ามี
- [ ] Toast notifications ทำงาน

### Form Validation
- [ ] Required fields แสดง error
- [ ] Number validation (age, weight, etc.)
- [ ] Format validation (email, phone)
- [ ] Thai text input ทำงาน

---

## 🔄 Data Flow Testing

### Create New Visit Flow
1. [ ] Start → เลือก respondent
2. [ ] General Info → บันทึก
3. [ ] SANSA Form → ทำแบบทดสอบ
4. [ ] MNA Assessment → ทำแบบทดสอบ
5. [ ] BIA Measurement → กรอกข้อมูล
6. [ ] Result → แสดงผลสรุป
7. [ ] Satisfaction → ทำแบบสอบถาม
8. [ ] Complete → บันทึกทั้งหมด

### View Existing Data
- [ ] เลือก R001 → แสดงข้อมูลที่มี
- [ ] ดู SANSA score (23.0)
- [ ] ดู MNA score (20.0, at_risk)
- [ ] ดู BIA data (weight 72, BMI 26.4)
- [ ] ดู Satisfaction comments (Thai text)

---

## 🧪 Edge Cases & Error Handling

### Error Scenarios
- [ ] Backend ไม่ตอบ → แสดง error
- [ ] Token หมดอายุ → refresh token
- [ ] Invalid input → แสดง validation error
- [ ] 404 respondent → แสดง "Not found"
- [ ] Network timeout → retry mechanism

### Empty States
- [ ] ไม่มี respondents → แสดง empty state
- [ ] ไม่มี food diary → แสดงว่าง
- [ ] ไม่มี visits → แสดงข้อความ

---

## ✅ Backend API Integration (Already Tested)

- ✅ POST /auth/login - Working
- ✅ GET /respondents - 5 records
- ✅ GET /mna/{id}/advice - result_category correct
- ✅ GET /sansa/{id} - scoring correct
- ✅ GET /satisfaction/{id} - Thai text OK
- ✅ GET /bia/{id} - body composition data
- ✅ GET /visits - 5 visits
- ✅ All exports working (CSV)

---

## 🎯 Critical Test Cases

### Priority 1 (Must Work)
1. [ ] Admin login and access dashboard
2. [ ] View existing 5 respondents (R001-R005)
3. [ ] View SANSA results with correct scores
4. [ ] View MNA results with advice text (Thai)
5. [ ] Export all CSVs successfully

### Priority 2 (Important)
1. [ ] Create new respondent
2. [ ] Complete full assessment flow
3. [ ] View results page with all data
4. [ ] Satisfaction survey submission

### Priority 3 (Nice to Have)
1. [ ] Food diary management
2. [ ] Knowledge page content
3. [ ] Mobile responsive design
4. [ ] Dark mode (if implemented)

---

## 📝 Test Data Available

### Respondents (5 records)
- R001: Age 65, Male, MNA=20.0 (at_risk), SANSA=23.0
- R002: Age 72, Female, MNA=21.0 (at_risk), SANSA=34.0
- R003: Age 68, Female, MNA=24.5 (normal), SANSA=27.0
- R004: Age 80, Male, MNA=2.0 (malnourished), SANSA=15.0
- R005: Age 75, Female, MNA=26.0 (normal), SANSA=30.0

### Test Admin Account
- Username: `admin`
- Password: `admin123`

---

## 🐛 Known Issues to Check

1. [ ] MNA result_category was null → **FIXED** (now shows correct category)
2. [ ] BIA schema conflict → **FIXED** (visceral_fat_kg)
3. [ ] SyntaxError in mna.py → **FIXED** (f-string escapes)

---

## 📋 Testing Notes

**Start Testing:** _______________
**Completed:** _______________
**Tested By:** _______________

**Issues Found:**
-
-
-

**Overall Status:** [ ] Pass [ ] Fail [ ] Needs Work

**Comments:**
