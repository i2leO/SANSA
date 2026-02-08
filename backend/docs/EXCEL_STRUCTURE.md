# Excel File Structure

**ไฟล์**: ข้อมูลแบบสอบถาม SANSA MNA BIA.xlsx

## Sheets ทั้งหมด (10 sheets)

### 1. **Code_Demo**
   - รหัสและคำอธิบายสำหรับข้อมูล Demographic
   - ใช้สำหรับ lookup ค่า encoded

### 2. **Demographic**
   - ข้อมูลประชากรศาสตร์ของผู้ตอบแบบสอบถาม
   - เช่น: อายุ, เพศ, การศึกษา, อาชีพ, รายได้, BMI, etc.

### 3. **Code_Self**
   - รหัสและคำอธิบายสำหรับข้อมูล Self Screen Assessment
   - คำตอบของแบบประเมินตนเอง

### 4. **Self Screen Assess (3)**
   - ข้อมูลแบบประเมินตนเองด้านโภชนาการ
   - คำตอบและคะแนนจากการประเมินตนเอง

### 5. **Code_Satisfaction**
   - รหัสและคำอธิบายสำหรับความพึงพอใจ
   - Likert scale และคำตอบอื่นๆ

### 6. **Satisfaction**
   - ข้อมูลความพึงพอใจ
   - คะแนนความพึงพอใจต่อโปรแกรม/บริการ

### 7. **Code_BIA**
   - รหัสและคำอธิบายสำหรับข้อมูล BIA
   - คำอธิบายตัวชี้วัดทางร่างกาย

### 8. **BIA**
   - ข้อมูล Body Composition Analysis
   - น้ำหนัก, ส่วนสูง, มวลกล้ามเนื้อ, ไขมัน, BMI, etc.

### 9. **Code_MNA** ⭐
   - รหัสและคำอธิบายสำหรับแบบประเมิน MNA
   - คำตอบแต่ละข้อพร้อมคะแนน

### 10. **MNA** ⭐ (กำลังทำอยู่)
   - ข้อมูลแบบประเมิน Mini Nutritional Assessment
   - **Columns ที่สำคัญ**:
     - `visit_id` - รหัสการเยี่ยม
     - **Screening (7 คำถาม)**: mna_s1, mna_s2, mna_s3, mna_s4, mna_s5, mna_s6, mna_s7
     - `mna_screen_total` - คะแนนรวม Screening
     - **Assessment (11 คำถาม)**: mna_a1, mna_a2, mna_a3, mna_a4, mna_a5, mna_a6, mna_a7, mna_a8, mna_a9, mna_a10, mna_a11
     - `mna_a12` - คอลัมน์พิเศษ (ไม่ใช้ในการคำนวณ)
     - `mna_ass_total` - คะแนนรวม Assessment
     - `mna_total` - คะแนนรวมทั้งหมด

## โครงสร้างการจัดเก็บ

```
Code Sheets (รหัส)     →    Data Sheets (ข้อมูลจริง)
─────────────────────────────────────────────────
Code_Demo              →    Demographic
Code_Self              →    Self Screen Assess (3)
Code_Satisfaction      →    Satisfaction
Code_BIA               →    BIA
Code_MNA               →    MNA
```

## หมายเหตุ

- **Code sheets**: เก็บคำอธิบายและ mapping ของรหัส
- **Data sheets**: เก็บข้อมูลจริงที่ collect มา
- แต่ละ visit จะมีข้อมูลครบทุก sheet
- ข้อมูลเชื่อมโยงกันด้วย `visit_id` หรือ identifier อื่นๆ

## สถานะปัจจุบัน

✅ **MNA Sheet**: Database structure พร้อมแล้ว - รอ import ข้อมูล
⏳ **Sheets อื่นๆ**: ยังไม่ได้ดำเนินการ
