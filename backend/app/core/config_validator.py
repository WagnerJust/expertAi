"""
Configuration validator for the RAG system.
Validates all configuration settings and dependencies.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
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
        try:
            pdf_dir.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create PDF directory: {e}")
    
    # Check ChromaDB path
    chroma_path = Path(settings.CHROMA_DB_PATH)
    if not chroma_path.parent.exists():
        try:
            chroma_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create ChromaDB directory: {e}")
    
    # Check required settings
    required_settings = [
        ("EMBEDDING_MODEL_NAME", settings.EMBEDDING_MODEL_NAME),
        ("LLM_SERVICE_URL", settings.LLM_SERVICE_URL),
        ("LLM_COMPLETION_ENDPOINT", settings.LLM_COMPLETION_ENDPOINT)
    ]
    
    for setting_name, setting_value in required_settings:
        if not setting_value:
            errors.append(f"Required setting {setting_name} is not configured")
    
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False
    
    logger.info("Configuration validation passed")
    return True

def validate_sprint3_environment() -> Dict[str, Any]:
    """
    Comprehensive validation for Sprint 3 environment and components.
    
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "config_summary": {},
        "component_status": {}
    }
    
    # Check Python version
    import sys
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor != 11:
        validation_result["errors"].append(
            f"Python 3.11 required, but found {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
        validation_result["valid"] = False
    else:
        validation_result["config_summary"]["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    # Check dependencies
    required_packages = [
        "chromadb",
        "sentence_transformers", 
        "httpx",
        "fastapi",
        "sqlalchemy",
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        validation_result["errors"].append(f"Missing required packages: {missing_packages}")
        validation_result["valid"] = False
    else:
        validation_result["config_summary"]["dependencies"] = "All required packages installed"
    
    # Test RAG components
    try:
        from ..rag_components.chunker import chunk_text
        validation_result["component_status"]["chunker"] = "✓ Working"
    except Exception as e:
        validation_result["errors"].append(f"Chunker error: {str(e)}")
        validation_result["valid"] = False
        validation_result["component_status"]["chunker"] = f"❌ Error: {str(e)}"
    
    try:
        from ..rag_components.embedder import get_embedding_model
        model = get_embedding_model()
        validation_result["component_status"]["embedder"] = f"✓ Working ({model.get_sentence_embedding_dimension()} dims)"
    except Exception as e:
        validation_result["errors"].append(f"Embedder error: {str(e)}")
        validation_result["valid"] = False
        validation_result["component_status"]["embedder"] = f"❌ Error: {str(e)}"
    
    try:
        from ..rag_components.vector_store_interface import initialize_vector_store
        client = initialize_vector_store()
        validation_result["component_status"]["vector_store"] = "✓ Working"
    except Exception as e:
        validation_result["errors"].append(f"Vector store error: {str(e)}")
        validation_result["valid"] = False
        validation_result["component_status"]["vector_store"] = f"❌ Error: {str(e)}"
    
    return validation_result
