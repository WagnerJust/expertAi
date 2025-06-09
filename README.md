# Project Title

## Objective

This project is a full-stack application with a FastAPI backend and a React frontend. It supports PDF ingestion, Q&A, and feedback workflows, using SQLite for initial development and Docker for containerization.

---

## Sprint 3 Highlights (Current - Python 3.11 & RAG Pipeline)

- **Environment:**
  - **Python 3.11.5** (upgraded from 3.13)
  - All dependencies updated for Python 3.11 compatibility
- **Backend RAG Components:**
  - **Text Chunking**: Configurable text splitting with metadata preservation
  - **Embedding Generation**: Local sentence-transformers model (all-mpnet-base-v2)
  - **Vector Storage**: **ChromaDB Docker service** with HTTP client (eliminates permission issues)
  - **LLM Integration**: Ollama Docker service for local inference
  - All components covered by comprehensive unit tests (11/12 passing - 92% success rate)
- **Docker Services:**
  - **ChromaDB**: Persistent vector storage at port 8001
  - **Ollama**: Local LLM service at port 11434
  - **PostgreSQL**: Metadata and history storage
- **DevOps:**
  - ChromaDB Docker setup script (`/scripts/setup-chroma-docker.sh`)
  - Updated docker-compose.yml with all required services
  - Health checks and proper service dependencies

---

## Sprint 2 Highlights (June 2025)

- **Backend:**
  - Python 3.11 (upgraded for stability and ChromaDB compatibility)
  - FastAPI, SQLAlchemy, Pydantic
  - Full CRUD for collections (create, list, retrieve, update, delete)
  - PDF upload and add-by-URL endpoints
  - PDF files stored in `/app/data/pdfs/{collection_id}/` (configurable)
  - Text extraction from PDFs (PyMuPDF)
  - **RAG Pipeline**: Text chunking, embedding generation, vector storage (ChromaDB)
  - **Vector Search**: ChromaDB Docker service with HTTP client
  - **LLM Integration**: Ollama service for local inference
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
# Start all services (backend, frontend, ChromaDB, Ollama, PostgreSQL)
docker compose up --build -d

# Backend API (FastAPI): http://localhost:8000
# Frontend (React): http://localhost:3000
# ChromaDB HTTP API: http://localhost:8001
# Ollama LLM Service: http://localhost:11434
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
- ChromaDB API: `http://[your-tailscale-ip]:8001`
- Ollama LLM Service: `http://[your-tailscale-ip]:11434`

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
- PostgreSQL DB: `postgres_data` (persistent database storage)  
- ChromaDB Vector DB: `chroma_data` (persistent vector storage via Docker service)
- Ollama Models: `ollama_data` (persistent LLM model storage)

## Initial Corpus
- On backend startup, all PDFs in the configured `initial_corpus_dir` are registered in the DB under the default collection.

---

See `SPRINT_2_REVIEW.md` for a full summary of Sprint 2 deliverables.
