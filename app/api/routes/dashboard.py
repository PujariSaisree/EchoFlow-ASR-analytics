from fastapi import APIRouter

from app.database import dashboard_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview() -> dict:
    return dashboard_overview()
