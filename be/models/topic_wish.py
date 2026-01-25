"""
TopicWish junction model for many-to-many relationship with probabilities.
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy.dialects.postgresql import UUID


class TopicWish(Base):
    """
    Junction table for Topic-Wish many-to-many relationship.
    Captures BERTopic's probabilistic topic assignments.

    Attributes:
        topic_id: Foreign key to topic
        wish_id: Foreign key to wish
        probability: Probability of wish belonging to topic
        is_primary: Whether this is the primary topic for the wish
    """

    __tablename__ = "topic_wishes"

    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
    wish_id = Column(UUID(as_uuid=True), ForeignKey("wishes.id", ondelete="CASCADE"), primary_key=True)
    probability = Column(Numeric(5, 4), nullable=False)  # 0.0000 to 1.0000
    is_primary = Column(Boolean, default=False)

    # Relationships
    topic = relationship("Topic", back_populates="topic_associations")
    wish = relationship("Wish", back_populates="topic_associations")

    def __repr__(self):
        return f"<TopicWish(topic_id={self.topic_id}, wish_id={self.wish_id}, prob={self.probability})>"
