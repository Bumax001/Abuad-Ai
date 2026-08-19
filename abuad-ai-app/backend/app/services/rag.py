from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings

INDEX_FILE = Path(__file__).resolve().parents[2] / "knowledge_index.json"

class RAGService:
    def __init__(self):
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.chunks: list[dict[str, Any]] = []
        self.last_indexed = None
        self._load()

    def _load(self):
        if not INDEX_FILE.exists():
            return
        try:
            payload = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            self.chunks = payload.get("chunks", [])
            self.last_indexed = payload.get("indexed_at")
            texts = [c["text"] for c in self.chunks]
            if texts:
                self.vectorizer = TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=30000,
                )
                self.matrix = self.vectorizer.fit_transform(texts)
        except Exception:
            self.chunks, self.vectorizer, self.matrix = [], None, None

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _chunk(self, text: str, size: int = 1200, overlap: int = 180):
        words = self._clean(text).split()
        if not words:
            return []
        chunks = []
        start = 0
        while start < len(words):
            end = min(len(words), start + size)
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def reindex(self) -> dict[str, int]:
        docs_dir = Path(settings.documents_dir)
        if not docs_dir.is_absolute():
            docs_dir = (Path(__file__).resolve().parents[2] / docs_dir).resolve()
        docs_dir.mkdir(parents=True, exist_ok=True)

        new_chunks = []
        for pdf in sorted(docs_dir.rglob("*.pdf")):
            try:
                reader = PdfReader(str(pdf))
            except Exception:
                continue
            for page_no, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                for idx, chunk in enumerate(self._chunk(text)):
                    new_chunks.append({
                        "id": f"{pdf.name}:{page_no}:{idx}",
                        "document": pdf.name,
                        "page": page_no,
                        "text": chunk,
                    })

        self.chunks = new_chunks
        texts = [c["text"] for c in self.chunks]
        if texts:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                max_features=30000,
            )
            self.matrix = self.vectorizer.fit_transform(texts)
        else:
            self.vectorizer, self.matrix = None, None

        self.last_indexed = datetime.now(timezone.utc).isoformat()
        INDEX_FILE.write_text(
            json.dumps({"chunks": self.chunks, "indexed_at": self.last_indexed}, ensure_ascii=False),
            encoding="utf-8",
        )
        return {"documents": len({c["document"] for c in self.chunks}), "chunks": len(self.chunks)}

    def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        if not self.vectorizer or self.matrix is None or not self.chunks:
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        indices = scores.argsort()[::-1]
        results = []
        for i in indices[: top_k or settings.rag_top_k]:
            score = float(scores[i])
            if score <= 0:
                continue
            item = dict(self.chunks[i])
            item["score"] = round(score, 4)
            results.append(item)
        return results

    def status(self):
        return {
            "documents": len({c["document"] for c in self.chunks}),
            "chunks": len(self.chunks),
            "indexed": bool(self.chunks and self.vectorizer),
            "last_indexed": self.last_indexed,
        }

rag = RAGService()
