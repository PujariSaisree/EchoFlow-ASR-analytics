from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.config import ensure_directories, settings
from app.errors import DatabaseError

SCHEMA = """
CREATE TABLE IF NOT EXISTS recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    created_at TEXT NOT NULL,
    duration REAL,
    language TEXT,
    model TEXT,
    processing_time REAL,
    rtf REAL,
    original_path TEXT,
    processed_path TEXT,
    status TEXT NOT NULL DEFAULT 'complete'
);

CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id INTEGER NOT NULL UNIQUE,
    full_text TEXT,
    word_count INTEGER,
    character_count INTEGER,
    segment_count INTEGER,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id INTEGER NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    text TEXT,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id INTEGER NOT NULL UNIQUE,
    speech_duration REAL,
    silence_duration REAL,
    speech_ratio REAL,
    silence_ratio REAL,
    wpm REAL,
    cpm REAL,
    question_count INTEGER,
    avg_words_per_segment REAL,
    sentence_count INTEGER,
    avg_sentence_length REAL,
    longest_sentence TEXT,
    shortest_sentence TEXT,
    sentiment_label TEXT,
    sentiment_positive REAL,
    sentiment_negative REAL,
    sentiment_neutral REAL,
    sentiment_method TEXT,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    ensure_directories()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise DatabaseError("A database error occurred while saving results.") from exc
    finally:
        conn.close()


def init_db() -> None:
    ensure_directories()
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_recording(
    conn: sqlite3.Connection,
    filename: str,
    original_path: str,
    processed_path: str,
    duration: float | None,
    language: str | None,
    model: str,
    processing_time: float,
    rtf: float | None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO recordings (
            filename, created_at, duration, language, model,
            processing_time, rtf, original_path, processed_path, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'complete')
        """,
        (
            filename,
            utc_now(),
            duration,
            language,
            model,
            processing_time,
            rtf,
            original_path,
            processed_path,
        ),
    )
    return int(cursor.lastrowid)


def insert_transcript(
    conn: sqlite3.Connection,
    recording_id: int,
    full_text: str,
    word_count: int,
    character_count: int,
    segment_count: int,
) -> None:
    conn.execute(
        """
        INSERT INTO transcripts (
            recording_id, full_text, word_count, character_count, segment_count
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (recording_id, full_text, word_count, character_count, segment_count),
    )


def insert_segments(conn: sqlite3.Connection, recording_id: int, segments: list[dict[str, Any]]) -> None:
    conn.executemany(
        """
        INSERT INTO segments (recording_id, start_time, end_time, text)
        VALUES (?, ?, ?, ?)
        """,
        [
            (recording_id, float(item["start"]), float(item["end"]), item.get("text") or "")
            for item in segments
        ],
    )


def insert_analytics(conn: sqlite3.Connection, recording_id: int, metrics: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO analytics (
            recording_id, speech_duration, silence_duration, speech_ratio,
            silence_ratio, wpm, cpm, question_count, avg_words_per_segment,
            sentence_count, avg_sentence_length, longest_sentence, shortest_sentence,
            sentiment_label, sentiment_positive, sentiment_negative, sentiment_neutral,
            sentiment_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            recording_id,
            metrics.get("speech_duration"),
            metrics.get("silence_duration"),
            metrics.get("speech_ratio"),
            metrics.get("silence_ratio"),
            metrics.get("wpm"),
            metrics.get("cpm"),
            metrics.get("question_count"),
            metrics.get("avg_words_per_segment"),
            metrics.get("sentence_count"),
            metrics.get("avg_sentence_length"),
            metrics.get("longest_sentence"),
            metrics.get("shortest_sentence"),
            metrics.get("sentiment_label"),
            metrics.get("sentiment_positive"),
            metrics.get("sentiment_negative"),
            metrics.get("sentiment_neutral"),
            metrics.get("sentiment_method"),
        ),
    )


def insert_keywords(conn: sqlite3.Connection, recording_id: int, keywords: list[dict[str, Any]]) -> None:
    conn.executemany(
        """
        INSERT INTO keywords (recording_id, keyword, frequency)
        VALUES (?, ?, ?)
        """,
        [(recording_id, item["keyword"], int(item["frequency"])) for item in keywords],
    )


def _hydrate(recording: sqlite3.Row, conn: sqlite3.Connection) -> dict[str, Any]:
    recording_id = recording["id"]
    transcript = conn.execute(
        "SELECT * FROM transcripts WHERE recording_id = ?", (recording_id,)
    ).fetchone()
    analytics = conn.execute(
        "SELECT * FROM analytics WHERE recording_id = ?", (recording_id,)
    ).fetchone()
    segments = conn.execute(
        "SELECT start_time, end_time, text FROM segments WHERE recording_id = ? ORDER BY start_time",
        (recording_id,),
    ).fetchall()
    keywords = conn.execute(
        "SELECT keyword, frequency FROM keywords WHERE recording_id = ? ORDER BY frequency DESC",
        (recording_id,),
    ).fetchall()
    return {
        "recording": dict(recording),
        "transcript": dict(transcript) if transcript else None,
        "analytics": dict(analytics) if analytics else None,
        "segments": [dict(row) for row in segments],
        "keywords": [dict(row) for row in keywords],
    }


def get_recording(recording_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM recordings WHERE id = ?", (recording_id,)).fetchone()
        if row is None:
            return None
        return _hydrate(row, conn)


def list_recordings(limit: int = 50) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT r.*, t.word_count, a.wpm, a.silence_ratio, a.speech_ratio, a.question_count
            FROM recordings r
            LEFT JOIN transcripts t ON t.recording_id = r.id
            LEFT JOIN analytics a ON a.recording_id = r.id
            ORDER BY r.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def delete_recording(recording_id: int) -> bool:
    payload = get_recording(recording_id)
    if payload is None:
        return False
    recording = payload["recording"]
    for key in ("original_path", "processed_path"):
        path = recording.get(key)
        if path:
            file_path = Path(path)
            if file_path.exists():
                file_path.unlink()
    with get_connection() as conn:
        conn.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
    return True


def dashboard_overview() -> dict[str, Any]:
    with get_connection() as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS total_recordings,
                AVG(duration) AS average_duration,
                AVG(a.wpm) AS average_wpm,
                AVG(a.silence_ratio) AS average_silence_ratio,
                AVG(processing_time) AS average_processing_time,
                AVG(rtf) AS average_rtf
            FROM recordings r
            LEFT JOIN analytics a ON a.recording_id = r.id
            """
        ).fetchone()
        recent = conn.execute(
            """
            SELECT r.id, r.filename, r.created_at, r.duration, r.model,
                   t.word_count, a.wpm
            FROM recordings r
            LEFT JOIN transcripts t ON t.recording_id = r.id
            LEFT JOIN analytics a ON a.recording_id = r.id
            ORDER BY r.id DESC
            LIMIT 8
            """
        ).fetchall()
        series = conn.execute(
            """
            SELECT r.id, r.filename, r.duration, a.wpm, a.silence_ratio,
                   a.speech_ratio, t.segment_count, r.processing_time, r.rtf
            FROM recordings r
            LEFT JOIN analytics a ON a.recording_id = r.id
            LEFT JOIN transcripts t ON t.recording_id = r.id
            ORDER BY r.id ASC
            LIMIT 40
            """
        ).fetchall()
    return {
        "totals": dict(totals) if totals else {},
        "recent": [dict(row) for row in recent],
        "series": [dict(row) for row in series],
    }


def get_setting(key: str, default: str | None = None) -> str | None:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        return str(row["value"])


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
