# Sprint 3: Core Backend Logic - RAG Pipeline (Chunking, Embedding, Vector Storage, LLM) 🧠

**Goal:** Implement the core Retrieval-Augmented Generation (RAG) pipeline components: text chunking, embedding generation, vector storage integration, and local Large Language Model (LLM) integration for Q&A (backend processing only at this stage).

**Tasks for Coding Assistant (Copilot):**

1.  **Text Processing & Chunking (Backend):**
    * Implement `backend/app/rag_components/chunker.py`:
        * Define a `Chunk` Pydantic schema (e.g., `text: str, article_title: str, source_pdf_filename: str, page_numbers: list[int], chunk_sequence_id: int, collection_id: str`).
        * Implement `chunk_text(text_content: str, article_title: str, pdf_filename: str, collection_id: str, page_info: dict) -> list[Chunk]`. `page_info` could be a mapping of page number to text on that page if extracted that way, or just total pages if text is monolithic.
        * Use a text splitting strategy (e.g., `langchain.text_splitter.RecursiveCharacterTextSplitter` or `nltk.sent_tokenize` followed by grouping). Target 500-1000 tokens, configurable overlap.
        * Metadata for each chunk must include: Article Title (from filename), Source PDF filename, Page number(s) the chunk originated from, Chunk sequence ID (within the document), Collection ID/Name.
    * Modify `pdf_ingestion_service.py`: After successful text extraction, it should call the chunking function. The chunks themselves might not be stored in SQLite directly but passed to the embedding stage.
    * **TFD:**
        * Unit tests in `backend/tests/unit/rag_components/test_chunker.py` for the chunking logic. Test with sample long texts, texts with short paragraphs, and ensure metadata is correctly propagated.
    * **Acceptance Criteria:** Text from PDFs is chunked into meaningful segments with accurate and complete metadata associated with each chunk. Chunking parameters are configurable.

2.  **Embedding Generation (Backend):**
    * Implement `backend/app/rag_components/embedder.py`:
        * Add `sentence-transformers` to `pyproject.toml` (`poetry add sentence-transformers`).
        * In `config.py`, define `EMBEDDING_MODEL_NAME` (e.g., `all-mpnet-base-v2` or `BAAI/bge-large-en-v1.5`).
        * `get_embedding_model()`: Loads the sentence transformer model specified in `config.py`. Handle model download on first use.
        * `generate_embeddings(chunks: list[Chunk], model) -> list[tuple[Chunk, list[float]]]`: Takes list of `Chunk` objects, generates embeddings for `chunk.text`, and returns list of (Chunk, embedding_vector) tuples.
    * Address hardware adaptability: Document the resource footprint (RAM, disk space for model) of the chosen default embedding model. The system should be configurable to use different SentenceTransformer models via `config.py`.
    * **TFD:**
        * Unit tests in `backend/tests/unit/rag_components/test_embedder.py` for embedding generation. Check output embedding dimension and type. Test that it correctly processes a list of chunks.
    * **Acceptance Criteria:** Embeddings are generated for text chunks using a locally run, configurable, open-source model. Model choice and justification (performance vs. resource) documented.

3.  **Vector Database Integration (Backend):**
    * Implement `backend/app/rag_components/vector_store_interface.py`:
        * Choose and integrate a local vector database (e.g., ChromaDB `poetry add chromadb`, or LanceDB `poetry add lancedb`). Document rationale for choice (ease of local use, filtering, persistence).
        * In `config.py`, define `VECTOR_DB_PATH` (e.g., `./data/vector_store/chroma_db`).
        * Functions:
            * `initialize_vector_store()`: Connects to/creates the persistent vector store.
            * `add_chunks_to_vector_store(collection_id: str, chunks_with_embeddings: list[tuple[Chunk, list[float]]])`: Adds chunks and their embeddings. Chunks' metadata (article title, page numbers, source PDF, chunk ID) must be stored alongside vectors for retrieval and filtering. Vector DB collection might be named after `collection_id`.
            * `search_relevant_chunks(collection_id: str, query_embedding: list[float], top_k: int = 5) -> list[Chunk]`: Searches for relevant chunks based on query embedding, *strictly filtered by the `collection_id`*. Returns list of `Chunk` objects (or dicts with chunk data).
            * `delete_collection_from_vector_store(collection_id: str)`: Removes all vectors associated with a specific collection (for re-indexing or collection deletion).
    * Ensure vector store data is persisted using Docker volumes (map `VECTOR_DB_PATH` parent dir).
    * Update `pdf_ingestion_service.py` to call `add_chunks_to_vector_store` after embedding.
    * **TFD:**
        * Unit/integration tests in `backend/tests/unit/rag_components/test_vector_store_interface.py` (or integration tests if they hit a real temp DB) for vector store operations: add, search (ensure filtering by `collection_id` works), delete by collection.
    * **Acceptance Criteria:** Text chunks, their embeddings, and associated metadata are stored in the chosen local vector database; data is queryable and filterable by `collection_id`; persistence is handled via Docker volumes; rationale for DB choice documented.

