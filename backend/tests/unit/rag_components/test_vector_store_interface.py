"""
Unit tests for ChromaDB vector store interface
"""

import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.rag_components.vector_store_interface import (
    initialize_vector_store,
    get_or_create_collection,
    add_chunks_to_vector_store,
    search_relevant_chunks,
    delete_collection_data_from_vector_store,
    delete_pdf_chunks_from_vector_store,
    get_collection_stats
)
from app.rag_components.chunker import Chunk

class TestVectorStoreInterface:
    """Test suite for vector store interface operations."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary directory for test ChromaDB."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing."""
        return [
            Chunk(
                id="test_pdf_chunk_0",
                text="This is the first chunk of text about machine learning.",
                article_title="Introduction to ML",
                source_pdf_filename="test.pdf",
                page_numbers=[1],
                chunk_sequence_id=0,
                collection_id="test_collection",
                pdf_db_id=1
            ),
            Chunk(
                id="test_pdf_chunk_1",
                text="This is the second chunk discussing neural networks.",
                article_title="Introduction to ML",
                source_pdf_filename="test.pdf",
                page_numbers=[2],
                chunk_sequence_id=1,
                collection_id="test_collection",
                pdf_db_id=1
            )
        ]
    
    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        return [
            [0.1, 0.2, 0.3, 0.4, 0.5],  # First chunk embedding
            [0.6, 0.7, 0.8, 0.9, 1.0]   # Second chunk embedding
        ]
    
    def test_initialize_vector_store(self, temp_db_path):
        """Test ChromaDB client initialization."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            client = initialize_vector_store()
            assert client is not None
            
            # Test that subsequent calls return the same client
            client2 = initialize_vector_store()
            assert client is client2
    
    def test_get_or_create_collection(self, temp_db_path):
        """Test collection creation and retrieval."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            collection = get_or_create_collection("test_collection")
            assert collection is not None
            assert collection.name == "test_collection"
            
            # Test that getting the same collection returns existing one
            collection2 = get_or_create_collection("test_collection")
            assert collection.name == collection2.name
    
    def test_add_chunks_to_vector_store(self, temp_db_path, sample_chunks, sample_embeddings):
        """Test adding chunks with embeddings to ChromaDB."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            chunks_with_embeddings = list(zip(sample_chunks, sample_embeddings))
            
            # Should not raise any exceptions
            add_chunks_to_vector_store("test_collection", chunks_with_embeddings)
            
            # Verify the collection exists and has the expected count
            collection = get_or_create_collection("test_collection")
            assert collection.count() == 2
    
    def test_search_relevant_chunks(self, temp_db_path, sample_chunks, sample_embeddings):
        """Test searching for relevant chunks."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            # First add some chunks
            chunks_with_embeddings = list(zip(sample_chunks, sample_embeddings))
            add_chunks_to_vector_store("test_collection", chunks_with_embeddings)
            
            # Search with a query embedding
            query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
            results = search_relevant_chunks(
                "test_collection", 
                query_embedding, 
                top_k=2
            )
            
            assert len(results) <= 2
            assert all(isinstance(chunk, Chunk) for chunk in results)
    
    def test_search_with_collection_filter(self, temp_db_path, sample_chunks, sample_embeddings):
        """Test searching with collection ID filter."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            # Add chunks with different collection IDs
            chunks_with_embeddings = list(zip(sample_chunks, sample_embeddings))
            add_chunks_to_vector_store("test_collection", chunks_with_embeddings)
            
            # Search with collection filter
            query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
            results = search_relevant_chunks(
                "test_collection",
                query_embedding,
                top_k=5,
                filter_collection_id="test_collection"
            )
            
            assert all(chunk.collection_id == "test_collection" for chunk in results)
    
    def test_delete_collection_data(self, temp_db_path, sample_chunks, sample_embeddings):
        """Test deleting data by collection ID."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            # Add chunks
            chunks_with_embeddings = list(zip(sample_chunks, sample_embeddings))
            add_chunks_to_vector_store("test_collection", chunks_with_embeddings)
            
            # Verify data exists
            collection = get_or_create_collection("test_collection")
            assert collection.count() == 2
            
            # Delete by collection ID
            delete_collection_data_from_vector_store("test_collection", "test_collection")
            
            # Verify data is deleted
            assert collection.count() == 0
    
    def test_delete_pdf_chunks(self, temp_db_path, sample_chunks, sample_embeddings):
        """Test deleting chunks by PDF ID."""
        with patch('app.core.config.settings.CHROMA_DB_PATH', temp_db_path):
            # Add chunks
            chunks_with_embeddings = list(zip(sample_chunks, sample_embeddings))
            add_chunks_to_vector_store("test_collection", chunks_with_embeddings)
            
            # Verify data exists
            collection = get_or_create_collection("test_collection")
            assert collection.count() == 2
            
            # Delete by PDF ID
            delete_pdf_chunks_from_vector_store("test_collection", 1)
            
            # Verify data is deleted
            assert collection.count() == 0
    
    def test_get_collection_stats(self, sample_chunks, sample_embeddings):
        """Test getting collection statistics."""
        # Add chunks
        chunks_with_embeddings = list(zip(sample_chunks, sample_embeddings))
        add_chunks_to_vector_store("test_collection", chunks_with_embeddings)
        
        # Get stats
        stats = get_collection_stats("test_collection")
        
        assert stats["success"] is True
        assert stats["collection_name"] == "test_collection"
        assert stats["total_chunks"] == 2
    
    def test_empty_chunks_list(self):
        """Test handling of empty chunks list."""
        # Should not raise any exceptions
        add_chunks_to_vector_store("test_collection", [])
        
        collection = get_or_create_collection("test_collection")
        assert collection.count() == 0
