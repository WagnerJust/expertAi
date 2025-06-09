"""
Vector Store Interface for ChromaDB
Handles all vector database operations including storage, retrieval, and deletion.
"""

import chromadb
from typing import List, Tuple, Optional, Dict, Any
from .chunker import Chunk
from ..core.config import settings
import logging
import os
import json

logger = logging.getLogger(__name__)

# Global client instance for reuse
_chroma_client = None

def initialize_vector_store():
    """
    Initialize and return a ChromaDB HTTP client.
    Uses Docker container for ChromaDB service.
    """
    global _chroma_client
    if _chroma_client is None:
        try:
            # Use HTTP client to connect to Docker container
            _chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_HTTP_HOST, 
                port=settings.CHROMA_HTTP_PORT
            )
            # Test the connection
            _chroma_client.heartbeat()
            logger.info(f"Initialized ChromaDB HTTP client at: {settings.CHROMA_HTTP_HOST}:{settings.CHROMA_HTTP_PORT}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise Exception(f"ChromaDB initialization failed: {str(e)}")
    return _chroma_client

def get_or_create_collection(collection_name: str):
    """
    Get or create a ChromaDB collection.
    Uses pre-computed embeddings (embedding_function=None).
    """
    client = initialize_vector_store()
    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=None  # We provide pre-computed embeddings
        )
        logger.info(f"Retrieved/created collection: {collection_name}")
        return collection
    except Exception as e:
        logger.error(f"Failed to get/create collection {collection_name}: {str(e)}")
        raise

def add_chunks_to_vector_store(
    chroma_collection_name: str,
    chunks_with_embeddings: List[Tuple[Chunk, List[float]]]
):
    """
    Add chunks with their embeddings to ChromaDB.
    
    Args:
        chroma_collection_name: Name of the ChromaDB collection
        chunks_with_embeddings: List of (Chunk, embedding) tuples
    """
    if not chunks_with_embeddings:
        logger.warning("No chunks provided to add to vector store")
        return
    
    try:
        collection = get_or_create_collection(chroma_collection_name)
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        for chunk, embedding in chunks_with_embeddings:
            documents.append(chunk.text)
            embeddings.append(embedding)
            
            # Convert chunk metadata to ChromaDB-compatible format
            # Use JSON serialization for complex data structures
            metadata = {
                "article_title": chunk.article_title,
                "source_pdf": chunk.source_pdf_filename,
                "page_numbers": json.dumps(chunk.page_numbers),  # Better serialization
                "collection_id": chunk.collection_id,
                "pdf_db_id": chunk.pdf_db_id,
                "chunk_sequence_id": chunk.chunk_sequence_id
            }
            metadatas.append(metadata)
            ids.append(chunk.id)
        
        # Add to collection with better error handling
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks_with_embeddings)} chunks to collection '{chroma_collection_name}'")
        
    except Exception as e:
        logger.error(f"Failed to add chunks to vector store: {str(e)}")
        raise

def search_relevant_chunks(
    chroma_collection_name: str,
    query_embedding: List[float],
    top_k: int = 5,
    filter_collection_id: Optional[str] = None
) -> List[Chunk]:
    """
    Search for relevant chunks in ChromaDB using vector similarity.
    
    Args:
        chroma_collection_name: Name of the ChromaDB collection
        query_embedding: The query embedding vector
        top_k: Number of results to return
        filter_collection_id: Optional filter by collection_id metadata
        
    Returns:
        List of Chunk objects reconstructed from search results
    """
    try:
        collection = get_or_create_collection(chroma_collection_name)
        
        # Construct filter if provided
        where_filter = None
        if filter_collection_id:
            where_filter = {"collection_id": filter_collection_id}
        
        # Perform vector search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Convert results back to Chunk objects
        chunks = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]
                
                # Convert page_numbers back from JSON string to list (safe parsing)
                try:
                    page_numbers_str = metadata.get('page_numbers', '[]')
                    # Use json.loads for proper JSON parsing
                    page_numbers = json.loads(page_numbers_str)
                    if not isinstance(page_numbers, list):
                        page_numbers = []
                except (json.JSONDecodeError, ValueError):
                    # Fallback for old format using ast.literal_eval
                    try:
                        import ast
                        page_numbers = ast.literal_eval(page_numbers_str)
                        if not isinstance(page_numbers, list):
                            page_numbers = []
                    except (ValueError, SyntaxError):
                        page_numbers = []
                
                chunk = Chunk(
                    id=results['ids'][0][i],
                    text=results['documents'][0][i],
                    article_title=metadata.get('article_title', ''),
                    source_pdf_filename=metadata.get('source_pdf', ''),
                    page_numbers=page_numbers,
                    chunk_sequence_id=metadata.get('chunk_sequence_id', 0),
                    collection_id=metadata.get('collection_id', ''),
                    pdf_db_id=metadata.get('pdf_db_id', 0)
                )
                chunks.append(chunk)
        
        logger.info(f"Found {len(chunks)} relevant chunks in collection '{chroma_collection_name}'")
        return chunks
        
    except Exception as e:
        logger.error(f"Error searching chunks: {str(e)}")
        return []

def delete_collection_data_from_vector_store(
    chroma_collection_name: str,
    filter_collection_id: str
):
    """
    Delete all chunks with a specific collection_id from ChromaDB.
    
    Args:
        chroma_collection_name: Name of the ChromaDB collection
        filter_collection_id: The collection_id to filter and delete
    """
    try:
        collection = get_or_create_collection(chroma_collection_name)
        
        # Delete items matching the collection_id metadata
        collection.delete(where={"collection_id": filter_collection_id})
        
        logger.info(f"Deleted chunks with collection_id '{filter_collection_id}' from collection '{chroma_collection_name}'")
        
    except Exception as e:
        logger.error(f"Error deleting collection data: {str(e)}")

def delete_pdf_chunks_from_vector_store(
    chroma_collection_name: str,
    pdf_db_id: int
):
    """
    Delete all chunks from a specific PDF from ChromaDB.
    
    Args:
        chroma_collection_name: Name of the ChromaDB collection
        pdf_db_id: The pdf_db_id to filter and delete
    """
    try:
        collection = get_or_create_collection(chroma_collection_name)
        
        # Delete items matching the pdf_db_id metadata
        collection.delete(where={"pdf_db_id": pdf_db_id})
        
        logger.info(f"Deleted chunks with pdf_db_id '{pdf_db_id}' from collection '{chroma_collection_name}'")
        
    except Exception as e:
        logger.error(f"Error deleting PDF chunks: {str(e)}")

def get_collection_stats(chroma_collection_name: str) -> Dict[str, Any]:
    """
    Get statistics about a ChromaDB collection.
    
    Args:
        chroma_collection_name: Name of the ChromaDB collection
        
    Returns:
        Dictionary with collection statistics
    """
    try:
        collection = get_or_create_collection(chroma_collection_name)
        count = collection.count()
        
        return {
            "success": True,
            "collection_name": chroma_collection_name,
            "total_chunks": count
        }
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {str(e)}")
        return {
            "success": False,
            "collection_name": chroma_collection_name, 
            "total_chunks": 0, 
            "error": str(e)
        }
