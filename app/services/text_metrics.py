from __future__ import annotations

import re
from collections import Counter
from typing import Any

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
    "of", "from", "by", "with", "as", "is", "are", "was", "were", "be", "been",
    "being", "it", "this", "that", "these", "those", "i", "you", "we", "they",
    "he", "she", "them", "his", "her", "our", "your", "my", "me", "us", "not",
    "no", "yes", "so", "too", "very", "just", "about", "into", "over", "after",
    "before", "then", "than", "also", "can", "could", "should", "would", "will",
    "do", "does", "did", "have", "has", "had", "there", "here", "what", "which",
    "who", "when", "where", "how", "why", "um", "uh", "like", "okay", "ok",
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "positive", "happy", "helpful", "clear",
    "success", "successful", "agree", "useful", "progress", "confident",
    "thank", "thanks", "pleased", "improve", "improved", "strong",
}

NEGATIVE_WORDS = {
    "bad", "poor", "negative", "issue", "problem", "concern", "delay", "fail",
    "failed", "unclear", "confused", "risk", "complaint", "angry", "difficult",
    "late", "missing", "error", "wrong", "weak",
}


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    return [item.strip() for item in pieces if item.strip()]


def detect_questions(text: str) -> list[str]:
    sentences = split_sentences(text)
    questions = [item for item in sentences if item.endswith("?")]
    if not questions:
        # Fallback: interrogative starters without a question mark.
        starters = re.compile(
            r"^(who|what|when|where|why|how|can|could|would|should|is|are|do|does|did)\b",
            re.IGNORECASE,
        )
        questions = [item for item in sentences if starters.match(item)]
    return questions


def extract_keywords(text: str, limit: int = 12) -> list[dict[str, Any]]:
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())
    filtered = [token for token in tokens if token not in STOPWORDS]
    counts = Counter(filtered)
    return [{"keyword": word, "frequency": freq} for word, freq in counts.most_common(limit)]


def sentence_statistics(text: str) -> dict[str, Any]:
    sentences = split_sentences(text)
    if not sentences:
        return {
            "sentence_count": 0,
            "avg_sentence_length": None,
            "longest_sentence": None,
            "shortest_sentence": None,
        }
    lengths = [len(item.split()) for item in sentences]
    longest = max(sentences, key=lambda item: len(item.split()))
    shortest = min(sentences, key=lambda item: len(item.split()))
    return {
        "sentence_count": len(sentences),
        "avg_sentence_length": sum(lengths) / len(lengths),
        "longest_sentence": longest,
        "shortest_sentence": shortest,
    }


def heuristic_sentiment(text: str) -> dict[str, Any]:
    tokens = re.findall(r"[A-Za-z']+", text.lower())
    if not tokens:
        return {
            "sentiment_label": "insufficient_data",
            "sentiment_positive": None,
            "sentiment_negative": None,
            "sentiment_neutral": None,
            "sentiment_method": "lexicon_heuristic",
        }
    positive = sum(1 for token in tokens if token in POSITIVE_WORDS)
    negative = sum(1 for token in tokens if token in NEGATIVE_WORDS)
    total = max(len(tokens), 1)
    pos_ratio = positive / total
    neg_ratio = negative / total
    remaining = max(0.0, 1.0 - pos_ratio - neg_ratio)
    if positive == 0 and negative == 0:
        label = "neutral"
    elif positive > negative:
        label = "leaning_positive"
    elif negative > positive:
        label = "leaning_negative"
    else:
        label = "mixed"
    return {
        "sentiment_label": label,
        "sentiment_positive": pos_ratio,
        "sentiment_negative": neg_ratio,
        "sentiment_neutral": remaining,
        "sentiment_method": "lexicon_heuristic",
    }


def compute_text_metrics(text: str) -> dict[str, Any]:
    questions = detect_questions(text)
    stats = sentence_statistics(text)
    keywords = extract_keywords(text)
    sentiment = heuristic_sentiment(text)
    topics = [item["keyword"] for item in keywords[:5]]
    return {
        "question_count": len(questions),
        "questions": questions,
        "keywords": keywords,
        "topic_indicators": topics,
        "topic_method": "keyword_frequency",
        **stats,
        **sentiment,
    }
