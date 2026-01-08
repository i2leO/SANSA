from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Enum, Text, ForeignKey, DECIMAL, Date, Time, JSON, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"


class Sex(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class RespondentStatus(str, enum.Enum):
    ELDERLY = "elderly"
    CAREGIVER = "caregiver"


class VisitType(str, enum.Enum):
    BASELINE = "baseline"
    FOLLOW_UP = "follow_up"
    FINAL = "final"


class ItemType(str, enum.Enum):
    SCREENING = "screening"
    DIETARY = "dietary"


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    MORNING_SNACK = "morning_snack"
    LUNCH = "lunch"
    AFTERNOON_SNACK = "afternoon_snack"
    DINNER = "dinner"
    BEFORE_BED = "before_bed"
    OTHER = "other"


class EntryMode(str, enum.Enum):
    STAFF = "staff"
    SELF = "self"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    respondents_created = relationship("Respondent", back_populates="creator", foreign_keys="Respondent.created_by")
    visits_created = relationship("Visit", back_populates="creator")
    mna_responses_created = relationship("MNAResponse", back_populates="creator")
    bia_records = relationship("BIARecord", back_populates="measurer")
    knowledge_posts = relationship("KnowledgePost", back_populates="creator")
    facilities_created = relationship("Facility", back_populates="creator")
    scoring_versions_created = relationship("ScoringRuleVersion", back_populates="creator")


class Respondent(Base):
    __tablename__ = "respondents"
    
    id = Column(Integer, primary_key=True, index=True)
    respondent_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Demographics - Page 2 General Information (10 fields)
    status = Column(Enum(RespondentStatus))  # ผู้สูงอายุ/ผู้ดูแลผู้สูงอายุ
    age = Column(Integer)
    sex = Column(Enum(Sex))
    education_level = Column(String(50))  # ระดับการศึกษา
    marital_status = Column(String(50))  # สถานภาพการสมรส
    monthly_income = Column(String(50))  # รายได้ต่อเดือน
    income_sources = Column(JSON)  # แหล่งรายได้ (array)
    chronic_diseases = Column(JSON)  # โรคประจำตัว (array with "other" text)
    living_arrangement = Column(String(50))  # ท่านอาศัยอยู่กับ
    
    # Legacy fields (keep for backward compatibility)
    income_range = Column(String(50))
    occupation = Column(String(100))
    
    # Optional contact
    phone = Column(String(20))
    email = Column(String(100))
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    creator = relationship("User", back_populates="respondents_created", foreign_keys=[created_by])
    visits = relationship("Visit", back_populates="respondent", cascade="all, delete-orphan")


class Facility(Base):
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True)
    type = Column(String(100))
    description = Column(Text)
    
    # Contact
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(100))
    website = Column(String(255))
    
    # Location
    latitude = Column(DECIMAL(10, 7))
    longitude = Column(DECIMAL(10, 7))
    map_link = Column(String(500))
    
    # Display
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    creator = relationship("User", back_populates="facilities_created")
    visits = relationship("Visit", back_populates="facility")


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("respondents.id"), nullable=False, index=True)
    visit_number = Column(Integer, nullable=False, default=1)
    visit_date = Column(Date, nullable=False, index=True)
    visit_time = Column(Time)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    visit_type = Column(Enum(VisitType), default=VisitType.BASELINE)
    notes = Column(Text)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    respondent = relationship("Respondent", back_populates="visits")
    facility = relationship("Facility", back_populates="visits")
    creator = relationship("User", back_populates="visits_created")
    sansa_response = relationship("SANSAResponse", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    satisfaction_response = relationship("SatisfactionResponse", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    mna_response = relationship("MNAResponse", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    bia_records = relationship("BIARecord", back_populates="visit", cascade="all, delete-orphan")
    food_diary_entries = relationship("FoodDiaryEntry", back_populates="visit", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('respondent_id', 'visit_number', name='unique_respondent_visit'),
    )


class ScoringRuleVersion(Base):
    __tablename__ = "scoring_rule_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    instrument_name = Column(String(50), nullable=False, index=True)
    version_number = Column(String(20), nullable=False)
    version_name = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    effective_date = Column(Date)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="scoring_versions_created")
    scoring_rules = relationship("ScoringRule", back_populates="version", cascade="all, delete-orphan")
    scoring_rule_values = relationship("ScoringRuleValue", back_populates="version", cascade="all, delete-orphan")
    sansa_responses = relationship("SANSAResponse", back_populates="scoring_version")
    mna_responses = relationship("MNAResponse", back_populates="scoring_version")
    
    __table_args__ = (
        UniqueConstraint('instrument_name', 'version_number', name='unique_instrument_version'),
    )


class ScoringRule(Base):
    __tablename__ = "scoring_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("scoring_rule_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_type = Column(String(50), nullable=False)
    rule_key = Column(String(100), nullable=False)
    rule_value = Column(Text)
    rule_order = Column(Integer, default=0)
    description = Column(Text)
    
    # Relationships
    version = relationship("ScoringRuleVersion", back_populates="scoring_rules")
    
    __table_args__ = (
        Index('idx_type_key', 'rule_type', 'rule_key'),
    )


class ScoringRuleValue(Base):
    __tablename__ = "scoring_rule_values"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("scoring_rule_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    level_code = Column(String(50), nullable=False, index=True)
    level_name = Column(String(100), nullable=False)
    min_score = Column(DECIMAL(10, 2))
    max_score = Column(DECIMAL(10, 2))
    level_order = Column(Integer, default=0)
    advice_text = Column(Text)
    
    # Relationships
    version = relationship("ScoringRuleVersion", back_populates="scoring_rule_values")


class SANSAResponse(Base):
    __tablename__ = "sansa_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    scoring_version_id = Column(Integer, ForeignKey("scoring_rule_versions.id"), nullable=False)
    
    # SANSA Assessment - 16 questions total
    # Screening (4 questions)
    q1_weight_change = Column(String(50))  # ลดลง=2, คงเดิม=0, เพิ่มขึ้น=2
    q1_score = Column(DECIMAL(10, 2))
    q2_food_intake = Column(String(50))  # น้อยลง=2, ปกติ=0, มากขึ้น=2
    q2_score = Column(DECIMAL(10, 2))
    q3_daily_activities = Column(String(50))  # ไม่ได้=2, ช้ากว่าปกติ=1, ปกติ=0
    q3_score = Column(DECIMAL(10, 2))
    q4_chronic_disease = Column(String(50))  # ไม่มี=0, มี=2
    q4_score = Column(DECIMAL(10, 2))
    
    # Dietary Assessment (12 questions)
    q5_meals_per_day = Column(String(50))  # แทบไม่ได้=0, 1=1, 2=2, 3=3, >3=4
    q5_score = Column(DECIMAL(10, 2))
    q6_portion_size = Column(String(50))  # 25%=0, 50%=1, 75%=2, 100%=3, >100%=4
    q6_score = Column(DECIMAL(10, 2))
    q7_food_texture = Column(String(50))  # เหลว=0, อ่อน=2, ปกติ=4
    q7_score = Column(DECIMAL(10, 2))
    q8_rice_starch = Column(String(50))  # กำปั้น: 0=0, 1-3=1, 4-6=2, 7-9=3, >9=4
    q8_score = Column(DECIMAL(10, 2))
    q9_protein = Column(String(50))  # ฝ่ามือ: 0=0, 1-2=1, 3-5=2, 6-8=3, >8=4
    q9_score = Column(DECIMAL(10, 2))
    q10_milk = Column(String(50))  # แก้ว: <1=0, 1=1, 2=2, 3=3, 4=4
    q10_score = Column(DECIMAL(10, 2))
    q11_fruits = Column(String(50))  # กำปั้น: 0=0, 1-2=1, 3-5=2, 6-8=3, >8=4
    q11_score = Column(DECIMAL(10, 2))
    q12_vegetables = Column(String(50))  # อึงมือ: 0=0, 0-1=1, 2-3=2, 4=3, >4=4
    q12_score = Column(DECIMAL(10, 2))
    q13_water = Column(String(50))  # แก้ว: แทบไม่ได้=0, 1-3=1, 4-6=2, 7-8=3, >8=4
    q13_score = Column(DECIMAL(10, 2))
    q14_sweet_drinks = Column(String(50))  # 3in1: 0=0, 1=1, 2=2, 3=3, >3=4
    q14_score = Column(DECIMAL(10, 2))
    q15_cooking_method = Column(String(50))  # ต้ม/นึ่ง=0, ผัด=1, แกงกะทิ=2, ทอด=4
    q15_score = Column(DECIMAL(10, 2))
    q16_oil_coconut = Column(String(50))  # นิ้วหัวแม่มือ: 0=0, 1-2=1, 3-4=2, 5-6=3, >6=4
    q16_score = Column(DECIMAL(10, 2))
    
    # Computed scores
    screening_total = Column(DECIMAL(10, 2))  # 0-8
    diet_total = Column(DECIMAL(10, 2))  # 0-48
    total_score = Column(DECIMAL(10, 2))  # 0-56
    result_level = Column(String(50), index=True)  # normal ≥38, at_risk 25-37, malnourished 0-24
    
    # Metadata
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    visit = relationship("Visit", back_populates="sansa_response")
    scoring_version = relationship("ScoringRuleVersion", back_populates="sansa_responses")


class SatisfactionResponse(Base):
    __tablename__ = "satisfaction_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # 7 Likert-scale questions (5 levels: มากที่สุด, มาก, ปานกลาง, น้อย, น้อยที่สุด)
    q1_clarity = Column(Integer)  # ความชัดเจนของคำถาม
    q2_ease_of_use = Column(Integer)  # ความสะดวกในการใช้งาน
    q3_confidence = Column(Integer)  # ความมั่นใจในการกรอก
    q4_presentation = Column(Integer)  # รูปแบบการนำเสนอ
    q5_results_display = Column(Integer)  # การแสดงผลลัพธ์
    q6_usefulness = Column(Integer)  # ประโยชน์ที่ได้รับ
    q7_overall_satisfaction = Column(Integer)  # ความพึงพอใจโดยรวม
    
    # Additional comments
    comments = Column(Text)
    
    # Metadata
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    visit = relationship("Visit", back_populates="satisfaction_response")


class MNAResponse(Base):
    __tablename__ = "mna_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    scoring_version_id = Column(Integer, ForeignKey("scoring_rule_versions.id"), nullable=False)
    
    # MNA Assessment - 18 questions total
    # Screening (7 questions)
    q1_food_intake_decline = Column(String(50))  # 0/1/2
    q1_score = Column(DECIMAL(10, 2))
    q2_weight_loss = Column(String(50))  # 0/1/2/3
    q2_score = Column(DECIMAL(10, 2))
    q3_mobility = Column(String(50))  # 0/1/2
    q3_score = Column(DECIMAL(10, 2))
    q4_stress_illness = Column(String(50))  # 0/2
    q4_score = Column(DECIMAL(10, 2))
    q5_neuropsychological = Column(String(50))  # 0/1/2
    q5_score = Column(DECIMAL(10, 2))
    q6_bmi = Column(String(50))  # 0/1/2/3 or CC alternative
    q6_score = Column(DECIMAL(10, 2))
    q7_calf_circumference = Column(String(50))  # 0/3
    q7_score = Column(DECIMAL(10, 2))
    screening_total = Column(DECIMAL(10, 2))  # Max 14
    
    # Full Assessment (11 questions - only if screening ≤11)
    q8_independent_living = Column(String(50))  # 0/1
    q8_score = Column(DECIMAL(10, 2))
    q9_medications = Column(String(50))  # 0/1
    q9_score = Column(DECIMAL(10, 2))
    q10_pressure_sores = Column(String(50))  # 0/1
    q10_score = Column(DECIMAL(10, 2))
    q11_full_meals = Column(String(50))  # 0/1/2
    q11_score = Column(DECIMAL(10, 2))
    q12_protein_consumption = Column(String(50))  # 0/0.5/1
    q12_score = Column(DECIMAL(10, 2))
    q13_fruits_vegetables = Column(String(50))  # 0/1
    q13_score = Column(DECIMAL(10, 2))
    q14_fluid_intake = Column(String(50))  # 0/0.5/1
    q14_score = Column(DECIMAL(10, 2))
    q15_eating_independence = Column(String(50))  # 0/1/2
    q15_score = Column(DECIMAL(10, 2))
    q16_self_nutrition = Column(String(50))  # 0/1/2
    q16_score = Column(DECIMAL(10, 2))
    q17_health_comparison = Column(String(50))  # 0/0.5/1/2
    q17_score = Column(DECIMAL(10, 2))
    q18_mid_arm_circumference = Column(String(50))  # 0/0.5/1
    q18_score = Column(DECIMAL(10, 2))
    assessment_total = Column(DECIMAL(10, 2))  # Max 16
    
    # Computed scores
    total_score = Column(DECIMAL(10, 2))  # Max 30
    result_category = Column(String(50), index=True)  # normal 24-30, at_risk 17-23.5, malnourished <17
    
    # Metadata
    completed_at = Column(TIMESTAMP)
    entry_mode = Column(Enum(EntryMode), default=EntryMode.STAFF)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    visit = relationship("Visit", back_populates="mna_response")
    scoring_version = relationship("ScoringRuleVersion", back_populates="mna_responses")
    creator = relationship("User", back_populates="mna_responses_created")


class BIARecord(Base):
    __tablename__ = "bia_records"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic info (from Page 9)
    age = Column(Integer)
    sex = Column(Enum(Sex))
    waist_circumference_cm = Column(DECIMAL(5, 2))  # เส้นรอบเอว
    
    # BIA measurements
    weight_kg = Column(DECIMAL(5, 2))  # น้ำหนัก
    height_cm = Column(DECIMAL(5, 2))  # ส่วนสูง
    bmi = Column(DECIMAL(5, 2))
    bmi_category = Column(String(50))  # <18.5(ผอม), 18.5-22.9(ปกติ), 23.0-24.9(เกิน), 25.0-29.9(อ้วน1), ≥30(อ้วน2)
    
    # Body composition
    fat_mass_kg = Column(DECIMAL(5, 2))  # มวลไขมัน
    body_fat_percentage = Column(DECIMAL(5, 2))  # %ไขมัน
    visceral_fat_kg = Column(DECIMAL(5, 2))  # ไขมันในช่องท้อง
    muscle_mass_kg = Column(DECIMAL(5, 2))  # มวลกล้ามเนื้อ
    bone_mass_kg = Column(DECIMAL(5, 2))  # มวลกระดูก
    water_percentage = Column(DECIMAL(5, 2))  # น้ำในร่างกาย%
    metabolic_rate = Column(Integer)  # อัตราเผาผลาญ
    
    # Additional anthropometry
    hip_circumference_cm = Column(DECIMAL(5, 2))
    waist_hip_ratio = Column(DECIMAL(4, 3))
    
    # Recommendations (from Page 9)
    weight_management = Column(String(50))  # คงไว้/ลด/เพิ่ม
    food_recommendation = Column(String(100))  # 3 options from form
    
    # Staff signature
    measured_by = Column(Integer, ForeignKey("users.id"))
    staff_signature = Column(String(255))
    measurement_date = Column(Date)
    
    # Metadata
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    visit = relationship("Visit", back_populates="bia_records")
    measurer = relationship("User", back_populates="bia_records")


class FoodDiaryEntry(Base):
    __tablename__ = "food_diary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Entry details
    entry_date = Column(Date, nullable=False, index=True)
    entry_time = Column(Time)
    meal_type = Column(Enum(MealType), nullable=False, index=True)
    menu_name = Column(String(255), nullable=False)
    description = Column(Text)
    portion_description = Column(String(255))
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    visit = relationship("Visit", back_populates="food_diary_entries")
    photos = relationship("FoodDiaryPhoto", back_populates="diary_entry", cascade="all, delete-orphan")


class FoodDiaryPhoto(Base):
    __tablename__ = "food_diary_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    diary_entry_id = Column(Integer, ForeignKey("food_diary_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File info
    original_filename = Column(String(255))
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    
    # Metadata
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    diary_entry = relationship("FoodDiaryEntry", back_populates="photos")


class KnowledgePost(Base):
    __tablename__ = "knowledge_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    content = Column(Text)
    summary = Column(Text)
    featured_image_path = Column(String(500))
    category = Column(String(100), index=True)
    tags = Column(String(255))
    
    # Publishing
    is_published = Column(Boolean, default=False, index=True)
    published_at = Column(TIMESTAMP)
    display_order = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    creator = relationship("User", back_populates="knowledge_posts")


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action_type = Column(String(50), nullable=False)
    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(Integer, index=True)
    
    # Changes
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_table_record', 'table_name', 'record_id'),
    )
