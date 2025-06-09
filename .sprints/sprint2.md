# Sprint 2: Core Backend Logic - PDF Ingestion & Initial Collection Management 🗂️

**Goal:** Implement backend functionality for creating and managing collections, uploading/linking PDFs, performing basic text extraction, and storing PDF files and their metadata.

**Tasks for Coding Assistant (Copilot):**

1.  **Collection Management Service & API (Backend):**
    * Implement `backend/app/services/collection_service.py`:
        * `create_collection(db: Session, collection: schemas.CollectionCreate) -> db_models.Collection`
        * `get_collection(db: Session, collection_id: int) -> db_models.Collection | None`
        * `get_collections(db: Session, skip: int = 0, limit: int = 100) -> list[db_models.Collection]`
        * `update_collection(db: Session, collection_id: int, collection_update: schemas.CollectionUpdate) -> db_models.Collection | None` (Create `schemas.CollectionUpdate` Pydantic model for partial updates, e.g., only name).
        * `delete_collection(db: Session, collection_id: int) -> db_models.Collection | None` (Consider what happens to associated PDFs: mark as orphaned, delete files, or prevent deletion if PDFs exist).
    * Implement API endpoints in `backend/app/apis/v1/router_collections.py` using the service methods. Ensure appropriate HTTP status codes and error handling (e.g., 404 for not found).
    * **TFD:**
        * Write unit tests in `backend/tests/unit/services/test_collection_service.py` for each function in `collection_service.py`, mocking database interactions.
        * Write integration tests in `backend/tests/integration/api/v1/test_router_collections.py` for the API endpoints, using a test database.
    * **Acceptance Criteria:** Full CRUD operations for collections are functional via API; data is persisted in PostgreSQL; all tests pass with good coverage.

2.  **PDF Ingestion Service & Storage (Backend):**
    * Implement `backend/app/services/pdf_ingestion_service.py`:
        * `store_uploaded_pdf(collection_id: int, pdf_file: UploadFile) -> Path`: Saves to a structured path like `data/pdfs/{collection_id}/{pdf_file.filename}`. The base `data/pdfs` path should be configurable via `config.py`. Ensure the directory is created if it doesn't exist.
        * `download_pdf_from_url(collection_id: int, url: str, filename: str) -> Path | None`: Downloads PDF from URL, saves similarly. Handle potential download errors.
        * `add_pdf_record_to_db(db: Session, title: str, filename: str, file_path: str, collection_id: int, status: str = "pending") -> db_models.PDFDocument`: Creates a `PDFDocument` record in the database.
    * Update `backend/app/core/config.py` to include `PDF_STORAGE_PATH`.
    * Ensure `docker compose.yml` correctly mounts the `pdf_storage` named volume to the path specified in `config.py`. Use named volumes for both PDF storage and PostgreSQL database to eliminate file permission issues.
    * **TFD:**
        * Unit tests in `backend/tests/unit/services/test_pdf_ingestion_service.py` for file storing logic (mocking `UploadFile` and file system operations), URL downloading (mocking `httpx` requests), and DB record creation.
    * **Acceptance Criteria:** PDF files are correctly stored in the designated Docker volume; metadata (title derived from filename, filename, collection association, initial status) is stored in SQLite.

3.  **PDF Processing - Text Extraction (Backend):**
    * Integrate a PDF parsing library (e.g., `PyMuPDF/fitz` or `pdfminer.six`) into `pdf_ingestion_service.py`. Add the chosen library to `backend/requirements.txt`.
    * Implement `extract_text_from_pdf(pdf_path: Path) -> tuple[str, int] | None`: Extracts all readable textual content and total page count. Return `None` or raise specific exception on failure.
    * Implement robust error handling for diverse PDF structures, layouts, encodings. Log errors and update PDF status in DB to "extraction_failed".
    * Consider a simple function to make the filename a "title" (e.g., "My_Document_Name.pdf" -> "My Document Name").
    * **TFD:**
        * Unit tests in `test_pdf_ingestion_service.py` for text extraction using various sample PDFs (simple text, multi-column, scanned image placeholder if OCR is future, password-protected if supported/skipped, corrupted). Test that page count is extracted.
    * **Acceptance Criteria:** Text is successfully extracted from common PDF types; page count is recorded; errors in PDF parsing are handled gracefully, logged, and PDF status updated.

4.  **PDF Management API Endpoints (Backend):**
    * Implement API endpoints in `backend/app/apis/v1/router_pdfs.py`:
        * `POST /collections/{collection_id}/pdfs/upload`: Handles file upload. Calls `store_uploaded_pdf`. The extracted text itself won't be stored directly in the PDFDocument table yet, but the file path will. It will also call `add_pdf_record_to_db` with initial status.
        * `POST /collections/{collection_id}/pdfs/url`: Handles PDF download from URL. Calls `download_pdf_from_url` and `add_pdf_record_to_db`.
        * (Optional for now, but good: `GET /collections/{collection_id}/pdfs` to list PDFs in a collection, `DELETE /pdfs/{pdf_id}` to remove a PDF).
    * These endpoints will use `collection_service` (to verify collection exists) and `pdf_ingestion_service`.
    * **TFD:**
        * Integration tests in `backend/tests/integration/api/v1/test_router_pdfs.py` for PDF upload and URL addition endpoints.
    * **Acceptance Criteria:** Backend API allows uploading PDF files and adding PDFs via URLs to a specified collection; PDF records created in DB.

5.  **Initial Corpus Ingestion (Backend):**
    * Implement a utility script or a one-off FastAPI startup event (using `app.add_event_handler("startup", ...)`).
    * This script/event should:
        * Check if a "default" collection exists by a predefined name (from `config.py`). If not, create it.
        * Scan the configurable initial corpus directory (from `config.py`, e.g., `/Users/justin/LLMS/Contexts/PromptEngineering/`).
        * For each PDF found, add it to the "default" collection using the existing `pdf_ingestion_service` functions (as if it were uploaded). This means creating a DB record. Text extraction not triggered by this initial scan unless explicitly designed so (can be part of re-indexing later).
    * Make the initial corpus directory path mountable in `docker compose.yml` for flexibility.
    * **TFD:** Test this initial ingestion. This might be a manual test or a test that mocks the directory structure and `pdf_ingestion_service` calls.
    * **Acceptance Criteria:** On first run or via a command, PDFs from the specified initial corpus directory are registered into a default collection in the database.

**Deliverable for CEO (Sprint 2):** 📊

* Live API demonstration (using Postman, Insomnia, or `curl`):
    * Creating a new collection.
    * Listing collections.
    * Renaming a collection.
    **Deliverable for CEO (Sprint 2):** 📊

* Live API demonstration (using Postman, Insomnia, or `curl`):
    * Creating a new collection.
    * Listing collections.
    * Renaming a collection.
    * Uploading a PDF file directly to the new collection.
    * Adding another PDF to the same collection via a public URL.
    * Deleting a collection.
* Show the CEO:
    * The structure of the stored PDF files within the Docker volume (e.g., using `docker exec -it <backend_container_id> ls /app/data/pdfs/<collection_id>`).
    * The PostgreSQL database entries for collections and PDF documents (e.g., using `docker exec -it <backend_container_id> psql -U llm_user -d llm_db -c "SELECT * FROM collections;"`).
* Updated `openapi.json` file (auto-generated by FastAPI, accessible via `/openapi.json`).
* A brief test report summary (e.g., output from `pytest --cov`).