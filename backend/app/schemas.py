from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum


# Enums
class UserRole(str, Enum):
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


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


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


class RespondentResponse(BaseModel):
    id: int
    respondent_code: str
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
    visit_date: date
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
    q1_weight_change: Optional[str] = None
    q2_food_intake: Optional[str] = None
    q3_daily_activities: Optional[str] = None
    q4_chronic_disease: Optional[str] = None
    # Dietary questions (Q5-Q16)
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


class SANSAResponseFull(BaseModel):
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
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Satisfaction Schemas
class SatisfactionResponseCreate(BaseModel):
    visit_id: int
    q1_clarity: Optional[int] = Field(None, ge=1, le=5)  # ความชัดเจนของคำถาม
    q2_ease_of_use: Optional[int] = Field(None, ge=1, le=5)  # ความสะดวกในการใช้งาน
    q3_confidence: Optional[int] = Field(None, ge=1, le=5)  # ความมั่นใจในการกรอก
    q4_presentation: Optional[int] = Field(None, ge=1, le=5)  # รูปแบบการนำเสนอ
    q5_results_display: Optional[int] = Field(None, ge=1, le=5)  # การแสดงผลลัพธ์
    q6_usefulness: Optional[int] = Field(None, ge=1, le=5)  # ประโยชน์ที่ได้รับ
    q7_overall_satisfaction: Optional[int] = Field(None, ge=1, le=5)  # ความพึงพอใจโดยรวม
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
    visit_id: int
    # Screening (Q1-Q7)
    q1_food_intake_decline: Optional[str] = None
    q2_weight_loss: Optional[str] = None
    q3_mobility: Optional[str] = None
    q4_stress_illness: Optional[str] = None
    q5_neuropsychological: Optional[str] = None
    q6_bmi: Optional[str] = None
    q7_calf_circumference: Optional[str] = None
    # Full Assessment (Q8-Q18)
    q8_independent_living: Optional[str] = None
    q9_medications: Optional[str] = None
    q10_pressure_sores: Optional[str] = None
    q11_full_meals: Optional[str] = None
    q12_protein_consumption: Optional[str] = None
    q13_fruits_vegetables: Optional[str] = None
    q14_fluid_intake: Optional[str] = None
    q15_eating_independence: Optional[str] = None
    q16_self_nutrition: Optional[str] = None
    q17_health_comparison: Optional[str] = None
    q18_mid_arm_circumference: Optional[str] = None


class MNAResponseUpdate(BaseModel):
    q1_food_intake_decline: Optional[str] = None
    q2_weight_loss: Optional[str] = None
    q3_mobility: Optional[str] = None
    q4_stress_illness: Optional[str] = None
    q5_neuropsychological: Optional[str] = None
    q6_bmi: Optional[str] = None
    q7_calf_circumference: Optional[str] = None
    q8_independent_living: Optional[str] = None
    q9_medications: Optional[str] = None
    q10_pressure_sores: Optional[str] = None
    q11_full_meals: Optional[str] = None
    q12_protein_consumption: Optional[str] = None
    q13_fruits_vegetables: Optional[str] = None
    q14_fluid_intake: Optional[str] = None
    q15_eating_independence: Optional[str] = None
    q16_self_nutrition: Optional[str] = None
    q17_health_comparison: Optional[str] = None
    q18_mid_arm_circumference: Optional[str] = None


class MNAResponseFull(BaseModel):
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
    muscle_mass_kg: Optional[Decimal] = None
    bone_mass_kg: Optional[Decimal] = None
    water_percentage: Optional[Decimal] = None
    metabolic_rate: Optional[int] = None
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
    muscle_mass_kg: Optional[Decimal] = None
    bone_mass_kg: Optional[Decimal] = None
    water_percentage: Optional[Decimal] = None
    metabolic_rate: Optional[int] = None
    hip_circumference_cm: Optional[Decimal] = None
    weight_management: Optional[str] = None
    food_recommendation: Optional[str] = None
    staff_signature: Optional[str] = None
    measurement_date: Optional[date] = None
    notes: Optional[str] = None


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
    muscle_mass_kg: Optional[Decimal]
    bone_mass_kg: Optional[Decimal]
    water_percentage: Optional[Decimal]
    metabolic_rate: Optional[int]
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


# BIA Schemas
class BIARecordCreate(BaseModel):
    visit_id: int
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=500)
    height_cm: Optional[Decimal] = Field(None, ge=0, le=300)
    bmi: Optional[Decimal] = None
    body_fat_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    muscle_mass_kg: Optional[Decimal] = Field(None, ge=0)
    bone_mass_kg: Optional[Decimal] = Field(None, ge=0)
    water_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    visceral_fat_level: Optional[int] = Field(None, ge=0)
    waist_circumference_cm: Optional[Decimal] = Field(None, ge=0)
    hip_circumference_cm: Optional[Decimal] = Field(None, ge=0)
    waist_hip_ratio: Optional[Decimal] = None
    notes: Optional[str] = None


class BIARecordUpdate(BaseModel):
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=500)
    height_cm: Optional[Decimal] = Field(None, ge=0, le=300)
    bmi: Optional[Decimal] = None
    body_fat_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    muscle_mass_kg: Optional[Decimal] = Field(None, ge=0)
    bone_mass_kg: Optional[Decimal] = Field(None, ge=0)
    water_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    visceral_fat_level: Optional[int] = Field(None, ge=0)
    waist_circumference_cm: Optional[Decimal] = Field(None, ge=0)
    hip_circumference_cm: Optional[Decimal] = Field(None, ge=0)
    waist_hip_ratio: Optional[Decimal] = None
    notes: Optional[str] = None


class BIARecordResponse(BaseModel):
    id: int
    visit_id: int
    weight_kg: Optional[Decimal]
    height_cm: Optional[Decimal]
    bmi: Optional[Decimal]
    body_fat_percentage: Optional[Decimal]
    muscle_mass_kg: Optional[Decimal]
    bone_mass_kg: Optional[Decimal]
    water_percentage: Optional[Decimal]
    visceral_fat_level: Optional[int]
    waist_circumference_cm: Optional[Decimal]
    hip_circumference_cm: Optional[Decimal]
    waist_hip_ratio: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime

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
    is_published: bool = False
    display_order: int = 0


class KnowledgePostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_published: Optional[bool] = None
    display_order: Optional[int] = None


class KnowledgePostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: Optional[str]
    summary: Optional[str]
    featured_image_path: Optional[str]
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
    rule_values: List[ScoringRuleValueResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# Message Response
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
