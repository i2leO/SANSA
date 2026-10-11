from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator, validator
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from app.services.sansa_definition import QUESTIONS_BY_FIELD, canonical_values


# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    STAFF = "staff"


class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class RespondentStatus(str, Enum):
    ELDERLY = "elderly"
    CAREGIVER = "caregiver"


# Closed vocabularies from revised4 Data_Dictionary. Historical values remain
# readable in RespondentResponse, but new completed profiles cannot introduce
# options that are absent from the approved workbook.
class ResearchSex(str, Enum):
    MALE = "male"
    FEMALE = "female"


class EducationLevel(str, Enum):
    NO_EDUCATION = "no_education"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    VOCATIONAL = "vocational"
    BACHELOR = "bachelor"
    GRADUATE = "graduate"


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"
    DIVORCED = "divorced"


class MonthlyIncome(str, Enum):
    UNDER_10K = "under_10k"
    FROM_10K_TO_20K = "10k_20k"
    FROM_20K_TO_30K = "20k_30k"
    OVER_30K = "over_30k"


class IncomeSource(str, Enum):
    OLD_AGE = "old_age"
    PENSION = "pension"
    SPOUSE = "spouse"
    CHILDREN = "children"
    WORK = "work"


class ChronicDisease(str, Enum):
    DM = "dm"
    HT = "ht"
    DLP = "dlp"
    CKD = "ckd"
    CA = "ca"


class LivingArrangement(str, Enum):
    ALONE = "alone"
    WITH_SPOUSE = "with_spouse"
    WITH_FRIENDS = "with_friends"
    WITH_FAMILY = "with_family"


class VisitType(str, Enum):
    BASELINE = "baseline"
    FOLLOW_UP = "follow_up"
    FINAL = "final"


class ItemType(str, Enum):
    SCREENING = "screening"
    DIETARY = "dietary"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    MORNING_SNACK = "morning_snack"
    LUNCH = "lunch"
    AFTERNOON_SNACK = "afternoon_snack"
    DINNER = "dinner"
    BEFORE_BED = "before_bed"
    OTHER = "other"


class EntryMode(str, Enum):
    STAFF = "staff"
    SELF = "self"


# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    qr_version: Optional[str] = None
    token_type: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: UserRole = UserRole.STAFF


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Respondent Schemas
class RespondentCreate(BaseModel):
    respondent_code: Optional[str] = None  # Auto-generated if not provided
    status: Optional[RespondentStatus] = None  # ผู้สูงอายุ/ผู้ดูแล
    age: Optional[int] = Field(None, ge=0, le=150)
    sex: Optional[Sex] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    monthly_income: Optional[str] = None  # รายได้ต่อเดือน
    income_sources: Optional[List[str]] = None  # แหล่งรายได้
    chronic_diseases: Optional[dict] = None  # โรคประจำตัว {diseases: [], other: ""}
    living_arrangement: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class RespondentUpdate(BaseModel):
    status: Optional[RespondentStatus] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    sex: Optional[Sex] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    monthly_income: Optional[str] = None
    income_sources: Optional[List[str]] = None
    chronic_diseases: Optional[dict] = None
    living_arrangement: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ChronicDiseasesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    diseases: List[ChronicDisease]
    other: str = ""


class RespondentProfileUpdate(BaseModel):
    """Complete participant profile required before the SANSA workflow."""

    model_config = ConfigDict(extra="forbid")
    status: RespondentStatus
    age: int = Field(..., ge=60, le=150)
    sex: ResearchSex
    education_level: EducationLevel
    marital_status: MaritalStatus
    monthly_income: MonthlyIncome
    income_sources: List[IncomeSource]
    chronic_diseases: ChronicDiseasesInput
    living_arrangement: LivingArrangement

    @model_validator(mode="after")
    def validate_other_disease(self):
        self.chronic_diseases.other = self.chronic_diseases.other.strip()
        return self


