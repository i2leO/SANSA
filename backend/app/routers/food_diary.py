from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import date, time
import os
import uuid
from pydantic import BaseModel

from ..database import get_db
from ..models import FoodDiaryEntry, FoodDiaryPhoto, Visit
from ..auth import get_current_user_optional

router = APIRouter(prefix="/food-diary", tags=["food-diary"])


# Schemas
class FoodDiaryEntryCreate(BaseModel):
    visit_id: int
    entry_date: date
    entry_time: Optional[time] = None
    meal_type: str
    menu_name: str
    description: Optional[str] = None
    portion_description: Optional[str] = None


class FoodDiaryPhotoResponse(BaseModel):
    id: int
    file_path: str
    original_filename: str

    class Config:
        from_attributes = True


class FoodDiaryEntryResponse(BaseModel):
    id: int
    entry_date: date
    entry_time: Optional[time]
    meal_type: str
    menu_name: str
    description: Optional[str]
    portion_description: Optional[str]
    photos: List[FoodDiaryPhotoResponse]

    class Config:
        from_attributes = True


@router.post("", response_model=FoodDiaryEntryResponse)
async def create_food_diary_entry(
    entry: FoodDiaryEntryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Create a new food diary entry"""
    # Verify visit exists
    visit = db.execute(
        select(Visit).where(Visit.id == entry.visit_id)
    ).scalar_one_or_none()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Create entry
    db_entry = FoodDiaryEntry(
        visit_id=entry.visit_id,
        entry_date=entry.entry_date,
        entry_time=entry.entry_time,
        meal_type=entry.meal_type,
        menu_name=entry.menu_name,
        description=entry.description,
        portion_description=entry.portion_description,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return db_entry


@router.get("/visit/{visit_id}", response_model=List[FoodDiaryEntryResponse])
async def get_food_diary_entries(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Get all food diary entries for a visit"""
    entries = (
        db.execute(
            select(FoodDiaryEntry)
            .where(FoodDiaryEntry.visit_id == visit_id)
            .order_by(
                FoodDiaryEntry.entry_date.desc(), FoodDiaryEntry.entry_time.desc()
            )
        )
        .scalars()
        .all()
    )

    return entries


@router.get("/{entry_id}", response_model=FoodDiaryEntryResponse)
async def get_food_diary_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Get a single food diary entry"""
    entry = db.execute(
        select(FoodDiaryEntry).where(FoodDiaryEntry.id == entry_id)
    ).scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return entry


@router.post("/{entry_id}/photos")
async def upload_food_photos(
    entry_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Upload photos for a food diary entry"""
    # Verify entry exists
    entry = db.execute(
        select(FoodDiaryEntry).where(FoodDiaryEntry.id == entry_id)
    ).scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Create uploads directory if not exists
    upload_dir = "uploads/food_diary"
    os.makedirs(upload_dir, exist_ok=True)

    uploaded_photos = []

    for file in files:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, stored_filename)

        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Create photo record
        photo = FoodDiaryPhoto(
            diary_entry_id=entry_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=f"/{file_path}",  # Store path with leading slash for frontend
            file_size_bytes=len(content),
            mime_type=file.content_type,
        )
        db.add(photo)
        uploaded_photos.append(
            {
                "filename": file.filename,
                "path": f"/{file_path}",
            }
        )

    db.commit()

    return {"message": f"Uploaded {len(files)} photos", "photos": uploaded_photos}


@router.delete("/{entry_id}")
async def delete_food_diary_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Delete a food diary entry and its photos"""
    entry = db.execute(
        select(FoodDiaryEntry).where(FoodDiaryEntry.id == entry_id)
    ).scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Delete associated photo files
    for photo in entry.photos:
        if os.path.exists(photo.file_path.lstrip("/")):
            os.remove(photo.file_path.lstrip("/"))

    # Delete entry (cascade will delete photos from DB)
    db.delete(entry)
    db.commit()

    return {"message": "Entry deleted successfully"}
