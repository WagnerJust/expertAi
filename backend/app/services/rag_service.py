"""
RAG Service - Core Q&A Logic
Orchestrates the RAG pipeline: retrieval, context preparation, and answer generation.
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging
from datetime import datetime

from ..models.db_models import Collection, QueryHistory
from ..rag_components.embedder import get_embedding_model, generate_embeddings_for_chunks
from ..rag_components.vector_store_interface import search_relevant_chunks
from ..rag_components.llm_handler import generate_answer_from_context, construct_rag_prompt, extract_answer_with_fallback
from ..rag_components.chunker import Chunk
from ..core.config import settings

logger = logging.getLogger(__name__)

async def answer_question_from_collection(
    db: Session,
    collection_id_sqlite: int,
    question_text: str,
    top_k: int = 5
) -> Dict:
    """
    Answer a question using RAG pipeline with ChromaDB filtering by collection.
    
    Args:
        db: SQLAlchemy database session
        collection_id_sqlite: SQLite collection ID
        question_text: The user's question
        top_k: Number of relevant chunks to retrieve
        
    Returns:
        Dictionary with answer, sources, and metadata
    """
    try:
        # Step 1: Get collection info from SQLite
        collection = db.query(Collection).filter(Collection.id == collection_id_sqlite).first()
        if not collection:
            return {
                "success": False,
                "error": f"Collection with ID {collection_id_sqlite} not found",
                "answer": None,
                "sources": [],
                "collection_name": None
            }
        
        collection_name = collection.name
        collection_id_string = str(collection.id)  # Use as filter for ChromaDB
        
        logger.info(f"Processing question for collection '{collection_name}' (ID: {collection_id_sqlite})")
        
        # Step 2: Generate question embedding
        embedding_model = get_embedding_model()
        question_embeddings = embedding_model.encode([question_text], convert_to_numpy=True)
        question_embedding = question_embeddings[0].tolist()
        
        # Step 3: Retrieve relevant chunks from ChromaDB
        relevant_chunks = search_relevant_chunks(
            chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
            query_embedding=question_embedding,
            top_k=top_k,
            filter_collection_id=collection_id_string
        )
        
        logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")
        
        # Step 4: Construct prompt with context
        prompt = construct_rag_prompt(
            question=question_text,
            context_chunks=relevant_chunks,
            collection_name=collection_name
        )
        
        # Step 5: Generate answer using LLM
        raw_answer = await generate_answer_from_context(prompt)
        
        # Step 6: Process and clean the answer
        if raw_answer:
            processed_answer = extract_answer_with_fallback(raw_answer)
        else:
            processed_answer = "I'm sorry, I'm unable to generate an answer at this time. Please try again later."
        
        # Step 7: Prepare sources information
        sources = []
        for chunk in relevant_chunks:
            source_info = {
                "source_pdf": chunk.source_pdf_filename,
                "article_title": chunk.article_title,
                "page_numbers": chunk.page_numbers,
                "chunk_preview": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
            }
            sources.append(source_info)
        
        # Step 8: Store query history in SQLite
        try:
            query_history = QueryHistory(
                collection_id=collection_id_sqlite,
                question_text=question_text,
                answer_text=processed_answer,
                sources_count=len(relevant_chunks),
                timestamp=datetime.utcnow()
            )
            db.add(query_history)
            db.commit()
            logger.info("Query history saved to database")
        except Exception as e:
            logger.error(f"Failed to save query history: {str(e)}")
            db.rollback()
        
        return {
            "success": True,
            "answer": processed_answer,
            "sources": sources,
            "collection_name": collection_name,
            "sources_count": len(relevant_chunks),
            "question": question_text
        }
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {str(e)}")
        return {
            "success": False,
            "error": f"RAG pipeline error: {str(e)}",
            "answer": "I'm sorry, an error occurred while processing your question.",
            "sources": [],
            "collection_name": None
        }

async def get_collection_summary(db: Session, collection_id_sqlite: int) -> Dict:
    """
    Get a summary of what's available in a collection for Q&A.
    
    Args:
        db: SQLAlchemy database session
        collection_id_sqlite: SQLite collection ID
        
    Returns:
        Dictionary with collection summary
    """
    try:
        # Get collection from SQLite
        collection = db.query(Collection).filter(Collection.id == collection_id_sqlite).first()
        if not collection:
            return {
                "success": False,
                "error": f"Collection with ID {collection_id_sqlite} not found"
            }
        
        # Get PDF count from SQLite
        pdf_count = len(collection.pdfs) if collection.pdfs else 0
        
        # Get chunk count from ChromaDB (if possible)
        from ..rag_components.vector_store_interface import get_collection_stats
        chroma_stats = get_collection_stats(settings.CHROMA_DEFAULT_COLLECTION_NAME)
        
        return {
            "success": True,
            "collection_name": collection.name,
            "collection_id": collection_id_sqlite,
            "pdf_count": pdf_count,
            "total_chunks_in_chroma": chroma_stats.get("total_chunks", 0),
            "created_at": collection.created_at,
            "description": collection.description
        }
        
    except Exception as e:
        logger.error(f"Error getting collection summary: {str(e)}")
        return {
            "success": False,
            "error": f"Error getting collection summary: {str(e)}"
        }

async def get_recent_queries(db: Session, collection_id_sqlite: int, limit: int = 10) -> List[Dict]:
    """
    Get recent queries for a collection.
    
    Args:
        db: SQLAlchemy database session
        collection_id_sqlite: SQLite collection ID
        limit: Number of recent queries to return
        
    Returns:
        List of recent query dictionaries
    """
    try:
        queries = db.query(QueryHistory)\
            .filter(QueryHistory.collection_id == collection_id_sqlite)\
            .order_by(QueryHistory.timestamp.desc())\
            .limit(limit)\
            .all()
        
        result = []
        for query in queries:
            result.append({
                "id": query.id,
                "question": query.question_text,
                "answer": query.answer_text,
                "sources_count": query.sources_count,
                "timestamp": query.timestamp
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting recent queries: {str(e)}")
        return []

def validate_question(question_text: str) -> Dict:
    """
    Validate a question before processing.
    
    Args:
        question_text: The question to validate
        
    Returns:
        Dictionary with validation result
    """
    if not question_text or not question_text.strip():
        return {
            "valid": False,
            "error": "Question cannot be empty"
        }
    
    # Check minimum length
    if len(question_text.strip()) < 3:
        return {
            "valid": False,
            "error": "Question is too short"
        }
    
    # Check maximum length
    if len(question_text) > 1000:
        return {
            "valid": False,
            "error": "Question is too long (max 1000 characters)"
        }
    
    return {
        "valid": True,
        "cleaned_question": question_text.strip()
    }
