from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse, Response

from app.config import settings
from app.database import delete_recording, get_recording, get_setting, list_recordings
from app.services.export_service import as_json, as_srt, as_txt, as_vtt
from app.services.insight_service import answer_question, build_insights
from app.services.pipeline import process_upload

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("")
def recordings() -> dict:
    return {"items": list_recordings()}


@router.post("/upload")
async def upload_recording(
    file: UploadFile = File(...),
    model: str | None = Form(default=None),
) -> dict:
    selected = model or get_setting("default_model", settings.default_model) or settings.default_model
    content = await file.read()
    recording_id = process_upload(file.filename or "audio", content, file.content_type, selected)
    payload = get_recording(recording_id)
    if payload is None:
        raise HTTPException(status_code=500, detail="Recording was processed but could not be loaded.")
    payload["insights"] = build_insights(payload)
    return payload


@router.get("/{recording_id}")
def recording_detail(recording_id: int) -> dict:
    payload = get_recording(recording_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    payload["insights"] = build_insights(payload)
    return payload


@router.delete("/{recording_id}")
def remove_recording(recording_id: int) -> dict:
    deleted = delete_recording(recording_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recording not found.")
    return {"deleted": True, "id": recording_id}


@router.get("/{recording_id}/audio")
def recording_audio(recording_id: int):
    payload = get_recording(recording_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    recording = payload["recording"]
    path = recording.get("original_path") or recording.get("processed_path")
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="The audio file is no longer available on disk.")
    return FileResponse(path, filename=recording.get("filename") or "audio")


@router.get("/{recording_id}/export")
def export_recording(recording_id: int, format: str = "txt"):
    payload = get_recording(recording_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    fmt = format.lower()
    filename = payload["recording"]["filename"]
    stem = filename.rsplit(".", 1)[0]
    if fmt == "txt":
        return PlainTextResponse(
            as_txt(payload),
            headers={"Content-Disposition": f'attachment; filename="{stem}.txt"'},
        )
    if fmt == "json":
        return Response(
            as_json(payload),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{stem}.json"'},
        )
    if fmt == "srt":
        return PlainTextResponse(
            as_srt(payload),
            headers={"Content-Disposition": f'attachment; filename="{stem}.srt"'},
        )
    if fmt == "vtt":
        return PlainTextResponse(
            as_vtt(payload),
            headers={"Content-Disposition": f'attachment; filename="{stem}.vtt"'},
        )
    raise HTTPException(status_code=400, detail="Unsupported export format. Use txt, json, srt, or vtt.")


@router.post("/{recording_id}/ask")
def ask_recording(recording_id: int, body: dict) -> dict:
    payload = get_recording(recording_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    question = (body or {}).get("question") or ""
    insights = build_insights(payload)
    return answer_question(question, payload, insights)
