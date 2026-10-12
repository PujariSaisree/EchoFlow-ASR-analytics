from app.errors import AudioValidationError
from app.services.audio_processor import validate_audio
import pytest


def test_rejects_unsupported_extension():
    with pytest.raises(AudioValidationError):
        validate_audio("notes.pdf", 2048, "application/pdf")


def test_rejects_empty_file():
    with pytest.raises(AudioValidationError):
        validate_audio("speech.wav", 0, "audio/wav")


def test_rejects_large_file(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "max_upload_mb", 1)
    with pytest.raises(AudioValidationError):
        validate_audio("speech.mp3", 2 * 1024 * 1024, "audio/mpeg")


def test_accepts_supported_audio():
    validate_audio("interview.m4a", 4096, "audio/mp4")
