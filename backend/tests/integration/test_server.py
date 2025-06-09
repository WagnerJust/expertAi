#!/usr/bin/env python3
"""
Quick test server to validate Q&A API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="RAG Q&A Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RAG Q&A Test API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_components": "available",
        "database": "connected"
    }

@app.post("/qa/ask")
async def ask_question(request: dict):
    """Mock Q&A endpoint for testing"""
    question = request.get("question", "")
    collection_id = request.get("collection_id", 1)
    
    if not question or len(question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question too short")
    
    # Mock response
    return {
        "success": True,
        "answer": f"This is a mock answer for the question: '{question}'. In a real implementation, this would be generated using the RAG pipeline.",
        "sources": [
            {"id": "doc1", "text": "Mock source 1", "metadata": {"source": "test.pdf"}},
            {"id": "doc2", "text": "Mock source 2", "metadata": {"source": "test2.pdf"}}
        ],
        "collection_name": f"Collection {collection_id}",
        "sources_count": 2,
        "question": question
    }

@app.get("/qa/collection/{collection_id}/summary")
async def get_collection_summary(collection_id: int):
    """Mock collection summary endpoint"""
    return {
        "success": True,
        "collection_name": f"Test Collection {collection_id}",
        "collection_id": collection_id,
        "pdf_count": 3,
        "total_chunks_in_chroma": 45,
        "created_at": "2024-12-29T17:00:00",
        "description": "Mock collection for testing"
    }

if __name__ == "__main__":
    print("Starting RAG Q&A Test Server...")
    print("API Documentation: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
