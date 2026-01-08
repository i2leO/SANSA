# Database Schema

## Entity Relationship Diagram

```
users (admin/staff)
    │
    ├──> respondents (1:N - created_by)
    │       │
    │       └──> visits (1:N)
    │               │
    │               ├──> sansa_responses (1:1)
    │               │       └──> sansa_items (1:N)
    │               │
    │               ├──> satisfaction_responses (1:1)
    │               │       └──> satisfaction_items (1:N)
    │               │
    │               ├──> mna_responses (1:1)
    │               │       └──> mna_items (1:N)
    │               │
    │               ├──> bia_records (1:N)
    │               │
    │               └──> food_diary_entries (1:N)
    │                       └──> food_diary_photos (1:N)
    │
    ├──> knowledge_posts (1:N - created_by)
    │
    ├──> facilities (1:N - created_by)
    │
    └──> scoring_rule_versions (1:N - created_by)
            └──> scoring_rules (1:N)
                    └──> scoring_rule_values (1:N)
```

## Tables

### users
Stores admin and staff accounts with JWT authentication.

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'staff') NOT NULL DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);
```

### respondents
Stores anonymous or coded respondent baseline information.

```sql
CREATE TABLE respondents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    respondent_code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Demographics (Section 1)
    age INT,
    sex ENUM('male', 'female', 'other', 'prefer_not_to_say'),
    education_level VARCHAR(50),
    income_range VARCHAR(50),
    occupation VARCHAR(100),
    marital_status VARCHAR(50),
    living_arrangement VARCHAR(50),
    
    -- Optional contact (if consented)
    phone VARCHAR(20),
    email VARCHAR(100),
    
    -- Metadata
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_code (respondent_code),
    INDEX idx_created_at (created_at)
);
```

### visits
Represents a data collection timepoint for a respondent.

```sql
CREATE TABLE visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    respondent_id INT NOT NULL,
    visit_number INT NOT NULL DEFAULT 1,
    visit_date DATE NOT NULL,
    visit_time TIME,
    facility_id INT,
    visit_type ENUM('baseline', 'follow_up', 'final') DEFAULT 'baseline',
    notes TEXT,
    
    -- Metadata
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (respondent_id) REFERENCES respondents(id),
    FOREIGN KEY (facility_id) REFERENCES facilities(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_respondent (respondent_id),
    INDEX idx_visit_date (visit_date),
    UNIQUE KEY unique_respondent_visit (respondent_id, visit_number)
);
```

### scoring_rule_versions
Stores versions of scoring rules for instruments.

```sql
CREATE TABLE scoring_rule_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instrument_name VARCHAR(50) NOT NULL,
    version_number VARCHAR(20) NOT NULL,
    version_name VARCHAR(100),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    
    -- Metadata
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE KEY unique_instrument_version (instrument_name, version_number),
    INDEX idx_instrument (instrument_name),
    INDEX idx_active (is_active)
);
```

### scoring_rules
Defines scoring rules (e.g., classification thresholds).

```sql
CREATE TABLE scoring_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version_id INT NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    rule_key VARCHAR(100) NOT NULL,
    rule_value TEXT,
    rule_order INT DEFAULT 0,
    description TEXT,
    
    FOREIGN KEY (version_id) REFERENCES scoring_rule_versions(id) ON DELETE CASCADE,
    INDEX idx_version (version_id),
    INDEX idx_type_key (rule_type, rule_key)
);
```

### scoring_rule_values
Stores classification levels and thresholds.

```sql
CREATE TABLE scoring_rule_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version_id INT NOT NULL,
    level_code VARCHAR(50) NOT NULL,
    level_name VARCHAR(100) NOT NULL,
    min_score DECIMAL(10,2),
    max_score DECIMAL(10,2),
    level_order INT DEFAULT 0,
    advice_text TEXT,
    
    FOREIGN KEY (version_id) REFERENCES scoring_rule_versions(id) ON DELETE CASCADE,
    INDEX idx_version (version_id),
    INDEX idx_level (level_code)
);
```

### sansa_responses
Stores SANSA assessment responses and computed scores.

```sql
CREATE TABLE sansa_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL UNIQUE,
    scoring_version_id INT NOT NULL,
    
    -- Computed scores
    screening_total DECIMAL(10,2),
    diet_total DECIMAL(10,2),
    total_score DECIMAL(10,2),
    result_level VARCHAR(50),
    
    -- Metadata
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE,
    FOREIGN KEY (scoring_version_id) REFERENCES scoring_rule_versions(id),
    INDEX idx_visit (visit_id),
    INDEX idx_result_level (result_level)
);
```

### sansa_items
Stores individual SANSA item responses (raw answers).

```sql
CREATE TABLE sansa_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sansa_response_id INT NOT NULL,
    item_type ENUM('screening', 'dietary') NOT NULL,
    item_number INT NOT NULL,
    item_code VARCHAR(20) NOT NULL,
    answer_value VARCHAR(255),
    item_score DECIMAL(10,2),
    
    FOREIGN KEY (sansa_response_id) REFERENCES sansa_responses(id) ON DELETE CASCADE,
    INDEX idx_response (sansa_response_id),
    INDEX idx_item_code (item_code),
    UNIQUE KEY unique_response_item (sansa_response_id, item_code)
);
```

### satisfaction_responses
Stores satisfaction survey responses.

```sql
CREATE TABLE satisfaction_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL UNIQUE,
    overall_satisfaction INT,
    comments TEXT,
    
    -- Metadata
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE,
    INDEX idx_visit (visit_id)
);
```

### satisfaction_items
Stores individual satisfaction Likert items.

```sql
CREATE TABLE satisfaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    satisfaction_response_id INT NOT NULL,
    item_number INT NOT NULL,
    item_code VARCHAR(20) NOT NULL,
    question_text TEXT,
    answer_value INT,
    
    FOREIGN KEY (satisfaction_response_id) REFERENCES satisfaction_responses(id) ON DELETE CASCADE,
    INDEX idx_response (satisfaction_response_id),
    UNIQUE KEY unique_response_item (satisfaction_response_id, item_code)
);
```

### mna_responses
Stores MNA (Mini Nutritional Assessment) responses.

```sql
CREATE TABLE mna_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL UNIQUE,
    scoring_version_id INT NOT NULL,
    
    -- Computed scores
    total_score DECIMAL(10,2),
    result_category VARCHAR(50),
    
    -- Metadata
    completed_at TIMESTAMP,
    entry_mode ENUM('staff', 'self') DEFAULT 'staff',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE,
    FOREIGN KEY (scoring_version_id) REFERENCES scoring_rule_versions(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_visit (visit_id),
    INDEX idx_category (result_category)
);
```

### mna_items
Stores individual MNA item responses.

```sql
CREATE TABLE mna_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mna_response_id INT NOT NULL,
    item_number INT NOT NULL,
    item_code VARCHAR(20) NOT NULL,
    answer_value VARCHAR(255),
    item_score DECIMAL(10,2),
    
    FOREIGN KEY (mna_response_id) REFERENCES mna_responses(id) ON DELETE CASCADE,
    INDEX idx_response (mna_response_id),
    UNIQUE KEY unique_response_item (mna_response_id, item_code)
);
```

### bia_records
Stores body composition and anthropometric measurements.

```sql
CREATE TABLE bia_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    
    -- BIA measurements
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    bmi DECIMAL(5,2),
    body_fat_percentage DECIMAL(5,2),
    muscle_mass_kg DECIMAL(5,2),
    bone_mass_kg DECIMAL(5,2),
    water_percentage DECIMAL(5,2),
    visceral_fat_level INT,
    
    -- Anthropometry
    waist_circumference_cm DECIMAL(5,2),
    hip_circumference_cm DECIMAL(5,2),
    waist_hip_ratio DECIMAL(4,3),
    
    -- Metadata
    measured_by INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE,
    FOREIGN KEY (measured_by) REFERENCES users(id),
    INDEX idx_visit (visit_id),
    INDEX idx_measured_date (created_at)
);
```

### food_diary_entries
Stores food diary entries.

```sql
CREATE TABLE food_diary_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    
    -- Entry details
    entry_date DATE NOT NULL,
    entry_time TIME,
    meal_type ENUM('breakfast', 'morning_snack', 'lunch', 'afternoon_snack', 
                   'dinner', 'before_bed', 'other') NOT NULL,
    menu_name VARCHAR(255) NOT NULL,
    description TEXT,
    portion_description VARCHAR(255),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (visit_id) REFERENCES visits(id) ON DELETE CASCADE,
    INDEX idx_visit (visit_id),
    INDEX idx_entry_date (entry_date),
    INDEX idx_meal_type (meal_type)
);
```

### food_diary_photos
Stores photo metadata for food diary entries.

```sql
CREATE TABLE food_diary_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    diary_entry_id INT NOT NULL,
    
    -- File info
    original_filename VARCHAR(255),
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes INT,
    mime_type VARCHAR(100),
    
    -- Metadata
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (diary_entry_id) REFERENCES food_diary_entries(id) ON DELETE CASCADE,
    INDEX idx_diary_entry (diary_entry_id)
);
```

### knowledge_posts
Stores educational content / infographics.

```sql
CREATE TABLE knowledge_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Content
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT,
    summary TEXT,
    featured_image_path VARCHAR(500),
    category VARCHAR(100),
    tags VARCHAR(255),
    
    -- Publishing
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    display_order INT DEFAULT 0,
    
    -- Metadata
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_slug (slug),
    INDEX idx_published (is_published),
    INDEX idx_category (category)
);
```

### facilities
Stores health service center information.

```sql
CREATE TABLE facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Facility info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,
    type VARCHAR(100),
    description TEXT,
    
    -- Contact
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(100),
    website VARCHAR(255),
    
    -- Location
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    map_link VARCHAR(500),
    
    -- Display
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    
    -- Metadata
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_code (code),
    INDEX idx_active (is_active)
);
```

### audit_log
Tracks important data changes for research integrity.

```sql
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Action details
    user_id INT,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT,
    
    -- Changes
    old_values JSON,
    new_values JSON,
    
    -- Metadata
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user (user_id),
    INDEX idx_table (table_name),
    INDEX idx_record (table_name, record_id),
    INDEX idx_created_at (created_at)
);
```

## SPSS Variable Naming Convention

### Respondent Variables
- `respondent_code`: Unique participant code
- `age`: Age in years
- `sex`: 1=male, 2=female, 3=other, 9=prefer not to say
- `education_level`: Coded education level
- `income_range`: Coded income bracket

### Visit Variables
- `visit_id`: Unique visit identifier
- `visit_number`: 1st, 2nd, 3rd visit
- `visit_date`: Date of visit (YYYY-MM-DD)

### SANSA Variables
- `sansa_q1`, `sansa_q2`, `sansa_q3`, `sansa_q4`: Screening items (raw scores)
- `sansa_d01` through `sansa_d12`: Dietary behavior items (0-4 each)
- `sansa_screening_total`: Sum of screening items
- `sansa_diet_total`: Sum of dietary items
- `sansa_total`: Overall SANSA score
- `sansa_level`: 1=normal, 2=at-risk, 3=malnourished
- `sansa_version`: Scoring version used

### MNA Variables
- `mna_q01` through `mna_q18`: MNA items
- `mna_total`: Total MNA score
- `mna_category`: 1=normal, 2=at-risk, 3=malnourished

### BIA Variables
- `bia_weight`: Weight in kg
- `bia_height`: Height in cm
- `bia_bmi`: Body mass index
- `bia_body_fat_pct`: Body fat percentage
- `bia_muscle_kg`: Muscle mass in kg
- `bia_waist_cm`: Waist circumference

### Satisfaction Variables
- `sat_q1` through `sat_q10`: Likert items (1-5)
- `sat_overall`: Overall satisfaction rating
- `sat_comment`: Open-ended feedback (text)

### Timestamps
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `completed_at`: Instrument completion timestamp
