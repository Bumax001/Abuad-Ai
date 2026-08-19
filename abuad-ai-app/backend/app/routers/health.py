from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["system"])

@router.get("/")
def home():
    return {"name": settings.app_name, "version": settings.app_version, "status": "running"}

@router.get("/health")
def health():
    return {"status": "healthy", "version": settings.app_version}
