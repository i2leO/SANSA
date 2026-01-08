# Contributing to SANSA

Thank you for your interest in contributing to the SANSA research data collection system. This document provides guidelines for making contributions.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This is a research system handling sensitive health data. Contributors must:

- ✅ Prioritize data integrity and privacy
- ✅ Test thoroughly before submitting changes
- ✅ Document all changes clearly
- ✅ Follow existing code patterns
- ❌ Never commit sensitive data (credentials, PII)
- ❌ Never bypass validation or security checks

## Getting Started

### Prerequisites

- Familiarity with Python (FastAPI, SQLAlchemy)
- Familiarity with TypeScript and React
- Understanding of REST APIs
- Basic SQL knowledge
- Git workflow knowledge

### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/SANSA.git
   cd SANSA
   ```

3. Run setup script:
   ```bash
   ./setup.sh
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### 1. Plan Your Changes

- Check existing issues and pull requests
- Discuss major changes before implementing
- Break large features into smaller, testable parts

### 2. Make Changes

Follow this workflow:

```bash
# Create feature branch
git checkout -b feature/add-new-instrument

# Make your changes
# ...

# Run tests
./dev.sh test-backend

# Commit with descriptive message
git commit -m "feat: Add new dietary assessment instrument"

# Push to your fork
git push origin feature/add-new-instrument
```

### 3. Test Thoroughly

Before submitting:

- [ ] Backend tests pass
- [ ] Frontend builds without errors
- [ ] Manual testing completed
- [ ] Database migrations work correctly
- [ ] No sensitive data in commits

## Coding Standards

### Backend (Python)

**Style Guide:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions/classes

**Example:**
```python
from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, schemas

def get_respondents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[models.Respondent]:
    """
    Retrieve respondents from database with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        search: Optional search term for code
        
    Returns:
        List of Respondent objects
    """
    query = db.query(models.Respondent).filter(
        models.Respondent.deleted_at.is_(None)
    )
    
    if search:
        query = query.filter(
            models.Respondent.code.ilike(f"%{search}%")
        )
    
    return query.offset(skip).limit(limit).all()
```

**Database Changes:**
- Always use Alembic migrations
- Never modify models without migration
- Test migrations up and down
- Document breaking changes

**API Endpoints:**
- Use appropriate HTTP methods
- Return consistent response formats
- Include proper status codes
- Validate input with Pydantic schemas

### Frontend (TypeScript/React)

**Style Guide:**
- Use TypeScript strictly (no `any` types)
- Functional components with hooks
- Use Tailwind for styling
- Maximum line length: 100 characters

**Example:**
```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import type { Respondent } from '@/types';

interface RespondentListProps {
  searchTerm?: string;
  onSelect: (respondent: Respondent) => void;
}

export function RespondentList({ searchTerm, onSelect }: RespondentListProps) {
  const [respondents, setRespondents] = useState<Respondent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRespondents = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get<Respondent[]>('/respondents', {
          params: { search: searchTerm }
        });
        setRespondents(response.data);
      } catch (err) {
        setError('Failed to load respondents');
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRespondents();
  }, [searchTerm]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="space-y-2">
      {respondents.map((respondent) => (
        <button
          key={respondent.id}
          onClick={() => onSelect(respondent)}
          className="w-full text-left p-4 border rounded hover:bg-gray-50"
        >
          <div className="font-medium">{respondent.code}</div>
          <div className="text-sm text-gray-600">
            Created: {new Date(respondent.created_at).toLocaleDateString()}
          </div>
        </button>
      ))}
    </div>
  );
}
```

**Component Structure:**
- One component per file
- Props interface defined first
- Hooks at top of component
- Event handlers before render
- Return statement last

**State Management:**
- Use Zustand stores for global state
- Use React state for local UI state
- Don't duplicate API data in store

## Testing Guidelines

### Backend Tests

Location: `backend/tests/`

**Unit Tests:**
```python
# tests/test_scoring.py
import pytest
from app.services.scoring_service import calculate_sansa_score

def test_calculate_sansa_score_normal():
    """Test SANSA score calculation for normal result."""
    screening_score = 4
    dietary_score = 45
    
    result = calculate_sansa_score(screening_score, dietary_score)
    
    assert result['level'] == 'normal'
    assert result['total_score'] == 49

def test_calculate_sansa_score_at_risk():
    """Test SANSA score calculation for at-risk result."""
    screening_score = 2
    dietary_score = 25
    
    result = calculate_sansa_score(screening_score, dietary_score)
    
    assert result['level'] == 'at_risk'
```

