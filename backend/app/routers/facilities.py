from __future__ import annotations

import random
import string
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_staff_or_admin, get_current_user_optional
from app.database import get_db
from app.models import Facility, User
from app.schemas import (
    FacilityCreate,
    FacilityUpdate,
    FacilityResponse,
    MessageResponse,
)

router = APIRouter(prefix="/facilities", tags=["facilities"])


def _generate_facility_code() -> str:
    return "FAC" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


@router.get("", response_model=list[FacilityResponse])
def list_facilities(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """List facilities.

    - Public: active & not deleted
    - Staff/Admin: can request include_inactive=true to see all
    """
    query = db.query(Facility).filter(Facility.is_deleted == False)

    if not current_user or not include_inactive:
        query = query.filter(Facility.is_active == True)

    return query.order_by(Facility.display_order.asc(), Facility.name.asc()).all()


@router.get("/{facility_id}", response_model=FacilityResponse)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = (
        db.query(Facility)
        .filter(Facility.id == facility_id, Facility.is_deleted == False)
        .first()
    )
    if not facility or not facility.is_active:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


@router.post("", response_model=FacilityResponse)
def create_facility(
    payload: FacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    code = payload.code
    if not code:
        while True:
            candidate = _generate_facility_code()
            existing = db.query(Facility).filter(Facility.code == candidate).first()
            if not existing:
                code = candidate
                break

    facility = Facility(
        name=payload.name,
        code=code,
        type=payload.type,
        description=payload.description,
        address=payload.address,
        phone=payload.phone,
        email=str(payload.email) if payload.email else None,
        website=payload.website,
        latitude=payload.latitude,
        longitude=payload.longitude,
        map_link=payload.map_link,
        is_active=payload.is_active,
        display_order=payload.display_order,
        created_by=current_user.id,
    )

    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility


@router.put("/{facility_id}", response_model=FacilityResponse)
def update_facility(
    facility_id: int,
    payload: FacilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    facility = (
        db.query(Facility)
        .filter(Facility.id == facility_id, Facility.is_deleted == False)
        .first()
    )
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    update_data = payload.dict(exclude_unset=True)
    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = str(update_data["email"])

    for field, value in update_data.items():
        setattr(facility, field, value)

    db.commit()
    db.refresh(facility)
    return facility


@router.delete("/{facility_id}", response_model=MessageResponse)
def delete_facility(
    facility_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility or facility.is_deleted:
        raise HTTPException(status_code=404, detail="Facility not found")

    facility.is_deleted = True
    db.commit()
    return {"message": "Facility deleted successfully"}
