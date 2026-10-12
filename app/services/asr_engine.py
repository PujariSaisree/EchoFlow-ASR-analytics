from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from app.config import settings
from app.errors import ModelError, TranscriptionError

_loaded: dict[str, Any] = {}


def supported_models() -> list[str]:
    return list(settings.allowed_models)


def _load_model(model_size: str):
    if model_size not in settings.allowed_models:
        raise ModelError(
            f"Unsupported model '{model_size}'. Choose tiny, base, small, or medium."
        )
    if model_size in _loaded:
        return _loaded[model_size]
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:  # pragma: no cover - import environment
        raise ModelError(
            "Faster-Whisper is not available. Install project dependencies and try again."
        ) from exc
    try:
        model = WhisperModel(
            model_size,
            device=settings.device,
            compute_type=settings.compute_type,
        )
    except Exception as exc:
        raise ModelError(
            "The speech recognition model could not be loaded on this machine."
        ) from exc
    _loaded[model_size] = model
    return model


def transcribe_audio(wav_path: Path, model_size: str) -> dict[str, Any]:
    model = _load_model(model_size)
    started = time.perf_counter()
    try:
        segment_iter, info = model.transcribe(str(wav_path), vad_filter=True)
        segments = []
        for item in segment_iter:
            text = (item.text or "").strip()
            if not text:
                continue
            segments.append(
                {
                    "start": float(item.start),
                    "end": float(item.end),
                    "text": text,
                }
            )
    except Exception as exc:
        raise TranscriptionError(
            "Transcription failed. The audio may be noisy, incomplete, or unsupported."
        ) from exc
    processing_time = time.perf_counter() - started
    full_text = " ".join(segment["text"] for segment in segments).strip()
    language = getattr(info, "language", None)
    duration = getattr(info, "duration", None)
    return {
        "model": model_size,
        "language": language,
        "duration": float(duration) if duration else None,
        "processing_time": processing_time,
        "segments": segments,
        "full_text": full_text,
    }
