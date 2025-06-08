"""
Configuration validator for the RAG system.
Validates all configuration settings and dependencies.
"""

import os
import logging
from pathlib import Path
from .config import settings

logger = logging.getLogger(__name__)

def validate_configuration() -> bool:
    """
    Validate all configuration settings and return True if valid.
    """
    errors = []
    
    # Check PDF directory
    pdf_dir = Path(settings.pdf_dir)
    if not pdf_dir.parent.exists():
        errors.append(f"PDF directory parent does not exist: {pdf_dir.parent}")
    
    # Check ChromaDB path
    chroma_path = Path(settings.CHROMA_DB_PATH)
    if not chroma_path.parent.exists():
        try:
            chroma_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create ChromaDB directory: {e}")
    
    # Check embedding model name
    valid_models = [
        "all-mpnet-base-v2",
        "all-MiniLM-L6-v2", 
        "multi-qa-mpnet-base-dot-v1"
    ]
    if settings.EMBEDDING_MODEL_NAME not in valid_models:
        logger.warning(f"Embedding model {settings.EMBEDDING_MODEL_NAME} not in recommended list")
    
    # Check LLM service URL format
    if not settings.LLM_SERVICE_URL.startswith(("http://", "https://")):
        errors.append(f"Invalid LLM service URL format: {settings.LLM_SERVICE_URL}")
    
    # Check chunk size settings
    if not hasattr(settings, 'DEFAULT_CHUNK_SIZE'):
        logger.info("Using default chunk size settings")
    
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False
    
    logger.info("Configuration validation passed")
    return True

def get_system_info() -> dict:
    """
    Get system information for diagnostics.
    """
    return {
        "python_version": os.sys.version,
        "pdf_dir": settings.pdf_dir,
        "chroma_db_path": settings.CHROMA_DB_PATH,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "llm_service_url": settings.LLM_SERVICE_URL,
        "db_url": settings.db_url
    }
