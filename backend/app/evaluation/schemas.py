from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class RetrievedDoc(BaseModel):
    text: str
    retrieval_score: float = Field(ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    pipeline: Literal["naive", "improved"] = "improved"
    ground_truth: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must contain non-whitespace characters")
        return cleaned

    @field_validator("ground_truth")
    @classmethod
    def normalize_ground_truth(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None


class ChatResponse(BaseModel):
    answer: str
    context: list[str]
    pipeline: Literal["naive", "improved"]
    model_version: str
    confidence: float = Field(ge=0.0, le=1.0)
    latency_seconds: float = Field(ge=0.0)
    metrics: dict[str, float]
    timestamp: datetime


class EvaluationResult(BaseModel):
    accuracy: float = Field(ge=0.0, le=1.0)
    faithfulness: float = Field(ge=0.0, le=1.0)
    hallucination: float = Field(ge=0.0, le=1.0)
    context_relevance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class QueryLogCreate(BaseModel):
    query: str
    retrieved_docs: list[str]
    answer: str
    pipeline: Literal["naive", "improved"]
    model_version: str
    latency: float
    accuracy: float
    faithfulness: float
    hallucination: float
    context_relevance: float
    confidence: float
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryLogRecord(QueryLogCreate):
    id: int


class MetricsSummary(BaseModel):
    accuracy: float
    faithfulness: float
    hallucination_rate: float
    context_relevance: float
    avg_latency: float
    confidence: float
    total_queries: int


class HallucinationTrendPoint(BaseModel):
    timestamp: datetime
    hallucination_rate: float


class ModelComparisonPoint(BaseModel):
    model_version: str
    accuracy: float
    faithfulness: float
    hallucination_rate: float
    context_relevance: float
    confidence: float
    avg_latency: float
    total_queries: int


class LatencyBucket(BaseModel):
    bucket: str
    count: int
