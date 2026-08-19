from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.db import Base, engine
from app.models.chat import Conversation  # noqa: F401
from app.routers import health, chat, knowledge, admin, feedback
from app.services.rag import rag

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Loading an existing index is instant; don't block startup on PDF parsing.
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI + RAG backend for the ABUAD university information chatbot.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.frontend_origin.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(admin.router)
app.include_router(feedback.router)
