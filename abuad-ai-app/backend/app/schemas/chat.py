from pydantic import BaseModel, Field

class HistoryMessage(BaseModel):
    role: str
    text: str = Field(min_length=1, max_length=10000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[HistoryMessage] = []
    session_id: str | None = None

class SourceItem(BaseModel):
    document: str
    page: int | None = None
    score: float

class ChatResponse(BaseModel):
    reply: str
    source: str
    session_id: str
    sources: list[SourceItem] = []

class KnowledgeStatus(BaseModel):
    documents: int
    chunks: int
    indexed: bool
