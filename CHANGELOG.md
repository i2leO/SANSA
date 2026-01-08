# Changelog

All notable changes to the SANSA project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### To Be Implemented

- Complete SANSA form with all 16 questions (4 screening + 12 dietary)
- MNA assessment router and frontend form
- BIA measurement router and frontend form
- Satisfaction survey item configuration UI
- Food diary photo upload functionality
- Knowledge post CRUD endpoints and admin UI
- Facility CRUD endpoints and admin UI
- Visit management router and UI
- Scoring rule management admin UI
- Full admin dashboard with data tables
- Comprehensive test suite (backend and frontend)
- Email notifications for staff
- Advanced export filters (date range, facility)
- Data visualization dashboards
- Report generation (PDF)
- Multi-language support (Thai/English)

## [1.0.0] - 2026-01-20

### Initial Release - Production Ready Foundation

This is the first production-ready release of SANSA (Self-administered Nutrition Screening and Assessment Tool), a comprehensive research data collection system.

### Added - Backend

#### Core Infrastructure

- FastAPI 0.109.0 application with async support
- SQLAlchemy 2.0 ORM with MySQL 8.0 support
- Alembic database migration system
- Pydantic v2 validation schemas
- Python 3.11+ compatibility
- Environment-based configuration management

#### Authentication & Authorization

- JWT authentication with access and refresh tokens
- Bcrypt password hashing with salt
- Role-based access control (admin, staff)
- Token refresh mechanism
- Anonymous respondent code generation (RES + 8 random chars)

#### Database Schema (16 Tables)

- **User Management**: `users` table with role support
- **Research Data**:
  - `respondents` - Anonymous participant records
  - `visits` - Multiple data collection timepoints
  - `sansa_responses` + `sansa_items` - SANSA assessment data
  - `mna_responses` + `mna_items` - MNA assessment data
  - `bia_records` - Body composition measurements
  - `satisfaction_responses` + `satisfaction_items` - Survey data
  - `food_diary_entries` + `food_diary_photos` - Food diary with images
- **Content Management**:
  - `knowledge_posts` - Educational content
  - `facilities` - Health service center directory
- **Configuration**:
  - `scoring_rule_versions` - Versioned scoring configurations
  - `scoring_rules` - Instrument scoring metadata
  - `scoring_rule_values` - Threshold values by level
- **Audit**: `audit_log` - Complete change tracking

#### API Endpoints

**Authentication** (`/auth`):

- `POST /auth/register` - Create new user (admin only)
- `POST /auth/login` - Authenticate user
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

**Respondents** (`/respondents`):

- `POST /respondents` - Create respondent with auto-generated code
- `GET /respondents` - List all respondents (paginated)
- `GET /respondents/{id}` - Get respondent details
- `PUT /respondents/{id}` - Update respondent
- `DELETE /respondents/{id}` - Soft delete respondent

**SANSA Assessment** (`/sansa`):

- `POST /sansa` - Submit SANSA response (auto-calculates scores)
- `GET /sansa/{id}` - Get SANSA response details
- `GET /sansa/{id}/advice` - Get nutritional advice based on results

**Data Export** (`/exports`):

- `GET /exports/sansa.csv` - Export SANSA data in SPSS format
- `GET /exports/mna.csv` - Export MNA data
- `GET /exports/bia.csv` - Export BIA measurements
- `GET /exports/combined.csv` - Export all data combined

#### Services

**Scoring Service**:

- Configurable threshold-based scoring
- SANSA total score calculation (screening + dietary)
- SANSA classification (normal/at-risk/malnourished)
- MNA score calculation and classification
- Database-stored thresholds (no hardcoded values)
- Version tracking for research reproducibility

**Export Service**:

- SPSS-compatible CSV generation
- Proper variable naming conventions:
  - `sansa_q1-q4` (screening questions)
  - `sansa_d01-d12` (dietary behavior items)
  - `mna_q01-q18` (MNA items)
  - `bia_weight`, `bia_height`, `bia_bmi`, etc.
- Numeric encoding for categorical variables
- Respondent code anonymization
- Timestamp fields for all records

#### Database Management

**Migrations**:

- Alembic configuration with auto-generation
- Migration templates included
- Version control for schema changes

**Seeding**:

- Default admin user (username: `admin`, password: `admin123`)
- SANSA scoring rules (version 1.0):
  - Normal: 38-48 points
  - At-risk: 25-37 points
  - Malnourished: 0-24 points
- MNA scoring rules (version 1.0):
  - Normal: 24-30 points
  - At-risk: 17-23.5 points
  - Malnourished: <17 points
- Sample facilities data

#### Security Features

- CORS middleware with configurable origins
- SQL injection prevention (ORM-only queries)
- Input validation on all endpoints
- Password strength requirements
- File upload validation (type and size)
- Soft deletes preserve data integrity

### Added - Frontend

#### Core Infrastructure

- React 18 with TypeScript 5.3
- Vite 5.x build tool with HMR
- React Router v6 for routing
- Tailwind CSS 3.4 for styling
- Axios HTTP client with interceptors
- Zustand state management

#### Features

**Public Pages**:

- Home page with navigation cards
- Respondent assessment flow:
  - Start page (new/existing code)
  - General information form (demographics)
  - SANSA form (placeholder for 16 questions)
  - Results page (score and advice display)
  - Satisfaction survey (placeholder)
  - Food diary entry (placeholder)
- Knowledge center (placeholder)
- Health facilities directory (placeholder)

**Admin Pages**:

