from fastapi import APIRouter, Header, HTTPException
from app.config import settings
from app.services.rag import rag

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

def require_admin(x_admin_key: str | None):
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key.")

@router.get("/status")
def status():
    return rag.status()

@router.post("/reindex")
def reindex(x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    return rag.reindex()
