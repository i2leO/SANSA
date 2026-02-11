from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_staff_or_admin, get_current_user_optional
from app.database import get_db
from app.models import KnowledgePost, User
from app.schemas import (
    KnowledgePostCreate,
    KnowledgePostUpdate,
    KnowledgePostResponse,
    MessageResponse,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "post"


def _ensure_unique_slug(
    db: Session, slug: str, exclude_id: Optional[int] = None
) -> str:
    base = slug
    suffix = 1
    while True:
        q = db.query(KnowledgePost).filter(KnowledgePost.slug == slug)
        if exclude_id is not None:
            q = q.filter(KnowledgePost.id != exclude_id)
        existing = q.first()
        if not existing:
            return slug
        suffix += 1
        slug = f"{base}-{suffix}"


@router.get("", response_model=list[KnowledgePostResponse])
def list_knowledge_posts(
    include_unpublished: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """List knowledge posts.

    - Public (no auth): only published posts
    - Staff/Admin: can request include_unpublished=true to see all
    """
    query = db.query(KnowledgePost).filter(KnowledgePost.is_deleted == False)

    if not current_user or not include_unpublished:
        query = query.filter(KnowledgePost.is_published == True)

    return query.order_by(
        KnowledgePost.display_order.asc(), KnowledgePost.created_at.desc()
    ).all()


@router.get("/{post_id}", response_model=KnowledgePostResponse)
def get_knowledge_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(KnowledgePost)
        .filter(KnowledgePost.id == post_id, KnowledgePost.is_deleted == False)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Knowledge post not found")
    if not post.is_published:
        # For simplicity: unpublished posts require staff/admin
        raise HTTPException(status_code=404, detail="Knowledge post not found")
    return post


@router.post("", response_model=KnowledgePostResponse)
def create_knowledge_post(
    payload: KnowledgePostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    slug = payload.slug or _slugify(payload.title)
    slug = _ensure_unique_slug(db, slug)

    post = KnowledgePost(
        title=payload.title,
        slug=slug,
        content=payload.content,
        summary=payload.summary,
        category=payload.category,
        tags=payload.tags,
        is_published=payload.is_published,
        published_at=datetime.utcnow() if payload.is_published else None,
        display_order=payload.display_order,
        created_by=current_user.id,
    )

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=KnowledgePostResponse)
def update_knowledge_post(
    post_id: int,
    payload: KnowledgePostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    post = (
        db.query(KnowledgePost)
        .filter(KnowledgePost.id == post_id, KnowledgePost.is_deleted == False)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Knowledge post not found")

    update_data = payload.dict(exclude_unset=True)

    if "slug" in update_data and update_data["slug"]:
        update_data["slug"] = _ensure_unique_slug(
            db, update_data["slug"], exclude_id=post_id
        )
    elif "title" in update_data and update_data.get("title"):
        # If title changed and slug wasn't provided, keep existing slug
        pass

    if "is_published" in update_data:
        new_published = bool(update_data["is_published"])
        if new_published and not post.is_published:
            post.published_at = datetime.utcnow()
        if not new_published:
            post.published_at = None

    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", response_model=MessageResponse)
def delete_knowledge_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_or_admin),
):
    post = db.query(KnowledgePost).filter(KnowledgePost.id == post_id).first()
    if not post or post.is_deleted:
        raise HTTPException(status_code=404, detail="Knowledge post not found")

    post.is_deleted = True
    db.commit()
    return {"message": "Knowledge post deleted successfully"}
