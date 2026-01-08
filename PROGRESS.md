# SANSA System Implementation Progress

## 📋 Overview

Complete implementation of the SANSA (Self-administered Nutrition Screening and Assessment) system based on 12 pages of requirements documentation.

## ✅ Completed Work

### Phase 1: Database & Backend (95% Complete)

#### 1.1 Database Models ✅

**File**: `/Users/dev/SANSA/backend/app/models.py`

- **Respondent Model** (Expanded):

  - Added `status` field (elderly/caregiver enum)
  - Added 10 general information fields:
    - `age`, `sex`, `education_level`, `marital_status`
    - `monthly_income`, `income_sources` (JSON array)
    - `chronic_diseases` (JSON object with "other" field)
    - `living_arrangement`

- **SANSAResponse Model** (Complete Rewrite):

  - Changed from items-based to column-based approach
  - 16 individual question columns (q1-q16):
    - Q1-Q4: Screening questions with scores
    - Q5-Q16: Dietary questions with scores
  - Automatic score columns for each question
  - `screening_total`, `diet_total`, `total_score`
  - `result_level` (normal/at_risk/malnourished)

- **SatisfactionResponse Model** (New):

  - 7 Likert-scale question columns (q1-q7)
  - 5-point scale (1-5)
  - `comments` field for open feedback
  - `completed_at` timestamp

- **MNAResponse Model** (New):

  - 18 question columns (q1-q18) with scores
  - Screening section (Q1-Q7): Max 14 points
  - Assessment section (Q8-Q18): Max 16 points (conditional)
  - `screening_total`, `assessment_total`, `total_score`
  - `result_category` (normal/at_risk/malnourished)
  - Implements conditional logic: assessment only if screening ≤ 11

- **BIARecord Model** (New):
  - Basic measurements: age, sex, waist circumference
  - Weight/height with auto-BMI calculation
  - Body composition fields:
    - Fat mass (kg), body fat (%), visceral fat (kg)
    - Muscle mass (kg), bone mass (kg)
    - Water percentage, metabolic rate
  - `bmi_category` (Asian-Pacific thresholds)
  - Recommendations: weight management, food advice
  - Staff signature and measurement date

**Backup**: All old files saved with `_old` suffix

#### 1.2 Scoring Service ✅

**File**: `/Users/dev/SANSA/backend/app/services/scoring_service.py`

- **SANSA Scoring**:

  - Complete scoring maps for all 16 questions
  - `calculate_sansa_question_score()`: Maps answers to scores
  - `calculate_sansa_scores()`: Returns screening, diet, total, and result level
  - Thresholds: Normal ≥38, At-risk 25-37, Malnourished 0-24
  - Total range: 0-56 points

- **MNA Scoring**:

  - Complete scoring maps for all 18 questions
  - `calculate_mna_question_score()`: Supports decimal scores (0.5)
  - `calculate_mna_score()`: Conditional assessment (only if screening ≤11)
  - Thresholds: Normal 24-30, At-risk 17-23.5, Malnourished <17
  - Total range: 0-30 points

- **BMI Classification**:
  - `get_bmi_category()`: Asian-Pacific thresholds
  - Categories: underweight (<18.5), normal (18.5-22.9), overweight (23-24.9), obese I (25-29.9), obese II (≥30)

#### 1.3 Pydantic Schemas ✅

**File**: `/Users/dev/SANSA/backend/app/schemas.py`

- **RespondentCreate/Update/Response**:

  - Added all 10 new fields with proper types
  - `income_sources`: List[str] for multiple selection
  - `chronic_diseases`: dict for diseases with "other" field

- **SANSAResponseCreate/Update/Full**:

  - All 16 question fields (q1_weight_change through q16_oil_coconut)
  - Corresponding score fields in Full schema
  - Screening and diet totals

- **SatisfactionResponseCreate/Update/Full**:

  - 7 Likert question fields (q1_clarity through q7_overall_satisfaction)
  - Comments field (optional)

- **MNAResponseCreate/Update/Full**:

  - All 18 question fields with descriptive names
  - Screening and assessment totals
  - Result category