- Admin login with JWT authentication
- Protected admin dashboard
- Logout functionality

**Form Validation**:

- React Hook Form for form management
- Zod schema validation
- Real-time error messages
- Field-level validation

**State Management**:

- Auth store (Zustand):
  - User authentication state
  - Login/logout actions
  - Token persistence
- UI store (Zustand):
  - Large text mode toggle
  - Accessibility preferences
  - Persisted to localStorage

**API Integration**:

- Axios client with base URL configuration
- Request interceptor adds JWT token automatically
- Response interceptor handles token refresh
- Error handling and retry logic

#### Accessibility Features

- Large text mode toggle (18px base / 22px large)
- High contrast support
- Keyboard navigation
- ARIA labels and roles
- Focus management
- Screen reader friendly

#### Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch-friendly button sizes (min 44x44px)
- Fluid typography
- Flexible layouts with Tailwind

### Added - Documentation

#### Architecture Documentation

- System overview and tech stack
- Architecture diagram (3-tier: Frontend, Backend, Database)
- Component descriptions
- Technology choices and rationale
- Data flow explanations
- Security considerations

#### Database Schema Documentation

- Complete SQL CREATE statements for all 16 tables
- Entity-Relationship (ER) description
- Relationships and foreign keys
- Index definitions
- SPSS variable mapping
- Enum value documentation

#### API Documentation

- Auto-generated Swagger/OpenAPI docs at `/docs`
- Request/response schemas
- Authentication requirements
- Example requests and responses

#### Setup Guides

- Main README with quick start
- Backend README with detailed API docs
- Frontend README with development guide
- Setup script (`setup.sh`) for automated installation
- Development helper script (`dev.sh`) for common tasks

#### Contributing Guidelines

- Code of conduct
- Development workflow
- Coding standards (Python and TypeScript)
- Testing guidelines
- Documentation requirements
- Pull request process
- Review checklist

#### Deployment Guide

- Pre-deployment checklist
- Production configuration examples
- Three deployment options:
  1. Traditional VPS with systemd
  2. Docker Compose
  3. Cloud platforms (AWS, GCP, Azure)
- Security hardening steps
- Monitoring and maintenance
- Backup and recovery procedures
- Troubleshooting guide

### Dependencies - Backend

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pymysql==1.1.0
cryptography==42.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
```

### Dependencies - Frontend

```
react: ^18.2.0
react-dom: ^18.2.0
react-router-dom: ^6.21.3
typescript: ^5.3.3
vite: ^5.0.8
tailwindcss: ^3.4.1
axios: ^1.6.5
zustand: ^4.5.0
react-hook-form: ^7.49.3
zod: ^3.22.4
```

### Configuration

**Backend Environment Variables**:

- `DATABASE_URL` - MySQL connection string
- `JWT_SECRET_KEY` - Secret for JWT signing
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiry (default: 7)
- `FRONTEND_URL` - CORS allowed origin
- `UPLOAD_DIR` - File upload directory (default: ./uploads)

**Frontend Environment Variables**:

- `VITE_API_URL` - Backend API base URL

### System Requirements

**Minimum**:

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space

**Recommended (Production)**:

- 4+ CPU cores
- 8+ GB RAM
- 50+ GB SSD
- Load balancer
- Database replication

### Known Limitations

This release provides a complete, runnable foundation with core functionality. The following features are placeholders for future implementation:

1. **SANSA Form**: Currently a placeholder; needs implementation of all 16 questions
2. **MNA Form**: Router exists but frontend form not implemented
3. **BIA Form**: Router exists but frontend form not implemented
4. **Satisfaction Survey**: Structure exists but items need configuration
5. **Food Diary**: Entry form exists but photo upload not implemented
6. **Knowledge Posts**: Database schema exists but CRUD UI not implemented
7. **Facilities**: Database schema exists but CRUD UI not implemented
8. **Admin Dashboard**: Basic structure exists but full data management UI pending
9. **Visit Management**: Router planned but not yet implemented
10. **Scoring Rules UI**: Database-driven but admin UI for configuration pending

### Migration Notes

This is the initial release, so no migrations are required.

### Breaking Changes

None (initial release).

### Security Notes

⚠️ **Important**: Before deploying to production:

1. Change default admin password (`admin123`)
2. Generate strong JWT secret key (min 32 characters)
3. Configure CORS allowed origins
4. Enable HTTPS/SSL
5. Set up database backups
6. Configure firewall rules
7. Review and update security headers
8. Enable rate limiting for sensitive endpoints

### Testing

- Backend test suite framework in place
- Frontend test configuration ready
- Manual testing completed for:
  - Authentication flow
  - Respondent creation
  - Basic API endpoints
  - Form validation
  - Routing
  - State management

### Contributors

[Add contributor names]

### License

[Specify license]

---

## Version History

- **1.0.0** (2026-01-20) - Initial production-ready release

## Roadmap

### Version 1.1.0 (Planned)

- Complete SANSA form implementation (16 questions)
- MNA form frontend
- BIA form frontend
- Full admin dashboard
- Enhanced export filters
- Test suite completion

### Version 1.2.0 (Planned)

- Food diary photo upload
- Knowledge post management UI
- Facility management UI
- Visit tracking
- Scoring rule configuration UI

### Version 2.0.0 (Future)

- Multi-language support (Thai/English)
- Email notifications
- Advanced analytics dashboard
- PDF report generation
- Mobile app integration
- Offline capability

---

For detailed changes in each release, see the [Release Notes](https://github.com/yourusername/sansa/releases).
