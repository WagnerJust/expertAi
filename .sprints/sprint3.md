# Sprint 3 (Revised for Python 3.11 & ChromaDB): Environment Update, Core Backend RAG Pipeline (Chunking, Embedding, ChromaDB Storage, Externalized LLM Service) 🐍🖼️🧠🐳

**Goal:** Standardize the development environment on Python 3.11. Implement the core Retrieval-Augmented Generation (RAG) pipeline components: text chunking, embedding generation, **ChromaDB vector storage integration**, and integrate with a local Large Language Model (LLM) running as a separate Docker service for Q&A.

**Context Reminder for Copilot:**
* Project: Local PDF RAG Q&A Web App.
* Backend: **Python (target 3.11)**, FastAPI, Venv, SQLAlchemy (SQLite).
* Frontend: React (Vite).
* Vector DB: **ChromaDB**
* Container: Docker, Docker Compose.
* Methodology: Waterfall "sprints," TFD critical.

**Tasks for Coding Assistant (Copilot):**

**0. Python Environment Update to 3.11:**
    * **Update Python Environment:**
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
    * **Update Backend Dockerfile:**
        * Modify `backend/Dockerfile` to use a Python 3.11 base image (e.g., `FROM python:3.11-slim` or `FROM python:3.11-bookworm`).
    * **Verify Existing Functionality:**
        * After updating, run all existing tests from Sprints 1 and 2 (`pytest`) to ensure no regressions are introduced by the Python version change.
        * Manually test starting the backend service locally and via Docker.
    * **TFD:** While this is an environment task, the verification step (running existing tests) is crucial.
    * **Acceptance Criteria:** `requirements.txt` specifies all dependencies. Virtual environment uses Python 3.11. `backend/Dockerfile` uses a Python 3.11 base image. All existing tests pass. Backend service runs correctly with Python 3.11.

**1. Text Processing & Chunking (Backend):**
    * Implement `backend/app/rag_components/chunker.py`:
        * Define a `Chunk` Pydantic schema (e.g., `id: str, text: str, article_title: str, source_pdf_filename: str, page_numbers: list[int], chunk_sequence_id: int, collection_id: str, pdf_db_id: int`). `id` should be a unique identifier for the chunk (e.g., `f"{pdf_filename}_chunk_{chunk_sequence_id}"`).
        * Implement `chunk_text(text_content: str, article_title: str, pdf_filename: str, collection_id: str, pdf_db_id: int, page_info: dict) -> list[Chunk]`.
        * Use a text splitting strategy. Target 500-1000 tokens, configurable overlap.
        * Metadata for each chunk: Article Title, Source PDF filename, Page number(s), Chunk sequence ID, Collection ID/Name, PDF DB ID.
    * Modify `pdf_ingestion_service.py`: After successful text extraction, call the chunking function.
    * **TFD:** Unit tests for chunking logic.
    * **Acceptance Criteria:** Text chunked with accurate metadata. Configurable chunking parameters. Chunks have unique IDs.

**2. Embedding Generation (Backend):**
    * Implement `backend/app/rag_components/embedder.py`:
        * Add `sentence-transformers` to `pyproject.toml` using Poetry with the new Python 3.11 env.
        * `config.py`: `EMBEDDING_MODEL_NAME` (e.g., `all-mpnet-base-v2`).
        * `get_embedding_model()`: Loads model.
        * `generate_embeddings_for_chunks(chunks: list[Chunk], model) -> list[tuple[Chunk, list[float]]]`.
    * Hardware adaptability: Document chosen model's resource needs. Configurable via `config.py`.
    * **TFD:** Unit tests for embedding generation.
    * **Acceptance Criteria:** Embeddings generated using a local, configurable model. Model choice justified.