4.  **Local Large Language Model (LLM) Integration (Backend):**
    * Implement `backend/app/rag_components/llm_handler.py`:
        * Select and integrate a local LLM (e.g., Llama 3 series, Mistral Instruct, Phi-3). Use GGUF format with a library like `llama-cpp-python` (`poetry add llama-cpp-python`).
        * In `config.py`, define `LLM_MODEL_PATH` (path to GGUF file) and `LLM_CONTEXT_SIZE`, `LLM_MAX_TOKENS_RESPONSE`.
        * `load_llm()`: Loads the LLM with specified model path and parameters (e.g., `n_ctx` for context window size, GPU layers if applicable `n_gpu_layers`).
        * `generate_answer_from_context(prompt: str, llm_instance) -> str`: Takes the fully formed prompt and returns the LLM's textual response.
    * Hardware adaptability: Document LLM choice, quantization level, and typical resource requirements. Configuration in `config.py` should allow changing the model path and parameters. Ensure strictly local inference (no API calls).
    * **TFD:**
        * Unit test in `backend/tests/unit/rag_components/test_llm_handler.py` to check if the LLM can be loaded (mock actual model loading for speed if necessary for CI, but have a way to test real loading) and can generate a simple, non-contextual response.
    * **Acceptance Criteria:** A selected local LLM is integrated and can perform inference based on a given prompt. Model choice, quantization, and hardware considerations documented.

5.  **RAG Service - Core Q&A Logic (Backend):**
    * Implement `backend/app/services/rag_service.py`:
        * `answer_question_from_collection(db: Session, collection_id: int, question_text: str) -> dict`:
            * Retrieve collection name from SQLite DB using `collection_id`.
            * Generate an embedding for the `question_text` using `embedder.py`.
            * Retrieve relevant `Chunk` objects from the vector store using `search_relevant_chunks`, filtering by `collection_id`.
            * Construct the prompt for the LLM using the optimized prompt template (from project requirements). Include `collection_name`, `question_text`, and the text content of the `retrieved_chunks`.
            * Send the prompt to the LLM via `llm_handler.generate_answer_from_context` to get an answer.
            * Process the LLM's response:
                * Extract the core answer.
                * Extract cited sources (Article Title, page number(s)) based on the metadata of the `retrieved_chunks` used in the context.
                * Implement hallucination mitigation: If context is empty or LLM cannot answer from context, ensure it returns "I don't know..." or similar, as per template.
            * Store the question, LLM's answer, retrieved context (e.g., list of chunk texts or chunk IDs), and cited sources in the SQLite database (e.g., `QueryHistory` table).
    * **TFD:**
        * Unit tests in `backend/tests/unit/services/test_rag_service.py` for prompt formatting logic.
        * Integration tests for `rag_service.py` (can mock LLM/vector store for some deterministic tests, but also aim for at least one test that goes through a small, controlled end-to-end RAG process if feasible for testing).
    * **Acceptance Criteria:** The `rag_service` can successfully take a question and collection ID, retrieve relevant context, construct a prompt, query the local LLM, and return an answer that is solely based on the provided context from the selected PDF collection. The system correctly responds "I don't know..." if the answer is not in the context. Questions, answers, context used, and citations are stored in the SQLite DB.

6.  **Manual Re-indexing Logic (Backend - Design & Stub for API trigger):**
    * In `backend/app/services/admin_service.py` (create this file) or `collection_service.py`:
        * Design the full logic for `reindex_collection(db: Session, collection_id: int) -> bool`:
            * Step 1: Delete existing chunks/embeddings for this collection from the vector store (`vector_store_interface.delete_collection_from_vector_store`).
            * Step 2: Fetch all `PDFDocument` records for this `collection_id` from the SQLite database.
            * Step 3: For each PDF:
                * Read its file path.
                * Re-extract text using `pdf_ingestion_service.extract_text_from_pdf`.
                * Re-chunk the text using `chunker.chunk_text`.
                * Re-generate embeddings using `embedder.generate_embeddings`.
                * Re-add the new chunks and embeddings to the vector store using `vector_store_interface.add_chunks_to_vector_store`.
                * Update PDF status in DB to "processed" or "reindex_error".
        * Create a stub function in the service and a placeholder for the API endpoint (to be fully implemented in Sprint 4).
    * **TFD:** Basic unit test for the existence of the service function signature.
    * **Acceptance Criteria:** Detailed re-indexing logic is designed. A function signature for re-indexing exists in the appropriate service.

**Deliverable for CEO (Sprint 3):** 💡

* A demonstration (can be via API calls using Postman/Insomnia or a simple Python script that uses the backend services directly):
    * Take 1-2 sample PDFs, ingest them into a new collection (this process should now trigger text extraction, chunking, embedding, and storage in the vector DB).
    * Ask a specific question that can only be answered from one of the ingested PDFs within that collection. Show the generated answer and the cited source (Article Title, page number).
    * Ask a question whose answer is clearly not in the ingested PDFs for that collection. Show the system's "I don't know..." response.
* Show the SQLite database entries for the `QueryHistory` table, demonstrating that questions, answers, and context/citations are being stored.
* A brief document or presentation slide explaining:
    * The chosen embedding model, its local nature, and basic hardware considerations.
    * The chosen vector database, why it was selected (e.g., local persistence, filtering), and how it stores data.
    * The chosen local LLM, its quantization, and basic hardware considerations.
* An updated test report summary (`pytest --cov`).