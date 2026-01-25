"""
Topics API router - handles topic retrieval and exploration.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from datetime import datetime
from pydantic import BaseModel, field_serializer

from database import get_db
from models.topic import Topic
from models.wish import Wish
from models.topic_wish import TopicWish
from config import settings

router = APIRouter()


# Pydantic models for response
class TopicResponse(BaseModel):
    """Response model for a topic."""
    id: int
    name: str
    description: str
    wish_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class WishInTopicResponse(BaseModel):
    """Response model for a wish in a topic."""
    id: str
    content: str
    probability: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('id')
    def serialize_id(self, id: object) -> str:
        """Convert UUID to string."""
        return str(id)


class TopicDetailResponse(TopicResponse):
    """Response model for topic detail with wishes."""
    wishes: List[WishInTopicResponse] = []


class TopicListResponse(BaseModel):
    """Response model for topic list."""
    topics: List[TopicResponse]
    total: int


@router.get("", response_model=TopicListResponse)
def list_topics(
    sort: str = Query("popular", pattern="^(popular|recent|name)$", description="Sort order"),
    limit: int = Query(100, ge=1, le=500, description="Maximum topics to return"),
    db: Session = Depends(get_db)
):
    """
    List all topics with optional sorting.

    Returns a list of topics. By default sorts by popularity (wish count).
    """
    query = db.query(Topic)

    # Apply sorting
    if sort == "popular":
        query = query.order_by(desc(Topic.wish_count))
    elif sort == "recent":
        query = query.order_by(desc(Topic.created_at))
    elif sort == "name":
        query = query.order_by(Topic.name)

    # Apply limit
    topics = query.limit(limit).all()
    total = db.query(Topic).count()

    return {
        "topics": topics,
        "total": total
    }


@router.get("/{topic_id}", response_model=TopicDetailResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Get a single topic with its wishes.

    Returns topic details along with wishes belonging to this topic,
    sorted by probability (most relevant first).
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get wishes for this topic with probabilities
    topic_wishes = db.query(TopicWish, Wish).join(
        Wish, TopicWish.wish_id == Wish.id
    ).filter(
        TopicWish.topic_id == topic_id,
        Wish.is_deleted == False
    ).order_by(desc(TopicWish.probability)).all()

    wishes = []
    for tw, wish in topic_wishes:
        wishes.append({
            "id": str(wish.id),
            "content": wish.content,
            "probability": float(tw.probability),
            "created_at": wish.created_at
        })

    return {
        **topic.__dict__,
        "wishes": wishes
    }


@router.get("/{topic_id}/wishes", response_model=List[WishInTopicResponse])
def get_topic_wishes(
    topic_id: int,
    limit: int = Query(20, ge=1, le=100, description="Maximum wishes to return"),
    db: Session = Depends(get_db)
):
    """
    Get wishes for a specific topic.

    Returns wishes belonging to the topic, sorted by probability.
    """
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get wishes with probabilities
    topic_wishes = db.query(TopicWish, Wish).join(
        Wish, TopicWish.wish_id == Wish.id
    ).filter(
        TopicWish.topic_id == topic_id,
        Wish.is_deleted == False
    ).order_by(desc(TopicWish.probability)).limit(limit).all()

    wishes = []
    for tw, wish in topic_wishes:
        wishes.append({
            "id": str(wish.id),
            "content": wish.content,
            "probability": float(tw.probability),
            "created_at": wish.created_at
        })

    return wishes


@router.get("/trending", response_model=List[TopicResponse])
def get_trending_topics(
    limit: int = Query(10, ge=1, le=50, description="Maximum topics to return"),
    db: Session = Depends(get_db)
):
    """
    Get trending topics (topics with most recent wishes).

    Returns topics that have received the most wishes recently.
    """
    # This is a simplified version - in production you'd use created_at filtering
    topics = db.query(Topic).order_by(
        desc(Topic.wish_count),
        desc(Topic.created_at)
    ).limit(limit).all()

    return topics
