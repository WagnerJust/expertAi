#!/usr/bin/env python3
"""Simple test of RAG components"""

import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

def test_imports():
    """Test basic imports"""
    try:
        from app.services.rag_service import validate_question
        print("✅ rag_service import successful")
        
        result = validate_question("What is this about?")
        print("✅ Question validation works:", result)
        
    except Exception as e:
        print("❌ Import error:", e)
        return False
    
    try:
        from app.rag_components.embedder import EmbeddingGenerator
        embedder = EmbeddingGenerator()
        print("✅ EmbeddingGenerator created")
        
        embedding = embedder.generate_embedding("test text")
        print("✅ Embedding generated, length:", len(embedding))
        
    except Exception as e:
        print("❌ Embedding error:", e)
        return False
    
    try:
        from app.rag_components.vector_store_interface import VectorStoreInterface
        vector_store = VectorStoreInterface()
        print("✅ VectorStoreInterface created")
        
    except Exception as e:
        print("❌ Vector store error:", e)
        return False
    
    return True

if __name__ == "__main__":
    print("Testing RAG components...")
    success = test_imports()
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
