from __future__ import annotations

import os
import re
from pathlib import Path
import requests

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

PROMPT_TEMPLATE = """
You are a helpful insurance claims assistant.
Use only the retrieved claims data to answer the user question.
Do not infer or invent facts that are not explicitly present in context.
If context is insufficient, say: Information is unavailable based on provided claims context.

Rules:
- Mention only claims that appear in Context Data.
- For claim listings, include: claim_id, status, diagnosis, amount, denial_reason (if denied).
- Do not add medical interpretations beyond explicit diagnosis text.
- If user asks for "all" but context is limited, state that results are based on retrieved claims only.

Context Data:
{context}

User Question:
{query}

Answer:
""".strip()


def _extract_claim_ids(text: str) -> set[str]:
    return {m.upper() for m in re.findall(r"CLM-\d+", text, flags=re.IGNORECASE)}


def generate_answer(query: str, context_docs: list[str]) -> str:
    load_dotenv(ENV_FILE, override=True)
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not groq_api_key:
        return "Error: GROQ_API_KEY is missing. Configure backend/.env to enable generation."

    prompt = PROMPT_TEMPLATE.format(context="\n\n".join(context_docs), query=query)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful insurance claims assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
    }

    try:
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {groq_api_key}"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            answer = choices[0].get("message", {}).get("content", "Error: empty response from Groq")

            # Reject answers that mention claims not present in retrieved evidence.
            context_ids = _extract_claim_ids("\n".join(context_docs))
            answer_ids = _extract_claim_ids(answer)
            if answer_ids and not answer_ids.issubset(context_ids):
                return (
                    "Information is unavailable based on provided claims context. "
                    "The model output referenced claims outside retrieved evidence."
                )

            return answer
        return "Error: empty response from Groq"
    except requests.HTTPError as exc:
        status = exc.response.status_code
        if status == 429:
            try:
                detail = exc.response.json().get("error", {}).get("message", exc.response.text)
            except Exception:
                detail = exc.response.text
            return f"Error: Groq rate limit ({status}): {detail}"
        if status == 400:
            return "Error: Invalid request sent to Groq API. Please try a different query."
        if status in (401, 403):
            try:
                detail = exc.response.json().get("error", {}).get("message", exc.response.text)
            except Exception:
                detail = exc.response.text
            return f"Error: Groq auth failed ({status}): {detail}"
        return f"Error generating response from Groq: {status} {exc.response.text}"
    except Exception as exc:
        return f"Error generating response from Groq: {exc}"
