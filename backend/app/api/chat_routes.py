from __future__ import annotations

from datetime import datetime, timezone
import threading

from fastapi import APIRouter, HTTPException

from app.evaluation.evaluator import evaluator
from app.evaluation.schemas import ChatRequest, ChatResponse, QueryLogCreate
from app.evaluation.storage import storage
from app.rag.pipeline import run_rag_query

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        rag_result = run_rag_query(request.message, pipeline=request.pipeline)
        answer = rag_result["answer"]
        if isinstance(answer, str) and answer.startswith("Error: GROQ_API_KEY is missing"):
            raise HTTPException(status_code=503, detail="Groq API key is not configured")

        eval_result = evaluator.evaluate(
            query=request.message,
            answer=answer,
            retrieved_docs=rag_result["context"],
            ground_truth=request.ground_truth,
        )

        timestamp = datetime.now(timezone.utc)
        storage.insert_log(
            QueryLogCreate(
                query=request.message,
                retrieved_docs=rag_result["context"],
                answer=answer,
                pipeline=request.pipeline,
                model_version=rag_result["model_version"],
                latency=rag_result["timings"]["total_seconds"],
                accuracy=eval_result.accuracy,
                faithfulness=eval_result.faithfulness,
                hallucination=eval_result.hallucination,
                context_relevance=eval_result.context_relevance,
                confidence=eval_result.confidence,
                timestamp=timestamp,
                metadata={"timings": rag_result["timings"]},
            )
        )

        return ChatResponse(
            answer=rag_result["answer"],
            context=rag_result["context"],
            pipeline=request.pipeline,
            model_version=rag_result["model_version"],
            confidence=eval_result.confidence,
            latency_seconds=rag_result["timings"]["total_seconds"],
            metrics={
                "accuracy": eval_result.accuracy,
                "faithfulness": eval_result.faithfulness,
                "hallucination": eval_result.hallucination,
                "context_relevance": eval_result.context_relevance,
            },
            timestamp=timestamp,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/trigger-etl")
def trigger_etl() -> dict:
    from app.etl import run_etl

    thread = threading.Thread(target=run_etl)
    thread.start()
    return {"status": "ETL started in background"}