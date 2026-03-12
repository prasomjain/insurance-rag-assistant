from __future__ import annotations

import importlib
import importlib.util

from app.evaluation.metrics import (
    clamp01,
    compute_accuracy,
    compute_confidence,
    compute_context_relevance,
    compute_faithfulness,
    compute_hallucination_rate,
)
from app.evaluation.schemas import EvaluationResult


class Evaluator:
    def __init__(self) -> None:
        # Use module spec checks to avoid expensive imports during app startup.
        self.ragas_available = self._module_exists("ragas")
        self.deepeval_available = self._module_exists("deepeval")

    @staticmethod
    def _module_exists(name: str) -> bool:
        return importlib.util.find_spec(name) is not None

    def evaluate(
        self,
        query: str,
        answer: str,
        retrieved_docs: list[str],
        ground_truth: str | None,
    ) -> EvaluationResult:
        # Deterministic baseline scores (always available)
        faithfulness = compute_faithfulness(answer, retrieved_docs)
        context_relevance = compute_context_relevance(query, retrieved_docs)
        accuracy = compute_accuracy(answer, ground_truth)
        if not ground_truth:
            # Fallback proxy when no labeled answer exists.
            accuracy = 0.6 * faithfulness + 0.4 * context_relevance

        # Optional library-assisted adjustment. If library execution fails, fallback remains.
        faithfulness = self._try_adjust_faithfulness(query, answer, retrieved_docs, faithfulness)
        context_relevance = self._try_adjust_relevance(query, answer, retrieved_docs, context_relevance)

        hallucination = compute_hallucination_rate(faithfulness)
        confidence = compute_confidence(faithfulness, context_relevance)

        return EvaluationResult(
            accuracy=clamp01(accuracy),
            faithfulness=clamp01(faithfulness),
            hallucination=clamp01(hallucination),
            context_relevance=clamp01(context_relevance),
            confidence=clamp01(confidence),
        )

    def _try_adjust_faithfulness(
        self,
        query: str,
        answer: str,
        retrieved_docs: list[str],
        baseline: float,
    ) -> float:
        if not self.ragas_available:
            return baseline

        try:
            datasets_mod = importlib.import_module("datasets")
            ragas_mod = importlib.import_module("ragas")
            ragas_metrics_mod = importlib.import_module("ragas.metrics")

            Dataset = getattr(datasets_mod, "Dataset")
            evaluate = getattr(ragas_mod, "evaluate")
            faithfulness = getattr(ragas_metrics_mod, "faithfulness")

            dataset = Dataset.from_dict(
                {
                    "question": [query],
                    "answer": [answer],
                    "contexts": [retrieved_docs],
                }
            )
            result = evaluate(dataset, metrics=[faithfulness])
            score = float(result["faithfulness"])  # type: ignore[index]
            return score
        except Exception:
            return baseline

    def _try_adjust_relevance(
        self,
        query: str,
        answer: str,
        retrieved_docs: list[str],
        baseline: float,
    ) -> float:
        if not self.ragas_available:
            return baseline

        try:
            datasets_mod = importlib.import_module("datasets")
            ragas_mod = importlib.import_module("ragas")
            ragas_metrics_mod = importlib.import_module("ragas.metrics")

            Dataset = getattr(datasets_mod, "Dataset")
            evaluate = getattr(ragas_mod, "evaluate")
            answer_relevancy = getattr(ragas_metrics_mod, "answer_relevancy")

            dataset = Dataset.from_dict(
                {
                    "question": [query],
                    "answer": [answer],
                    "contexts": [retrieved_docs],
                }
            )
            result = evaluate(dataset, metrics=[answer_relevancy])
            score = float(result["answer_relevancy"])  # type: ignore[index]
            return score
        except Exception:
            return baseline


evaluator = Evaluator()
