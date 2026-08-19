import httpx
from app.config import settings

BASE_SYSTEM_PROMPT = (
    "You are ABUAD AI Assistant, a university information assistant for "
    "Afe Babalola University, Ado-Ekiti. Be accurate, respectful and concise. "
    "Never invent fees, dates, policies, requirements, contacts or official decisions. "
    "When university-specific evidence is provided, use it as the primary source. "
    "If the evidence does not answer the question, clearly say that verified information "
    "is unavailable instead of guessing. For general questions, you may answer normally."
)

async def generate_reply(message: str, history: list[dict], context: list[dict]) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    evidence = "\n\n".join(
        f"[Source: {c['document']}, page {c.get('page')}]\n{c['text']}"
        for c in context
    )
    system = BASE_SYSTEM_PROMPT
    if evidence:
        system += (
            "\n\nVERIFIED UNIVERSITY EVIDENCE:\n" + evidence +
            "\n\nUse this evidence when answering university-specific questions. "
            "Do not cite a source that is not included above."
        )

    contents = []
    for item in history[-settings.max_history_messages:]:
        role = "model" if item["role"] in ("model", "assistant") else "user"
        contents.append({"role": role, "parts": [{"text": item["text"]}]})
    contents.append({"role": "user", "parts": [{"text": message}]})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {"temperature": 0.15, "maxOutputTokens": 1000},
    }

    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url, params={"key": settings.gemini_api_key}, json=payload)
        response.raise_for_status()
        data = response.json()

    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    reply = "".join(p.get("text", "") for p in parts).strip()
    if not reply:
        raise RuntimeError("The AI provider returned an empty response.")
    return reply