- **BIARecordCreate/Update/Response**:
  - All body composition fields
  - BMI auto-calculation support
  - Recommendations fields

#### 1.4 API Routers ✅

**SANSA Router** (`/Users/dev/SANSA/backend/app/routers/sansa.py`):

- ✅ POST `/sansa` - Create with auto-scoring
- ✅ GET `/sansa/{id}` - Get by ID
- ✅ GET `/sansa/visit/{visit_id}` - Get by visit
- ✅ PUT `/sansa/{id}` - Update (staff only)
- ✅ DELETE `/sansa/{id}` - Delete (staff only)
- ✅ GET `/sansa/{id}/advice` - Get advice text

**Satisfaction Router** (`/Users/dev/SANSA/backend/app/routers/satisfaction.py`):

- ✅ POST `/satisfaction` - Create survey response
- ✅ GET `/satisfaction/{id}` - Get by ID
- ✅ GET `/satisfaction/visit/{visit_id}` - Get by visit
- ✅ PUT `/satisfaction/{id}` - Update (staff only)
- ✅ DELETE `/satisfaction/{id}` - Delete (staff only)
- ✅ GET `/satisfaction/visit/{visit_id}/summary` - Get average scores

**BIA Router** (`/Users/dev/SANSA/backend/app/routers/bia.py`):

- ✅ POST `/bia` - Create BIA record (staff only)
- ✅ GET `/bia/{id}` - Get by ID
- ✅ GET `/bia/visit/{visit_id}` - Get by visit
- ✅ PUT `/bia/{id}` - Update with BMI recalc (staff only)
- ✅ DELETE `/bia/{id}` - Delete (staff only)
- ✅ GET `/bia/visit/{visit_id}/interpretation` - Get body composition analysis

**MNA Router** (`/Users/dev/SANSA/backend/app/routers/mna.py`):

- ✅ POST `/mna` - Create with auto-scoring
- ✅ GET `/mna/{id}` - Get by ID
- ✅ GET `/mna/visit/{visit_id}` - Get by visit
- ✅ PUT `/mna/{id}` - Update (staff only)
- ✅ DELETE `/mna/{id}` - Delete (staff only)
- ✅ GET `/mna/{id}/advice` - Get advice text

**Main App** (`/Users/dev/SANSA/backend/app/main.py`):

- ✅ Registered all 4 new routers

#### 1.5 Pending Backend Tasks ⏳

- ⏳ **Alembic Migration**: Need to generate migration for new models
  - Blocked: No virtual environment found
  - Command: `alembic revision --autogenerate -m "expand_models_complete_sansa"`
  - Manual alternative: Create migration script from scratch

---

### Phase 2: Frontend User-Facing Forms (100% Complete) ✅

#### 2.1 General Information Page ✅

**File**: `/Users/dev/SANSA/frontend/src/pages/GeneralInfoPage.tsx`

**Features**:

- Beautiful gradient UI (blue-to-indigo)
- All 10 fields from Page 2 requirements
- Status selection: elderly/caregiver (radio buttons)
- Basic demographics: age, sex, education, marital status
- Monthly income dropdown (4 ranges)
- Income sources: Multi-select checkboxes (5 options)
- Chronic diseases: Multi-select checkboxes with "other" text field
- Living arrangement dropdown
- Form validation with proper state management
- Progress indicator: 33% (Step 1 of 3)
- Thai language labels throughout

**Navigation**: → SANSA Form Page

#### 2.2 SANSA Form Page ✅

**File**: `/Users/dev/SANSA/frontend/src/pages/SANSAFormPage.tsx`

**Features**:

- Beautiful gradient UI (green-to-teal)
- Two sections matching documentation:

  **Section 1 - Screening (Q1-Q4)**:

  - Q1: Weight change (ลดลง/คงเดิม/เพิ่มขึ้น)
  - Q2: Food intake (น้อยลง/ปกติ/มากขึ้น)
  - Q3: Daily activities (ไม่ได้/ช้ากว่าปกติ/ปกติ)
  - Q4: Chronic disease (ไม่มี/มี)

  **Section 2 - Dietary (Q5-Q16)**:

  - Q5: Meals per day (แทบไม่ได้/1/2/3/>3)
  - Q6: Portion size (25%/50%/75%/100%/>100%)
  - Q7: Food texture (เหลว/อ่อน/ปกติ)
  - Q8-Q16: Food groups with Thai measurement units (กำปั้น, ฝ่ามือ, แก้ว, etc.)

