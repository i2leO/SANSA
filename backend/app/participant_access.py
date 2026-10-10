"""Ownership checks for the existing participant-data routers."""
from typing import Optional
from fastapi import Depends, Header, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.auth import get_current_user_optional
from app.config import get_settings
from app.database import get_db
from app.models import User, Respondent, Visit, SANSAResponse, MNAResponse, BIARecord, SatisfactionResponse, FoodDiaryEntry

async def require_participant_access(request: Request, db: Session = Depends(get_db),
        staff: Optional[User] = Depends(get_current_user_optional),
        participant_token: Optional[str] = Header(None, alias='X-Respondent-Token')):
    if staff and staff.role in ('admin', 'staff'):
        return
    denied = HTTPException(401, 'กรุณาเข้าสู่ระบบด้วย QR ของคุณ')
    if not participant_token:
        raise denied
    settings = get_settings()
    try:
        payload = jwt.decode(participant_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get('type') != 'participant':
            raise denied
        owner = db.get(Respondent, int(payload['sub']))
        if not owner or owner.is_deleted or not owner.qr_secret_hash or owner.qr_secret_hash != payload.get('qr_version'):
            raise denied
    except (JWTError, KeyError, ValueError, TypeError):
        raise denied
    params = request.path_params
    owner_ids = []
    def identity(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise HTTPException(422, "รหัสข้อมูลไม่ถูกต้อง")
    def from_visit(value):
        visit = db.get(Visit, identity(value))
        if not visit or visit.is_deleted:
            raise HTTPException(404, 'ไม่พบการประเมิน')
        return visit.respondent_id
    if 'respondent_code' in params:
        record = db.query(Respondent).filter_by(respondent_code=params['respondent_code']).first()
        owner_ids.append(record.id if record else None)
    if 'respondent_id' in params:
        owner_ids.append(identity(params['respondent_id']))
    if 'visit_id' in params:
        owner_ids.append(from_visit(params['visit_id']))
    for key, model in [('sansa_response_id',SANSAResponse),('mna_response_id',MNAResponse),('bia_record_id',BIARecord),('satisfaction_response_id',SatisfactionResponse),('entry_id',FoodDiaryEntry)]:
        if key in params:
            record = db.get(model, identity(params[key]))
            if not record:
                raise HTTPException(404, 'ไม่พบข้อมูล')
            owner_ids.append(from_visit(record.visit_id))
    if request.method in ('POST','PUT','PATCH') and 'application/json' in request.headers.get('content-type',''):
        try:
            body = await request.json()
        except ValueError:
            raise HTTPException(422, 'รูปแบบข้อมูลไม่ถูกต้อง')
        if isinstance(body, dict):
            if body.get('visit_id') is not None:
                owner_ids.append(from_visit(body['visit_id']))
            if body.get('respondent_id') is not None:
                owner_ids.append(identity(body['respondent_id']))
    if not owner_ids or any(identity != owner.id for identity in owner_ids):
        raise HTTPException(403, 'ไม่สามารถเข้าถึงข้อมูลผู้เข้าร่วมอื่นได้')
