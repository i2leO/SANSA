"""Admin-issued personal QR credentials and revocable participant sessions."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from jose import jwt
from sqlalchemy.orm import Session
from app.auth import get_current_active_admin, create_access_token, create_refresh_token
from app.config import get_settings
from app.database import get_db
from app.models import Respondent, User

router = APIRouter(prefix='/participant-auth', tags=['participant-auth'])

class QRLogin(BaseModel):
    secret: str = Field(min_length=32, max_length=128)

@router.post('/respondents/{respondent_id}/qr')
def issue_qr(respondent_id: int, response: Response, db: Session = Depends(get_db), admin: User = Depends(get_current_active_admin)):
    respondent = db.query(Respondent).filter(Respondent.id == respondent_id, Respondent.is_deleted.is_(False)).with_for_update().first()
    if not respondent:
        raise HTTPException(404, 'ไม่พบผู้เข้าร่วม')
    secret = secrets.token_urlsafe(32)
    respondent.qr_secret_hash = hashlib.sha256(secret.encode()).hexdigest()
    db.commit()
    response.headers['Cache-Control'] = 'no-store'
    return {'secret': secret, 'respondent_code': respondent.respondent_code}

@router.post('/users/{user_id}/qr')
def issue_user_qr(user_id: int, response: Response, db: Session = Depends(get_db), admin: User = Depends(get_current_active_admin)):
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).with_for_update().first()
    if not user or user.role not in ('admin', 'staff'):
        raise HTTPException(404, 'ไม่พบบัญชีเจ้าหน้าที่หรือผู้ดูแลระบบ')
    secret = secrets.token_urlsafe(32)
    user.qr_secret_hash = hashlib.sha256(secret.encode()).hexdigest()
    db.commit()
    response.headers['Cache-Control'] = 'no-store'
    return {'secret': secret, 'username': user.username, 'role': user.role}

@router.post('/login')
def qr_login(payload: QRLogin, response: Response, db: Session = Depends(get_db)):
    digest = hashlib.sha256(payload.secret.encode()).hexdigest()
    user = db.query(User).filter(User.qr_secret_hash == digest, User.is_active.is_(True)).first()
    if user and user.role in ('admin', 'staff'):
        claims = {'sub': str(user.id), 'username': user.username, 'role': user.role, 'qr_version': digest}
        access_token = create_access_token(claims)
        refresh_token = create_refresh_token(claims)
        response.headers['Cache-Control'] = 'no-store'
        return {
            'actor_type': 'user',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at,
            },
        }
    respondent = db.query(Respondent).filter(Respondent.qr_secret_hash == digest, Respondent.is_deleted.is_(False)).first()
    if not respondent:
        raise HTTPException(401, 'QR ไม่ถูกต้องหรือถูกเปลี่ยนแล้ว กรุณาติดต่อผู้ดูแลระบบ')
    settings = get_settings()
    token = jwt.encode({'sub': str(respondent.id), 'type': 'participant', 'qr_version': digest,
                        'exp': datetime.now(timezone.utc) + timedelta(hours=1)}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    response.headers['Cache-Control'] = 'no-store'
    return {'actor_type': 'participant', 'access_token': token, 'respondent_code': respondent.respondent_code, 'expires_in': 3600}
