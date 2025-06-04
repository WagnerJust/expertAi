# Sprint 3: Core Backend Logic - RAG Pipeline (Chunking, Embedding, Vector Storage, Externalized LLM Service) 🧠🐳

**Goal:** Implement the core Retrieval-Augmented Generation (RAG) pipeline components: text chunking, embedding generation, vector storage integration. Integrate with a **local Large Language Model (LLM) running as a separate Docker service** for Q&A (backend processing only at this stage).

**Context Reminder for Copilot:**
* Project: Local PDF RAG Q&A Web App.
* Backend: Python, FastAPI, Poetry, SQLAlchemy (SQLite).
* Frontend: React (Vite).
* Container: Docker, Docker Compose.
* Methodology: Waterfall "sprints," TFD critical.

**Tasks for Coding Assistant (Copilot):**

1.  **Text Processing & Chunking (Backend):**
    * Implement `backend/app/rag_components/chunker.py`:
        * Define a `Chunk` Pydantic schema (e.g., `text: str, article_title: str, source_pdf_filename: str, page_numbers: list[int], chunk_sequence_id: int, collection_id: str`).
        * Implement `chunk_text(text_content: str, article_title: str, pdf_filename: str, collection_id: str, page_info: dict) -> list[Chunk]`.
        * Use a text splitting strategy (e.g., `langchain.text_splitter.RecursiveCharacterTextSplitter`). Target 500-1000 tokens, configurable overlap.
        * Metadata for each chunk: Article Title, Source PDF filename, Page number(s), Chunk sequence ID, Collection ID/Name.
    * Modify `pdf_ingestion_service.py`: After successful text extraction, call the chunking function.
    * **TFD:** Unit tests for chunking logic.
    * **Acceptance Criteria:** Text chunked with accurate metadata. Configurable chunking parameters.

2.  **Embedding Generation (Backend):**
    * Implement `backend/app/rag_components/embedder.py`:
        * Add `sentence-transformers` to `pyproject.toml`.
        * `config.py`: `EMBEDDING_MODEL_NAME` (e.g., `all-mpnet-base-v2`).
        * `get_embedding_model()`: Loads model.
        * `generate_embeddings(chunks: list[Chunk], model) -> list[tuple[Chunk, list[float]]]`.
    * Hardware adaptability: Document chosen model's resource needs. Configurable via `config.py`.
    * **TFD:** Unit tests for embedding generation.
    * **Acceptance Criteria:** Embeddings generated using a local, configurable model. Model choice justified.

3.  **Vector Database Integration (Backend):**
    * Implement `backend/app/rag_components/vector_store_interface.py`:
        * Choose and integrate LanceDB (`poetry add chromadb`) or LanceDB. Document rationale.
        * `config.py`: `VECTOR_DB_PATH`.
        * Functions: `initialize_vector_store()`, `add_chunks_to_vector_store(...)`, `search_relevant_chunks(...)`, `delete_collection_from_vector_store(...)`.
        * Ensure vector store data persisted via Docker volume.
    * Update `pdf_ingestion_service.py` to call `add_chunks_to_vector_store`.
    * **TFD:** Unit/integration tests for vector store operations (add, search with collection filter, delete).
    * **Acceptance Criteria:** Chunks/embeddings stored, searchable by query & collection_id. Persistence via Docker volumes. Rationale for DB choice documented.

