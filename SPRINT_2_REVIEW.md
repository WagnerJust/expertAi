# SPRINT 2 REVIEW

## Backend Core Logic: Collection & PDF Ingestion

### System Enhancements
- **Python 3.13** (Dockerized)
- **FastAPI**: Extended with full CRUD for collections and PDF management
- **PDF Storage**: Files saved to `/app/data/pdfs/{collection_id}/` (configurable)
- **Text Extraction**: Integrated PyMuPDF for PDF text and page count
- **Initial Corpus Ingestion**: On startup, scans and registers PDFs from a configurable directory into a default collection

### API Endpoints Implemented
- **Collections:**
  - `POST /api/v1/collections` (create)
  - `GET /api/v1/collections` (list)
  - `GET /api/v1/collections/{collection_id}` (retrieve)
  - `PUT /api/v1/collections/{collection_id}` (update/rename)
  - `DELETE /api/v1/collections/{collection_id}` (delete, prevents if PDFs exist)
- **PDFs:**
  - `POST /api/v1/collections/{collection_id}/pdfs/upload` (upload file)
  - `POST /api/v1/collections/{collection_id}/pdfs/url` (add by URL)
  - `GET /api/v1/collections/{collection_id}/pdfs` (list PDFs in collection)
  - `DELETE /api/v1/pdfs/{pdf_id}` (remove PDF)

### Database Schema (Key Tables)
- **Collection:** id, name, created_at
- **PDFDocument:** id, filename, title, status, collection_id

### Key Features Delivered
- **Collection CRUD**: Service and API, with partial update (rename)
- **PDF Ingestion**: Upload, download by URL, and DB record creation
- **Text Extraction**: Extracts all text and page count from PDFs; robust error handling
- **Initial Corpus**: On startup, registers all PDFs from a specified directory into the DB
- **Docker Compose**: Volume mounts for PDF storage and SQLite DB

### Testing & Quality
- **Unit Tests**: For all service logic (collections, PDF ingestion, extraction)
- **Integration Tests**: For all API endpoints (collections, PDFs)
- **Test Coverage**: All new logic and endpoints covered; all tests pass

### Demo Checklist
- [x] Create/list/rename/delete collections via API
- [x] Upload PDF and add by URL to a collection
- [x] List and delete PDFs
- [x] Initial corpus PDFs registered on startup
- [x] All tests pass (`pytest --cov`)
- [x] OpenAPI spec available at `/openapi.json`
- [x] PDF files and DB visible in Docker volume

---

**See repo for code, Dockerfiles, and test results.**
