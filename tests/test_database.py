from app.database import (
    delete_recording,
    get_connection,
    get_recording,
    init_db,
    insert_analytics,
    insert_recording,
    insert_transcript,
    list_recordings,
)
from app.config import settings


def test_database_insert_retrieve_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "database_path", tmp_path / "echoflow.db")
    monkeypatch.setattr(settings, "upload_dir", tmp_path / "uploads")
    monkeypatch.setattr(settings, "processed_dir", tmp_path / "processed")
    init_db()
    with get_connection() as conn:
        recording_id = insert_recording(
            conn,
            filename="sample.wav",
            original_path="",
            processed_path="",
            duration=12.0,
            language="en",
            model="tiny",
            processing_time=3.0,
            rtf=0.25,
        )
        insert_transcript(conn, recording_id, "hello world", 2, 11, 1)
        insert_analytics(
            conn,
            recording_id,
            {
                "speech_duration": 8,
                "silence_duration": 4,
                "speech_ratio": 0.67,
                "silence_ratio": 0.33,
                "wpm": 90,
                "cpm": 400,
                "question_count": 1,
            },
        )
    payload = get_recording(recording_id)
    assert payload is not None
    assert payload["transcript"]["word_count"] == 2
    assert list_recordings()[0]["filename"] == "sample.wav"
    assert delete_recording(recording_id) is True
    assert get_recording(recording_id) is None
