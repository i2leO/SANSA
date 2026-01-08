# SANSA System Architecture

## Overview
Production-ready research data collection & nutrition assessment web application for collecting SANSA (Self-administered Nutrition Screening and Assessment Tool) data, satisfaction surveys, food diaries, and related research instruments.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 + SQLModel
- **Migrations**: Alembic
- **Database**: MySQL 8.0
- **Authentication**: JWT (access + refresh tokens)
- **Validation**: Pydantic v2
- **Testing**: pytest

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod validation
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **State**: React Context + hooks

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React+Vite)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │   Home   │  │   Forms  │  │  Diary   │  │    Admin    │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTPS/REST
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │   Auth   │  │  SANSA   │  │  Export  │  │   Scoring   │ │
│  │  Router  │  │  Router  │  │  Router  │  │   Service   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                          SQLAlchemy
                              │
┌─────────────────────────────────────────────────────────────┐
│                       MySQL 8.0 Database                     │
│  • Users & Auth           • Scoring Rules & Versions         │
│  • Respondents & Visits   • Food Diary & Photos             │
│  • SANSA Responses        • Knowledge Content               │
│  • MNA, BIA Records       • Facilities                      │
│  • Satisfaction Survey    • Audit Logs                      │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Authentication & Authorization
- **Admin/Staff**: JWT-based (access + refresh tokens)
- **Respondents**: Anonymous code or participant code (no login required)
- **Roles**: admin (full access), staff (data entry), respondent (self-report)

### 2. Data Collection Instruments

#### SANSA Tool
- **Screening**: 4 questions with scores
- **Dietary Behavior**: 12 items with scores
- **Total Score**: Configurable calculation (screening + diet)
- **Classification**: Configurable thresholds (normal/at-risk/malnourished)

#### Satisfaction Survey
- Likert scale items
- Open-ended comments

#### MNA (Mini Nutritional Assessment)
- Full form (staff or respondent entry)
- Configurable scoring

#### BIA & Anthropometry
- Body composition data
- Waist circumference
- Staff-entered

#### Food Diary
- Date, time, meal type
- Menu description
- Multiple photo uploads

### 3. Content Management
- **Knowledge Posts**: Infographic content (admin CRUD)
- **Health Facilities**: Service center directory (admin CRUD)

### 4. Export & Reporting
- **SPSS CSV Format**: Wide format with codebook headers
- **Datasets**: Per instrument + combined
- **Filters**: Date range, facility, staff, etc.

## Data Flow

### Respondent Flow
1. Enter participant code OR generate anonymous code
2. Complete Section 1 (demographics)
3. Complete SANSA screening + dietary behavior
4. View results and recommendations
5. Complete satisfaction survey
6. (Optional) Add food diary entries

### Staff Flow
1. Login with JWT
2. Search/create respondent
3. Enter staff-administered instruments (BIA, MNA)
4. Review/edit data

### Admin Flow
1. Login with JWT
2. Manage users (staff accounts)
3. Manage content (knowledge, facilities)
4. Configure scoring rules
5. Export data for analysis

## Security Features
- JWT tokens with expiration
- Password hashing (bcrypt)
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- File upload validation (type, size)
- Rate limiting (optional)

## Database Design Principles
- **Normalized schema**: Avoid data redundancy
- **Audit trails**: Created/updated timestamps, user tracking
- **Soft deletes**: Preserve data integrity
- **Versioning**: Instrument and scoring rule versions
- **Indexes**: Optimize common queries
- **Foreign keys**: Enforce referential integrity

## Scoring System Architecture

### Configurable Scoring
- Store scoring rules in database tables
- Version control for rule changes
- Track which version was used for each assessment
- Support multiple result classification levels

### Score Calculation Service
```python
1. Fetch scoring rule version (current or specific)
2. Calculate item scores
3. Calculate totals
4. Determine classification level
5. Store: raw answers + computed scores + rule version ID
```

## File Storage
- **Location**: Local filesystem (`/uploads` directory)
- **Organization**: By upload date (YYYY/MM/DD/)
- **Naming**: UUID-based to prevent conflicts
- **Metadata**: Stored in database (original name, size, type)
- **Validation**: MIME type, file extension, size limits

## Export Format (SPSS)

### Variable Naming Convention
- `respondent_code`: Anonymous identifier
- `visit_date`: Visit timestamp
- `sansa_q1`, `sansa_q2`, ...: SANSA screening items
- `sansa_d01`, `sansa_d02`, ...: SANSA dietary behavior items
- `sansa_screening_total`: Screening subscore
- `sansa_diet_total`: Dietary behavior subscore
- `sansa_total`: Overall score
- `sansa_level`: Classification result
- `mna_q1`, `mna_q2`, ...: MNA items
- `mna_total`, `mna_category`: MNA results
- `sat_q1`, `sat_q2`, ...: Satisfaction items
- `sat_comment`: Open text

## Development Workflow

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment Considerations
- Environment variables for configuration
- Database connection pooling
- Static file serving (uploads)
- HTTPS/SSL in production
- Database backups
- Log rotation
- Monitoring and error tracking

## Research Requirements Compliance
✅ Data integrity: Raw answers + computed scores + version tracking
✅ Audit trails: User and timestamp tracking
✅ Configurable thresholds: Database-stored scoring rules
✅ Minimal PII: Pseudonymous codes
✅ Accessibility: Large font toggle, high contrast
✅ SPSS export: Wide format with codebook headers
