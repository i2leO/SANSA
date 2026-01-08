# SANSA Backend API

FastAPI backend for the SANSA (Self-administered Nutrition Screening and Assessment Tool) research system.

## Features

- ✅ JWT Authentication (access + refresh tokens)
- ✅ User management (admin/staff roles)
- ✅ Anonymous respondent codes
- ✅ SANSA screening & dietary assessment
- ✅ Configurable scoring thresholds
- ✅ MNA, BIA, Satisfaction surveys
- ✅ Food diary with photo uploads
- ✅ Knowledge content management
- ✅ Facility directory
- ✅ SPSS CSV exports
- ✅ Audit trails

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2

## Prerequisites

- Python 3.11 or higher
- MySQL 8.0 or higher
- pip and virtualenv

## Installation

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure your settings:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/sansa_db
JWT_SECRET_KEY=your-secret-key-min-32-characters-long
FRONTEND_URL=http://localhost:5173
```

**Important**: Change the `JWT_SECRET_KEY` to a strong random string for production!

### 4. Create Database

Create the MySQL database:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE sansa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 5. Run Migrations

Initialize Alembic and create database tables:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Seed Database

Populate database with default data:

```bash
python scripts/seed.py
```

This creates:
- Default admin user (username: `admin`, password: `admin123`)
- SANSA scoring version with default thresholds
- MNA scoring version with standard thresholds
- Sample health facilities

**Change the admin password after first login!**

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication
- `POST /auth/login` - Login with username/password
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `POST /auth/register` - Register new user (admin only)
- `GET /auth/users` - List users (admin only)

### Respondents
- `POST /respondents` - Create respondent (generates anonymous code)
- `GET /respondents/{code}` - Get respondent by code
- `GET /respondents` - List respondents (staff/admin)
- `PUT /respondents/{id}` - Update respondent
- `POST /respondents/check-code` - Check if code exists

### SANSA
- `POST /sansa` - Submit SANSA assessment (auto-calculates scores)
- `GET /sansa/{id}` - Get SANSA response
- `GET /sansa/visit/{visit_id}` - Get SANSA by visit
- `GET /sansa/{id}/advice` - Get advice based on result level

### Exports (Staff/Admin only)
- `GET /exports/sansa.csv` - Export SANSA data (SPSS format)
- `GET /exports/mna.csv` - Export MNA data
- `GET /exports/bia.csv` - Export BIA data
- `GET /exports/combined.csv` - Export combined dataset

Query parameters for exports:
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `facility_id`: Filter by facility

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic config
├── app/
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database connection
│   ├── config.py        # App configuration
│   ├── auth.py          # Authentication utilities
│   ├── main.py          # FastAPI application
│   ├── routers/         # API route handlers
│   │   ├── auth.py
│   │   ├── respondents.py
│   │   ├── sansa.py
│   │   └── exports.py
│   └── services/        # Business logic
│       ├── scoring_service.py
│       └── export_service.py
├── scripts/
│   └── seed.py          # Database seeding
├── uploads/             # File upload directory
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── alembic.ini          # Alembic configuration
```

## Database Models

### Core Entities
- **User**: Admin and staff accounts
- **Respondent**: Anonymous participants
- **Visit**: Data collection timepoints
- **Facility**: Health service centers

### Instruments
- **SANSAResponse** + **SANSAItem**: SANSA assessment
- **MNAResponse** + **MNAItem**: MNA assessment
- **BIARecord**: Body composition measurements
- **SatisfactionResponse** + **SatisfactionItem**: Satisfaction survey
- **FoodDiaryEntry** + **FoodDiaryPhoto**: Food diary

### Configuration
- **ScoringRuleVersion**: Scoring version control
- **ScoringRuleValue**: Classification thresholds
- **KnowledgePost**: Educational content
- **AuditLog**: Change tracking

## Scoring System

The scoring system is fully configurable via database tables:

1. **Scoring Rule Versions**: Define versions for each instrument
2. **Scoring Rule Values**: Define classification levels and thresholds
3. **Automatic Calculation**: Scores computed on submission
4. **Version Tracking**: Each response stores which version was used

### Default SANSA Thresholds

- **Normal**: 37-52 points
- **At Risk**: 24-36 points
- **Malnourished**: 0-23 points

### Default MNA Thresholds

- **Normal**: 24-30 points
- **At Risk**: 17-23.5 points
- **Malnourished**: 0-16.5 points

Thresholds can be updated via admin panel or database queries.

## SPSS Export Format

Exports use SPSS-compatible CSV format:

### Variable Naming
- `respondent_code`: Participant identifier
- `sansa_q1` - `sansa_q4`: SANSA screening items
- `sansa_d01` - `sansa_d12`: SANSA dietary items
- `sansa_total`: Total score
- `sansa_level`: Classification (1=normal, 2=at-risk, 3=malnourished)
- `mna_q01` - `mna_q18`: MNA items
- `bia_weight`, `bia_height`, `bia_bmi`: Anthropometry

### Categorical Encoding
- **Sex**: 1=male, 2=female, 3=other, 9=prefer not to say
- **Classification levels**: 1=normal, 2=at-risk, 3=malnourished

## Security Features

- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Role-based access control (admin/staff)
- CORS protection
- Input validation with Pydantic
- SQL injection prevention via ORM
- Soft deletes for data preservation

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Common Tasks

### Create New Admin User

```bash
python scripts/seed.py
```

### Create New Migration

```bash
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### Update Scoring Thresholds

```sql
-- Update SANSA "at risk" threshold
UPDATE scoring_rule_values 
SET min_score = 25, max_score = 37 
WHERE level_code = 'at_risk' 
AND version_id = (
    SELECT id FROM scoring_rule_versions 
    WHERE instrument_name = 'SANSA' AND is_active = TRUE
);
```

### Generate Anonymous Code

The system automatically generates codes in format: `RES` + 8 random characters
Example: `RESAB12CD34`

## Troubleshooting

### Database Connection Error

Check your DATABASE_URL in `.env`:
```env
DATABASE_URL=mysql+pymysql://user:password@host:port/database
```

### Migration Errors

Reset migrations (development only):
```bash
alembic downgrade base
alembic upgrade head
```

### JWT Errors

Ensure JWT_SECRET_KEY is at least 32 characters:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use strong `JWT_SECRET_KEY`
3. Use production database credentials
4. Set up HTTPS/SSL
5. Use process manager (systemd, supervisor)
6. Set up database backups
7. Configure log rotation
8. Use reverse proxy (nginx)

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support

For issues or questions, refer to the main project documentation.
