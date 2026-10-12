from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from app.config import settings
from app.database import (
    get_connection,
    insert_analytics,
    insert_keywords,
    insert_recording,
    insert_segments,
    insert_transcript,
)
from app.services.asr_engine import transcribe_audio
from app.services.audio_processor import probe_duration, to_whisper_wav, validate_audio
from app.services.speech_metrics import compute_speech_metrics
from app.services.text_metrics import compute_text_metrics


def process_upload(
    filename: str,
    content: bytes,
    content_type: str | None,
    model_size: str,
) -> int:
    validate_audio(filename, len(content), content_type)
    suffix = Path(filename).suffix.lower()
    token = uuid4().hex
    original_path = settings.upload_dir / f"{token}{suffix}"
    processed_path = settings.processed_dir / f"{token}.wav"
    original_path.write_bytes(content)

    to_whisper_wav(original_path, processed_path)
    duration = probe_duration(processed_path)
    asr = transcribe_audio(processed_path, model_size)
    asr_duration = asr.get("duration") or duration
    speech = compute_speech_metrics(
        duration=asr_duration,
        segments=asr["segments"],
        full_text=asr["full_text"],
        processing_time=asr["processing_time"],
    )
    text = compute_text_metrics(asr["full_text"])
    combined = {**speech, **text}

    with get_connection() as conn:
        recording_id = insert_recording(
            conn,
            filename=filename,
            original_path=str(original_path),
            processed_path=str(processed_path),
            duration=speech["duration"],
            language=asr.get("language"),
            model=asr["model"],
            processing_time=speech["processing_time"],
            rtf=speech["rtf"],
        )
        insert_transcript(
            conn,
            recording_id,
            asr["full_text"],
            speech["word_count"],
            speech["character_count"],
            speech["segment_count"],
        )
        insert_segments(conn, recording_id, asr["segments"])
        insert_analytics(conn, recording_id, combined)
        insert_keywords(conn, recording_id, text["keywords"])
    return recording_id