- Form validation with Zod
- Progress indicator: 66% (Step 2 of 3)
- Thai labels matching exact requirements

**Navigation**: → Satisfaction Survey Page

#### 2.3 Satisfaction Survey Page ✅

**File**: `/Users/dev/SANSA/frontend/src/pages/SatisfactionPage.tsx`

**Features**:

- Beautiful gradient UI (purple-to-pink)
- 7 Likert-scale questions (5 levels: มากที่สุด to น้อยที่สุด):
  - Q1: ความชัดเจนของคำถาม (Question clarity)
  - Q2: ความสะดวกในการใช้งาน (Ease of use)
  - Q3: ความมั่นใจในการกรอกข้อมูล (Confidence)
  - Q4: รูปแบบการนำเสนอ (Presentation)
  - Q5: การแสดงผลลัพธ์ (Results display)
  - Q6: ประโยชน์ที่ได้รับ (Usefulness)
  - Q7: ความพึงพอใจโดยรวม (Overall satisfaction)
- Visual 5-level scale with colors
- Comments textarea for additional feedback
- Skip option available
- Progress indicator: 100% (Step 3 of 3)

**Navigation**: → Result Page

---

### Phase 3: Staff Tools (100% Complete) ✅

#### 3.1 BIA Measurement Page ✅

**File**: `/Users/dev/SANSA/frontend/src/pages/BIAMeasurementPage.tsx`

**Features**:

- Beautiful gradient UI (teal-to-cyan)
- Staff-only tool (requires authentication)
- **Section 1 - Basic Info**:

  - Age, Sex, Waist circumference

  **Section 2 - Basic Measurements**:

  - Weight (kg) - required
  - Height (cm) - required
  - Auto-BMI calculation with color-coded category
  - Asian-Pacific BMI thresholds displayed

  **Section 3 - Body Composition**:

  - Fat mass (kg)
  - Body fat percentage (%)
  - Visceral fat (kg)
  - Muscle mass (kg)
  - Bone mass (kg)
  - Water percentage (%)
  - Metabolic rate (kcal/day)

  **Section 4 - Recommendations**:

  - Weight management (maintain/decrease/increase)
  - Food recommendation (textarea)
  - Staff signature

- Real-time BMI calculation on input change
- Validation for required fields

**Navigation**: Can be accessed from admin/staff dashboard

#### 3.2 MNA Assessment Page ✅

**File**: `/Users/dev/SANSA/frontend/src/pages/MNAAssessmentPage.tsx`

**Features**:

- Beautiful gradient UI (amber-to-orange)
- Implements official MNA protocol
- **Screening Section (Q1-Q7)** - Always shown:

  - Q1: Food intake decline
  - Q2: Weight loss
  - Q3: Mobility
  - Q4: Psychological stress
  - Q5: Neuropsychological problems
  - Q6: BMI or calf circumference
  - Q7: Independent living
  - **Real-time scoring display**

  **Assessment Section (Q8-Q18)** - Conditional:

  - Shows ONLY if screening score ≤ 11
  - Q8-Q18: Detailed nutrition assessment
  - Medications, meals, protein, fluids, self-care
  - Physical measurements (arm/calf circumference)

- Dynamic scoring with instant feedback
- Visual indicator when assessment is required
- Scoring maps with decimal support (0.5 points)
- MNA® official thresholds implemented

**Navigation**: Can be accessed from assessment flow

---

### Phase 4: Infrastructure & Quality (Pending) ⏳

#### 4.1 Export Service Updates ⏳

**File**: `/Users/dev/SANSA/backend/app/services/export_service.py`

**Needed Changes**:

