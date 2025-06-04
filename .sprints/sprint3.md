# Sprint 3: Core Backend Logic - RAG Pipeline (Chunking, Embedding, LanceDB Vector Storage, Externalized LLM Service) 🧠🐳

**Goal:** Implement the core Retrieval-Augmented Generation (RAG) pipeline components: text chunking, embedding generation, **LanceDB vector storage integration**, and integrate with a local Large Language Model (LLM) running as a separate Docker service for Q&A.

**Context Reminder for Copilot:**
* Project: Local PDF RAG Q&A Web App.
* Backend: Python, FastAPI, Poetry, SQLAlchemy (SQLite).
* Frontend: React (Vite).
* Vector DB: **LanceDB**
* Container: Docker, Docker Compose.
* Methodology: Waterfall "sprints," TFD critical.

**Tasks for Coding Assistant (Copilot):**

1.  **Text Processing & Chunking (Backend):**
    * Implement `backend/app/rag_components/chunker.py`:
        * Define a `Chunk` Pydantic schema (e.g., `text: str, article_title: str, source_pdf_filename: str, page_numbers: list[int], chunk_sequence_id: int, collection_id: str, pdf_db_id: int`). Include `pdf_db_id` to link back to the PDF in your SQLite DB.
        * Implement `chunk_text(text_content: str, article_title: str, pdf_filename: str, collection_id: str, pdf_db_id: int, page_info: dict) -> list[Chunk]`.
        * Use a text splitting strategy (e.g., `langchain.text_splitter.RecursiveCharacterTextSplitter`). Target 500-1000 tokens, configurable overlap.
        * Metadata for each chunk: Article Title, Source PDF filename, Page number(s), Chunk sequence ID, Collection ID/Name, PDF DB ID.
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

3.  **Vector Database Integration (Backend with LanceDB):**
    * Implement `backend/app/rag_components/vector_store_interface.py`:
        * Add **LanceDB** to `pyproject.toml` (`poetry add lancedb pylance`).
        * In `config.py`, define `LANCEDB_URI` (e.g., `./data/vector_store/lancedb_store`).
        * **LanceDB Specific Implementation:**
            * `initialize_vector_store()`: Connects to the LanceDB URI. `db = lancedb.connect(LANCEDB_URI)`
            * Define a Pydantic model or schema for the data to be stored in LanceDB tables. This schema should include the vector field and all metadata fields from your `Chunk` object (e.g., `text`, `article_title`, `source_pdf_filename`, `page_numbers`, `chunk_sequence_id`, `collection_id`, `pdf_db_id`).
            * `add_chunks_to_vector_store(collection_id: str, chunks_with_embeddings: list[tuple[Chunk, list[float]]])`:
                * Table names in LanceDB could be based on `collection_id` (e.g., `f"collection_{collection_id.replace('-', '_')}"`). Ensure table name sanitization.
                * For each collection, try to open an existing table or create it if it doesn't exist using the defined schema. `table = db.create_table(table_name, schema=YourLanceDBSchema, mode="overwrite" or "append")` or `table = db.open_table(table_name)`.
                * Prepare data as a list of dictionaries or a Pandas DataFrame matching the LanceDB table schema, then add using `table.add(data_to_add)`.
            * `search_relevant_chunks(collection_id: str, query_embedding: list[float], top_k: int = 5) -> list[Chunk]`:
                * Open the LanceDB table corresponding to `collection_id`.
                * Perform a vector search: `results = table.search(query_embedding).limit(top_k).to_list()` (or `.to_df()`).
                * Convert search results (which will be dictionaries or DataFrame rows) back into `Chunk` Pydantic objects (or similar structured dicts).
            * `delete_collection_from_vector_store(collection_id: str)`:
                * LanceDB allows dropping tables: `db.drop_table(f"collection_{collection_id.replace('-', '_')}")`.
            * `delete_pdf_chunks_from_vector_store(collection_id: str, pdf_db_id: int)`:
                * Open the table for `collection_id`.
                * Delete rows where the `pdf_db_id` metadata field matches the given `pdf_db_id`: `table.delete(f"pdf_db_id = {pdf_db_id}")`.
    * Ensure LanceDB data is persisted using Docker volumes (map `LANCEDB_URI` parent directory).
    * Update `pdf_ingestion_service.py` to call `add_chunks_to_vector_store`.
    * **TFD:**
        * Unit/integration tests in `backend/tests/unit/rag_components/test_vector_store_interface.py` for LanceDB operations: table creation, add, search (ensure filtering by `collection_id` via table name works), delete by collection, delete by `pdf_db_id`.
    * **Acceptance Criteria:** Text chunks, embeddings, and metadata stored in LanceDB. Data queryable and filterable (implicitly by table per collection). Persistence via Docker volumes. LanceDB is used as specified.

