"""Staff dashboard aggregates; never returns participant-level data."""
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.auth import get_current_staff_or_admin
from app.database import get_db
from app.models import Facility, KnowledgePost, Respondent, User, Visit

router = APIRouter(prefix='/admin', tags=['dashboard'])

@router.get('/dashboard', response_model=dict[str, int])
def dashboard_counts(db: Session = Depends(get_db), current_user: User = Depends(get_current_staff_or_admin)):
    today = datetime.now(ZoneInfo('Asia/Bangkok')).date()
    return {
        'respondents': db.query(Respondent).filter(Respondent.is_deleted.is_(False)).count(),
        'visits_today': db.query(Visit).join(Respondent).filter(Visit.is_deleted.is_(False), Respondent.is_deleted.is_(False), Visit.visit_date == today).count(),
        'knowledge': db.query(KnowledgePost).filter(KnowledgePost.is_deleted.is_(False)).count(),
        'facilities': db.query(Facility).filter(Facility.is_deleted.is_(False)).count(),
        'incomplete_visits': db.query(Visit).join(Respondent).filter(
            Visit.is_deleted.is_(False),
            Respondent.is_deleted.is_(False),
            or_(
                ~Visit.sansa_response.has(),
                ~Visit.mna_response.has(),
                ~Visit.bia_records.any(),
            ),
        ).count(),
        'knowledge_drafts': db.query(KnowledgePost).filter(
            KnowledgePost.is_deleted.is_(False),
            KnowledgePost.is_published.is_(False),
        ).count(),
        'facilities_inactive': db.query(Facility).filter(
            Facility.is_deleted.is_(False),
            Facility.is_active.is_(False),
        ).count(),
    }
