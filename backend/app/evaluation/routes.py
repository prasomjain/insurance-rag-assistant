from __future__ import annotations

from fastapi import APIRouter, Query

from app.evaluation.storage import storage

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/metrics")
def get_metrics() -> dict:
    return storage.metrics_summary()


@router.get("/logs")
def get_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    return {
        "logs": storage.list_logs(limit=limit, offset=offset),
        "limit": limit,
        "offset": offset,
    }


@router.get("/hallucination-trend")
def get_hallucination_trend(limit: int = Query(default=200, ge=1, le=2000)) -> dict:
    return {"points": storage.hallucination_trend(limit=limit)}


@router.get("/model-comparison")
def get_model_comparison() -> dict:
    return {"models": storage.model_comparison()}


@router.get("/latency-distribution")
def get_latency_distribution() -> dict:
    return {"buckets": storage.latency_distribution()}


@router.get("/confidence-scores")
def get_confidence_scores(limit: int = Query(default=200, ge=1, le=2000)) -> dict:
    return {"points": storage.confidence_series(limit=limit)}