- Add all 10 Respondent fields to CSV export
- Add all 16 SANSA question columns
- Add all 7 satisfaction question columns
- Add BIA measurement columns (body composition)
- Add all 18 MNA question columns
- Ensure SPSS-compatible variable naming
- Update column headers with Thai/English labels

#### 4.2 Seed Data Updates ⏳

**File**: `/Users/dev/SANSA/backend/scripts/seed.py`

**Needed Changes**:

- Create sample respondents with all 10 fields
- Include diverse chronic diseases examples
- Create sample SANSA responses with realistic answers
- Create sample satisfaction responses
- Create sample BIA records with valid measurements
- Create sample MNA responses (both screening and full)
- Ensure data relationships are valid (visit_id references)

#### 4.3 Database Migration ⏳

**Status**: Blocked by missing Python virtual environment

**Steps Required**:

1. Set up Python venv in backend directory
2. Install dependencies: `pip install -r requirements.txt`
3. Generate migration: `alembic revision --autogenerate -m "expand_models_complete_sansa"`
4. Review generated migration file
5. Apply migration: `alembic upgrade head`
6. Verify all tables and columns created

#### 4.4 Testing ⏳

- Unit tests for scoring service
- Integration tests for API endpoints
- Frontend form validation tests
- End-to-end user journey tests

---

## 📊 Implementation Statistics

### Backend

- **Files Created**: 4 new routers (satisfaction, bia, mna, updated sansa)
- **Files Modified**: 3 (models.py, schemas.py, main.py, scoring_service.py)
- **Lines of Code**: ~2,000+ lines
- **API Endpoints**: 24 new endpoints across 4 routers

### Frontend

- **Files Created**: 3 new pages (Satisfaction, BIA, MNA)
- **Files Modified**: 2 (GeneralInfoPage, SANSAFormPage)
- **Lines of Code**: ~1,500+ lines
- **UI Components**: 5 complete form pages with validation

### Database

- **New Models**: 3 (SatisfactionResponse, MNAResponse, BIARecord)
- **Expanded Models**: 2 (Respondent, SANSAResponse)
- **Total Fields Added**: 60+ new columns
- **Removed Tables**: 3 (SANSAItem, SatisfactionItem, MNAItem - replaced by column-based)

---

## 🎯 Scoring Rules Implemented

### SANSA (0-56 points)

- **Screening (Q1-Q4)**: 0-8 points
- **Dietary (Q5-Q16)**: 0-48 points
- **Thresholds**:
  - Normal: ≥38
  - At-risk: 25-37
  - Malnourished: 0-24

### MNA (0-30 points)

- **Screening (Q1-Q7)**: 0-14 points
- **Assessment (Q8-Q18)**: 0-16 points (only if screening ≤11)
- **Thresholds**:
  - Normal: 24-30
  - At-risk: 17-23.5
  - Malnourished: <17

### BMI (Asian-Pacific)

- **Underweight**: <18.5
- **Normal**: 18.5-22.9
- **Overweight**: 23-24.9
- **Obese I**: 25-29.9
- **Obese II**: ≥30

### Satisfaction (1-5 scale)

- **Average ≥4.5**: มากที่สุด (Excellent)
- **Average ≥3.5**: มาก (Good)
- **Average ≥2.5**: ปานกลาง (Moderate)
- **Average ≥1.5**: น้อย (Poor)
- **Average <1.5**: น้อยที่สุด (Very Poor)

---

## 🔄 User Journey Flow

### Respondent Journey (Self-Service)

1. **Start**: Enter respondent code or create new
2. **General Info**: Fill 10 demographic fields (33%)
3. **SANSA Form**: Answer 16 nutrition questions (66%)
4. **Satisfaction**: Rate experience (7 questions) (100%)
5. **Result**: View scores and recommendations

### Staff Journey (Clinical Assessment)

1. **Login**: Authenticate as staff/admin
2. **Dashboard**: View respondent list
3. **Select Respondent**: Choose for assessment
4. **BIA Measurement**: Record body composition
5. **MNA Assessment**: Conduct full nutrition screening
6. **Review**: View comprehensive results
7. **Export**: Generate CSV for analysis

---

## 🚀 Next Steps

### Immediate (Critical)