class RespondentResponse(BaseModel):
    id: int
    respondent_code: str
    source_dataset: Optional[str] = None
    source_record_id: Optional[int] = None
    status: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    education_level: Optional[str]
    marital_status: Optional[str]
    monthly_income: Optional[str]
    income_sources: Optional[List[str]]
    chronic_diseases: Optional[dict]
    living_arrangement: Optional[str]
    income_range: Optional[str]  # legacy
    occupation: Optional[str]  # legacy
    updated_at: datetime

    class Config:
        from_attributes = True


# Visit Schemas
class VisitCreate(BaseModel):
    respondent_id: int
    visit_number: int = 1
    visit_date: date
    visit_time: Optional[time] = None
    facility_id: Optional[int] = None
    visit_type: VisitType = VisitType.BASELINE
    notes: Optional[str] = None


class VisitUpdate(BaseModel):
    visit_date: Optional[date] = None
    visit_time: Optional[time] = None
    facility_id: Optional[int] = None
    visit_type: Optional[VisitType] = None
    notes: Optional[str] = None


class VisitResponse(BaseModel):
    id: int
    respondent_id: int
    visit_number: int
    visit_date: Optional[date]
    visit_time: Optional[time]
    facility_id: Optional[int]
    visit_type: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# SANSA Schemas
class SANSAResponseCreate(BaseModel):
    visit_id: int
    # Screening questions (Q1-Q4)
    q1_weight_change: str = Field(..., min_length=1)
    q2_food_intake: str = Field(..., min_length=1)
    q3_daily_activities: str = Field(..., min_length=1)
    q4_chronic_disease: str = Field(..., min_length=1)
    # Dietary questions (Q5-Q16)
    q5_meals_per_day: str = Field(..., min_length=1)
    q6_portion_size: str = Field(..., min_length=1)
    q7_food_texture: str = Field(..., min_length=1)
    q8_rice_starch: str = Field(..., min_length=1)
    q9_protein: str = Field(..., min_length=1)
    q10_milk: str = Field(..., min_length=1)
    q11_fruits: str = Field(..., min_length=1)
    q12_vegetables: str = Field(..., min_length=1)
    q13_water: str = Field(..., min_length=1)
    q14_sweet_drinks: str = Field(..., min_length=1)
    q15_cooking_method: str = Field(..., min_length=1)
    q16_oil_coconut: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_codebook_answers(self):
        for field_name, question in QUESTIONS_BY_FIELD.items():
            answer = getattr(self, field_name)
            if answer not in canonical_values(field_name):
                raise ValueError(
                    f"คำตอบ SANSA ข้อ {question['number']} ไม่อยู่ในนิยามแบบประเมินที่อนุมัติ"
                )
        return self


class SANSAResponseUpdate(BaseModel):
    q1_weight_change: Optional[str] = None
    q2_food_intake: Optional[str] = None
    q3_daily_activities: Optional[str] = None
    q4_chronic_disease: Optional[str] = None
    q5_meals_per_day: Optional[str] = None
    q6_portion_size: Optional[str] = None
    q7_food_texture: Optional[str] = None
    q8_rice_starch: Optional[str] = None
    q9_protein: Optional[str] = None
    q10_milk: Optional[str] = None
    q11_fruits: Optional[str] = None
    q12_vegetables: Optional[str] = None
    q13_water: Optional[str] = None
    q14_sweet_drinks: Optional[str] = None
    q15_cooking_method: Optional[str] = None
    q16_oil_coconut: Optional[str] = None


class SANSADomainScores(BaseModel):
    d1_total: Optional[Decimal] = None
    d2_total: Optional[Decimal] = None
    d3_total: Optional[Decimal] = None


class SANSAPredictionOutput(BaseModel):
    d2_total: Decimal
    d3_total: Decimal
    waist_cm: Decimal
    age_group01: int
    l_over: Decimal
    l_normal: Decimal
    p_under: Decimal
    p_normal: Decimal
    p_over: Decimal
    predicted_group: str
    model_version: str


