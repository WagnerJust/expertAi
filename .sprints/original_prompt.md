Tags: Waterfall Methodology, Sprint Planning, Planning, Prompt Engineering, Web App, Python, backend, frontend, code.



YOUR MAIN Task:

Below is the outline for a project. I need it separated into detailed sprints following the waterfall methodology. These sprints/prompts will be given to my coding assistant LLM, Github Copilot, in order to complete the application. Each task should have acceptance criteria that should be met, and each sprint should finish with a deliverable to show the CEO.





---------------

# Project Title: Localized PDF Knowledge Base Q&A System 📚**Objective:**

Develop a robust, entirely local Retrieval-Augmented Generation (RAG) system. The system will be a **fully functional web application with a decoupled frontend (React) and Python backend**, enabling users to:1. Manage collections of PDF documents (uploading files or adding via links).2. Select a specific PDF collection for context.3. Ask questions and receive answers derived exclusively from the chosen PDF collection.

The system must be containerized using Docker for portability and ease of deployment, project dependencies managed using **Poetry**, and all source code managed in a **Git repository**. Development must follow a **Test-Focused Development (TFD)** approach.



---## Core Requirements:**1. PDF & Collection Management (Backend & UI):** * **Initial Corpus Directory:** The system may initially ingest PDF files from `/Users/justin/LLMS/Contexts/PromptEngineering/` (configurable, mountable) as a default collection. * **Dynamic PDF Addition (UI Feature):** * Users must be able to add new PDFs to a collection via the web UI by: * Uploading PDF files directly. * Providing a public URL to a PDF document (backend will download it). * **Collection Management (UI Feature):** * Users must be able to create, name, and manage multiple "collections" of PDF documents. * Users must be able to select a specific collection as the context for their Q&A chat session. * **Filename as Title:** Assume the filename of each PDF (e.g., "Scholarly_Article_Title.pdf") represents the title of the article. This title should be captured as key metadata. * **Comprehensive Text Extraction:** Accurately extract all readable textual content from each PDF file. * **Robustness (Parsing):** Implement error handling for diverse PDF structures, layouts, encodings. Consider local OCR (e.g., Tesseract) for scanned images if feasible within specified hardware adaptability constraints, with graceful fallback. * **Efficiency:** Optimize ingestion and indexing for responsiveness. Re-indexing will be a manual process triggered by the user. * **Storage:** * PDF files will be stored in a structured directory within a Docker volume. * Collection metadata (e.g., collection name, list of associated PDF filenames/paths, creation date) must be stored in a simple local database (e.g., SQLite, managed within a Docker volume) for easy querying and management by the backend.



---**2. Text Processing & Chunking:** * **Semantic Chunking:** Divide extracted text into meaningful segments (target: 500-1000 tokens, adaptable). Explore strategies beyond fixed-size if beneficial. * **Metadata Association:** For each chunk, meticulously store metadata including: * Article Title (from filename) * Source PDF filename * Page number(s) * Chunk sequence ID * **Collection ID/Name** (to associate chunk with its PDF collection) * Optionally: Section/subsection titles.



---**3. Embedding Generation & Vector Storage:** * **Embedding Model:** Utilize high-performing, open-source sentence embedding models (e.g., `all-mpnet-base-v2`, `BAAI/bge-large-en-v1.5`). * **Hardware Adaptability (Models):** The choice of embedding model (and LLM in section 4) should consider the **dynamic hardware target (8GB+ RAM, Apple M-series GPU or better, M1/AMD Ryzen 7 5800X or better CPUs)**. The system should ideally: * Offer configurations for different hardware tiers (e.g., different model sizes/quantization). * Or, provide clear guidance on selecting appropriate models based on user's hardware. * Justify model choice(s) based on performance, resource footprint, and adaptability. * **Local Vector Database:** Implement a local vector database (e.g., Chroma, FAISS, LanceDB) with persistence via Docker volumes. The database must support efficient filtering by **Collection ID/Name**. Document rationale for choice. * **Indexing Strategy:** Design for efficient retrieval and filtering.



