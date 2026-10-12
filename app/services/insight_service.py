from __future__ import annotations

from typing import Any


def _fmt_seconds(value: float | None) -> str:
    if value is None:
        return "an unknown duration"
    if value < 60:
        return f"{value:.1f} seconds"
    minutes = value / 60.0
    return f"{minutes:.1f} minutes"


def _fmt_ratio(value: float | None) -> str | None:
    if value is None:
        return None
    return f"{value * 100:.1f}%"


def _fmt_number(value: float | None, digits: int = 1) -> str | None:
    if value is None:
        return None
    return f"{value:.{digits}f}"


def build_insights(payload: dict[str, Any]) -> dict[str, Any]:
    recording = payload.get("recording") or {}
    transcript = payload.get("transcript") or {}
    analytics = payload.get("analytics") or {}
    keywords = payload.get("keywords") or []
    segments = payload.get("segments") or []

    duration = recording.get("duration")
    word_count = transcript.get("word_count")
    wpm = analytics.get("wpm")
    silence_ratio = analytics.get("silence_ratio")
    speech_ratio = analytics.get("speech_ratio")
    questions = analytics.get("question_count")
    rtf = recording.get("rtf")
    processing_time = recording.get("processing_time")
    language = recording.get("language")
    model = recording.get("model")

    findings: list[dict[str, Any]] = []

    if word_count is not None and duration is not None:
        findings.append(
            {
                "title": "Conversation length and volume",
                "statement": (
                    f"The recording contains {word_count} words across {_fmt_seconds(duration)}."
                ),
                "metrics": {"word_count": word_count, "duration": duration},
            }
        )

    if wpm is not None:
        findings.append(
            {
                "title": "Speaking rate",
                "statement": f"The detected speaking rate is {wpm:.1f} words per minute.",
                "metrics": {"wpm": wpm},
                "business_question": "How quickly was speech delivered?",
            }
        )

    silence_text = _fmt_ratio(silence_ratio)
    if silence_text:
        findings.append(
            {
                "title": "Silence share",
                "statement": f"Approximately {silence_text} of the recording contains silence or non-transcribed audio.",
                "metrics": {"silence_ratio": silence_ratio},
                "business_question": "How much of the recording contained silence?",
            }
        )

    if questions is not None:
        findings.append(
            {
                "title": "Question usage",
                "statement": f"{questions} question-like sentence(s) were detected in the transcript.",
                "metrics": {"question_count": questions},
                "business_question": "How frequently were questions used?",
            }
        )

    if keywords:
        top = ", ".join(item["keyword"] for item in keywords[:5])
        findings.append(
            {
                "title": "Frequent concepts",
                "statement": f"The most frequent keywords were: {top}.",
                "metrics": {"keywords": keywords[:5]},
                "business_question": "What concepts appear frequently?",
            }
        )

    review_areas: list[str] = []
    if silence_ratio is not None and silence_ratio >= 0.35:
        review_areas.append(
            "Silence ratio is relatively high. Review whether pauses, hold time, or missed speech affected the recording."
        )
    if wpm is not None and wpm >= 180:
        review_areas.append(
            "Speaking rate is high relative to a typical conversational range. Review dense segments for missed details."
        )
    if wpm is not None and wpm <= 90 and (word_count or 0) > 20:
        review_areas.append(
            "Speaking rate is relatively low. Review whether the interaction included long explanations or unused time."
        )
    if questions is not None and questions >= 8:
        review_areas.append(
            "Many questions were detected. Review whether the conversation was exploratory, diagnostic, or unresolved."
        )
    if not segments:
        review_areas.append(
            "No transcript segments were produced. Review audio quality, language, and whether speech is present."
        )

    summary_parts = [item["statement"] for item in findings]
    summary = " ".join(summary_parts) if summary_parts else (
        "Insufficient structured metrics were available to generate a conversation summary."
    )

    return {
        "summary": summary,
        "findings": findings,
        "review_areas": review_areas,
        "supporting_metrics": {
            "duration": duration,
            "word_count": word_count,
            "wpm": wpm,
            "speech_ratio": speech_ratio,
            "silence_ratio": silence_ratio,
            "question_count": questions,
            "processing_time": processing_time,
            "rtf": rtf,
            "language": language,
            "model": model,
            "wpm_display": _fmt_number(wpm),
            "speech_ratio_display": _fmt_ratio(speech_ratio),
            "silence_ratio_display": _fmt_ratio(silence_ratio),
            "rtf_display": _fmt_number(rtf, 2),
        },
        "method": "deterministic_metric_narration",
        "caveat": (
            "These observations are derived only from computed transcript metrics. "
            "They are not a complete assessment of meeting quality or speaker intent."
        ),
    }


def answer_question(question: str, payload: dict[str, Any], insights: dict[str, Any]) -> dict[str, Any]:
    text = question.strip().lower()
    analytics = payload.get("analytics") or {}
    recording = payload.get("recording") or {}
    transcript = payload.get("transcript") or {}
    keywords = payload.get("keywords") or []

    mapping = [
        (("wpm", "words per minute", "how fast", "speaking rate", "talking"), "wpm", analytics.get("wpm"),
         "The detected speaking rate is {value:.1f} words per minute."),
        (("silence",), "silence_ratio", analytics.get("silence_ratio"),
         "Approximately {pct:.1f}% of the recording is silence or non-transcribed audio."),
        (("speech ratio", "how much speech"), "speech_ratio", analytics.get("speech_ratio"),
         "Approximately {pct:.1f}% of the recording contains detected speech."),
        (("question",), "question_count", analytics.get("question_count"),
         "{value} question-like sentence(s) were detected."),
        (("topic", "keyword"), "keywords", keywords[:8],
         "The most frequent keywords were: {joined}."),
        (("long", "duration", "how long"), "duration", recording.get("duration"),
         "The recording duration is {seconds:.1f} seconds."),
        (("rtf", "efficient", "processing"), "rtf", recording.get("rtf"),
         "The real-time factor is {value:.2f}. Values below 1.0 mean faster than real time."),
        (("word count", "how many words"), "word_count", transcript.get("word_count"),
         "The transcript contains {value} words."),
    ]

    for needles, metric, value, template in mapping:
        if any(needle in text for needle in needles):
            if value in (None, [], ""):
                return {
                    "answer": f"The available structured data does not include a reliable value for {metric}.",
                    "metric": metric,
                    "sufficient_data": False,
                }
            if metric in {"silence_ratio", "speech_ratio"}:
                answer = template.format(pct=float(value) * 100)
            elif metric == "keywords":
                joined = ", ".join(item["keyword"] for item in value)
                answer = template.format(joined=joined)
            elif metric == "duration":
                answer = template.format(seconds=float(value))
            else:
                answer = template.format(value=value)
            return {"answer": answer, "metric": metric, "sufficient_data": True, "value": value}

    if any(token in text for token in ("summarize", "stand out", "review", "characteristics")):
        return {
            "answer": insights.get("summary"),
            "metric": "composite",
            "sufficient_data": bool(insights.get("findings")),
            "review_areas": insights.get("review_areas"),
        }

    return {
        "answer": (
            "That question cannot be answered from the structured metrics currently stored "
            "for this recording. Ask about speaking rate, silence, questions, keywords, duration, or RTF."
        ),
        "metric": None,
        "sufficient_data": False,
    }
