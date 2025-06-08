# Sprint 1: System Design & Foundation 🏗️

**Goal:** Establish the project's backbone: directory structures, essential configurations, API design, database schema, and initial setup of development and containerization tools.

**Tasks for Coding Assistant (Copilot):**

 CRITICAL *** project_root = Current Workspace Directory ***
 Ensure you properly have the backend and frontend directories on the same level. Last time the frontend directory was accidently put inside the backend directory
 
1.  **Project Initialization:**
    * Create `project_root/`.
    * Initialize Git: `git init` in `project_root/`.
    * Create `.gitignore` (for Python, Node.js, common OS files).
    * Create `README.md` with project title and objective.
    * **Acceptance Criteria:** Git repo initialized; `.gitignore` and `README.md` exist.

2.  **Backend Setup (Python/FastAPI & venv):**
    * Create `backend/`.
    * Initialize a Python 3.11 virtual environment:
      ```bash
      python3.11 -m venv venv
      source venv/bin/activate
      ```
    * Create `backend/requirements.txt` and add dependencies: `fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `python-multipart`, `alembic`, and `pytest` for testing.
    * Install dependencies:
      ```bash
      pip install -r requirements.txt
      ```
    * Create `backend/app/` and subdirectories: `core/`, `apis/v1/`, `services/`, `models/`, `db/`, `rag_components/`, `utils/`. Add `__init__.py` to all.
    * `backend/app/main.py`: Basic FastAPI app, root health check endpoint (`/`).
    * `backend/app/core/config.py`: Settings class (e.g., `Settings(BaseSettings)` from Pydantic-settings) for initial PDF dir, DB URL (`sqlite:///./local_database.sqlite`).
    * `backend/app/models/schemas.py`: Pydantic models for:
        * `CollectionBase`, `CollectionCreate`, `Collection` (ID, name, created\_at)
        * `PDFDocumentBase`, `PDFDocumentCreate`, `PDFDocument` (ID, filename, title, collection\_id, status [e.g., "pending", "processed", "error"])
        * `QueryBase`, `QueryCreate`, `Query` (ID, text, collection\_id, timestamp)
        * `AnswerBase`, `AnswerCreate`, `Answer` (ID, query\_id, text, context\_used, sources [e.g., list of strings like "Title, pg. X"])
        * `FeedbackBase`, `FeedbackCreate`, `Feedback` (ID, answer\_id, rating [e.g., "up", "down"], comment [optional])
        * Generic API response models (e.g., `MsgDetail`).
    * `backend/app/models/db_models.py`: SQLAlchemy ORM models mirroring schemas (Collection, PDFDocument, QueryHistory, AnswerFeedback). Define relationships. `QueryHistory` could store question, answer, context, sources, and link to `AnswerFeedback`.
    * `backend/app/db/session.py` (or similar): SQLAlchemy engine, `SessionLocal`, `Base` for ORM models. Function to create initial DB tables (e.g., `Base.metadata.create_all(bind=engine)`). (Alembic for migrations can be set up here too, add `alembic` to Poetry).
    * **Acceptance Criteria:** Backend structure created; FastAPI app runs with `/` endpoint; Pydantic/SQLAlchemy models defined; DB session setup; initial DB schema can be created.

3.  **Frontend Setup (React):**
    * Create `frontend/`.
    * Initialize React app: `cd frontend; npx create-vite@latest . --template react` (or CRA: `npx create-react-app .`).
    * Create `frontend/src/` subdirectories: `components/common/`, `components/collections/`, `components/pdfs/`, `components/qa/`, `pages/`, `services/`, `contexts/`, `hooks/`, `assets/`, `styles/`.
    * Basic `App.jsx`, `main.jsx` (for Vite) or `App.js`, `index.js` (for CRA).
    * **Acceptance Criteria:** React app created and starts; directory structure in place.

4.  **API Contract Definition (OpenAPI Design):**
    * Based on core requirements, design API endpoints. This will guide FastAPI router implementation.
        * Collections: `POST /api/v1/collections`, `GET /api/v1/collections`, `GET /api/v1/collections/{collection_id}`, `PUT /api/v1/collections/{collection_id}`, `DELETE /api/v1/collections/{collection_id}`
        * PDFs: `POST /api/v1/collections/{collection_id}/pdfs/upload`, `POST /api/v1/collections/{collection_id}/pdfs/url`
        * Q&A: `POST /api/v1/collections/{collection_id}/qa`, `GET /api/v1/collections/{collection_id}/history`
        * Feedback: `POST /api/v1/qa/answers/{answer_id}/feedback`
        * Admin: `POST /api/v1/admin/collections/{collection_id}/reindex`
    * Focus on request/response bodies using Pydantic models defined earlier. FastAPI will auto-generate the `openapi.json` at `/openapi.json` (or `/api/v1/openapi.json` if routers are prefixed).
    * **Acceptance Criteria:** Clear plan for API endpoints and their Pydantic models; understanding of how FastAPI will generate the spec.

5.  **Docker Setup (Initial):**
    * `backend/Dockerfile`: For Python FastAPI app (e.g., `python:3.11-slim`, copy app, install dependencies via `pip install -r requirements.txt`).
    * `frontend/Dockerfile`: For React app (multi-stage: Node build, Nginx serve).
    * `{CURRENT_WORKSPACE_DIR}/docker compose.yml`: Services for `backend`, `frontend`. Define named volumes for `pdf_storage`, `db_volume` (for SQLite database), `vector_db_volume`, `ollama_data`. Use named volumes instead of bind mounts to eliminate permission issues with SQLite database files.
    * **Acceptance Criteria:** Dockerfiles exist; `docker compose.yml` defines services and named volumes (no permission issues).

6.  **Test Setup (TFD):**
    * Backend: Add `pytest`, `pytest-cov`, `httpx`, `pytest-asyncio` to `backend/requirements.txt` for development/testing.
    * Create `backend/tests/` with `conftest.py`, `unit/`, and `integration/` subdirectories.
    * Write a simple unit test for the root health check endpoint in `backend/app/main.py` (e.g., checking status code and response).
    * Frontend: Ensure testing libraries (e.g., Jest, Vitest, React Testing Library) are set up (default with Vite/CRA). Write a basic rendering test for the `App.jsx` component.
    * **Acceptance Criteria:** Test directories and configs in place; basic tests pass for backend health check and frontend App component.

**Deliverable for CEO (Sprint 1):** 📝

* Access to the Git repository with the initial commit for Sprint 1.
* A document (`SPRINT_1_REVIEW.md`) briefly outlining:
    * Confirmed System Architecture and Technology Stack (Python/FastAPI, React, SQLite, Docker, Poetry, chosen PDF/Embedding/LLM libraries - even if not yet implemented).
    * Initial API Contract Design (summary of endpoints and Pydantic models, link to where `openapi.json` will be available).
    * Basic Database Schema (description of tables derived from `db_models.py`).
* Demonstration (live or screenshots/screencast):
    * Backend service starts via `uvicorn backend.app.main:app --reload` (showing health check endpoint `/` returning 200 OK).
    * Frontend placeholder page loads via `npm run dev` (or `yarn dev`).
    * `docker compose build` runs successfully for initial Dockerfiles.
    * Basic tests pass for backend and frontend.