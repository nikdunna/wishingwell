"""
Wishes API router - handles wish submission and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer

from database import get_db
from models.wish import Wish
from models.topic_wish import TopicWish
from models.rejected_wish import RejectedWish
from services.content_moderation import should_reject_wish
from config import settings

router = APIRouter()


# Pydantic models for request/response
class WishCreate(BaseModel):
    """Request model for creating a wish."""
    content: str = Field(..., min_length=1, max_length=1000, description="The wish text")


class WishResponse(BaseModel):
    """Response model for a wish."""
    id: str
    content: str
    created_at: datetime
    updated_at: datetime
    topic_id: Optional[int] = None

    class Config:
        from_attributes = True

    @field_serializer('id')
    def serialize_id(self, id: object) -> str:
        """Convert UUID to string."""
        return str(id)


class WishListResponse(BaseModel):
    """Response model for wish list."""
    wishes: List[WishResponse]
    total: int
    page: int
    limit: int
    has_more: bool


class WishDetailResponse(WishResponse):
    """Response model for wish detail with related wishes."""
    topic_name: Optional[str] = None
    related_wishes: List[WishResponse] = []


@router.post("", response_model=WishResponse, status_code=201)
def create_wish(wish_data: WishCreate, db: Session = Depends(get_db)):
    """
    Submit a new wish.

    The wish will be checked for content policy violations before being saved.
    If approved, it will be stored and will be assigned a topic during the next
    batch update.
    """
    # Content moderation check
    is_safe, rejection_reason = should_reject_wish(wish_data.content)

    if not is_safe:
        # Log rejected wish
        rejected = RejectedWish(
            content=wish_data.content,
            rejection_reason=rejection_reason,
            moderation_model=settings.MODERATION_MODEL
        )
        db.add(rejected)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=f"Wish rejected: {rejection_reason}"
        )

    # Create wish
    wish = Wish(content=wish_data.content)
    db.add(wish)
    db.commit()
    db.refresh(wish)

    # Explicitly construct response to trigger field_serializer
    return WishResponse(
        id=str(wish.id),
        content=wish.content,
        created_at=wish.created_at,
        updated_at=wish.updated_at,
        topic_id=wish.topic_id
    )


@router.get("", response_model=WishListResponse)
def list_wishes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Items per page"),
    sort: str = Query("recent", pattern="^(recent|popular)$", description="Sort order: 'recent' or 'popular'"),
    db: Session = Depends(get_db)
):
    """
    List wishes with pagination and sorting.

    Returns a paginated list of wishes. The 'popular' sort is based on
    topic size (wishes in popular topics appear first).
    """
    # Build query
    query = db.query(Wish).filter(Wish.is_deleted == False)

    # Apply sorting
    if sort == "recent":
        query = query.order_by(desc(Wish.created_at))
    elif sort == "popular":
        # Sort by topic wish count
        query = query.outerjoin(Wish.topic).order_by(
            desc(TopicWish.probability),
            desc(Wish.created_at)
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    wishes = query.offset(offset).limit(limit).all()

    # Calculate if there are more pages
    has_more = (offset + len(wishes)) < total

    # Convert SQLAlchemy objects to response models
    wish_responses = [
        WishResponse(
            id=str(wish.id),
            content=wish.content,
            created_at=wish.created_at,
            updated_at=wish.updated_at,
            topic_id=wish.topic_id
        )
        for wish in wishes
    ]

    return {
        "wishes": wish_responses,
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": has_more
    }


@router.get("/random", response_model=WishResponse)
def get_random_wish(db: Session = Depends(get_db)):
    """Get a random wish (useful for the home page)."""
    wish = db.query(Wish).filter(Wish.is_deleted == False).order_by(func.random()).first()

    if not wish:
        raise HTTPException(status_code=404, detail="No wishes found")

    return WishResponse(
        id=str(wish.id),
        content=wish.content,
        created_at=wish.created_at,
        updated_at=wish.updated_at,
        topic_id=wish.topic_id
    )


@router.get("/{wish_id}", response_model=WishDetailResponse)
def get_wish(wish_id: str, db: Session = Depends(get_db)):
    """
    Get a single wish with its topic and related wishes.

    Returns the wish details along with other wishes in the same topic.
    """
    wish = db.query(Wish).filter(Wish.id == wish_id, Wish.is_deleted == False).first()

    if not wish:
        raise HTTPException(status_code=404, detail="Wish not found")

    # Get topic name if available
    topic_name = None
    related_wishes = []

    if wish.topic_id:
        from models.topic import Topic

        topic = db.query(Topic).filter(Topic.id == wish.topic_id).first()
        if topic:
            topic_name = topic.name

            # Get related wishes (same topic, excluding current wish)
            related = db.query(Wish).filter(
                Wish.topic_id == wish.topic_id,
                Wish.id != wish_id,
                Wish.is_deleted == False
            ).limit(5).all()

            # Convert related wishes to response models
            related_wishes = [
                WishResponse(
                    id=str(w.id),
                    content=w.content,
                    created_at=w.created_at,
                    updated_at=w.updated_at,
                    topic_id=w.topic_id
                )
                for w in related
            ]

    return {
        "id": str(wish.id),
        "content": wish.content,
        "created_at": wish.created_at,
        "updated_at": wish.updated_at,
        "topic_id": wish.topic_id,
        "topic_name": topic_name,
        "related_wishes": related_wishes
    }


@router.delete("/{wish_id}", status_code=204)
def delete_wish(wish_id: str, db: Session = Depends(get_db)):
    """
    Soft delete a wish (marks as deleted but keeps in database).

    Note: This is a soft delete - the wish is marked is_deleted=True
    but remains in the database for analytics purposes.
    """
    wish = db.query(Wish).filter(Wish.id == wish_id).first()

    if not wish:
        raise HTTPException(status_code=404, detail="Wish not found")

    wish.is_deleted = True
    db.commit()

    return None
