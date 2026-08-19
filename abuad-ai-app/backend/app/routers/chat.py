import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database.db import get_db
from app.models.chat import Conversation
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.faq import faq_lookup
from app.services.rag import rag
from app.services.gemini import generate_reply

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    session_id = payload.session_id or str(uuid.uuid4())
    history = [{"role": m.role, "text": m.text} for m in payload.history]
    sources = rag.search(payload.message)

    # Exact starter FAQs are useful even before official PDFs are uploaded.
    faq_reply = faq_lookup(payload.message)
    try:
        if faq_reply and not sources:
            reply = faq_reply
            source = "faq"
        else:
            reply = await generate_reply(payload.message, history, sources)
            source = "rag+gemini" if sources else "gemini"
    except Exception as exc:
        # Give a grounded response when AI is unavailable.
        if faq_reply:
            reply, source = faq_reply, "faq-fallback"
        elif sources:
            reply = (
                "I found relevant information in the university documents, but the AI "
                "service is currently unavailable. Please review the cited source material."
            )
            source = "rag-fallback"
        else:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    db.add(Conversation(
        session_id=session_id,
        user_message=payload.message,
        assistant_message=reply,
        source=source,
    ))
    db.commit()

    return ChatResponse(
        reply=reply,
        source=source,
        session_id=session_id,
        sources=[
            {"document": s["document"], "page": s.get("page"), "score": s["score"]}
            for s in sources
        ],
    )
