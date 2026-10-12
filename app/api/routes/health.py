from fastapi import APIRouter

from app.services.asr_engine import supported_models
from app.services.audio_processor import ffmpeg_available

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "EchoFlow",
        "ffmpeg": ffmpeg_available(),
        "models": supported_models(),
    }


@router.get("/models")
def models() -> dict:
    return {"models": supported_models(), "default": "tiny"}