---**4. Local Large Language Model (LLM) Integration:** * **LLM Selection:** Integrate local LLMs (e.g., Llama 3 series, Mistral Instruct, Phi-3). Specify model(s) and quantization (e.g., GGUF/AWQ/GPTQ). * **Hardware Adaptability (LLM):** Similar to embedding models, LLM choice/configuration must be adaptable or provide guidance for the specified dynamic hardware range. * **Strictly Local Inference:** No external API calls for generation. * **Contextual Grounding:** LLM generates answers *solely* based on context from the *selected PDF collection*.



---**5. Prompt Engineering & Hallucination Mitigation:** * **Optimized Prompt Template:** Develop a template instructing the LLM to: * Use *only* provided context from the *selected collection*. * State "I don't know..." if the answer isn't in the context. * Maintain conciseness. * Cite source(s) (Article Title, page number) from the collection. * **Example Template (to be refined):** ```text

You are a specialized assistant for answering questions based on a selected collection of PDF documents. Your knowledge is strictly limited to the information present in the retrieved context from this collection. Do not use any external knowledge. If the answer is not found, you MUST respond with "I don't know" or "The information is not available in the provided documents." Selected Collection: {collection_name}

Question: {question} Retrieved Context:

---

{retrieved_context}

--- Based ONLY on the retrieved context, answer the question. Cite Article Title and page number.

Answer:

