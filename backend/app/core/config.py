from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    pdf_dir: str = "./data/pdfs"  # Updated default for clarity
    db_url: str = os.getenv("DB_URL", "postgresql://llm_user:llm_password@localhost:5432/llm_db")
    initial_corpus_dir: str = "./initial_corpus"
    default_collection_name: str = "Default Collection"
    EMBEDDING_MODEL_NAME: str = "all-mpnet-base-v2"
    
    # PostgreSQL specific settings
    postgres_db: str = os.getenv("POSTGRES_DB", "llm_db")
    postgres_user: str = os.getenv("POSTGRES_USER", "llm_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "llm_password")
    
    # ChromaDB settings
    CHROMA_DB_PATH: str = "./data/vector_store/chroma_db"  # Legacy - used only for file-based mode
    CHROMA_DEFAULT_COLLECTION_NAME: str = "rag_documents"
    CHROMA_HTTP_HOST: str = "localhost"  # ChromaDB HTTP host
    CHROMA_HTTP_PORT: int = 8001  # ChromaDB HTTP port
    
    # LLM Service settings (Ollama service)
    LLM_SERVICE_URL: str = "http://llm-service:11434"  # Use Docker service name
    LLM_COMPLETION_ENDPOINT: str = "/api/generate"

settings = Settings()
