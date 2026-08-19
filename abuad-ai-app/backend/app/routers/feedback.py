from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.feedback import Feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)
    rating: int = Field(ge=-1, le=1)

@router.post("")
def feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    db.add(Feedback(**payload.model_dump()))
    db.commit()
    return {"ok": True}