```

---**6. User Interface (UI) & Functionality (React Frontend, Python Backend):** * **Decoupled Architecture:** * **Frontend:** React application. * **Backend:** Python API (e.g., FastAPI, Flask) serving the frontend and handling core logic. * **Core UI Features:** * **Q&A Interface:** Input for questions, display for answers. * **PDF/Collection Management (as per Section 1):** * Upload PDFs / Add PDFs via URL. * Create, name, and manage collections. * Select active collection for chat. * **Manual Re-indexing Trigger:** A UI element (e.g., "Update Collection" button) to initiate re-indexing for a selected collection after adding/removing PDFs. * **Query History:** Display a list of past questions and answers for the current collection. History should be **persistent across sessions** for each collection and stored in the backend database (e.g., SQLite). * **Answer Feedback:** Allow users to rate answers (e.g., thumbs up/down). This feedback should be **associated with the specific question, retrieved context, and generated answer**, and stored in the backend database (e.g., SQLite) for potential future analysis. * **View Context:** Optionally, allow users to view retrieved context chunks that informed an answer. * **Polished Design:** Strive for a clean, intuitive, and professional user experience. (Visual specifics can be iterated upon). * **Accessibility:** Interface should be accessible when the system is run via Docker.



---**7. Test-Focused Development, Evaluation & Testing:** * **Test-Focused Development (TFD) Approach: CRUCIAL REQUIREMENT.** The development process must prioritize writing tests before or concurrently with feature implementation. This includes comprehensive unit tests, integration tests, and end-to-end (E2E) tests where appropriate for both backend and frontend. * **Define Metrics:** Relevance of retrieved documents, factual accuracy of answers based on context, robustness to out-of-scope questions (per collection), UI responsiveness, test coverage. * **Test Cases:** Develop a diverse set of test queries and user interactions, including: * Questions with answers clearly present in the documents. * Questions requiring synthesis of information from multiple chunks/documents. * Questions whose answers are *not* in the documents for the selected collection. * Ambiguous or poorly phrased questions (to test robustness). * UI interactions for PDF and collection management.



---## Proposed Application Architecture (Foundation for AI Code Assistant):



The following is a **suggested** directory structure and component breakdown. The AI assistant should use this as a foundational guideline, adapting as necessary based on specific implementation choices and best practices for the selected frameworks (e.g., FastAPI for backend, React for frontend).

project_root/

├── backend/

│ ├── app/

│ │ ├── init.py

│ │ ├── main.py # FastAPI app initialization, global middleware, API routers

│ │ ├── core/ # Core logic: settings, security configurations

│ │ │ ├── init.py

│ │ │ ├── config.py # Application settings (env variables, etc.)

│ │ │ └── security.py # Authentication/Authorization helpers (if expanded in future)

│ │ ├── apis/ # API endpoint definitions (routers)

│ │ │ ├── init.py

│ │ │ └── v1/ # API version 1

│ │ │ ├── init.py

│ │ │ ├── router_collections.py # Endpoints for /collections

│ │ │ ├── router_pdfs.py # Endpoints for PDF management within collections

│ │ │ ├── router_qa.py # Endpoints for Q&A and feedback

│ │ │ └── router_admin.py # Endpoints for admin tasks (e.g., re-indexing trigger)

│ │ ├── services/ # Business logic layer

│ │ │ ├── init.py

│ │ │ ├── collection_service.py # Logic for managing PDF collections

│ │ │ ├── pdf_ingestion_service.py # Logic for PDF parsing, text extraction, downloading

│ │ │ ├── rag_service.py # Core RAG pipeline logic (retrieval, generation)

│ │ │ └── feedback_service.py # Logic for handling user feedback

│ │ ├── models/ # Data models

│ │ │ ├── init.py

│ │ │ ├── schemas.py # Pydantic models for API request/response validation

│ │ │ └── db_models.py # ORM models for SQLite database (collections, history, feedback)

│ │ ├── db/ # Database setup, migrations (e.g., Alembic), and the SQLite file

│ │ │ ├── init.py

│ │ │ └── local_database.sqlite # (Actual DB file managed by Docker volume)

│ │ ├── rag_components/ # Specific components of the RAG pipeline

│ │ │ ├── init.py

│ │ │ ├── chunker.py # Text chunking strategies

│ │ │ ├── embedder.py # Embedding model loading and usage

│ │ │ ├── vector_store_interface.py # Abstraction for vector DB operations

│ │ │ └── llm_handler.py # LLM loading, prompt formatting, and inference

│ │ └── utils/ # Common utility functions

│ │ └── init.py

│ ├── tests/ # Backend tests (following TFD)

│ │ ├── init.py

│ │ ├── conftest.py # Pytest fixtures and configuration

│ │ ├── unit/ # Unit tests for services, utils, RAG components

│ │ └── integration/ # Integration tests for API endpoints and service interactions

│ ├── Dockerfile # Dockerfile for the backend service

│ └── pyproject.toml # Poetry dependency management for backend

├── frontend/

│ ├── public/ # Static assets served directly

│ │ ├── index.html

│ │ └── ... # Favicons, manifest.json, etc.

│ ├── src/

│ │ ├── App.js # Main React application component, routing setup

│ │ ├── index.js # Entry point for the React application

│ │ ├── components/ # Reusable UI components (dumb components)

│ │ │ ├── common/ # Buttons, Modals, Loaders etc.

│ │ │ ├── collections/ # Components related to collection management

│ │ │ ├── pdfs/ # Components for PDF upload/listing

│ │ │ └── qa/ # Components for Q&A interface, feedback

│ │ ├── pages/ # Top-level view components (smart components)

│ │ │ ├── HomePage.js

│ │ │ ├── CollectionChatPage.js

│ │ │ └── ManageCollectionsPage.js

│ │ ├── services/ # Frontend services for API calls (e.g., using axios or fetch)

│ │ │ ├── collectionApi.js

│ │ │ ├── pdfApi.js

│ │ │ └── qaApi.js

│ │ ├── contexts/ # React Context API for global state management

│ │ │ └── AppContext.js # e.g., selected collection, theme

│ │ ├── hooks/ # Custom React Hooks

│ │ ├── assets/ # Static assets like images, fonts bundled by the build process

│ │ ├── styles/ # Global styles, theme definitions (e.g., CSS-in-JS, SASS)

│ │ └── setupTests.js # Test setup for Jest/React Testing Library

│ ├── tests/ # Frontend tests (following TFD)

│ │ ├── unit/

│ │ └── integration/

│ ├── Dockerfile # Dockerfile for building and serving the frontend

│ ├── package.json

│ └── ... # Other frontend configurations (babel.config.js, .eslintrc.js, etc.)

├── docker-compose.yml # Orchestrates all services (backend, frontend, vector DB)

├── .gitignore # Specifies intentionally untracked files that Git should ignore

└── README.md # Project overview, setup, and usage instructions





---

## Deliverables:



1. **Source Code & Version Control: CRUCIAL REQUIREMENT**

* Access to a **Git repository** containing the complete, well-organized source code history for both backend and frontend.

* Well-organized Python backend code.

* Well-organized React frontend code.

* **`pyproject.toml` (for Poetry)** and any lock files.

* **Comprehensive test suite** (unit, integration, and relevant E2E tests) demonstrating TFD.

2. **Dockerization Artifacts:** 🐳

* **`Dockerfile` (potentially separate for backend and frontend, or a multi-stage build).**

* **`docker-compose.yml`** for orchestrating backend, frontend (if served separately), vector database persistence, and local database (for metadata/history/feedback) persistence.

* Build and Run Scripts (`.sh` or `.bat`).

3. **Comprehensive Documentation:**

* **Setup & Installation:** Including Git repo cloning, Docker build/run, and Poetry environment setup.

* **Hardware Adaptability Guide:**

* Instructions on how to configure/select models based on user hardware, aligning with Core Requirement 3 & 4.

* **Recommended minimum and ideal hardware specifications** for different tiers of performance (e.g., "To comfortably run with a 7B parameter LLM and process up to X PDFs, we recommend Y RAM and Z CPU/GPU").

* **Usage Instructions:** For all UI features (Q&A, collection management, PDF addition, history, feedback, manual re-indexing).

* **System Architecture:** Overview of frontend, backend, data flow, and choices made based on the proposed architecture. Consideration should be given to backend frameworks that facilitate OpenAPI specification generation (e.g., FastAPI).

* **API Contract Documentation & OpenAPI Specification:**

* Detailed specification of the API between the frontend and backend.

* **An OpenAPI (e.g., Swagger) specification document (`openapi.json` or `openapi.yaml`) that is kept updated with the API development.**

* **Corpus & Collection Management:**

* How to manage the initial PDF directory and add/manage collections and PDFs via the UI.

* Details on the **manual re-indexing process (triggered via UI)** and its impact.

* Docker volume management for PDFs, collection metadata, vector DB, user feedback data, and query history.

* **Testing Strategy Document:** Overview of the TFD approach, types of tests implemented, and how to run them.

* **Troubleshooting.**

4. **Demonstration Materials:**

* Example queries and outputs.

* Brief report/presentation summarizing the design choices, challenges (especially regarding hardware adaptability and TFD implementation), and results.



---

## Key Constraints & Considerations:



* **Strictly Local Operation:** All components run locally.

* **Version Control:** Git repository is mandatory.

* **Test-Focused Development:** TFD is a core development principle for this project.

* **Portability & Reproducibility:** Docker is key.

* **Modularity & Maintainability:** Clear separation between frontend, backend, and RAG core, guided by the proposed architecture.

* **Resource Efficiency & Adaptability:** Crucial due to dynamic hardware target. Document resource usage and provide recommended hardware specifications for different configurations.

* **Scalability (Conceptual):** Discuss scaling for more users, larger/more collections, and potential bottlenecks (PDF parsing, indexing, concurrent API requests).

* **Limitations & Future Work:** Document limitations (OCR, LLM bias) and future improvements.