class BIAReferenceOutput(BaseModel):
    bmi_rounded: Decimal
    bmi_class: str
    pbf_class: str
    nutrition_reference: str


class SANSAComparison(BaseModel):
    predicted_group: str
    nutrition_reference: str
    matches: bool


class SANSARevisedResult(BaseModel):
    domain_scores: Optional[SANSADomainScores] = None
    prediction: Optional[SANSAPredictionOutput] = None
    reference: Optional[BIAReferenceOutput] = None
    comparison: Optional[SANSAComparison] = None
    bia_record_id: Optional[int] = None
    issues: List[str] = Field(default_factory=list)
    saved: bool = False
    verified_024: bool = False
    missing_answer_fields: List[str] = Field(default_factory=list)
    invalid_answer_fields: List[str] = Field(default_factory=list)
    score_mismatch_fields: List[str] = Field(default_factory=list)


class SANSAParticipantResult(BaseModel):
    """Participant-safe result for one visit, including approved item feedback."""

    predicted_group: Optional[str] = None
    ready: bool
    item_results: List[dict] = Field(default_factory=list)


class ParticipantWaistUpdate(BaseModel):
    waist_input_value: Decimal = Field(..., gt=0)
    waist_input_unit: str
    waist_circumference_cm: Decimal = Field(..., ge=40, le=200)

    @model_validator(mode="after")
    def validate_unit_conversion(self):
        if self.waist_input_unit not in {"cm", "inch"}:
            raise ValueError("หน่วยเส้นรอบเอวต้องเป็น cm หรือ inch")
        expected = self.waist_input_value if self.waist_input_unit == "cm" else self.waist_input_value * Decimal("2.54")
        if abs(expected - self.waist_circumference_cm) > Decimal("0.05"):
            raise ValueError("ค่าเส้นรอบเอวหลังแปลงหน่วยไม่ตรงกัน")
        return self


class SANSAResponseFull(BaseModel):
    revised: Optional[SANSARevisedResult] = None
    id: int
    visit_id: int
    scoring_version_id: int
    # All 16 questions with scores
    q1_weight_change: Optional[str]
    q1_score: Optional[Decimal]
    q2_food_intake: Optional[str]
    q2_score: Optional[Decimal]
    q3_daily_activities: Optional[str]
    q3_score: Optional[Decimal]
    q4_chronic_disease: Optional[str]
    q4_score: Optional[Decimal]
    q5_meals_per_day: Optional[str]
    q5_score: Optional[Decimal]
    q6_portion_size: Optional[str]
    q6_score: Optional[Decimal]
    q7_food_texture: Optional[str]
    q7_score: Optional[Decimal]
    q8_rice_starch: Optional[str]
    q8_score: Optional[Decimal]
    q9_protein: Optional[str]
    q9_score: Optional[Decimal]
    q10_milk: Optional[str]
    q10_score: Optional[Decimal]
    q11_fruits: Optional[str]
    q11_score: Optional[Decimal]
    q12_vegetables: Optional[str]
    q12_score: Optional[Decimal]
    q13_water: Optional[str]
    q13_score: Optional[Decimal]
    q14_sweet_drinks: Optional[str]
    q14_score: Optional[Decimal]
    q15_cooking_method: Optional[str]
    q15_score: Optional[Decimal]
    q16_oil_coconut: Optional[str]
    q16_score: Optional[Decimal]
    # Totals
    screening_total: Optional[Decimal]
    diet_total: Optional[Decimal]
    total_score: Optional[Decimal]
    result_level: Optional[str]
    source_dataset: Optional[str] = None
    answer_capture_mode: Optional[str] = None
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Satisfaction Schemas
class SatisfactionResponseCreate(BaseModel):
    visit_id: int
    q1_clarity: int = Field(..., ge=1, le=5)  # ความชัดเจนของคำถาม
    q2_ease_of_use: int = Field(..., ge=1, le=5)  # ความสะดวกในการใช้งาน
    q3_confidence: int = Field(..., ge=1, le=5)  # ความมั่นใจในการกรอก
    q4_presentation: int = Field(..., ge=1, le=5)  # รูปแบบการนำเสนอ
    q5_results_display: int = Field(..., ge=1, le=5)  # การแสดงผลลัพธ์
    q6_usefulness: int = Field(..., ge=1, le=5)  # ประโยชน์ที่ได้รับ
    q7_overall_satisfaction: int = Field(..., ge=1, le=5)  # ความพึงพอใจโดยรวม
    comments: Optional[str] = None


