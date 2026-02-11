from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_active_admin, get_current_staff_or_admin
from app.database import get_db
from app.models import ScoringRuleValue, ScoringRuleVersion, User
from app.schemas import (
    MessageResponse,
    ScoringRuleValueResponse,
    ScoringRuleVersionResponse,
)

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.get("/versions", response_model=list[ScoringRuleVersionResponse])
def list_scoring_versions(
    instrument_name: Optional[str] = None,
    include_inactive: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    query = db.query(ScoringRuleVersion).options(
        joinedload(ScoringRuleVersion.scoring_rule_values)
    )

    if instrument_name:
        query = query.filter(ScoringRuleVersion.instrument_name == instrument_name)

    if not include_inactive:
        query = query.filter(ScoringRuleVersion.is_active == True)

    versions = query.order_by(ScoringRuleVersion.created_at.desc()).all()

    # Sort nested rule values for stable output
    for version in versions:
        version.scoring_rule_values.sort(key=lambda rv: (rv.level_order, rv.id))

    return versions


@router.put("/values/{value_id}", response_model=ScoringRuleValueResponse)
def update_scoring_value(
    value_id: int,
    min_score: Optional[Decimal] = None,
    max_score: Optional[Decimal] = None,
    level_name: Optional[str] = None,
    advice_text: Optional[str] = None,
    level_order: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    value = db.query(ScoringRuleValue).filter(ScoringRuleValue.id == value_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Scoring value not found")

    if min_score is not None:
        value.min_score = min_score
    if max_score is not None:
        value.max_score = max_score
    if level_name is not None:
        value.level_name = level_name
    if advice_text is not None:
        value.advice_text = advice_text
    if level_order is not None:
        value.level_order = level_order

    db.commit()
    db.refresh(value)
    return value


@router.post("/versions/{version_id}/activate", response_model=MessageResponse)
def activate_scoring_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin),
):
    version = (
        db.query(ScoringRuleVersion).filter(ScoringRuleVersion.id == version_id).first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Scoring version not found")

    # Deactivate other versions for the same instrument
    (
        db.query(ScoringRuleVersion)
        .filter(ScoringRuleVersion.instrument_name == version.instrument_name)
        .update({ScoringRuleVersion.is_active: False})
    )

    version.is_active = True
    db.commit()

    return {
        "message": f"Activated scoring version {version.instrument_name} v{version.version_number}"
    }
