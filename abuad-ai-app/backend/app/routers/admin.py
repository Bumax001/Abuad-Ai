from pathlib import Path
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from app.config import settings
from app.services.rag import rag

router = APIRouter(prefix="/api/admin", tags=["admin"])

def require_admin(x_admin_key: str | None):
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key.")

def documents_path() -> Path:
    p = Path(settings.documents_dir)
    if not p.is_absolute():
        p = (Path(__file__).resolve().parents[3] / p).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p

@router.get("/documents")
def list_documents(x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    result = []
    base = documents_path()
    for f in sorted(base.rglob("*.pdf")):
        result.append({
            "name": f.name,
            "path": str(f.relative_to(base)),
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
        })
    return {"documents": result, "count": len(result)}

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    x_admin_key: str | None = Header(default=None),
):
    require_admin(x_admin_key)
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are accepted.")
    safe_name = Path(file.filename).name.replace("\x00", "")
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    target = documents_path() / safe_name
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb} MB limit.")
    target.write_bytes(data)
    result = rag.reindex()
    return {"message": "Document uploaded and knowledge base re-indexed.", "file": safe_name, **result}

@router.delete("/documents/{filename}")
def delete_document(filename: str, x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    target = documents_path() / safe_name
    if not target.exists():
        raise HTTPException(status_code=404, detail="Document not found.")
    target.unlink()
    result = rag.reindex()
    return {"message": "Document deleted and knowledge base re-indexed.", **result}

@router.post("/reindex")
def reindex(x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    return rag.reindex()
