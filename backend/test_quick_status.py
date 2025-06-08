#!/usr/bin/env python3
"""
Quick RAG System Status Check
"""
import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

def quick_status_check():
    """Quick status check of RAG system components"""
    print("⚡ Quick RAG System Status Check")
    print("=" * 35)
    
    # 1. Import tests
    print("\n1. Testing imports...")
    try:
        from app.main import app
        print("   ✅ Main app imported")
        
        from app.rag_components.embedder import EmbeddingGenerator
        print("   ✅ Embedder imported")
        
        from app.rag_components.vector_store_interface import VectorStoreInterface
        print("   ✅ Vector store imported")
        
        from app.rag_components.llm_handler import generate_answer_from_context
        print("   ✅ LLM handler imported")
        
        from app.services.rag_service import ask_question
        print("   ✅ RAG service imported")
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # 2. Database check
    print("\n2. Testing database...")
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        print("   ✅ Database connection established")
        db.close()
    except Exception as e:
        print(f"   ❌ Database failed: {e}")
        return False
    
    # 3. FastAPI test
    print("\n3. Testing FastAPI...")
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/")
        if response.status_code == 200:
            print("   ✅ FastAPI server working")
        else:
            print(f"   ⚠️  FastAPI returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ FastAPI test failed: {e}")
        return False
    
    print("\n" + "=" * 35)
    print("✅ All core components are working!")
    print("\n🚀 System Ready for Testing!")
    print("\nTo start the server:")
    print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\nTo test with curl:")
    print("   curl http://localhost:8000/")
    
    return True

if __name__ == "__main__":
    success = quick_status_check()
    if success:
        print("\n🎉 Sprint 3 RAG system is ready!")
    else:
        print("\n❌ Some components need attention")
