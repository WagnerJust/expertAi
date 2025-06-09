#!/usr/bin/env python3
"""
Direct test of FastAPI endpoints without startup events
"""
import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

def test_imports():
    """Test that all imports work"""
    print("🧪 Testing Core Imports")
    print("=" * 40)
    
    try:
        print("\n1. Testing FastAPI import...")
        from fastapi import FastAPI
        print("   ✅ FastAPI imported successfully")
        
        print("\n2. Testing database models...")
        from app.models.db_models import Collection, PDFDocument
        print("   ✅ Database models imported successfully")
        
        print("\n3. Testing RAG components...")
        from app.rag_components.embedder import EmbeddingGenerator
        from app.rag_components.vector_store_interface import VectorStoreInterface
        print("   ✅ RAG components imported successfully")
        
        print("\n4. Testing services...")
        from app.services.rag_service import validate_question
        print("   ✅ Services imported successfully")
        
        print("\n5. Testing API routers...")
        from app.apis.v1.router_qa import router as qa_router
        print("   ✅ API routers imported successfully")
        
        print("\n6. Testing config...")
        from app.core.config import settings
        print(f"   ✅ Config loaded - LLM URL: {settings.LLM_SERVICE_URL}")
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✅ All imports successful!")
    return True

def test_basic_functions():
    """Test basic function calls"""
    print("\n🧪 Testing Basic Functions")
    print("=" * 40)
    
    try:
        print("\n1. Testing question validation...")
        from app.services.rag_service import validate_question
        result = validate_question("What is the main topic?")
        print(f"   ✅ Question validation: {result}")
        
        print("\n2. Testing embedding generator...")
        from app.rag_components.embedder import EmbeddingGenerator
        embedder = EmbeddingGenerator()
        print("   ✅ Embedding generator created")
        
        # Test embedding generation
        test_text = "This is a test sentence for embedding."
        embedding = embedder.generate_embedding(test_text)
        print(f"   ✅ Generated embedding of length: {len(embedding)}")
        
    except Exception as e:
        print(f"   ❌ Function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 40)
    print("✅ Basic functions working!")
    return True

if __name__ == "__main__":
    if test_imports():
        test_basic_functions()