class SatisfactionResponseUpdate(BaseModel):
    q1_clarity: Optional[int] = Field(None, ge=1, le=5)
    q2_ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    q3_confidence: Optional[int] = Field(None, ge=1, le=5)
    q4_presentation: Optional[int] = Field(None, ge=1, le=5)
    q5_results_display: Optional[int] = Field(None, ge=1, le=5)
    q6_usefulness: Optional[int] = Field(None, ge=1, le=5)
    q7_overall_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None


class SatisfactionResponseFull(BaseModel):
    id: int
    visit_id: int
    q1_clarity: Optional[int]
    q2_ease_of_use: Optional[int]
    q3_confidence: Optional[int]
    q4_presentation: Optional[int]
    q5_results_display: Optional[int]
    q6_usefulness: Optional[int]
    q7_overall_satisfaction: Optional[int]
    comments: Optional[str]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# MNA Schemas
class MNAResponseCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    q19_calf_circumference_assess: Optional[str] = None
    visit_id: int
    # Screening (Q1-Q7)
    q1_food_intake_decline: Optional[str] = None
    q2_weight_loss: Optional[str] = None
    q3_mobility: Optional[str] = None
    q4_stress_illness: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q4_stress_illness", "q4_psychological_stress"),
    )
    q5_neuropsychological: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "q5_neuropsychological", "q5_neuropsychological_problems"
        ),
    )
    q6_bmi: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q6_bmi", "q6_bmi_or_calf"),
    )
    q7_calf_circumference: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "q7_calf_circumference", "q18_calf_circumference"
        ),
    )
    # Full Assessment (Q8-Q18)
    q8_independent_living: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q8_independent_living", "q7_independent_living"),
    )
    q9_medications: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q9_medications", "q8_medications"),
    )
    q10_pressure_sores: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q10_pressure_sores", "q9_pressure_ulcers"),
    )
    q11_full_meals: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q11_full_meals", "q10_meals_per_day"),
    )
    q12_protein_consumption: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q12_protein_consumption", "q11_protein_markers"),
    )
    q13_fruits_vegetables: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q13_fruits_vegetables", "q12_fruits_vegetables"),
    )
    q14_fluid_intake: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q14_fluid_intake", "q13_fluid_intake"),
    )
    q15_eating_independence: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q15_eating_independence", "q14_feeding_ability"),
    )
    q16_self_nutrition: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q16_self_nutrition", "q15_self_nutrition_view"),
    )
    q17_health_comparison: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q17_health_comparison", "q16_health_comparison"),
    )
    q18_mid_arm_circumference: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "q18_mid_arm_circumference", "q17_mid_arm_circumference"
        ),
    )


class MNAResponseUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    q19_calf_circumference_assess: Optional[str] = None
    q1_food_intake_decline: Optional[str] = None
    q2_weight_loss: Optional[str] = None
    q3_mobility: Optional[str] = None
    q4_stress_illness: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q4_stress_illness", "q4_psychological_stress"),
    )
    q5_neuropsychological: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "q5_neuropsychological", "q5_neuropsychological_problems"
        ),
    )
    q6_bmi: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q6_bmi", "q6_bmi_or_calf"),
    )
    q7_calf_circumference: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "q7_calf_circumference", "q18_calf_circumference"
        ),
    )
    q8_independent_living: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q8_independent_living", "q7_independent_living"),
    )
    q9_medications: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q9_medications", "q8_medications"),
    )
    q10_pressure_sores: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q10_pressure_sores", "q9_pressure_ulcers"),
    )
    q11_full_meals: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q11_full_meals", "q10_meals_per_day"),
    )
    q12_protein_consumption: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q12_protein_consumption", "q11_protein_markers"),
    )
    q13_fruits_vegetables: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q13_fruits_vegetables", "q12_fruits_vegetables"),
    )
    q14_fluid_intake: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q14_fluid_intake", "q13_fluid_intake"),
    )
    q15_eating_independence: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q15_eating_independence", "q14_feeding_ability"),
    )
    q16_self_nutrition: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q16_self_nutrition", "q15_self_nutrition_view"),
    )
    q17_health_comparison: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("q17_health_comparison", "q16_health_comparison"),
    )
    q18_mid_arm_circumference: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "q18_mid_arm_circumference", "q17_mid_arm_circumference"
        ),
    )


class MNAResultSummary(BaseModel):
    available: bool = False
    source: str
    has_raw_answers: bool = False
    has_item_scores: bool = False
    screening_total: Optional[Decimal] = None
    assessment_total: Optional[Decimal] = None
    total: Optional[Decimal] = None
    category: Optional[str] = None
    category_code: Optional[str] = None
    category_label: Optional[str] = None
    integrity_status: str
    issues: List[str] = Field(default_factory=list)


class MNAResponseFull(BaseModel):
    history_requires_review: bool = False
    source_dataset: str = "web"
    answer_capture_mode: str = "raw_answers"
    current_result: Optional[MNAResultSummary] = None
    q19_calf_circumference_assess: Optional[str] = None
    mna_a12: Optional[Decimal] = None
    mac_cm: Optional[Decimal] = None
    cc_cm: Optional[Decimal] = None
    id: int
    visit_id: int
    scoring_version_id: int
    # All 18 questions with scores
    q1_food_intake_decline: Optional[str]
    mna_s1: Optional[Decimal]
    q2_weight_loss: Optional[str]
    mna_s2: Optional[Decimal]
    q3_mobility: Optional[str]
    mna_s3: Optional[Decimal]
    q4_stress_illness: Optional[str]
    mna_s4: Optional[Decimal]
    q5_neuropsychological: Optional[str]
    mna_s5: Optional[Decimal]
    q6_bmi: Optional[str]
    mna_s6: Optional[Decimal]
    q7_calf_circumference: Optional[str]
    mna_s7: Optional[Decimal]
    q8_independent_living: Optional[str]
    mna_a1: Optional[Decimal]
    q9_medications: Optional[str]
    mna_a2: Optional[Decimal]
    q10_pressure_sores: Optional[str]
    mna_a3: Optional[Decimal]
    q11_full_meals: Optional[str]
    mna_a4: Optional[Decimal]
    q12_protein_consumption: Optional[str]
    mna_a5: Optional[Decimal]
    q13_fruits_vegetables: Optional[str]
    mna_a6: Optional[Decimal]
    q14_fluid_intake: Optional[str]
    mna_a7: Optional[Decimal]
    q15_eating_independence: Optional[str]
    mna_a8: Optional[Decimal]
    q16_self_nutrition: Optional[str]
    mna_a9: Optional[Decimal]
    q17_health_comparison: Optional[str]
    mna_a10: Optional[Decimal]
    q18_mid_arm_circumference: Optional[str]
    mna_a11: Optional[Decimal]
    # Totals
    mna_screen_total: Optional[Decimal]
    mna_ass_total: Optional[Decimal]
    mna_total: Optional[Decimal]
    result_category: Optional[str]
    completed_at: Optional[datetime]
    entry_mode: Optional[str]

    class Config:
        from_attributes = True


