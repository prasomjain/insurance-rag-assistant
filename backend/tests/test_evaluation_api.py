from fastapi.testclient import TestClient

import app.api.chat_routes as chat_routes
from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_evaluation_endpoints_shape() -> None:
    metrics = client.get("/evaluation/metrics")
    logs = client.get("/evaluation/logs")
    trend = client.get("/evaluation/hallucination-trend")
    model = client.get("/evaluation/model-comparison")
    latency = client.get("/evaluation/latency-distribution")
    confidence = client.get("/evaluation/confidence-scores")

    assert metrics.status_code == 200
    assert logs.status_code == 200
    assert trend.status_code == 200
    assert model.status_code == 200
    assert latency.status_code == 200
    assert confidence.status_code == 200

    assert "logs" in logs.json()
    assert "points" in trend.json()
    assert "models" in model.json()
    assert "buckets" in latency.json()
    assert "points" in confidence.json()


def test_metrics_endpoint_when_no_logs_has_defaults() -> None:
    response = client.get("/evaluation/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert "accuracy" in payload
    assert "faithfulness" in payload
    assert "hallucination_rate" in payload
    assert "avg_latency" in payload


def test_chat_rejects_whitespace_message() -> None:
    response = client.post("/chat", json={"message": "   ", "pipeline": "improved"})
    assert response.status_code == 422


def test_chat_returns_503_when_gemini_key_missing(monkeypatch) -> None:
    def fake_run_rag_query(*args, **kwargs):
        return {
            "answer": "Error: GEMINI_API_KEY is missing. Configure backend/.env to enable generation.",
            "context": [],
            "model_version": "improved-rag-v1",
            "timings": {"total_seconds": 0.01, "retrieval_seconds": 0.0, "rerank_seconds": 0.0, "generation_seconds": 0.01},
        }

    monkeypatch.setattr(chat_routes, "run_rag_query", fake_run_rag_query)

    response = client.post("/chat", json={"message": "test", "pipeline": "improved"})
    assert response.status_code == 503
