import wave
from pathlib import Path

import pytest

from app.services.audio_processor import ffmpeg_available, probe_duration, to_whisper_wav, validate_audio


def _write_silence_wav(path: Path, seconds: float = 0.25, rate: int = 8000) -> None:
    n_frames = int(seconds * rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(b"\x00\x00" * n_frames)


def test_wav_fixture_is_valid(tmp_path):
    path = tmp_path / "tone.wav"
    _write_silence_wav(path)
    validate_audio(path.name, path.stat().st_size, "audio/wav")
    assert path.stat().st_size > 0


@pytest.mark.skipif(not ffmpeg_available(), reason="FFmpeg is required for decoding tests")
def test_conversion_and_duration(tmp_path):
    source = tmp_path / "input.wav"
    destination = tmp_path / "output.wav"
    _write_silence_wav(source, seconds=0.4, rate=8000)
    to_whisper_wav(source, destination)
    duration = probe_duration(destination)
    assert destination.exists()
    assert 0.3 <= duration <= 0.6