**3. Vector Database Integration (Backend with ChromaDB):**
    * Implement `backend/app/rag_components/vector_store_interface.py`:
        * Add **ChromaDB** to `pyproject.toml` (`poetry add chromadb`).
        * In `config.py`, define `CHROMA_DB_PATH` (e.g., `./data/vector_store/chroma_db`) and `CHROMA_DEFAULT_COLLECTION_NAME` (can be a generic name if you plan to filter by metadata, or you can use multiple Chroma collections).
        * **ChromaDB Specific Implementation:**
            * `initialize_vector_store()`: Creates a persistent Chroma client. `client = chromadb.PersistentClient(path=CHROMA_DB_PATH)`.
            * `get_or_create_collection(collection_name: str)`: Uses `client.get_or_create_collection(name=collection_name, embedding_function=None)` (as embeddings are pre-computed).
            * `add_chunks_to_vector_store(chroma_collection_name: str, chunks_with_embeddings: list[tuple[Chunk, list[float]]])`:
                * Get the Chroma collection.
                * For each `(chunk, embedding)`:
                    * `documents` list will contain `chunk.text`.
                    * `metadatas` list will contain dictionaries derived from `chunk` object (e.g., `{"article_title": chunk.article_title, "source_pdf": chunk.source_pdf_filename, "page_numbers": str(chunk.page_numbers), "collection_id": chunk.collection_id, "pdf_db_id": chunk.pdf_db_id}`). Ensure metadata values are Chroma-compatible types (str, int, float, bool).
                    * `ids` list will contain `chunk.id`.
                * Add to collection: `collection.add(documents=docs, embeddings=embs, metadatas=metas, ids=ids_list)`.
            * `search_relevant_chunks(chroma_collection_name: str, query_embedding: list[float], top_k: int = 5, filter_collection_id: str | None = None) -> list[Chunk]`:
                * Get the Chroma collection.
                * Construct a `where` filter if `filter_collection_id` is provided: `where_filter = {"collection_id": filter_collection_id}`.
                * Perform a vector search: `results = collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where_filter if filter_collection_id else None)`.
                * Convert search results (especially `results['metadatas'][0]` and `results['documents'][0]`) back into `Chunk` Pydantic objects or structured dicts.
            * `delete_collection_data_from_vector_store(chroma_collection_name: str, filter_collection_id: str)`:
                * Get the Chroma collection.
                * Delete items matching the `collection_id` metadata: `collection.delete(where={"collection_id": filter_collection_id})`.
            * `delete_pdf_chunks_from_vector_store(chroma_collection_name: str, pdf_db_id: int)`:
                * Get the Chroma collection.
                * Delete items matching the `pdf_db_id` metadata: `collection.delete(where={"pdf_db_id": pdf_db_id})`.
    * Ensure ChromaDB data is persisted using Docker volumes (map `CHROMA_DB_PATH` parent dir).
    * Update `pdf_ingestion_service.py` to call `add_chunks_to_vector_store`.
    * **TFD:**
        * Unit/integration tests in `backend/tests/unit/rag_components/test_vector_store_interface.py` for ChromaDB operations: collection creation/getting, add, search (with metadata filtering for `collection_id`), delete by `collection_id` metadata, delete by `pdf_db_id` metadata.
    * **Acceptance Criteria:** Text chunks, embeddings, and metadata stored in ChromaDB. Data queryable and filterable by metadata (`collection_id`). Persistence via Docker volumes. ChromaDB is used as specified.

**4. Local LLM Integration via Dedicated Docker Service (Backend & Docker Compose):**
    * **Update `docker-compose.yml`:** Add new service `llm-service` for `ghcr.io/abetlen/llama-cpp-python:latest` (ports, volumes for models, `MODEL` env var) as previously detailed.
    * **Implement `backend/app/rag_components/llm_handler.py`:**
        * Add `httpx` to `pyproject.toml`.
        * Client for `llm-service` (HTTP requests to `/v1/completions` or similar).
        * `config.py`: `LLM_SERVICE_URL`, `LLM_COMPLETION_ENDPOINT`.
        * `generate_answer_from_context(prompt_text: str, max_tokens: int = 500) -> str | None`.
    * **Hardware Adaptability (LLM Service):** Document GGUF model configuration for the Docker service.
    * **TFD:** Unit tests for `llm_handler.py` mocking `httpx` calls.
    * **Acceptance Criteria:** `llm-service` in `docker-compose.yml` starts. `llm_handler.py` communicates with it. LLM Docker service configuration documented.

**5. RAG Service - Core Q&A Logic (Backend):**
    * Implement `backend/app/services/rag_service.py`:
        * `answer_question_from_collection(db: Session, collection_id_sqlite: int, question_text: str) -> dict`:
            * Retrieve collection name and string `collection_id` (used for Chroma metadata filtering) from SQLite DB using `collection_id_sqlite`.
            * Generate question embedding.
            * Retrieve relevant `Chunk` objects from `vector_store_interface.py` using ChromaDB, filtering by the string `collection_id`.
            * Construct prompt.
            * Call `llm_handler.generate_answer_from_context(prompt_text)`.
            * Process LLM response. Implement "I don't know..." logic. Store history in SQLite.
    * **TFD:** Unit tests for prompt formatting. Integration tests for `rag_service.py`.
    * **Acceptance Criteria:** `rag_service` orchestrates RAG pipeline with ChromaDB and externalized LLM. Returns context-based answers or "I don't know." History stored.

**6. Manual Re-indexing Logic (Backend - Design & Stub for API trigger):**
    * In `backend/app/services/admin_service.py`:
        * Design full logic for `reindex_collection(db: Session, collection_id_sqlite: int) -> bool`:
            * Get string `collection_id` from `collection_id_sqlite`.
            * Clear ChromaDB data for this `collection_id` using `vector_store_interface.delete_collection_data_from_vector_store`.
            * Re-fetch PDFs, re-extract, re-chunk, re-embed, re-add to ChromaDB.
        * Create stub function and placeholder for API endpoint.
    * **TFD:** Basic unit test for function signature.
    * **Acceptance Criteria:** Re-indexing logic designed for ChromaDB. Placeholder function exists.

**Deliverable for CEO (Sprint 3 - Python 3.11 & ChromaDB):** 🐍💡🐳

* Confirmation that the backend development environment and Docker image now use Python 3.11 and all previous tests pass.
* A demonstration (API calls or script):
    * Show `docker-compose.yml` with `llm-service` and backend configured for ChromaDB. Start services.
    * Ingest sample PDFs into a collection (triggering full RAG pipeline including ChromaDB storage).
    * Ask a question; show backend logs (API call to `llm-service`, ChromaDB interaction if logged) and final answer with citations.
    * Ask an unanswerable question; show "I don't know."
* Show SQLite `QueryHistory`. Show ChromaDB data location in Docker volume.
* Brief document/slide explaining:
    * Python 3.11 update.
    * Embedding model.
    * **ChromaDB setup and usage (including metadata filtering).**
    * LLM Docker service setup.
* Updated test report summary.