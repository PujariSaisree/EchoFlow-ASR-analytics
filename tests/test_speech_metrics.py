from app.services.speech_metrics import compute_speech_metrics, count_characters, count_words


def test_word_and_character_counts():
    text = "Decision support needs structured speech data."
    assert count_words(text) == 6
    assert count_characters(text) == len(text)


def test_wpm_silence_and_rtf():
    segments = [
        {"start": 0.0, "end": 4.0, "text": "one two three four five six seven eight nine ten"},
    ]
    text = segments[0]["text"]
    metrics = compute_speech_metrics(
        duration=10.0,
        segments=segments,
        full_text=text,
        processing_time=2.5,
    )
    assert metrics["word_count"] == 10
    assert metrics["speech_duration"] == 4.0
    assert metrics["silence_duration"] == 6.0
    assert metrics["silence_ratio"] == 0.6
    assert metrics["speech_ratio"] == 0.4
    assert metrics["wpm"] == 60.0
    assert metrics["rtf"] == 0.25
