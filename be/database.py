"""
Database connection and session management for Wishing Well.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,         # Connection pool size
    max_overflow=10      # Additional connections when needed
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency for FastAPI to get database sessions.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/wishes")
        def list_wishes(db: Session = Depends(get_db)):
            wishes = db.query(Wish).all()
            return wishes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    This creates all tables that don't exist yet.
    Note: In production, use Alembic migrations instead.
    """
    from models import wish, topic, model_update, rejected_wish  # noqa: F401

    Base.metadata.create_all(bind=engine)
