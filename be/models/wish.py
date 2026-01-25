"""
Wish model for storing user-submitted wishes.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base


class Wish(Base):
    """
    Represents a user-submitted wish.

    Attributes:
        id: UUID primary key
        content: The wish text
        created_at: Timestamp when wish was created
        updated_at: Timestamp when wish was last updated
        topic_id: Foreign key to primary topic
        is_deleted: Soft delete flag
    """

    __tablename__ = "wishes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    topic = relationship("Topic", back_populates="wishes")
    topic_associations = relationship(
        "TopicWish",
        back_populates="wish",
        cascade="all, delete-orphan"
    )

    @property
    def id_str(self) -> str:
        """Return UUID as string for JSON serialization."""
        return str(self.id)

    def __repr__(self):
        return f"<Wish(id={self.id}, content={self.content[:50]}...)>"
