"""
ModelUpdate model for tracking BERTopic training history.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from database import Base


class ModelUpdate(Base):
    """
    Represents a BERTopic model training run.

    Attributes:
        id: Primary key
        version: Auto-incrementing version number
        status: Training status (running, completed, failed)
        wishes_count: Number of wishes trained on
        topics_created: Number of topics created
        started_at: Training start timestamp
        completed_at: Training completion timestamp
        configuration: Training configuration as JSON
    """

    __tablename__ = "model_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)  # 'running', 'completed', 'failed'
    wishes_count = Column(Integer, default=0)
    topics_created = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    configuration = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ModelUpdate(id={self.id}, version={self.version}, status={self.status})>"
