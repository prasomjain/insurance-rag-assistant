from __future__ import annotations

import math
import re
from collections import Counter


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def jaccard_similarity(text_a: str, text_b: str) -> float:
    set_a = set(tokenize(text_a))
    set_b = set(tokenize(text_b))
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def cosine_similarity(text_a: str, text_b: str) -> float:
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0

    counter_a = Counter(tokens_a)
    counter_b = Counter(tokens_b)
    all_terms = set(counter_a) | set(counter_b)

    numerator = sum(counter_a[t] * counter_b[t] for t in all_terms)
    denom_a = math.sqrt(sum(v * v for v in counter_a.values()))
    denom_b = math.sqrt(sum(v * v for v in counter_b.values()))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)


def compute_accuracy(answer: str, ground_truth: str | None) -> float:
    if not ground_truth:
        return 0.0
    similarity = cosine_similarity(answer, ground_truth)
    return clamp01(similarity)


def compute_context_relevance(query: str, retrieved_docs: list[str]) -> float:
    if not retrieved_docs:
        return 0.0
    similarities = [cosine_similarity(query, doc) for doc in retrieved_docs]
    return clamp01(sum(similarities) / len(similarities))


def compute_faithfulness(answer: str, retrieved_docs: list[str]) -> float:
    if not retrieved_docs:
        return 0.0
    best_support = max(jaccard_similarity(answer, doc) for doc in retrieved_docs)
    return clamp01(best_support)


def compute_hallucination_rate(faithfulness: float) -> float:
    return clamp01(1.0 - faithfulness)


def compute_confidence(faithfulness: float, context_relevance: float) -> float:
    return clamp01((faithfulness + context_relevance) / 2.0)
