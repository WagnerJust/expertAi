from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pdf_dir: str = "./data/pdfs"  # Updated default for clarity
    db_url: str = "sqlite:///./db_data/local_database.sqlite"
    initial_corpus_dir: str = "./initial_corpus"
    default_collection_name: str = "Default Collection"
    EMBEDDING_MODEL_NAME: str = "all-mpnet-base-v2"
    
    # ChromaDB settings
    CHROMA_DB_PATH: str = "./data/vector_store/chroma_db"
    CHROMA_DEFAULT_COLLECTION_NAME: str = "rag_documents"
    
    # LLM Service settings (Ollama service)
    LLM_SERVICE_URL: str = "http://llm-service:11434"  # Use Docker service name
    LLM_COMPLETION_ENDPOINT: str = "/api/generate"

settings = Settings()
