# SPRINT 1 REVIEW

## System Architecture & Technology Stack
- **Backend:** Python 3.10, FastAPI, SQLAlchemy, Pydantic, Poetry, Alembic, SQLite (Docker volume), Docker
- **Frontend:** React (Vite), JavaScript, Docker, Nginx (for static serve)
- **Testing:** Pytest (backend), Vitest/React Testing Library (frontend)
- **Containerization:** Docker, docker compose with named volumes for data persistence
- **PDF/Embedding/LLM:** (To be selected in future sprints)

## API Contract Design
- **Collections:**
  - `POST /api/v1/collections` (create)
  - `GET /api/v1/collections` (list)
  - `GET /api/v1/collections/{collection_id}` (retrieve)
  - `PUT /api/v1/collections/{collection_id}` (update)
  - `DELETE /api/v1/collections/{collection_id}` (delete)
- **PDFs:**
  - `POST /api/v1/collections/{collection_id}/pdfs/upload` (upload)
  - `POST /api/v1/collections/{collection_id}/pdfs/url` (add by URL)
- **Q&A:**
  - `POST /api/v1/collections/{collection_id}/qa` (ask question)
  - `GET /api/v1/collections/{collection_id}/history` (get Q&A history)
- **Feedback:**
  - `POST /api/v1/qa/answers/{answer_id}/feedback`
- **Admin:**
  - `POST /api/v1/admin/collections/{collection_id}/reindex`
- **OpenAPI Spec:** FastAPI auto-generates at `/openapi.json` (or `/api/v1/openapi.json`)
- **Pydantic Models:** See `backend/app/models/schemas.py`

## Database Schema (from db_models.py)
- **Collection:** id, name, created_at
- **PDFDocument:** id, filename, title, status, collection_id
- **QueryHistory:** id, text, collection_id, timestamp
- **Answer:** id, query_id, text, context_used, sources
- **AnswerFeedback:** id, answer_id, rating, comment

## Demonstration Checklist
- [x] Backend service starts: `uvicorn backend.app.main:app --reload` (health check `/` returns 200 OK)
- [x] Frontend placeholder loads: `npm run dev` (Vite)
- [x] `docker compose build` runs for both services
- [x] Basic tests pass for backend and frontend

---

**See repo for code, Dockerfiles, and test results.**
