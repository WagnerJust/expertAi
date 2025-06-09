"""
Q&A API Router - Handles RAG-based question answering endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List

from ...db.session import get_db
from ...services.rag_service import (
    answer_question_from_collection,
    get_collection_summary,
    get_recent_queries,
    validate_question
)
from ...services.admin_service import reindex_collection, reindex_collection_batch, get_system_stats
from ...models.schemas import (
    QuestionRequest, 
    QuestionResponse,
    CollectionSummaryResponse,
    RecentQueriesResponse,
    ReindexResponse,
    SystemStats
)
from pydantic import BaseModel

router = APIRouter(prefix="/qa", tags=["Q&A"])

# Pydantic models for API
# (These are now imported from schemas.py)

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about documents in a specific collection.
    Uses RAG pipeline to retrieve relevant context and generate answers.
    """
    # Validate the question
    validation = validate_question(request.question)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])
    
    # Process the question through RAG pipeline
    result = await answer_question_from_collection(
        db=db,
        collection_id=request.collection_id,
        question_text=validation["cleaned_question"],
        top_k=request.top_k
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return QuestionResponse(**result)

@router.get("/collection/{collection_id}/summary", response_model=CollectionSummaryResponse)
async def get_collection_qa_summary(
    collection_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a summary of a collection for Q&A purposes.
    Shows how many documents and chunks are available.
    """
    result = await get_collection_summary(db=db, collection_id=collection_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Collection not found"))
    
    return CollectionSummaryResponse(**result)

@router.get("/collection/{collection_id}/recent-queries", response_model=RecentQueriesResponse)
async def get_collection_recent_queries(
    collection_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent Q&A queries for a collection.
    """
    queries = await get_recent_queries(
        db=db,
        collection_id=collection_id,
        limit=limit
    )
    
    return RecentQueriesResponse(
        collection_id=collection_id,
        queries=queries,
        count=len(queries)
    )

# Admin endpoints
@router.post("/admin/reindex-collection/{collection_id}", response_model=ReindexResponse)
async def admin_reindex_collection(
    collection_id: int,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Re-index all documents in a collection.
    This will clear existing embeddings and rebuild them from scratch.
    """
    result = await reindex_collection(db=db, collection_id=collection_id)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Re-indexing failed"))
    
    return ReindexResponse(**result)

@router.post("/admin/reindex-collection-batch/{collection_id}", response_model=ReindexResponse)
async def admin_reindex_collection_batch(
    collection_id: int,
    batch_size: int = 5,  # Small batch size to prevent overwhelming
    db: Session = Depends(get_db)
):
    """
    Admin endpoint: Re-index all documents in a collection using batch processing.
    This processes PDFs in smaller batches for better performance and error handling.
    """
    result = await reindex_collection_batch(
        db=db, 
        collection_id=collection_id,
        batch_size=batch_size
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Batch re-indexing failed"))
    
    return ReindexResponse(**result)

@router.get("/admin/system-stats", response_model=SystemStats)
async def admin_get_system_stats(db: Session = Depends(get_db)):
    """
    Admin endpoint: Get system statistics for monitoring.
    """
    stats = get_system_stats(db=db)
    
    if not stats["success"]:
        raise HTTPException(status_code=500, detail=stats.get("error", "Failed to get stats"))
    
    return SystemStats(**stats)

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the Q&A service.
    """
    from ...rag_components.llm_handler import health_check_llm_service
    
    # Check LLM service health
    llm_healthy = await health_check_llm_service()
    
    return {
        "qa_service": "healthy",
        "llm_service": "healthy" if llm_healthy else "unhealthy",
        "overall_status": "healthy" if llm_healthy else "degraded"
    }
