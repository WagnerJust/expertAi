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

## Environment Configuration

The project uses environment variables for configuration. Before running the application:

1. **Copy the example environment file:**
   ```sh
   cp .env.example .env
   ```

2. **Update the `.env` file with your specific paths:**
   - `INITIAL_CORPUS_PATH`: Path to directory containing PDFs to be automatically ingested on startup

**Example `.env` configuration:**
```env
INITIAL_CORPUS_PATH=/Users/yourname/Documents/PDFs/InitialCorpus/
```

---

## Quickstart

### Option 1: Standard Docker Setup
```sh
# Start all services (backend, frontend)
docker compose up --build -d

# Backend API (FastAPI): http://localhost:8000
# Frontend (React): http://localhost:3000
```

### Option 2: Tailscale-Enabled Setup 🌐
Perfect for accessing your app from anywhere on your Tailscale network!

```sh
# Production mode with Tailscale support
./start-tailscale.sh

# Development mode with hot-reload and Tailscale support
./start-dev-tailscale.sh

# Check Tailscale connectivity and service health
./tailscale-health-check.sh
```

**Tailscale Access URLs:**
- Frontend: `http://[your-tailscale-ip]:3000`
- Backend API: `http://[your-tailscale-ip]:8000`
- API Documentation: `http://[your-tailscale-ip]:8000/docs`

**Prerequisites for Tailscale:**
- [Tailscale](https://tailscale.com) installed and connected
- Docker and Docker Compose installed

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

## Volumes
- PDF files: `pdf_storage` (mounted to `/app/data/pdfs` in backend container)
- SQLite DB: `sqlite_db_volume`

## Initial Corpus
- On backend startup, all PDFs in the configured `initial_corpus_dir` are registered in the DB under the default collection.

---

See `SPRINT_2_REVIEW.md` for a full summary of Sprint 2 deliverables.
