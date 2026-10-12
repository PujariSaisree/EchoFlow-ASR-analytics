from fastapi import APIRouter

from app.api.routes import dashboard, evaluation, health, recordings, settings

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(recordings.router)
api_router.include_router(dashboard.router)
api_router.include_router(evaluation.router)
api_router.include_router(settings.router)
