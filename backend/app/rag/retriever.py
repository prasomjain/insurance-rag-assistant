from __future__ import annotations

import os
import re
from typing import Any, cast

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../chroma_db")
_client: Any | None = None
_collection: Any | None = None


DIAGNOSIS_TERMS = {
    "diabetes": ["diabetes", "e10", "e11"],
    "hypertension": ["hypertension", "i10"],
    "asthma": ["asthma", "j45"],
    "hyperlipidemia": ["hyperlipidemia", "e78"],
    "anxiety": ["anxiety", "f41"],
    "reflux": ["reflux", "gerd", "k21"],
    "migraine": ["migraine", "g43"],
    "dermatitis": ["dermatitis", "eczema", "l20"],
    "uti": ["uti", "urinary tract infection", "n39"],
    "osteoarthritis": ["osteoarthritis", "m17"],
}


def _parse_filters(query: str) -> dict[str, Any]:
    q = query.lower()
    status: str | None = None
    if "denied" in q:
        status = "Denied"
    elif "approved" in q:
        status = "Approved"
    elif "pending" in q:
        status = "Pending"

    diagnosis_keywords: list[str] = []
    for name, terms in DIAGNOSIS_TERMS.items():
        if any(t in q for t in terms):
            diagnosis_keywords.extend(terms)
            diagnosis_keywords.append(name)

    # Capture ICD-like code hints from query (e.g., E11.9, I10)
    diagnosis_keywords.extend(re.findall(r"[A-Za-z]\d{2}(?:\.\d+)?", query))

    return {
        "status": status,
        "diagnosis_keywords": [k.lower() for k in dict.fromkeys(diagnosis_keywords)],
    }


def _matches_filters(item: dict[str, Any], filters: dict[str, Any]) -> bool:
    metadata = item.get("metadata") or {}
    text = str(item.get("text", "")).lower()
    status = filters.get("status")
    if status and str(metadata.get("status", "")).lower() != str(status).lower():
        return False

    keywords: list[str] = filters.get("diagnosis_keywords") or []
    if keywords:
        diagnosis_blob = " ".join(
            [
                str(metadata.get("diagnosis_name", "")),
                str(metadata.get("diagnosis_code", "")),
                text,
            ]
        ).lower()
        if not any(k in diagnosis_blob for k in keywords):
            return False

    return True


def _get_collection() -> Any:
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    _collection = cast(Any, _client).get_or_create_collection(
        name="claims_collection",
        embedding_function=cast(Any, sentence_transformer_ef),
    )
    return _collection


def retrieve(query: str, n_results: int = 8) -> list[dict[str, Any]]:
    if not query.strip() or n_results < 1:
        return []

    filters = _parse_filters(query)
    query_n_results = n_results
    if filters["status"] or filters["diagnosis_keywords"]:
        # Pull a broader candidate set when query has hard constraints, then filter precisely.
        query_n_results = max(n_results * 4, 24)

    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=query_n_results)
    documents_payload = results.get("documents") or [[]]
    distances_payload = results.get("distances") or [[]]
    metadatas_payload = results.get("metadatas") or [[]]

    documents = documents_payload[0] if documents_payload else []
    distances = distances_payload[0] if distances_payload else []
    metadatas = metadatas_payload[0] if metadatas_payload else []

    output: list[dict[str, Any]] = []
    for idx, doc in enumerate(documents):
        if doc is None:
            continue
        distance = float(distances[idx]) if idx < len(distances) else 1.0
        score = max(0.0, min(1.0, 1.0 - distance))
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        output.append(
            {
                "text": str(doc),
                "retrieval_score": score,
                "distance": distance,
                "metadata": metadata,
            }
        )

    filtered = [item for item in output if _matches_filters(item, filters)]
    if filtered:
        filtered.sort(key=lambda x: float(x.get("retrieval_score", 0.0)), reverse=True)
        return filtered[:n_results]

    output.sort(key=lambda x: float(x.get("retrieval_score", 0.0)), reverse=True)
    return output[:n_results]
