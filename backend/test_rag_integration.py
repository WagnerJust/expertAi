#!/usr/bin/env python3
"""
Test script for RAG pipeline integration
Tests the core RAG functionality without requiring LLM service
"""

import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

from app.db.session import get_db
from app.services.rag_service import validate_question, get_collection_summary
from app.rag_components.vector_store_interface import VectorStoreInterface
from app.rag_components.embedder import EmbeddingGenerator
import asyncio

async def test_rag_components():
    """Test core RAG components"""
    print("🧪 Testing RAG Components")
    print("=" * 50)
    
    # 1. Test question validation
    print("\n1. Testing Question Validation")
    test_questions = [
        "What is the main topic?",
        "   ",  # Invalid - too short
        "How does this work?" * 20,  # Valid but long
        "Tell me about the document content"
    ]
    
    for q in test_questions:
        result = validate_question(q)
        print(f"   Question: '{q[:50]}...' -> Valid: {result['valid']}")
        if not result['valid']:
            print(f"      Error: {result['error']}")
    
    # 2. Test Embedding Generator
    print("\n2. Testing Embedding Generator")
    try:
        embedder = EmbeddingGenerator()
        test_text = "This is a test document for embedding generation."
        embedding = embedder.generate_embedding(test_text)
        print(f"   ✅ Generated embedding with shape: {len(embedding)}")
    except Exception as e:
        print(f"   ❌ Embedding generation failed: {e}")
    
    # 3. Test Vector Store Interface
    print("\n3. Testing Vector Store Interface")
    try:
        vector_store = VectorStoreInterface()
        
        # Test creating a collection
        collection_name = "test_collection"
        collection = vector_store.get_or_create_collection(collection_name)
        print(f"   ✅ Created/retrieved collection: {collection_name}")
        
        # Test adding documents
        test_docs = [
            {"id": "doc1", "text": "This is the first test document.", "metadata": {"source": "test"}},
            {"id": "doc2", "text": "This is the second test document.", "metadata": {"source": "test"}},
        ]
        
        for doc in test_docs:
            embedding = embedder.generate_embedding(doc["text"])
            vector_store.add_document(
                collection_name=collection_name,
                doc_id=doc["id"],
                text=doc["text"],
                embedding=embedding,
                metadata=doc["metadata"]
            )
        print(f"   ✅ Added {len(test_docs)} test documents")
        
        # Test search
        query = "first document"
        query_embedding = embedder.generate_embedding(query)
        results = vector_store.search_similar(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=2
        )
        print(f"   ✅ Search returned {len(results)} results")
        
        # Clean up test collection
        vector_store.delete_collection(collection_name)
        print(f"   ✅ Cleaned up test collection")
        
    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
    
    # 4. Test Database Integration
    print("\n4. Testing Database Integration")
    try:
        db = next(get_db())
        
        # Test get_collection_summary with a non-existent collection
        result = await get_collection_summary(db=db, collection_id_sqlite=999)
        print(f"   ✅ Collection summary for non-existent collection: {result['success']}")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Database integration test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 RAG Components Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_rag_components())
