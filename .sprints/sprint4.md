# Sprint 4: Backend API Finalization & Initial Frontend Scaffolding 🌉

**Goal:** Expose all backend RAG functionalities via robust APIs, finalize backend Docker configurations, generate a complete OpenAPI specification, and set up the foundational elements of the React frontend including API communication layers and basic routing.

**Tasks for Coding Assistant (Copilot):**

1.  **Q&A API Endpoint (Backend):**
    * Implement the API endpoint in `backend/app/apis/v1/router_qa.py`:
        * `POST /collections/{collection_id}/qa`:
            * Takes a Pydantic schema `QuestionRequest(question: str)`.
            * Uses `rag_service.answer_question_from_collection` to get the answer, sources, and context.
            * Returns a Pydantic schema `AnswerResponse(query_id: int, answer: str, sources: list[str], retrieved_context: list[str])`.
    * Ensure proper dependency injection of `db: Session = Depends(get_db)`.
    * **TFD:**
        * Write integration tests in `backend/tests/integration/api/v1/test_router_qa.py` for this endpoint. Test successful Q&A, scenarios where the answer is not found ("I don't know..."), and invalid `collection_id`.
    * **Acceptance Criteria:** The Q&A API endpoint is fully functional, robustly tested, and returns structured responses including the answer, sources, and query ID.

2.  **Query History API Endpoint (Backend):**
    * Implement the API endpoint in `backend/app/apis/v1/router_qa.py`:
        * `GET /collections/{collection_id}/history`:
            * Retrieves persistent query history (e.g., questions, answers, sources, timestamps) for the specified `collection_id` from the SQLite database (`QueryHistory` table).
            * Returns a list of `QueryHistoryResponse` Pydantic schemas.
    * **TFD:**
        * Write integration tests for the query history API endpoint, ensuring correct data retrieval and filtering by collection.
    * **Acceptance Criteria:** The query history API endpoint is implemented, tested, and correctly retrieves history for a given collection.

3.  **Feedback API Endpoint (Backend):**
    * Implement `backend/app/services/feedback_service.py`:
        * `store_answer_feedback(db: Session, answer_id: int, feedback_data: schemas.FeedbackCreate) -> db_models.AnswerFeedback`. (Ensure `Answer` schema/model has an `id` and `QueryHistory` stores the `answer_id`).
    * Implement the API endpoint in `backend/app/apis/v1/router_qa.py`:
        * `POST /qa/answers/{answer_id}/feedback`: Takes `schemas.FeedbackCreate` and stores it using `feedback_service`.
    * **TFD:**
        * Unit tests for `feedback_service.py`.
        * Integration tests for the feedback API endpoint.
    * **Acceptance Criteria:** Backend API for submitting feedback on answers is implemented, tested, and stores feedback associated with a specific answer.

4.  **Admin API Endpoint - Manual Re-indexing (Backend - Full Implementation):**
    * Fully implement the re-indexing logic in `backend/app/services/admin_service.py` (or `collection_service.py`) as designed in Sprint 3.
    * Implement the API endpoint in `backend/app/apis/v1/router_admin.py`:
        * `POST /admin/collections/{collection_id}/reindex`: Triggers the re-indexing process for the specified collection. This should be an asynchronous task or clearly communicate it's a long-running process. For simplicity in a first pass, it can be synchronous, but note this as a potential improvement.
    * **TFD:**
        * Write integration tests for the re-indexing API endpoint. This test might be longer running and require careful setup (e.g., a small collection with a few PDFs) and verification of the vector store state before and after.
    * **Acceptance Criteria:** The manual re-indexing API endpoint is fully implemented and tested, successfully clearing and reprocessing all documents in a specified collection.

5.  **Finalize Backend Dockerfile & docker compose.yml:**
    * Ensure all necessary models (embedding, LLM if packaged) are either baked into the Docker image (if small enough and licensed appropriately) or correctly downloaded/mounted during container startup. For LLMs, it's often better to mount them from the host due to size.
    * Configure environment variables in `docker compose.yml` for all paths (PDFs, SQLite DB, Vector DB, LLM models, embedding models) and ensure they are read by `backend/app/core/config.py`.
    * Review resource allocations (memory, CPU) for the backend service in `docker compose.yml`, especially considering LLM and embedding model requirements.
    * **Backend Python Environment Setup:**
        * Ensure Python 3.11 is installed and accessible (e.g., via `pyenv global 3.11.x` or by having it in your PATH).
        * Create a new virtual environment for Python 3.11:
          ```bash
          python3.11 -m venv venv
          source venv/bin/activate
          ```
        * Update or create `backend/requirements.txt` to specify all dependencies compatible with Python 3.11.
        * Install dependencies:
          ```bash
          pip install -r requirements.txt
          ```
    * **Acceptance Criteria:** Backend Docker configuration is finalized, uses environment variables for paths, and manages model files effectively. `docker compose up` successfully starts the fully configured backend.

6.  **Generate/Update & Document OpenAPI Specification:**
    * Ensure FastAPI (`/openapi.json`) auto-generates an accurate and complete specification for all implemented V1 API endpoints.
    * Review the Pydantic models and FastAPI route definitions to ensure they produce a clear and usable OpenAPI spec. Add descriptions and examples to Pydantic models and route docstrings where helpful.
    * Store a static copy of the `openapi.json` (e.g., in `docs/api/openapi.json`) and reference it in the `README.md`.
    * **Acceptance Criteria:** A comprehensive and accurate `openapi.json` is available and documented, reflecting all backend APIs.

7.  **Frontend Basic Structure & Routing (React):**
    * Set up basic page components in `frontend/src/pages/`: `HomePage.jsx`, `ManageCollectionsPage.jsx`, `CollectionChatPage.jsx`.
    * Implement basic routing using `react-router-dom` in `frontend/src/App.jsx`:
        * `/`: `HomePage`
        * `/collections`: `ManageCollectionsPage`
        * `/collections/:collectionId`: `CollectionChatPage`
    * **Acceptance Criteria:** Frontend basic structure and routing are set up, allowing navigation between the home page, collections management, and chat page for a specific collection.