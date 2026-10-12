from __future__ import annotations

import json
from typing import Any


def _format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds * 1000))
    hours, remainder = divmod(total, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _format_vtt(seconds: float) -> str:
    return _format_timestamp(seconds).replace(",", ".")


def as_txt(payload: dict[str, Any]) -> str:
    transcript = payload.get("transcript") or {}
    return transcript.get("full_text") or ""


def as_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, default=str)


def as_srt(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    for index, segment in enumerate(payload.get("segments") or [], start=1):
        start = _format_timestamp(float(segment["start_time"]))
        end = _format_timestamp(float(segment["end_time"]))
        lines.append(str(index))
        lines.append(f"{start} --> {end}")
        lines.append(segment.get("text") or "")
        lines.append("")
    return "\n".join(lines).strip() + ("\n" if lines else "")


def as_vtt(payload: dict[str, Any]) -> str:
    lines = ["WEBVTT", ""]
    for segment in payload.get("segments") or []:
        start = _format_vtt(float(segment["start_time"]))
        end = _format_vtt(float(segment["end_time"]))
        lines.append(f"{start} --> {end}")
        lines.append(segment.get("text") or "")
        lines.append("")
    return "\n".join(lines)
