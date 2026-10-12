from __future__ import annotations

import re


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _levenshtein(left: list[str], right: list[str]) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, left_token in enumerate(left, start=1):
        current = [i]
        for j, right_token in enumerate(right, start=1):
            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (left_token != right_token)
            current.append(min(insertion, deletion, substitution))
        previous = current
    return previous[-1]


def word_error_rate(reference: str, hypothesis: str) -> float | None:
    ref_tokens = _tokens(reference)
    if not ref_tokens:
        return None
    hyp_tokens = _tokens(hypothesis)
    return _levenshtein(ref_tokens, hyp_tokens) / len(ref_tokens)


def character_error_rate(reference: str, hypothesis: str) -> float | None:
    ref_chars = list(re.sub(r"\s+", "", reference.lower()))
    if not ref_chars:
        return None
    hyp_chars = list(re.sub(r"\s+", "", hypothesis.lower()))
    return _levenshtein(ref_chars, hyp_chars) / len(ref_chars)
