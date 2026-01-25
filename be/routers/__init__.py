"""
API routers for Wishing Well backend.
"""
from .wishes import router as wishes_router
from .topics import router as topics_router
from .admin import router as admin_router

__all__ = ["wishes_router", "topics_router", "admin_router"]
