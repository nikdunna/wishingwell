"""
FastAPI application for Wishing Well backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import engine, init_db
from routers import wishes, topics, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    Initializes database on startup and closes connections on shutdown.
    """
    # Startup
    print("Initializing Wishing Well API...")
    init_db()
    print("Database initialized successfully")

    yield

    # Shutdown
    print("Closing database connections...")
    engine.dispose()
    print("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wishes.router, prefix=f"{settings.API_V1_PREFIX}/wishes", tags=["wishes"])
app.include_router(topics.router, prefix=f"{settings.API_V1_PREFIX}/topics", tags=["topics"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"])


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
