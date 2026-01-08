# SANSA - Research Data Collection System

**Self-administered Nutrition Screening and Assessment Tool**

A production-ready web application for collecting nutrition assessment data, food diaries, and related research instruments. Built with FastAPI (backend) and React + Vite (frontend).

## 🎯 System Overview

SANSA is a comprehensive research system designed for:
- **Nutrition Screening**: SANSA 4-item screening questionnaire
- **Dietary Assessment**: 12-item dietary behavior assessment
- **Additional Tools**: MNA, BIA, satisfaction surveys, food diary
- **Content Management**: Educational content and facility directories
- **Data Export**: SPSS-compatible CSV exports for research analysis

### Key Features

✅ **Configurable Scoring** - Database-stored thresholds that can be updated without code changes  
✅ **Anonymous Codes** - Privacy-focused respondent identification  
✅ **JWT Authentication** - Secure admin/staff access  
✅ **Audit Trails** - Track all data changes for research integrity  
✅ **Accessibility** - Large text mode, high contrast support  
✅ **Multi-instrument** - SANSA, MNA, BIA, satisfaction, food diary  
✅ **Export Ready** - SPSS CSV format with proper variable naming  

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Frontend (React + Vite + TS)      │
│   - Respondent forms                │
│   - Admin dashboard                 │
│   - Knowledge center                │
└──────────────┬──────────────────────┘
               │ REST API (HTTPS)
┌──────────────┴──────────────────────┐
│   Backend (FastAPI + Python)        │
│   - JWT Authentication              │
│   - Scoring services                │
│   - Export services                 │
└──────────────┬──────────────────────┘
               │ SQLAlchemy ORM
┌──────────────┴──────────────────────┐
│   Database (MySQL 8.0)              │
│   - Research data                   │
│   - Scoring rules                   │
│   - Audit logs                      │
└─────────────────────────────────────┘
```

## 📋 Project Structure

```
SANSA/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── auth.py         # JWT authentication
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   ├── scripts/            # Utility scripts
│   │   └── seed.py         # Database seeding
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend docs
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── stores/        # State management
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   ├── package.json       # Node dependencies
│   └── README.md         # Frontend docs
│
└── docs/                   # Documentation
    ├── ARCHITECTURE.md    # System architecture
    └── DATABASE_SCHEMA.md # Database design
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** and pip
- **Node.js 18+** and npm
- **MySQL 8.0+**
- **Git**

### 1. Clone Repository

```bash
git clone <repository-url>
cd SANSA
```

### 2. Setup Database

Create MySQL database:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE sansa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and JWT secret

# Run migrations
alembic upgrade head

# Seed database with default data
python scripts/seed.py

# Start server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000  
API docs: http://localhost:8000/docs

### 4. Setup Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000)

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### 5. Access the System

**For Respondents:**
- Go to http://localhost:5173
- Click "Start Assessment"
- Choose "New Participant" to get an anonymous code

**For Admin/Staff:**
- Go to http://localhost:5173/admin/login
- Default credentials: `admin` / `admin123`
- **⚠️ Change password after first login!**

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and tech stack
- [Database Schema](docs/DATABASE_SCHEMA.md) - Complete database design
- [Backend README](backend/README.md) - API documentation
- [Frontend README](frontend/README.md) - Frontend guide

## 🔧 Configuration

### Backend (.env)

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/sansa_db
JWT_SECRET_KEY=your-secret-key-min-32-characters
FRONTEND_URL=http://localhost:5173
UPLOAD_DIR=./uploads
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## 📊 Data Export

Export research data in SPSS-compatible CSV format:

1. Login as admin/staff
2. Navigate to Export section
3. Choose export type:
   - SANSA data only
   - MNA data only
   - BIA data only
   - Combined dataset

Exports include:
- Proper variable naming (e.g., `sansa_q1`, `mna_q01`)
- Categorical encoding (numeric codes)
- Timestamp fields
- Respondent codes (anonymous)

## 🔐 Security Features

