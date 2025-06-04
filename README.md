# Project Title

## Objective

This project is a full-stack application with a FastAPI backend and a React frontend. It supports PDF ingestion, Q&A, and feedback workflows, using SQLite for initial development and Docker for containerization.

---

## Sprint 2 Highlights (June 2025)

- **Backend:**
  - Python 3.13 (Dockerized)
  - FastAPI, SQLAlchemy, Pydantic, Poetry
  - Full CRUD for collections (create, list, retrieve, update, delete)
  - PDF upload and add-by-URL endpoints
  - PDF files stored in `/app/data/pdfs/{collection_id}/` (configurable)
  - Text extraction from PDFs (PyMuPDF)
  - Initial corpus ingestion: auto-registers PDFs from a configured directory on startup
  - All endpoints and logic covered by unit/integration tests (pytest)
- **Frontend:**
  - React (Vite), placeholder UI
- **DevOps:**
  - Docker Compose for backend/frontend, volume mounts for PDF storage and SQLite
  - OpenAPI docs at `/openapi.json`

---

## Quickstart

```sh
# Start all services (backend, frontend)
docker compose up --build -d

# Backend API (FastAPI): http://localhost:8000
# Frontend (React): http://localhost:3000
```

---

## Installing `llama-cpp-python` 0.3.9 on Apple Silicon (M Series Macs)

To install `llama-cpp-python` version 0.3.9 on an M series Mac, you must:

1. **Clear any previous build caches** to avoid conflicts:
   ```sh
   poetry cache clear pypi --all
   poetry run pip cache purge
   ```

2. **Set the required environment variables** before installing:
   ```sh
   source $(poetry env info --path)/bin/activate
   export CMAKE_ARGS="-DLLAMA_METAL=ON -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_APPLE_SILICON_PROCESSOR=arm64"
   export FORCE_CMAKE=1
   ```

3. **Install dependencies with Poetry**:
   ```sh
   poetry install
   ```

---

## API Overview

- `POST /api/v1/collections` — Create collection
- `GET /api/v1/collections` — List collections
- `PUT /api/v1/collections/{id}` — Rename collection
- `DELETE /api/v1/collections/{id}` — Delete collection (prevents if PDFs exist)
- `POST /api/v1/collections/{id}/pdfs/upload` — Upload PDF
- `POST /api/v1/collections/{id}/pdfs/url` — Add PDF by URL
- `GET /api/v1/collections/{id}/pdfs` — List PDFs in collection
- `DELETE /api/v1/pdfs/{pdf_id}` — Delete PDF

See `/openapi.json` for full schema.

## Testing

```sh
cd backend
poetry install --no-root
poetry run pytest --cov
```

## Volumes
- PDF files: `pdf_storage` (mounted to `/app/data/pdfs` in backend container)
- SQLite DB: `sqlite_db_volume`

## Initial Corpus
- On backend startup, all PDFs in the configured `initial_corpus_dir` are registered in the DB under the default collection.

---

See `SPRINT_2_REVIEW.md` for a full summary of Sprint 2 deliverables.
