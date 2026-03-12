from app.evaluation.metrics import (
    compute_accuracy,
    compute_confidence,
    compute_context_relevance,
    compute_faithfulness,
    compute_hallucination_rate,
)


def test_accuracy_is_high_for_similar_text() -> None:
    score = compute_accuracy("claim denied for coding error", "claim denied for coding error")
    assert score > 0.9


def test_context_relevance_with_matching_query() -> None:
    score = compute_context_relevance(
        "denied diabetes claims",
        [
            "Status Denied with diagnosis code diabetes and prior authorization missing",
            "Approved orthopedic claim",
        ],
    )
    assert 0.0 <= score <= 1.0


def test_faithfulness_and_hallucination_inverse() -> None:
    faithfulness = compute_faithfulness(
        "claim denied because prior authorization missing",
        ["Denial Reason: Prior Authorization Missing."],
    )
    hallucination = compute_hallucination_rate(faithfulness)
    assert 0.0 <= faithfulness <= 1.0
    assert abs((faithfulness + hallucination) - 1.0) < 1e-9


def test_confidence_average() -> None:
    confidence = compute_confidence(0.8, 0.6)
    assert abs(confidence - 0.7) < 1e-9
