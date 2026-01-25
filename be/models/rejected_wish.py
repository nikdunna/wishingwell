"""
RejectedWish model for logging moderated content.
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database import Base


class RejectedWish(Base):
    """
    Represents a wish that was rejected by content moderation.

    Attributes:
        id: UUID primary key
        content: The rejected wish text
        rejection_reason: Reason for rejection
        moderation_model: Model that performed moderation
        created_at: Timestamp when wish was rejected
    """

    __tablename__ = "rejected_wishes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    rejection_reason = Column(String(255), nullable=False)
    moderation_model = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<RejectedWish(id={self.id}, reason={self.rejection_reason})>"
