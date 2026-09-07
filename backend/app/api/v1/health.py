"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return application health status."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }
