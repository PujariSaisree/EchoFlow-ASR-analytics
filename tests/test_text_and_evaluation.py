from app.services.evaluation import character_error_rate, word_error_rate
from app.services.text_metrics import compute_text_metrics, detect_questions


def test_question_detection():
    text = "What should we review? The timeline is tight. How many risks remain?"
    questions = detect_questions(text)
    assert len(questions) == 2


def test_keyword_extraction():
    metrics = compute_text_metrics("Budget risk budget planning risk review budget.")
    words = {item["keyword"]: item["frequency"] for item in metrics["keywords"]}
    assert words["budget"] == 3
    assert metrics["question_count"] == 0


def test_wer_and_cer():
    reference = "the meeting started on time"
    hypothesis = "the meeting started late"
    assert word_error_rate(reference, hypothesis) == 1 / 5
    assert character_error_rate("abc", "abc") == 0
    assert word_error_rate("   ", "hello") is None
