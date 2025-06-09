"""
Integration test for the complete RAG pipeline.
Tests the full flow from PDF ingestion to question answering.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

from app.rag_components.chunker import chunk_text, Chunk
from app.rag_components.embedder import generate_embeddings_for_chunks
from app.rag_components.vector_store_interface import (
    add_chunks_to_vector_store,
    search_relevant_chunks,
    initialize_vector_store
)
from app.services.pdf_ingestion_service import extract_text_from_pdf
from app.core.config import settings

class TestRAGPipelineIntegration:
    
    @pytest.fixture
    def temp_chroma_db(self):
        """Create a temporary ChromaDB instance for testing."""
        temp_dir = tempfile.mkdtemp()
        original_path = settings.CHROMA_DB_PATH
        settings.CHROMA_DB_PATH = str(Path(temp_dir) / "test_chroma")
        
        yield temp_dir
        
        # Cleanup
        settings.CHROMA_DB_PATH = original_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing."""
        return {
            "text": "This is a sample document about artificial intelligence. " * 50,
            "page_info": {0: [1], 1: [2]}
        }
    
    def test_complete_rag_pipeline_flow(self, temp_chroma_db, sample_pdf_content):
        """Test the complete RAG pipeline from chunking to vector storage."""
        
        # Step 1: Chunk the text
        chunks = chunk_text(
            text_content=sample_pdf_content["text"],
            article_title="Test AI Document",
            pdf_filename="test_ai.pdf",
            collection_id="test_collection",
            pdf_db_id=1,
            page_info=sample_pdf_content["page_info"]
        )
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        
        # Step 2: Generate embeddings
        chunks_with_embeddings = generate_embeddings_for_chunks(chunks)
        
        assert len(chunks_with_embeddings) == len(chunks)
        assert all(len(embedding) > 0 for _, embedding in chunks_with_embeddings)
        
        # Step 3: Store in ChromaDB
        add_chunks_to_vector_store(
            chroma_collection_name="test_collection",
            chunks_with_embeddings=chunks_with_embeddings
        )
        
        # Step 4: Search for relevant chunks
        # Use the embedding of the first chunk as a query
        query_embedding = chunks_with_embeddings[0][1]
        
        retrieved_chunks = search_relevant_chunks(
            chroma_collection_name="test_collection",
            query_embedding=query_embedding,
            top_k=3,
            filter_collection_id="test_collection"
        )
        
        assert len(retrieved_chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in retrieved_chunks)
        assert retrieved_chunks[0].collection_id == "test_collection"
    
    def test_chunking_metadata_consistency(self):
        """Test that chunking preserves all required metadata."""
        test_text = "Sample text for chunking. " * 100
        
        chunks = chunk_text(
            text_content=test_text,
            article_title="Metadata Test",
            pdf_filename="metadata_test.pdf",
            collection_id="meta_col",
            pdf_db_id=123,
            page_info={0: [1, 2]}
        )
        
        for i, chunk in enumerate(chunks):
            assert chunk.article_title == "Metadata Test"
            assert chunk.source_pdf_filename == "metadata_test.pdf"
            assert chunk.collection_id == "meta_col"
            assert chunk.pdf_db_id == 123
            assert chunk.chunk_sequence_id == i
            assert chunk.id == f"metadata_test.pdf_chunk_{i}"
    
    def test_embedding_consistency(self):
        """Test that embeddings are consistent for the same text."""
        chunk1 = Chunk(
            id="test_1",
            text="Artificial intelligence is fascinating",
            article_title="AI Article",
            source_pdf_filename="ai.pdf",
            page_numbers=[1],
            chunk_sequence_id=0,
            collection_id="ai_col",
            pdf_db_id=1
        )
        
        chunk2 = Chunk(
            id="test_2",
            text="Artificial intelligence is fascinating",  # Same text
            article_title="AI Article 2",
            source_pdf_filename="ai2.pdf",
            page_numbers=[1],
            chunk_sequence_id=0,
            collection_id="ai_col",
            pdf_db_id=2
        )
        
        embeddings1 = generate_embeddings_for_chunks([chunk1])
        embeddings2 = generate_embeddings_for_chunks([chunk2])
        
        # Same text should produce same embeddings
        assert embeddings1[0][1] == embeddings2[0][1]