- **JWT Authentication** - Access + refresh tokens
- **Password Hashing** - bcrypt with salt
- **Role-Based Access** - Admin and staff roles
- **Input Validation** - Pydantic schemas
- **SQL Injection Prevention** - ORM queries only
- **CORS Protection** - Configured origins
- **File Upload Validation** - Type and size checks

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test  # When implemented
```

## 📦 Database Schema Highlights

### Core Tables
- `users` - Admin and staff accounts
- `respondents` - Anonymous participants
- `visits` - Data collection timepoints
- `scoring_rule_versions` - Configurable scoring

### Instrument Tables
- `sansa_responses` + `sansa_items`
- `mna_responses` + `mna_items`
- `bia_records`
- `satisfaction_responses` + `satisfaction_items`
- `food_diary_entries` + `food_diary_photos`

### Content Tables
- `knowledge_posts` - Educational content
- `facilities` - Health service centers

## 🎨 Frontend Features

- **Responsive Design** - Mobile and desktop
- **Accessibility** - Large text mode toggle
- **Form Validation** - React Hook Form + Zod
- **State Management** - Zustand stores
- **Routing** - React Router v6
- **Styling** - Tailwind CSS

## 🔄 Research Workflow

1. **Respondent Registration**
   - Generate anonymous code OR enter existing code
   - Fill general information (demographics)

2. **Assessment**
   - Complete SANSA screening (4 questions)
   - Complete dietary behavior (12 items)
   - Auto-calculate scores and classification
   - View results and recommendations

3. **Follow-up (Optional)**
   - Satisfaction survey
   - Food diary entries with photos
   - Additional visits (follow-up data)

4. **Staff Tasks (Optional)**
   - Enter BIA measurements
   - Enter MNA assessments
   - Manage respondent data

5. **Data Export**
   - Filter by date range, facility
   - Export to SPSS CSV format
   - Analyze in statistical software

## 🛠️ Common Tasks

### Update Scoring Thresholds

```bash
mysql -u root -p sansa_db
```

```sql
-- View current thresholds
SELECT * FROM scoring_rule_values 
WHERE version_id = (
    SELECT id FROM scoring_rule_versions 
    WHERE instrument_name='SANSA' AND is_active=TRUE
);

-- Update threshold
UPDATE scoring_rule_values 
SET min_score=25, max_score=37 
WHERE level_code='at_risk' AND version_id=...;
```

### Create New Admin User

```bash
cd backend
python scripts/seed.py  # Creates default admin
```

Or via API:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"newadmin","email":"admin@example.com","password":"securepass","role":"admin"}'
```

### Reset Database

```bash
cd backend
alembic downgrade base
alembic upgrade head
python scripts/seed.py
```

## 🚀 Production Deployment

### Backend

1. Set production environment variables
2. Use production database
3. Set `DEBUG=False`
4. Use strong `JWT_SECRET_KEY`
5. Set up HTTPS/SSL
6. Use process manager (systemd, supervisor)
7. Configure log rotation
8. Set up automated backups

### Frontend

1. Build production bundle:
```bash
npm run build
```

2. Serve `dist/` directory with nginx/Apache
3. Configure CORS origins
4. Enable HTTPS

### Database

1. Regular backups (daily recommended)
2. Secure MySQL credentials
3. Enable MySQL SSL if remote
4. Monitor disk space
5. Set up replication (optional)

## 📈 System Requirements

### Minimum
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space
- MySQL 8.0+
- Python 3.11+
- Node.js 18+

### Recommended (Production)
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB disk space (SSD)
- Load balancer for frontend
- Database replication

## 🐛 Troubleshooting

### Backend won't start
- Check DATABASE_URL in .env
- Verify MySQL is running
- Check port 8000 is not in use
- Run `alembic upgrade head`

### Frontend won't start
- Check Node.js version (18+)
- Delete `node_modules` and reinstall
- Check port 5173 is not in use
- Verify .env has correct API URL

### Database errors
- Check MySQL service is running
- Verify database exists
- Check user permissions
- Review migration status

## 🤝 Contributing

This is a research system. For modifications:
1. Test thoroughly with sample data
2. Update documentation
3. Maintain data integrity
4. Follow existing code patterns

## 📄 License

[Specify license here]

## 👥 Team

[Add team information]

## 📞 Support

For issues or questions:
- Check documentation in `/docs`
- Review API docs at `/docs` endpoint
- Check backend/frontend README files

---

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Status:** Production Ready (with noted limitations for full implementation)
