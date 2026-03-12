from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.evaluation.schemas import ChatRequest, QueryLogCreate
from app.evaluation.storage import EvaluationStorage
from app.rag.pipeline import run_rag_query


def test_chat_request_rejects_whitespace_only_message() -> None:
    with pytest.raises(Exception):
        ChatRequest(message="   ")


def test_run_rag_query_rejects_blank_input() -> None:
    with pytest.raises(ValueError):
        run_rag_query("   ")


def test_storage_log_list_parses_json_fields(tmp_path: Path) -> None:
    db = EvaluationStorage(tmp_path / "edge_case_logs.db")
    db.insert_log(
        QueryLogCreate(
            query="test",
            retrieved_docs=["doc1", "doc2"],
            answer="answer",
            pipeline="naive",
            model_version="naive-rag-v1",
            latency=0.5,
            accuracy=0.4,
            faithfulness=0.5,
            hallucination=0.5,
            context_relevance=0.4,
            confidence=0.45,
            timestamp=datetime.now(timezone.utc),
            metadata={"source": "test"},
        )
    )

    logs = db.list_logs(limit=5, offset=0)
    assert len(logs) == 1
    assert isinstance(logs[0]["retrieved_docs"], list)
    assert isinstance(logs[0]["metadata_json"], dict)