**API Tests:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_respondent():
    """Test respondent creation endpoint."""
    response = client.post("/respondents/", json={
        "code": "RES12345678"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data['code'] == "RES12345678"
    assert 'id' in data
```

**Run tests:**
```bash
cd backend
source venv/bin/activate
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests

Location: `frontend/src/__tests__/`

**Component Tests:**
```typescript
// __tests__/RespondentList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { RespondentList } from '@/components/RespondentList';
import { vi } from 'vitest';

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn()
  }
}));

describe('RespondentList', () => {
  it('renders respondents after loading', async () => {
    const mockRespondents = [
      { id: 1, code: 'RES12345678', created_at: '2024-01-01' }
    ];
    
    vi.mocked(api.get).mockResolvedValue({ data: mockRespondents });
    
    render(<RespondentList onSelect={vi.fn()} />);
    
    await waitFor(() => {
      expect(screen.getByText('RES12345678')).toBeInTheDocument();
    });
  });
});
```

## Documentation

### Code Documentation

**Backend:**
- Docstrings for all public functions
- Type hints for all parameters
- Document exceptions raised

**Frontend:**
- JSDoc comments for complex logic
- Props interfaces document all properties
- README for each major feature

### API Documentation

- FastAPI auto-generates docs at `/docs`
- Add descriptions to Pydantic schemas:
  ```python
  class RespondentCreate(BaseModel):
      """Schema for creating a new respondent."""
      code: str = Field(
          ..., 
          min_length=11, 
          max_length=11,
          description="Unique respondent code (RES + 8 chars)"
      )
  ```

### Database Schema

- Document schema changes in migrations
- Update [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
- Include ER diagrams for major changes

## Submitting Changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add MNA assessment form
fix: Correct SANSA score calculation
docs: Update API documentation
refactor: Simplify respondent validation
test: Add tests for export service
chore: Update dependencies
```

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples:**
```
feat(api): Add BIA measurement endpoints

Implement POST and GET endpoints for BIA measurements.
Includes validation for weight, height, and impedance values.

Closes #42
```

```
fix(scoring): Correct threshold comparison logic

The at-risk threshold was using >= instead of > which
caused incorrect classification at boundary values.

Fixes #58
```

### Pull Request Process

1. **Update your branch:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Create pull request:**
   - Clear title describing the change
   - Description includes:
     - What changed
     - Why it changed
     - Testing performed
     - Screenshots (if UI change)
   - Link related issues

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Backend tests pass
   - [ ] Frontend builds successfully
   - [ ] Manual testing completed
   - [ ] Database migrations tested
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex logic
   - [ ] Documentation updated
   - [ ] No warnings or errors
   - [ ] Tests added/updated
   
   ## Related Issues
   Closes #XX
   ```

4. **Review process:**
   - Address reviewer feedback
   - Keep discussions professional
   - Update PR based on comments
   - Request re-review when ready

### Review Checklist

Reviewers should verify:

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] No performance regressions
- [ ] Database migrations are safe
- [ ] Error handling is appropriate
- [ ] Logging is adequate
- [ ] No hardcoded values
- [ ] Backwards compatibility maintained

## Common Contributions

### Adding a New Instrument

Example: Adding a new dietary assessment

1. **Backend:**
   ```bash
   # 1. Create database migration
   cd backend
   alembic revision -m "add_new_instrument_tables"
   
   # 2. Define models in app/models.py
   # 3. Create Pydantic schemas in app/schemas.py
   # 4. Implement router in app/routers/new_instrument.py
   # 5. Add scoring logic if needed
   # 6. Write tests
   ```

2. **Frontend:**
   ```bash
   # 1. Add types in src/types/index.ts
   # 2. Create form page in src/pages/NewInstrumentPage.tsx
   # 3. Add route in src/App.tsx
   # 4. Update navigation
   ```

3. **Documentation:**
   - Update DATABASE_SCHEMA.md
   - Update API documentation
   - Add usage examples

### Fixing Bugs

1. Create issue describing bug
2. Write failing test that reproduces bug
3. Fix the bug
4. Verify test passes
5. Submit PR referencing issue

### Improving Performance

1. Profile the code to identify bottleneck
2. Implement optimization
3. Benchmark before and after
4. Document performance gains
5. Ensure no functionality changes

## Questions?

- Check [documentation](docs/)
- Review existing code for patterns
- Ask in discussions/issues
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to SANSA! Your work helps advance nutrition research. 🎉