1. Set up Python virtual environment
2. Generate and run Alembic migration
3. Test backend endpoints with Postman/Thunder Client
4. Fix any database constraint issues

### Short-term (High Priority)

1. Update export service with all new fields
2. Create comprehensive seed data
3. Update ResultPage to show all assessment scores
4. Add navigation between assessment types

### Medium-term (Enhancement)

1. Add data visualization charts (BMI trends, score history)
2. Implement PDF report generation
3. Add email notifications for completed assessments
4. Create admin analytics dashboard

### Long-term (Future Features)

1. Multi-language support (Thai/English toggle)
2. Mobile app version
3. Integration with hospital systems (HL7/FHIR)
4. Machine learning for nutrition recommendations

---

## 📁 File Structure Summary

```
backend/
├── app/
│   ├── models.py (MODIFIED - 60+ new fields)
│   ├── schemas.py (MODIFIED - all new schemas)
│   ├── main.py (MODIFIED - 4 new routers)
│   ├── services/
│   │   └── scoring_service.py (MODIFIED - SANSA/MNA scoring)
│   └── routers/
│       ├── sansa.py (MODIFIED - column-based)
│       ├── satisfaction.py (NEW)
│       ├── bia.py (NEW)
│       └── mna.py (NEW)

frontend/
└── src/
    └── pages/
        ├── GeneralInfoPage.tsx (MODIFIED - 10 fields)
        ├── SANSAFormPage.tsx (MODIFIED - 16 questions)
        ├── SatisfactionPage.tsx (NEW - 7 Likert)
        ├── BIAMeasurementPage.tsx (NEW - body composition)
        └── MNAAssessmentPage.tsx (NEW - 18 questions conditional)
```

---

## 🎨 Design Patterns Used

### Backend

- **Column-based Storage**: Simplified from items tables to direct columns for fixed questionnaires
- **Service Layer**: Scoring logic separated from API routes
- **Schema Validation**: Pydantic for request/response validation
- **Conditional Logic**: MNA assessment only if needed (screening ≤11)

### Frontend

- **Gradient Themes**: Each page has unique color gradient
- **Progress Indicators**: Visual feedback on completion status
- **Form State Management**: React hooks for complex form state
- **Real-time Calculation**: BMI and MNA screening scores update live
- **Error Handling**: User-friendly error messages in Thai

---

## ✅ Quality Checklist

- [x] All 16 SANSA questions implemented with correct scoring
- [x] All 18 MNA questions with conditional assessment logic
- [x] All 7 satisfaction Likert questions
- [x] All 10 respondent demographic fields
- [x] BIA with auto-BMI calculation and Asian-Pacific thresholds
- [x] Thai language labels throughout all forms
- [x] Responsive design with Tailwind CSS
- [x] Form validation on both frontend and backend
- [x] API authentication for staff-only endpoints
- [x] Proper error handling and user feedback
- [ ] Database migration applied
- [ ] Export service updated with all fields
- [ ] Seed data with realistic samples
- [ ] Unit tests for scoring logic
- [ ] Integration tests for API endpoints

---

## 📝 Notes

### Technical Decisions

1. **Column-based vs Items Table**: Chose columns for fixed questionnaires (simpler queries, better performance)
2. **Conditional MNA**: Implemented frontend conditional rendering + backend validation
3. **BMI Thresholds**: Used Asian-Pacific standards as per requirements
4. **Decimal Scores**: MNA supports 0.5 point increments (Decimal type in DB)
5. **JSON Fields**: Used for dynamic lists (income sources, chronic diseases)

### Known Issues

- Virtual environment not set up (blocks migration)
- Some old API tests may fail (schema changes)
- ResultPage needs update to display all new scores

### Future Considerations

- Consider GraphQL for complex nested queries
- Implement caching for frequently accessed data
- Add WebSocket for real-time collaboration (staff + respondent)
- Consider i18n library for better multi-language support

---

**Last Updated**: Current Session
**Status**: Phase 1-3 Complete (95%), Phase 4 Pending (Infrastructure)
**Next Action**: Set up Python venv and run Alembic migration