4.  **Local LLM Integration via Dedicated Docker Service (Backend & Docker Compose):**
    * **Update `docker-compose.yml`:**
        * Add a new service named `llm-service` (or similar) for the LLM server:
            ```yaml
            services:
              # ... your existing backend and frontend services
              llm-service:
                image: ghcr.io/abetlen/llama-cpp-python:latest
                # Ensure host port doesn't conflict with your backend (FastAPI often uses 8000)
                # If backend is on 8000, map LLM to a different host port e.g., 8001
                ports:
                  - "8001:8000" # Host:Container
                volumes:
                  # Create a './models' directory at your project root and place GGUF files there
                  - ./models:/models 
                environment:
                  # Make sure 'your-chosen-llama-model.gguf' exists in the ./models directory
                  - MODEL=/models/your-chosen-llama-model.gguf 
                  # Add other necessary llama-cpp-python server environment variables if needed
                  # e.g., N_CTX, N_GPU_LAYERS (if applicable and image supports it)
                # Add healthcheck if desired
                # Add resource limits if needed
            ```
        * Ensure your `backend` service and `llm-service` are on the same Docker network (default with docker-compose).
    * **Implement `backend/app/rag_components/llm_handler.py`:**
        * Add `httpx` to `pyproject.toml` (`poetry add httpx`).
        * This module will now be an HTTP client for the `llm-service`.
        * In `config.py`, define `LLM_SERVICE_URL` (e.g., `http://llm-service:8000` - using the Docker service name and its *internal* container port).
            * Also define `LLM_COMPLETION_ENDPOINT` (e.g., `/v1/completions` which is common for OpenAI-compatible servers like the `llama-cpp-python` server. Verify this endpoint from the `ghcr.io/abetlen/llama-cpp-python` image documentation if needed).
        * `generate_answer_from_context(prompt_text: str, max_tokens: int = 500) -> str | None`:
            * Constructs the API request payload for the LLM service (e.g., JSON with `prompt`, `max_tokens`, `temperature`, `stop` sequences, etc., according to the LLM service's API spec).
            * Uses `httpx.AsyncClient` (if in FastAPI async context) or `httpx.Client` to send a POST request to `LLM_SERVICE_URL + LLM_COMPLETION_ENDPOINT`.
            * Parses the JSON response to extract the generated text.
            * Handles potential HTTP errors or errors from the LLM service.
    * **Hardware Adaptability (LLM Service):**
        * Documentation should now cover:
            * How to specify the GGUF model file for the `llm-service` via the `MODEL` environment variable in `docker-compose.yml`.
            * How to manage and provide model files via the Docker volume mount.
            * Guidance on any `llama-cpp-python` server-specific environment variables for tuning (e.g., context size `N_CTX`, GPU layers `N_GPU_LAYERS` if applicable and supported by the image on your hardware).
    * **TFD:**
        * Unit tests in `backend/tests/unit/rag_components/test_llm_handler.py` will mock `httpx` client calls and responses from the LLM service. Test various response scenarios (success, error).
    * **Acceptance Criteria:** `llm-service` is defined in `docker-compose.yml` and starts correctly with a specified GGUF model. `llm_handler.py` can successfully send prompts to this service and receive generated text via HTTP. Configuration and hardware considerations for the Dockerized LLM are documented.

5.  **RAG Service - Core Q&A Logic (Backend):**
    * Implement `backend/app/services/rag_service.py`:
        * `answer_question_from_collection(db: Session, collection_id: int, question_text: str) -> dict`:
            * Retrieve collection name.
            * Generate question embedding (`embedder.py`).
            * Retrieve relevant `Chunk` objects (`vector_store_interface.py`).
            * Construct the prompt for the LLM (using the refined template).
            * Call `llm_handler.generate_answer_from_context(prompt_text)` to get the answer from the external LLM service.
            * Process LLM response: extract answer, citations.
            * Implement "I don't know..." logic.
            * Store question, answer, context, sources in SQLite.
    * **TFD:** Unit tests for prompt formatting. Integration tests for `rag_service.py` (mocking `llm_handler` or other components as needed for deterministic tests).
    * **Acceptance Criteria:** `rag_service` orchestrates the RAG pipeline, now calling the externalized LLM service via `llm_handler`. Returns answers based on context or "I don't know." History stored.

6.  **Manual Re-indexing Logic (Backend - Design & Stub for API trigger):**
    * In `backend/app/services/admin_service.py` (or `collection_service.py`):
        * Design full logic for `reindex_collection(db: Session, collection_id: int) -> bool`: (Logic remains the same: clear vector store for collection, re-fetch PDFs, re-extract, re-chunk, re-embed, re-add to vector store).
        * Create stub function and placeholder for API endpoint (full implementation in Sprint 4).
    * **TFD:** Basic unit test for function signature.
    * **Acceptance Criteria:** Re-indexing logic designed. Placeholder function exists.

**Deliverable for CEO (Sprint 3 - Revised):** 💡🐳

* A demonstration (can be via API calls using Postman/Insomnia or a simple Python script that uses the backend services directly):
    * Show the `docker-compose.yml` with the new `llm-service`. Start all services (`docker-compose up`).
    * Ingest sample PDFs into a collection (triggering text extraction, chunking, embedding, vector store population).
    * Ask a specific question answerable from the ingested PDFs. Show the backend logs indicating a call to the `llm-service` and the final generated answer with citations.
    * Ask an unanswerable question; show the "I don't know" response.
* Show SQLite entries for `QueryHistory`.
* A brief document or presentation slide explaining:
    * The chosen embedding model and vector database (as before).
    * **The new LLM setup:** How the `ghcr.io/abetlen/llama-cpp-python` Docker service is configured, how models are provided to it, and how the backend communicates with it. Basic hardware considerations for running this LLM service.
* An updated test report summary (`pytest --cov`).