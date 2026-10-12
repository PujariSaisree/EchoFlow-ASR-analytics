from fastapi import APIRouter, HTTPException

from app.database import get_recording
from app.services.evaluation import character_error_rate, word_error_rate

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

REFERENCE_REQUIRED = "Reference transcript required for accuracy evaluation."


@router.post("/{recording_id}")
def evaluate_recording(recording_id: int, body: dict) -> dict:
    payload = get_recording(recording_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    reference = ((body or {}).get("reference_transcript") or "").strip()
    recording = payload["recording"]
    transcript = payload.get("transcript") or {}
    hypothesis = transcript.get("full_text") or ""
    result = {
        "recording_id": recording_id,
        "audio_duration": recording.get("duration"),
        "processing_time": recording.get("processing_time"),
        "rtf": recording.get("rtf"),
        "model": recording.get("model"),
        "wer": None,
        "cer": None,
        "message": None,
    }
    if not reference:
        result["message"] = REFERENCE_REQUIRED
        return result
    result["wer"] = word_error_rate(reference, hypothesis)
    result["cer"] = character_error_rate(reference, hypothesis)
    return result