4.  **Local LLM Integration via Dedicated Docker Service (Backend & Docker Compose):**
    * **Update `docker-compose.yml`:**
        * Add new service `llm-service` for `ghcr.io/abetlen/llama-cpp-python:latest` as previously detailed (ports, volumes for models, `MODEL` environment variable).
    * **Implement `backend/app/rag_components/llm_handler.py`:**
        * Add `httpx` to `pyproject.toml`.
        * Client for `llm-service` (HTTP requests to `/v1/completions` or similar).
        * `config.py`: `LLM_SERVICE_URL`, `LLM_COMPLETION_ENDPOINT`.
        * `generate_answer_from_context(prompt_text: str, max_tokens: int = 500) -> str | None`.
    * **Hardware Adaptability (LLM Service):** Document GGUF model configuration for the Docker service.
    * **TFD:** Unit tests for `llm_handler.py` mocking `httpx` calls.
    * **Acceptance Criteria:** `llm-service` in `docker-compose.yml` starts. `llm_handler.py` communicates with it. LLM Docker service configuration documented.

5.  **RAG Service - Core Q&A Logic (Backend):**
    * Implement `backend/app/services/rag_service.py`:
        * `answer_question_from_collection(db: Session, collection_id: int, question_text: str) -> dict`:
            * Retrieve collection name.
            * Generate question embedding (`embedder.py`).
            * Retrieve relevant `Chunk` objects (from `vector_store_interface.py` using LanceDB).
            * Construct prompt.
            * Call `llm_handler.generate_answer_from_context(prompt_text)`.
            * Process LLM response: extract answer, citations.
            * Implement "I don't know..." logic.
            * Store question, answer, context, sources in SQLite.
    * **TFD:** Unit tests for prompt formatting. Integration tests for `rag_service.py`.
    * **Acceptance Criteria:** `rag_service` orchestrates RAG pipeline with LanceDB and externalized LLM. Returns context-based answers or "I don't know." History stored.

6.  **Manual Re-indexing Logic (Backend - Design & Stub for API trigger):**
    * In `backend/app/services/admin_service.py`:
        * Design full logic for `reindex_collection(db: Session, collection_id: int) -> bool`: (Clear LanceDB table for collection, re-fetch PDFs, re-extract, re-chunk, re-embed, re-add to LanceDB table).
        * Create stub function and placeholder for API endpoint.
    * **TFD:** Basic unit test for function signature.
    * **Acceptance Criteria:** Re-indexing logic designed for LanceDB. Placeholder function exists.

**Deliverable for CEO (Sprint 3 - Revised for LanceDB):** 💡🐳

* A demonstration (API calls or script):
    * Show `docker-compose.yml` with `llm-service` and backend configured for LanceDB. Start services.
    * Ingest sample PDFs into a collection (triggering full RAG pipeline including LanceDB storage).
    * Ask a question; show backend logs (API call to `llm-service`, LanceDB interaction if logged) and final answer with citations.
    * Ask an unanswerable question; show "I don't know."
* Show SQLite `QueryHistory`. Show LanceDB data location in Docker volume.
* Brief document/slide explaining:
    * Embedding model.
    * **LanceDB setup and usage.**
    * LLM Docker service setup.
* Updated test report summary.