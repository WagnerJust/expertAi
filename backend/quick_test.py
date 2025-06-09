#!/usr/bin/env python3
"""Quick test to verify Sprint 3 components work"""

import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

def test_chunker():
    print("🧪 Testing Chunker...")
    from app.rag_components.chunker import Chunk, chunk_text
    
    # Test chunk creation
    chunk = Chunk(
        text="This is a test chunk",
        source_pdf_filename="test.pdf",
        article_title="Test Article",
        page_numbers=[1],
        collection_id="1"
    )
    print(f"✅ Chunk created: {chunk.text[:20]}...")
    
    # Test chunking function
    text = "This is a long text. " * 20
    chunks = chunk_text(text, max_chunk_size=50, overlap_size=10)
    print(f"✅ Text chunked into {len(chunks)} pieces")
    return True

def test_vector_store():
    print("🧪 Testing Vector Store...")
    try:
        from app.rag_components.vector_store_interface import initialize_vector_store
        client = initialize_vector_store()
        print("✅ Vector store initialized")
        return True
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False

def test_embedder_import():
    print("🧪 Testing Embedder Import...")
    try:
        from app.rag_components.embedder import EmbeddingGenerator
        print("✅ EmbeddingGenerator imported successfully")
        return True
    except Exception as e:
        print(f"❌ Embedder import error: {e}")
        return False

def main():
    print("🚀 Sprint 3 Component Verification")
    print("=" * 40)
    
    results = []
    results.append(test_chunker())
    results.append(test_vector_store())
    results.append(test_embedder_import())
    
    print("\n📊 Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    print(f"Total: {len(results)}")
    
    if all(results):
        print("\n🎉 All core components are working!")
    else:
        print("\n⚠️  Some components need attention")

if __name__ == "__main__":
    main()
