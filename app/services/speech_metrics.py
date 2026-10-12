from __future__ import annotations

from typing import Any

import numpy as np


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return float(numerator / denominator)


def count_words(text: str) -> int:
    return len([token for token in text.split() if token.strip()])


def count_characters(text: str) -> int:
    return len(text.replace("\n", ""))


def compute_speech_metrics(
    duration: float,
    segments: list[dict[str, Any]],
    full_text: str,
    processing_time: float,
) -> dict[str, Any]:
    speech_duration = 0.0
    for segment in segments:
        start = float(segment.get("start") or 0)
        end = float(segment.get("end") or start)
        speech_duration += max(0.0, end - start)
    speech_duration = min(speech_duration, duration) if duration else speech_duration
    silence_duration = max(0.0, duration - speech_duration) if duration else 0.0
    word_count = count_words(full_text)
    character_count = count_characters(full_text)
    segment_count = len(segments)
    minutes = duration / 60.0 if duration else 0.0
    wpm = (word_count / minutes) if minutes > 0 else None
    cpm = (character_count / minutes) if minutes > 0 else None
    avg_words = (word_count / segment_count) if segment_count else None
    rtf = _safe_ratio(processing_time, duration) if duration else None
    return {
        "duration": float(duration) if duration is not None else None,
        "speech_duration": float(speech_duration),
        "silence_duration": float(silence_duration),
        "speech_ratio": _safe_ratio(speech_duration, duration) if duration else None,
        "silence_ratio": _safe_ratio(silence_duration, duration) if duration else None,
        "word_count": word_count,
        "character_count": character_count,
        "segment_count": segment_count,
        "avg_words_per_segment": avg_words,
        "wpm": wpm,
        "cpm": cpm,
        "processing_time": float(processing_time),
        "rtf": rtf,
    }


def series_summary(values: list[float | None]) -> dict[str, float | None]:
    clean = [float(item) for item in values if item is not None]
    if not clean:
        return {"mean": None, "min": None, "max": None}
    array = np.array(clean, dtype=float)
    return {
        "mean": float(array.mean()),
        "min": float(array.min()),
        "max": float(array.max()),
    }
