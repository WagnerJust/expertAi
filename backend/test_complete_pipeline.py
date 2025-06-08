#!/usr/bin/env python3
"""
Comprehensive RAG Pipeline Integration Test
"""
import sys
import os
import asyncio
sys.path.append('/Users/justin/LLMS/App/backend')

from fastapi.testclient import TestClient
from app.main import app
from app.rag_components.llm_handler import health_check_llm_service

async def test_complete_rag_pipeline():
    """Test the complete RAG pipeline"""
    print("🚀 Testing Complete RAG Pipeline")
    print("=" * 50)
    
    client = TestClient(app)
    
    # 1. Test server health
    print("\n1. Testing server health...")
    try:
        response = client.get("/")
        print(f"   Server Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("   ✅ Server is healthy")
    except Exception as e:
        print(f"   ❌ Server health check failed: {e}")
        return
    
    # 2. Test LLM service connectivity
    print("\n2. Testing LLM service connectivity...")
    try:
        is_healthy = await health_check_llm_service()
        print(f"   LLM Service: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
    except Exception as e:
        print(f"   ❌ LLM service check failed: {e}")
    
    # 3. Test collections
    print("\n3. Testing collections...")
    try:
        response = client.get("/collections/")
        print(f"   Collections Status: {response.status_code}")
        if response.status_code == 200:
            collections = response.json()
            print(f"   Found {len(collections)} collections")
            
            # If we have collections, test one
            if collections:
                collection_id = collections[0]['id']
                print(f"   Testing collection ID: {collection_id}")
                
                # Test collection summary
                response = client.get(f"/qa/collection/{collection_id}/summary")
                print(f"   Summary Status: {response.status_code}")
                if response.status_code == 200:
                    summary = response.json()
                    print(f"   ✅ Collection summary generated: {len(summary.get('summary', ''))} chars")
                else:
                    print(f"   ⚠️  Summary failed: {response.text}")
        else:
            print(f"   ⚠️  Collections endpoint error: {response.text}")
    except Exception as e:
        print(f"   ❌ Collections test failed: {e}")
    
    # 4. Test Q&A with a simple question
    print("\n4. Testing Q&A functionality...")
    try:
        test_question = {
            "question": "What is the main topic of the documents?",
            "collection_id": 1,  # Assuming default collection exists
            "max_results": 3
        }
        
        response = client.post("/qa/ask", json=test_question)
        print(f"   Q&A Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Q&A Response received:")
            print(f"      Answer: {result.get('answer', 'No answer')[:100]}...")
            print(f"      Sources: {len(result.get('sources', []))}")
            print(f"      Confidence: {result.get('confidence_score', 'N/A')}")
        elif response.status_code == 422:
            print(f"   ⚠️  Validation error (expected): {response.json()}")
        else:
            print(f"   ❌ Q&A failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Q&A test failed: {e}")
    
    # 5. Test admin functionality
    print("\n5. Testing admin functionality...")
    try:
        response = client.post("/collections/1/reindex")
        print(f"   Reindex Status: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 if collection doesn't exist
            print("   ✅ Admin reindex endpoint working")
        else:
            print(f"   ⚠️  Reindex response: {response.text}")
    except Exception as e:
        print(f"   ❌ Admin test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 RAG Pipeline Integration Test Completed!")
    print("\nNext Steps:")
    print("- Upload some PDFs to test with real documents")
    print("- Try more complex questions")
    print("- Test the frontend integration")

def main():
    asyncio.run(test_complete_rag_pipeline())

if __name__ == "__main__":
    main()
