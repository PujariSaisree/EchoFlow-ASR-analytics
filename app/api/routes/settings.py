from fastapi import APIRouter, HTTPException

from app.config import settings
from app.database import get_setting, set_setting
from app.services.asr_engine import supported_models

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def read_settings() -> dict:
    return {
        "default_model": get_setting("default_model", settings.default_model),
        "allowed_models": supported_models(),
        "max_upload_mb": settings.max_upload_mb,
        "privacy": {
            "audio_processing": "local",
            "asr": "local Faster-Whisper",
            "storage": "local SQLite",
            "external_speech_apis": False,
        },
    }


@router.put("")
def update_settings(body: dict) -> dict:
    model = (body or {}).get("default_model")
    if model not in supported_models():
        raise HTTPException(status_code=400, detail="Unsupported model selection.")
    set_setting("default_model", model)
    return read_settings()