# BIA Schemas
class BIARecordCreate(BaseModel):
    visit_id: int
    age: Optional[int] = None
    sex: Optional[Sex] = None
    waist_circumference_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = Field(None, gt=0)
    height_cm: Optional[Decimal] = Field(None, gt=0)
    fat_mass_kg: Optional[Decimal] = None
    body_fat_percentage: Optional[Decimal] = None
    visceral_fat_kg: Optional[Decimal] = None
    visceral_fat_level: Optional[Decimal] = None
    muscle_mass_kg: Optional[Decimal] = None
    bone_mass_kg: Optional[Decimal] = None
    water_percentage: Optional[Decimal] = None
    metabolic_rate: Optional[int] = None
    mac_cm: Optional[Decimal] = None
    cc_cm: Optional[Decimal] = None
    hip_circumference_cm: Optional[Decimal] = None
    weight_management: Optional[str] = None  # คงไว้/ลด/เพิ่ม
    food_recommendation: Optional[str] = None
    staff_signature: Optional[str] = None
    measurement_date: Optional[date] = None
    notes: Optional[str] = None


class BIARecordUpdate(BaseModel):
    age: Optional[int] = None
    sex: Optional[Sex] = None
    waist_circumference_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = Field(None, gt=0)
    height_cm: Optional[Decimal] = Field(None, gt=0)
    fat_mass_kg: Optional[Decimal] = None
    body_fat_percentage: Optional[Decimal] = None
    visceral_fat_kg: Optional[Decimal] = None
    visceral_fat_level: Optional[Decimal] = None
    muscle_mass_kg: Optional[Decimal] = None
    bone_mass_kg: Optional[Decimal] = None
    water_percentage: Optional[Decimal] = None
    metabolic_rate: Optional[int] = None
    mac_cm: Optional[Decimal] = None
    cc_cm: Optional[Decimal] = None
    hip_circumference_cm: Optional[Decimal] = None
    weight_management: Optional[str] = None
    food_recommendation: Optional[str] = None
    staff_signature: Optional[str] = None
    measurement_date: Optional[date] = None
    notes: Optional[str] = None


class BIAStaffSubmission(BaseModel):
    """Complete staff measurement row from revised4 BIA_MNA_Staff."""

    model_config = ConfigDict(extra="forbid")
    waist_circumference_cm: Decimal = Field(..., gt=0, le=300)
    weight_kg: Decimal = Field(..., gt=0)
    height_cm: Decimal = Field(..., gt=0)
    fat_mass_kg: Decimal = Field(..., ge=0)
    body_fat_percentage: Decimal = Field(..., ge=0, le=100)
    visceral_fat_level: Decimal = Field(..., ge=0)
    muscle_mass_kg: Decimal = Field(..., ge=0)
    bone_mass_kg: Decimal = Field(..., ge=0)
    water_percentage: Decimal = Field(..., ge=0, le=100)
    metabolic_rate: int = Field(..., gt=0)
    mac_cm: Decimal = Field(..., gt=0)
    cc_cm: Decimal = Field(..., gt=0)


class BIARecordResponse(BaseModel):
    id: int
    visit_id: int
    age: Optional[int]
    sex: Optional[str]
    waist_circumference_cm: Optional[Decimal]
    weight_kg: Optional[Decimal]
    height_cm: Optional[Decimal]
    bmi: Optional[Decimal]
    bmi_category: Optional[str]
    fat_mass_kg: Optional[Decimal]
    body_fat_percentage: Optional[Decimal]
    visceral_fat_kg: Optional[Decimal]
    visceral_fat_level: Optional[Decimal]
    muscle_mass_kg: Optional[Decimal]
    bone_mass_kg: Optional[Decimal]
    water_percentage: Optional[Decimal]
    metabolic_rate: Optional[int]
    mac_cm: Optional[Decimal]
    cc_cm: Optional[Decimal]
    hip_circumference_cm: Optional[Decimal]
    waist_hip_ratio: Optional[Decimal]
    weight_management: Optional[str]
    food_recommendation: Optional[str]
    staff_signature: Optional[str]
    measurement_date: Optional[date]
    measured_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Keep legacy schemas for backward compatibility
