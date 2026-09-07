"""API v1 router — aggregates all v1 sub-routers."""

from fastapi import APIRouter

from app.api.v1.actions import router as actions_router
from app.api.v1.agents import router as agents_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.businesses import router as businesses_router
from app.api.v1.health import router as health_router
from app.api.v1.mappings import router as mappings_router
from app.api.v1.ml import router as ml_router
from app.api.v1.reports import router as reports_router
from app.api.v1.uploads import router as uploads_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(businesses_router)
api_v1_router.include_router(uploads_router)
api_v1_router.include_router(mappings_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(ml_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(actions_router)
api_v1_router.include_router(reports_router)
