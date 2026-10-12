from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from app.config import settings
from app.errors import AudioProcessingError, AudioValidationError, DependencyError

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
ALLOWED_MIME_HINTS = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/flac",
    "audio/ogg",
    "audio/webm",
    "application/octet-stream",
}


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def validate_audio(filename: str, size_bytes: int, content_type: str | None) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise AudioValidationError(
            "Unsupported file type. Upload WAV, MP3, M4A, FLAC, OGG, or WebM."
        )
    if size_bytes <= 0:
        raise AudioValidationError("The uploaded file is empty.")
    if size_bytes > settings.max_upload_bytes:
        raise AudioValidationError(
            f"The file is too large. Maximum size is {settings.max_upload_mb} MB."
        )
    if content_type:
        normalized = content_type.split(";")[0].strip().lower()
        if normalized and normalized not in ALLOWED_MIME_HINTS:
            raise AudioValidationError(
                "The file MIME type is not recognized as supported audio."
            )


def probe_duration(path: Path) -> float:
    if not shutil.which("ffprobe"):
        raise DependencyError(
            "FFmpeg/ffprobe is not installed. Install FFmpeg to process audio locally."
        )
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        value = result.stdout.strip()
        duration = float(value)
    except (subprocess.CalledProcessError, ValueError) as exc:
        raise AudioProcessingError(
            "The audio file could not be read. It may be corrupted or incomplete."
        ) from exc
    if duration <= 0:
        raise AudioProcessingError("The audio file has no measurable duration.")
    return duration


def to_whisper_wav(source: Path, destination: Path) -> Path:
    if not shutil.which("ffmpeg"):
        raise DependencyError(
            "FFmpeg is not installed. EchoFlow needs FFmpeg for local audio decoding."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        str(settings.target_sample_rate),
        "-vn",
        str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not destination.exists():
        raise AudioProcessingError(
            "Audio could not be converted to a 16 kHz mono WAV for transcription."
        )
    return destination
