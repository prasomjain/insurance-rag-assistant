from __future__ import annotations

import os
import re
import time
from collections import Counter
from typing import Literal

from app.rag.generator import generate_answer
from app.rag.retriever import retrieve

PipelineName = Literal["naive", "improved"]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def _heuristic_rerank(query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
    query_tokens = _tokenize(query)
    query_counter = Counter(query_tokens)

    ranked = []
    for entry in docs:
        doc_tokens = _tokenize(entry["text"])
        doc_counter = Counter(doc_tokens)
        overlap = sum(min(query_counter[t], doc_counter[t]) for t in query_counter)
        lexical = overlap / max(1, len(query_tokens))
        status_boost = 0.1 if "denied" in query.lower() and "denied" in entry["text"].lower() else 0.0
        blended = 0.7 * float(entry.get("retrieval_score", 0.0)) + 0.3 * lexical + status_boost
        item = dict(entry)
        item["rerank_score"] = min(1.0, max(0.0, blended))
        ranked.append(item)

    ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]


def _cross_encoder_rerank(query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
    model_name = os.getenv("RAG_CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    try:
        from sentence_transformers import CrossEncoder

        model = CrossEncoder(model_name)
        pairs = [(query, doc["text"]) for doc in docs]
        scores = model.predict(pairs)

        ranked = []
        for idx, score in enumerate(scores):
            item = dict(docs[idx])
            item["rerank_score"] = float(score)
            ranked.append(item)

        ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_k]
    except Exception:
        return _heuristic_rerank(query, docs, top_k=top_k)


def run_rag_query(user_query: str, pipeline: PipelineName = "improved", n_results: int = 8) -> dict:
    cleaned_query = user_query.strip()
    if not cleaned_query:
        raise ValueError("Query cannot be empty")
    if n_results < 1:
        raise ValueError("n_results must be >= 1")

    started = time.perf_counter()

    retrieval_started = time.perf_counter()
    if pipeline == "improved":
        n_results = max(n_results, 12)
    retrieved = retrieve(cleaned_query, n_results=n_results)
    retrieval_seconds = time.perf_counter() - retrieval_started

    rerank_seconds = 0.0
    selected = retrieved[:4]
    if pipeline == "improved":
        rerank_started = time.perf_counter()
        use_cross_encoder = os.getenv("RAG_ENABLE_CROSS_ENCODER", "false").lower() == "true"
        if use_cross_encoder:
            selected = _cross_encoder_rerank(cleaned_query, retrieved, top_k=5)
        else:
            selected = _heuristic_rerank(cleaned_query, retrieved, top_k=5)
        rerank_seconds = time.perf_counter() - rerank_started

    docs = [entry["text"] for entry in selected]

    generation_started = time.perf_counter()
    answer = generate_answer(cleaned_query, docs)
    generation_seconds = time.perf_counter() - generation_started
    total_seconds = time.perf_counter() - started

    model_version = "improved-rag-v1" if pipeline == "improved" else "naive-rag-v1"

    return {
        "answer": answer,
        "context": docs,
        "pipeline": pipeline,
        "model_version": model_version,
        "timings": {
            "retrieval_seconds": retrieval_seconds,
            "rerank_seconds": rerank_seconds,
            "generation_seconds": generation_seconds,
            "total_seconds": total_seconds,
        },
        "retrieved_docs": selected,
    }
