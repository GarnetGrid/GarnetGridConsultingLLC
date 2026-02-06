from __future__ import annotations

import json
import os
import httpx

JUDGE_RUBRIC = {
    "powerbi": [
        "DAX syntax is valid and uses real functions",
        "Uses a proper Date table / time intelligence pattern when relevant",
        "Explains key concepts correctly (context, relationships, totals)",
        "Avoids hallucinated tables/columns OR clearly marks placeholders",
    ],
    "d365fo": [
        "Correctly explains ttsBegin/ttsCommit semantics and rollback behavior",
        "Uses correct X++ syntax / extensibility patterns",
        "Provides actionable troubleshooting steps",
        "Avoids hallucinated APIs/classes OR clearly marks placeholders",
    ],
}

async def judge_answer(mode: str, question: str, answer: str) -> dict:
    base = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    model = os.getenv("JUDGE_MODEL", os.getenv("CHAT_MODEL", "llama3.2"))
    rubric = JUDGE_RUBRIC.get((mode or "").lower(), JUDGE_RUBRIC["powerbi"])

    prompt = {
        "mode": mode,
        "question": question,
        "answer": answer,
        "rubric": rubric,
        "instructions": [
            "Score each rubric item: 0 (miss), 1 (partial), 2 (good).",
            "Return STRICT JSON only. No markdown.",
            "Schema: {items:[{rubric:string,score:int,notes:string}], total:int, max:int, grade:string, confidence:float}",
            "confidence is 0..1 based on how sure you are the answer is correct and complete."
        ],
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a strict evaluator. Output JSON only."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{base}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return {"items": [], "total": 0, "max": 2 * len(rubric), "grade": "N/A", "confidence": 0.0, "error": str(e)}

    content = ((data.get("message") or {}).get("content")) or ""
    try:
        obj = json.loads(content)
        # basic normalization
        obj.setdefault("max", 2 * len(rubric))
        if "confidence" in obj:
            try:
                obj["confidence"] = float(obj["confidence"])
            except Exception:
                obj["confidence"] = 0.0
        return obj
    except Exception:
        return {
            "items": [],
            "total": 0,
            "max": 2 * len(rubric),
            "grade": "N/A",
            "confidence": 0.0,
            "notes": "Judge returned non-JSON.",
            "raw": content[:2000],
        }
