from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from app.evaluation.evaluator import evaluator
from app.evaluation.schemas import QueryLogCreate
from app.evaluation.storage import storage
from app.rag.pipeline import run_rag_query


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "evaluation" / "benchmark_queries.json"


def run_benchmark() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Benchmark file not found: {DATASET_PATH}")

    rows = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    pipelines: list[Literal["naive", "improved"]] = ["naive", "improved"]

    total = 0
    for row in rows:
        query = row["query"]
        ground_truth = row.get("ground_truth")

        for pipeline in pipelines:
            rag_result = run_rag_query(query, pipeline=pipeline)
            eval_result = evaluator.evaluate(
                query=query,
                answer=rag_result["answer"],
                retrieved_docs=rag_result["context"],
                ground_truth=ground_truth,
            )

            storage.insert_log(
                QueryLogCreate(
                    query=query,
                    retrieved_docs=rag_result["context"],
                    answer=rag_result["answer"],
                    pipeline=pipeline,
                    model_version=rag_result["model_version"],
                    latency=rag_result["timings"]["total_seconds"],
                    accuracy=eval_result.accuracy,
                    faithfulness=eval_result.faithfulness,
                    hallucination=eval_result.hallucination,
                    context_relevance=eval_result.context_relevance,
                    confidence=eval_result.confidence,
                    timestamp=datetime.now(timezone.utc),
                    metadata={"benchmark": True},
                )
            )
            total += 1
            print(f"Logged benchmark result for pipeline={pipeline} query={query}")

    print(f"Benchmark completed. Inserted {total} query evaluation rows.")


if __name__ == "__main__":
    run_benchmark()
