"""
Admin API router - handles model training and administrative tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.model_update import ModelUpdate
from models.topic import Topic
from models.wish import Wish
from services.scheduler import trigger_manual_update, start_scheduler, stop_scheduler
from config import settings

router = APIRouter()


# Pydantic models for request/response
class TrainingStatus(BaseModel):
    """Response model for training status."""
    version: int
    status: str
    wishes_count: int
    topics_created: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    configuration: Optional[dict] = None


class TrainingHistoryResponse(BaseModel):
    """Response model for training history."""
    history: List[TrainingStatus]
    total: int


class SystemStats(BaseModel):
    """Response model for system statistics."""
    total_wishes: int
    unassigned_wishes: int
    total_topics: int
    latest_training: TrainingStatus = None
    scheduler_enabled: bool


@router.post("/model/train", response_model=TrainingStatus)
def trigger_training(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a manual BERTopic training run.

    This will process all unassigned wishes and create new topics.
    The training runs in the background - use GET /admin/model/status
    to check progress.
    """
    # Check if there's already a training run in progress
    running_training = db.query(ModelUpdate).filter(
        ModelUpdate.status == "running"
    ).first()

    if running_training:
        raise HTTPException(
            status_code=409,
            detail=f"Training already in progress (version {running_training.version})"
        )

    # Check if there are unassigned wishes
    unassigned_count = db.query(Wish).filter(
        Wish.topic_id.is_(None),
        Wish.is_deleted == False
    ).count()

    if unassigned_count < settings.HDBSCAN_MIN_CLUSTER_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough unassigned wishes to train ({unassigned_count} < {settings.HDBSCAN_MIN_CLUSTER_SIZE})"
        )

    # Create a new model update record
    next_version = _get_next_version(db)
    model_update = ModelUpdate(
        version=next_version,
        status="running",
        wishes_count=unassigned_count,
        topics_created=0,
        configuration={
            "embedding_model": settings.EMBEDDING_MODEL,
            "umap_components": settings.UMAP_N_COMPONENTS,
            "min_cluster_size": settings.HDBSCAN_MIN_CLUSTER_SIZE
        }
    )
    db.add(model_update)
    db.commit()
    db.refresh(model_update)

    # Trigger background training
    background_tasks.add_task(trigger_manual_update)

    return model_update


@router.get("/model/status", response_model=TrainingStatus)
def get_training_status(db: Session = Depends(get_db)):
    """
    Get the status of the most recent training run.

    Returns details about the latest training, including status,
    number of wishes processed, and topics created.
    """
    model_update = db.query(ModelUpdate).order_by(
        desc(ModelUpdate.version)
    ).first()

    if not model_update:
        raise HTTPException(status_code=404, detail="No training runs found")

    return model_update


@router.get("/model/history", response_model=TrainingHistoryResponse)
def get_training_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get the history of all training runs.

    Returns a list of past training runs with their status and results.
    """
    model_updates = db.query(ModelUpdate).order_by(
        desc(ModelUpdate.version)
    ).limit(limit).all()

    total = db.query(ModelUpdate).count()

    return {
        "history": model_updates,
        "total": total
    }


@router.get("/stats", response_model=SystemStats)
def get_system_stats(db: Session = Depends(get_db)):
    """
    Get system statistics and overview.

    Returns counts of wishes, topics, unassigned wishes, and latest training info.
    """
    # Count total wishes
    total_wishes = db.query(Wish).filter(Wish.is_deleted == False).count()

    # Count unassigned wishes
    unassigned_wishes = db.query(Wish).filter(
        Wish.topic_id.is_(None),
        Wish.is_deleted == False
    ).count()

    # Count total topics
    total_topics = db.query(Topic).count()

    # Get latest training
    latest_training = db.query(ModelUpdate).order_by(
        desc(ModelUpdate.version)
    ).first()

    return {
        "total_wishes": total_wishes,
        "unassigned_wishes": unassigned_wishes,
        "total_topics": total_topics,
        "latest_training": latest_training,
        "scheduler_enabled": settings.ENABLE_SCHEDULER
    }


@router.post("/scheduler/start")
def start_scheduler_service():
    """
    Start the background scheduler for automatic batch updates.

    The scheduler will process unassigned wishes at regular intervals.
    """
    try:
        start_scheduler()
        return {"status": "Scheduler started"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
def stop_scheduler_service():
    """
    Stop the background scheduler.

    No more automatic batch updates will occur.
    """
    try:
        stop_scheduler()
        return {"status": "Scheduler stopped"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.post("/model/reset-stuck")
def reset_stuck_training(db: Session = Depends(get_db)):
    """
    Reset any stuck training runs.

    If a training run crashed and left status as 'running', this will
    mark it as 'failed' so new training can start.
    """
    stuck_trainings = db.query(ModelUpdate).filter(
        ModelUpdate.status == "running"
    ).all()

    if not stuck_trainings:
        return {"message": "No stuck training runs found"}

    for training in stuck_trainings:
        training.status = "failed"

    db.commit()

    return {
        "message": f"Reset {len(stuck_trainings)} stuck training run(s)",
        "reset_count": len(stuck_trainings)
    }


def _get_next_version(db: Session) -> int:
    """Get the next version number for model updates."""
    last_update = db.query(ModelUpdate).order_by(ModelUpdate.version.desc()).first()
    if last_update:
        return last_update.version + 1
    return 1
