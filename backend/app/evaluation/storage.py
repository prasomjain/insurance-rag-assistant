from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.evaluation.schemas import QueryLogCreate


class EvaluationStorage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    retrieved_docs TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    pipeline TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    accuracy REAL NOT NULL,
                    faithfulness REAL NOT NULL,
                    hallucination REAL NOT NULL,
                    context_relevance REAL NOT NULL,
                    confidence REAL NOT NULL,
                    latency REAL NOT NULL,
                    metadata_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON query_logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_model_version ON query_logs(model_version)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_pipeline ON query_logs(pipeline)")

    def insert_log(self, payload: QueryLogCreate) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO query_logs (
                    query, retrieved_docs, answer, pipeline, model_version,
                    accuracy, faithfulness, hallucination, context_relevance,
                    confidence, latency, metadata_json, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.query,
                    json.dumps(payload.retrieved_docs),
                    payload.answer,
                    payload.pipeline,
                    payload.model_version,
                    payload.accuracy,
                    payload.faithfulness,
                    payload.hallucination,
                    payload.context_relevance,
                    payload.confidence,
                    payload.latency,
                    json.dumps(payload.metadata),
                    payload.timestamp.astimezone(timezone.utc).isoformat(),
                ),
            )
            last_id = cursor.lastrowid
            return int(last_id) if last_id is not None else -1

    def list_logs(self, limit: int = 100, offset: int = 0) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM query_logs
                ORDER BY datetime(timestamp) DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()

        output: list[dict] = []
        for row in rows:
            item = dict(row)
            item["retrieved_docs"] = json.loads(item.get("retrieved_docs") or "[]")
            item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
            output.append(item)

        return output

    def metrics_summary(self) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_queries,
                    COALESCE(AVG(accuracy), 0) AS accuracy,
                    COALESCE(AVG(faithfulness), 0) AS faithfulness,
                    COALESCE(AVG(hallucination), 0) AS hallucination_rate,
                    COALESCE(AVG(context_relevance), 0) AS context_relevance,
                    COALESCE(AVG(confidence), 0) AS confidence,
                    COALESCE(AVG(latency), 0) AS avg_latency
                FROM query_logs
                """
            ).fetchone()
        return dict(row) if row else {}

    def hallucination_trend(self, limit: int = 200) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT timestamp, hallucination AS hallucination_rate
                FROM query_logs
                ORDER BY datetime(timestamp) ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def model_comparison(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    model_version,
                    COUNT(*) AS total_queries,
                    COALESCE(AVG(accuracy), 0) AS accuracy,
                    COALESCE(AVG(faithfulness), 0) AS faithfulness,
                    COALESCE(AVG(hallucination), 0) AS hallucination_rate,
                    COALESCE(AVG(context_relevance), 0) AS context_relevance,
                    COALESCE(AVG(confidence), 0) AS confidence,
                    COALESCE(AVG(latency), 0) AS avg_latency
                FROM query_logs
                GROUP BY model_version
                ORDER BY model_version ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def latency_distribution(self) -> list[dict]:
        buckets = [
            ("0-0.5s", 0.0, 0.5),
            ("0.5-1s", 0.5, 1.0),
            ("1-2s", 1.0, 2.0),
            ("2-3s", 2.0, 3.0),
            ("3s+", 3.0, float("inf")),
        ]

        with self._connect() as conn:
            all_latencies = conn.execute("SELECT latency FROM query_logs").fetchall()

        values = [float(row["latency"]) for row in all_latencies]
        output = []
        for name, low, high in buckets:
            if high == float("inf"):
                count = sum(1 for latency in values if latency >= low)
            else:
                count = sum(1 for latency in values if low <= latency < high)
            output.append({"bucket": name, "count": count})
        return output

    def confidence_series(self, limit: int = 200) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT timestamp, confidence
                FROM query_logs
                ORDER BY datetime(timestamp) ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


_db_file = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "evaluation_logs.db"
storage = EvaluationStorage(db_path=_db_file)
