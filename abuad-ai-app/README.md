# ABUAD AI — Final Year Project

AI-powered university information assistant for Afe Babalola University (ABUAD).

## v4 highlights
- ChatGPT-style student interface
- FastAPI backend
- Gemini AI integration
- Grounded PDF RAG with page-level sources
- SQLite conversation storage
- Admin knowledge console
- PDF upload/delete/re-index
- Response feedback API
- PWA/offline-ready frontend
- Voice input and text-to-speech features
- Configurable backend URL

## Run backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
uvicorn app.main:app --reload --port 8000
```

Set `GEMINI_API_KEY` and a strong `ADMIN_KEY` in `backend/.env`.
Never commit `.env`.

## Knowledge base
Put official ABUAD PDFs in `documents/`, or use `admin.html` while the backend is running.
Only upload current, authoritative university documents.

## Admin
Open `admin.html` through the same server/origin as the frontend, enter the admin key, then upload PDFs and re-index.

## Frontend/backend connection
The frontend uses the same origin by default. For local development where the frontend is served separately:
```js
localStorage.setItem('abuadai_backend_url_v4', 'http://127.0.0.1:8000')
```

## Important
This project is a final-year academic system. Verify all university-specific facts against official ABUAD sources before production deployment.
