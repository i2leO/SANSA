from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    Enum,
    Text,
    ForeignKey,
    DECIMAL,
    Date,
    Time,
    JSON,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
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
    qr_secret_hash = Column(String(64), unique=True, nullable=True)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    respondents_created = relationship(
        "Respondent", back_populates="creator", foreign_keys="Respondent.created_by"
    )
    visits_created = relationship("Visit", back_populates="creator")
    mna_responses_created = relationship("MNAResponse", back_populates="creator")
    bia_records = relationship("BIARecord", back_populates="measurer")
    knowledge_posts = relationship("KnowledgePost", back_populates="creator")
    facilities_created = relationship("Facility", back_populates="creator")
    scoring_versions_created = relationship(
        "ScoringRuleVersion", back_populates="creator"
    )


class SourceImportBatch(Base):
    """Immutable provenance for one imported research workbook."""

    __tablename__ = "source_import_batches"

    id = Column(Integer, primary_key=True, index=True)
    source_dataset = Column(String(100), nullable=False, index=True)
    source_filename = Column(String(255), nullable=False)
    source_sha256 = Column(String(64), nullable=False, unique=True, index=True)
    schema_version = Column(String(100), nullable=False)
    populated_rows = Column(Integer, nullable=False)
    sheet_manifest = Column(JSON, nullable=False)
    imported_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class SourceImportSheet(Base):
    """Read-only snapshot of one workbook sheet at import time."""

    __tablename__ = "source_import_sheets"

    id = Column(Integer, primary_key=True, index=True)
    import_batch_id = Column(
        Integer, ForeignKey("source_import_batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sheet_name = Column(String(100), nullable=False)
    sheet_role = Column(String(30), nullable=False)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    values_json = Column(JSON, nullable=False)
    formulas_json = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint("import_batch_id", "sheet_name", name="uq_source_import_sheet"),
    )


class Respondent(Base):
    __tablename__ = "respondents"

    id = Column(Integer, primary_key=True, index=True)
    respondent_code = Column(String(50), unique=True, nullable=False, index=True)
    source_dataset = Column(String(100), nullable=True, index=True)
    source_record_id = Column(Integer, nullable=True)
    source_import_batch_id = Column(
        Integer, ForeignKey("source_import_batches.id"), nullable=True, index=True
    )

    qr_secret_hash = Column(String(64), unique=True, nullable=True)

    # Demographics - New unified fields
    status = Column(Enum(RespondentStatus))  # ผู้สูงอายุ/ผู้ดูแลผู้สูงอายุ
    age = Column(Integer)
    sex = Column(Enum(Sex))  # male/female/other
    education_level = Column(String(50))
    marital_status = Column(String(50))
    monthly_income = Column(String(50))
    income_sources = Column(JSON)  # Array of income sources
    chronic_diseases = Column(JSON)  # Object with disease flags
    living_arrangement = Column(String(50))

    # Legacy fields (kept for backward compatibility)
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
    creator = relationship(
        "User", back_populates="respondents_created", foreign_keys=[created_by]
    )
    visits = relationship(
        "Visit", back_populates="respondent", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "source_dataset", "source_record_id", name="uq_respondent_source_record"
        ),
    )


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
    respondent_id = Column(
        Integer, ForeignKey("respondents.id"), nullable=False, index=True
    )
    visit_number = Column(Integer, nullable=False, default=1)
    visit_date = Column(Date, nullable=True, index=True)
    visit_time = Column(Time)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    visit_type = Column(Enum(VisitType), default=VisitType.BASELINE)
    notes = Column(Text)
    source_assessment_id = Column(String(100), nullable=True, index=True)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    respondent = relationship("Respondent", back_populates="visits")
    facility = relationship("Facility", back_populates="visits")
    creator = relationship("User", back_populates="visits_created")
    sansa_response = relationship(
        "SANSAResponse",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    satisfaction_response = relationship(
        "SatisfactionResponse",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    mna_response = relationship(
        "MNAResponse",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan",
    )
    bia_records = relationship(
        "BIARecord", back_populates="visit", cascade="all, delete-orphan"
    )
    prediction_results = relationship(
        "SANSAPredictionResult", back_populates="visit", cascade="all, delete-orphan"
    )
    food_diary_entries = relationship(
        "FoodDiaryEntry", back_populates="visit", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "respondent_id", "visit_number", name="unique_respondent_visit"
        ),
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
    scoring_rules = relationship(
        "ScoringRule", back_populates="version", cascade="all, delete-orphan"
    )
    scoring_rule_values = relationship(
        "ScoringRuleValue", back_populates="version", cascade="all, delete-orphan"
    )
    sansa_responses = relationship("SANSAResponse", back_populates="scoring_version")
    mna_responses = relationship("MNAResponse", back_populates="scoring_version")

    __table_args__ = (
        UniqueConstraint(
            "instrument_name", "version_number", name="unique_instrument_version"
        ),
    )


class ScoringRule(Base):
    __tablename__ = "scoring_rules"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(
        Integer,
        ForeignKey("scoring_rule_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_type = Column(String(50), nullable=False)
    rule_key = Column(String(100), nullable=False)
    rule_value = Column(Text)
    rule_order = Column(Integer, default=0)
    description = Column(Text)

    # Relationships
    version = relationship("ScoringRuleVersion", back_populates="scoring_rules")

    __table_args__ = (Index("idx_type_key", "rule_type", "rule_key"),)


class ScoringRuleValue(Base):
    __tablename__ = "scoring_rule_values"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(
        Integer,
        ForeignKey("scoring_rule_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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
    visit_id = Column(
        Integer,
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    scoring_version_id = Column(
        Integer, ForeignKey("scoring_rule_versions.id"), nullable=False
    )

    # SANSA Questions (Q1-Q16) with answers and scores
    q1_weight_change = Column(String(50))
    q1_score = Column(DECIMAL(10, 2))
    q2_food_intake = Column(String(50))
    q2_score = Column(DECIMAL(10, 2))
    q3_daily_activities = Column(String(50))
    q3_score = Column(DECIMAL(10, 2))
    q4_chronic_disease = Column(String(50))
    q4_score = Column(DECIMAL(10, 2))
    q5_meals_per_day = Column(String(50))
    q5_score = Column(DECIMAL(10, 2))
    q6_portion_size = Column(String(50))
    q6_score = Column(DECIMAL(10, 2))
    q7_food_texture = Column(String(50))
    q7_score = Column(DECIMAL(10, 2))
    q8_rice_starch = Column(String(50))
    q8_score = Column(DECIMAL(10, 2))
    q9_protein = Column(String(50))
    q9_score = Column(DECIMAL(10, 2))
    q10_milk = Column(String(50))
    q10_score = Column(DECIMAL(10, 2))
    q11_fruits = Column(String(50))
    q11_score = Column(DECIMAL(10, 2))
    q12_vegetables = Column(String(50))
    q12_score = Column(DECIMAL(10, 2))
    q13_water = Column(String(50))
    q13_score = Column(DECIMAL(10, 2))
    q14_sweet_drinks = Column(String(50))
    q14_score = Column(DECIMAL(10, 2))
    q15_cooking_method = Column(String(50))
    q15_score = Column(DECIMAL(10, 2))
    q16_oil_coconut = Column(String(50))
    q16_score = Column(DECIMAL(10, 2))
    screening_total = Column(DECIMAL(10, 2))
    diet_total = Column(DECIMAL(10, 2))
    total_score = Column(DECIMAL(10, 2))
    result_level = Column(String(50), index=True)
    source_dataset = Column(String(100))
    answer_capture_mode = Column(String(30), default="raw_answers")

    # Metadata
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    visit = relationship("Visit", back_populates="sansa_response")
    scoring_version = relationship(
        "ScoringRuleVersion", back_populates="sansa_responses"
    )


class SANSAPredictionResult(Base):
    __tablename__ = "sansa_prediction_results"

    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False)
    model_version = Column(String(50), nullable=False)
    age_group01 = Column(Integer, nullable=False)
    d2_total = Column(DECIMAL(12, 4), nullable=False)
    d3_total = Column(DECIMAL(12, 4), nullable=False)
    waist_cm = Column(DECIMAL(12, 4), nullable=False)
    l_over = Column(DECIMAL(24, 12), nullable=False)
    l_normal = Column(DECIMAL(24, 12), nullable=False)
    p_under = Column(DECIMAL(18, 16), nullable=False)
    p_normal = Column(DECIMAL(18, 16), nullable=False)
    p_over = Column(DECIMAL(18, 16), nullable=False)
    predicted_group = Column(
        Enum("UNDER", "NORMAL", "OVER", name="sansa_prediction_group",
             create_constraint=True, validate_strings=True), nullable=False
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    visit = relationship("Visit", back_populates="prediction_results")

    __table_args__ = (
        UniqueConstraint("visit_id", "model_version", name="uq_sansa_prediction_visit_version"),
        CheckConstraint("age_group01 IN (0, 1)", name="ck_sansa_prediction_age_group"),
        CheckConstraint(
            "p_under BETWEEN 0 AND 1 AND p_normal BETWEEN 0 AND 1 AND p_over BETWEEN 0 AND 1",
            name="ck_sansa_prediction_probabilities",
        ),
    )


class SatisfactionResponse(Base):
    __tablename__ = "satisfaction_responses"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(
        Integer,
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # 7 Likert-scale questions (1-5)
    q1_clarity = Column(Integer)
    q2_ease_of_use = Column(Integer)
    q3_confidence = Column(Integer)
    q4_presentation = Column(Integer)
    q5_results_display = Column(Integer)
    q6_usefulness = Column(Integer)
    q7_overall_satisfaction = Column(Integer)
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
    visit_id = Column(
        Integer,
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    scoring_version_id = Column(
        Integer, ForeignKey("scoring_rule_versions.id"), nullable=False
    )
    # A score-only import must never be presented as if the participant chose
    # a specific raw option.  These fields make that provenance explicit.
    source_dataset = Column(String(50), nullable=False, default="web")
    answer_capture_mode = Column(String(30), nullable=False, default="raw_answers")

    # MNA Questions (Q1-Q18) with answers and scores
    q1_food_intake_decline = Column(String(50))
    mna_s1 = Column(DECIMAL(10, 2))
    q2_weight_loss = Column(String(50))
    mna_s2 = Column(DECIMAL(10, 2))
    q3_mobility = Column(String(50))
    mna_s3 = Column(DECIMAL(10, 2))
    q4_stress_illness = Column(String(50))
    mna_s4 = Column(DECIMAL(10, 2))
    q5_neuropsychological = Column(String(50))
    mna_s5 = Column(DECIMAL(10, 2))
    q6_bmi = Column(String(50))
    mna_s6 = Column(DECIMAL(10, 2))
    q7_calf_circumference = Column(String(50))
    mna_s7 = Column(DECIMAL(10, 2))
    mna_screen_total = Column(DECIMAL(10, 2))
    q8_independent_living = Column(String(50))
    mna_a1 = Column(DECIMAL(10, 2))
    q9_medications = Column(String(50))
    mna_a2 = Column(DECIMAL(10, 2))
    q10_pressure_sores = Column(String(50))
    mna_a3 = Column(DECIMAL(10, 2))
    q11_full_meals = Column(String(50))
    mna_a4 = Column(DECIMAL(10, 2))
    q12_protein_consumption = Column(String(50))
    mna_a5 = Column(DECIMAL(10, 2))
    q13_fruits_vegetables = Column(String(50))
    mna_a6 = Column(DECIMAL(10, 2))
    q14_fluid_intake = Column(String(50))
    mna_a7 = Column(DECIMAL(10, 2))
    q15_eating_independence = Column(String(50))
    mna_a8 = Column(DECIMAL(10, 2))
    q16_self_nutrition = Column(String(50))
    mna_a9 = Column(DECIMAL(10, 2))
    q17_health_comparison = Column(String(50))
    mna_a10 = Column(DECIMAL(10, 2))
    q18_mid_arm_circumference = Column(String(50))
    mna_a11 = Column(DECIMAL(10, 2))
    # Full-assessment R is distinct from the historical screening calf slot.
    q19_calf_circumference_assess = Column(String(50))
    mna_a12 = Column(DECIMAL(10, 2))
    mac_cm = Column(DECIMAL(5, 2))
    cc_cm = Column(DECIMAL(5, 2))
    mna_ass_total = Column(DECIMAL(10, 2))
    mna_total = Column(DECIMAL(10, 2))
    result_category = Column(String(50), index=True)

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
    visit_id = Column(
        Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Basic info
    age = Column(Integer)
    sex = Column(Enum(Sex))

    # Anthropometry
    waist_circumference_cm = Column(DECIMAL(5, 2))
    waist_input_value = Column(DECIMAL(7, 2), nullable=True)
    waist_input_unit = Column(String(10), nullable=True)
    weight_kg = Column(DECIMAL(5, 2))
    height_cm = Column(DECIMAL(5, 2))
    bmi = Column(DECIMAL(5, 2))
    bmi_category = Column(String(50))

    # Body composition
    fat_mass_kg = Column(DECIMAL(5, 2))
    body_fat_percentage = Column(DECIMAL(5, 2))
    visceral_fat_kg = Column(DECIMAL(5, 2))
    visceral_fat_level = Column(DECIMAL(5, 2))
    muscle_mass_kg = Column(DECIMAL(5, 2))
    bone_mass_kg = Column(DECIMAL(5, 2))
    water_percentage = Column(DECIMAL(5, 2))
    metabolic_rate = Column(Integer)
    mac_cm = Column(DECIMAL(5, 2))
    cc_cm = Column(DECIMAL(5, 2))

    # Additional measurements
    hip_circumference_cm = Column(DECIMAL(5, 2))
    waist_hip_ratio = Column(DECIMAL(4, 3))

    # Recommendations
    weight_management = Column(String(50))
    food_recommendation = Column(String(100))

    # Staff info
    measured_by = Column(Integer, ForeignKey("users.id"))
    source_staff_id = Column(String(100), nullable=True)
    staff_signature = Column(String(255))
    measurement_date = Column(Date)

    # Metadata
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    visit = relationship("Visit", back_populates="bia_records")
    measurer = relationship("User", back_populates="bia_records")

    __table_args__ = (UniqueConstraint("visit_id", name="uq_bia_visit"),)


class FoodDiaryEntry(Base):
    __tablename__ = "food_diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(
        Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True
    )

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
    photos = relationship(
        "FoodDiaryPhoto", back_populates="diary_entry", cascade="all, delete-orphan"
    )


class FoodDiaryPhoto(Base):
    __tablename__ = "food_diary_photos"

    id = Column(Integer, primary_key=True, index=True)
    diary_entry_id = Column(
        Integer,
        ForeignKey("food_diary_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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
    media_path = Column(String(500))
    media_type = Column(String(20))
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

    __table_args__ = (Index("idx_table_record", "table_name", "record_id"),)


class AssessmentRevision(Base):
    """Immutable snapshot of an MNA/BIA record after every successful write."""

    __tablename__ = "assessment_revisions"

    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("respondents.id", ondelete="CASCADE"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"), nullable=False, index=True)
    instrument = Column(String(20), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    action_type = Column(String(20), nullable=False)
    snapshot = Column(JSON, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    change_reason = Column(String(255), nullable=True)
    is_current = Column(Boolean, nullable=False, default=True, index=True)
    recorded_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("instrument", "record_id", "revision_number", name="uq_assessment_revision"),
        Index("idx_assessment_history", "respondent_id", "instrument", "recorded_at"),
    )