class MNAItemInput(BaseModel):
    item_number: int
    item_code: str
    answer_value: str
    item_score: Decimal


class MNAResponseCreateV2(BaseModel):
    """Alternative MNA response schema using item list format"""

    visit_id: int
    entry_mode: EntryMode = EntryMode.STAFF
    items: List[MNAItemInput]


class MNAItemResponse(BaseModel):
    item_number: int
    item_code: str
    answer_value: str
    item_score: Decimal

    class Config:
        from_attributes = True


class MNAResponseFullV2(BaseModel):
    """Alternative MNA response schema using item list format"""

    id: int
    visit_id: int
    scoring_version_id: int
    mna_total: Optional[Decimal]
    result_category: Optional[str]
    entry_mode: str
    completed_at: Optional[datetime]
    items: List[MNAItemResponse]

    class Config:
        from_attributes = True


# Food Diary Schemas
class FoodDiaryEntryCreate(BaseModel):
    visit_id: int
    entry_date: date
    entry_time: Optional[time] = None
    meal_type: MealType
    menu_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    portion_description: Optional[str] = None


class FoodDiaryEntryUpdate(BaseModel):
    entry_date: Optional[date] = None
    entry_time: Optional[time] = None
    meal_type: Optional[MealType] = None
    menu_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    portion_description: Optional[str] = None


class FoodDiaryPhotoResponse(BaseModel):
    id: int
    original_filename: Optional[str]
    stored_filename: str
    file_path: str
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FoodDiaryEntryResponse(BaseModel):
    id: int
    visit_id: int
    entry_date: date
    entry_time: Optional[time]
    meal_type: str
    menu_name: str
    description: Optional[str]
    portion_description: Optional[str]
    photos: List[FoodDiaryPhotoResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# Knowledge Post Schemas
class KnowledgePostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    featured_image_path: Optional[str] = None
    media_path: Optional[str] = None
    media_type: Optional[str] = None
    is_published: bool = False
    display_order: int = 0


class KnowledgePostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    featured_image_path: Optional[str] = None
    media_path: Optional[str] = None
    media_type: Optional[str] = None
    is_published: Optional[bool] = None
    display_order: Optional[int] = None


class KnowledgePostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: Optional[str]
    summary: Optional[str]
    featured_image_path: Optional[str]
    media_path: Optional[str]
    media_type: Optional[str]
    category: Optional[str]
    tags: Optional[str]
    is_published: bool
    published_at: Optional[datetime]
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# Facility Schemas
class FacilityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    map_link: Optional[str] = None
    is_active: bool = True
    display_order: int = 0


class FacilityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    map_link: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class FacilityResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
    type: Optional[str]
    description: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    map_link: Optional[str]
    is_active: bool
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# Scoring Rule Schemas
class ScoringRuleValueInput(BaseModel):
    level_code: str
    level_name: str
    min_score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    level_order: int = 0
    advice_text: Optional[str] = None


class ScoringRuleVersionCreate(BaseModel):
    instrument_name: str
    version_number: str
    version_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    effective_date: Optional[date] = None
    rule_values: List[ScoringRuleValueInput] = []


class ScoringRuleValueResponse(BaseModel):
    id: int
    level_code: str
    level_name: str
    min_score: Optional[Decimal]
    max_score: Optional[Decimal]
    level_order: int
    advice_text: Optional[str]

    class Config:
        from_attributes = True


class ScoringRuleVersionResponse(BaseModel):
    id: int
    instrument_name: str
    version_number: str
    version_name: Optional[str]
    description: Optional[str]
    is_active: bool
    effective_date: Optional[date]
    rule_values: List[ScoringRuleValueResponse] = Field(
        validation_alias="scoring_rule_values",
        serialization_alias="rule_values",
    )
    created_at: datetime

    class Config:
        from_attributes = True


# Message Response
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
