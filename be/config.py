"""
Environment configuration for Wishing Well backend.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/wishingwell"
    )

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    MODERATION_MODEL: str = os.getenv("MODERATION_MODEL", "text-moderation-latest")

    # BERTopic
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    UMAP_N_COMPONENTS: int = int(os.getenv("UMAP_N_COMPONENTS", "5"))
    HDBSCAN_MIN_CLUSTER_SIZE: int = int(os.getenv("HDBSCAN_MIN_CLUSTER_SIZE", "10"))
    MIN_TOPIC_SIZE: int = int(os.getenv("MIN_TOPIC_SIZE", "5"))

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Wishing Well API"
    VERSION: str = "0.1.0"

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # Scheduler
    BATCH_UPDATE_INTERVAL_MINUTES: int = int(os.getenv("BATCH_UPDATE_INTERVAL_MINUTES", "60"))
    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"

    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))


settings = Settings()
