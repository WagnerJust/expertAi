from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CollectionBase(BaseModel):
    name: str

class CollectionCreate(CollectionBase):
    pass

class Collection(CollectionBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class CollectionUpdate(BaseModel):
    name: Optional[str] = None

class PDFDocumentBase(BaseModel):
    filename: str
    title: Optional[str]
    status: str

class PDFDocumentCreate(PDFDocumentBase):
    collection_id: int

class PDFDocument(PDFDocumentBase):
    id: int
    collection_id: int
    class Config:
        orm_mode = True

class QueryBase(BaseModel):
    text: str

class QueryCreate(QueryBase):
    collection_id: int

class Query(QueryBase):
    id: int
    collection_id: int
    timestamp: datetime
    class Config:
        orm_mode = True

class AnswerBase(BaseModel):
    text: str
    context_used: str
    sources: List[str]

class AnswerCreate(AnswerBase):
    query_id: int

class Answer(AnswerBase):
    id: int
    query_id: int
    class Config:
        orm_mode = True

class FeedbackBase(BaseModel):
    rating: str
    comment: Optional[str]

class FeedbackCreate(FeedbackBase):
    answer_id: int

class Feedback(FeedbackBase):
    id: int
    answer_id: int
    class Config:
        orm_mode = True

class MsgDetail(BaseModel):
    detail: str

# Q&A specific schemas for RAG pipeline
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="The question to ask")
    collection_id: int = Field(..., description="ID of the collection to search in")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of relevant chunks to retrieve")

class SourceInfo(BaseModel):
    source_pdf: str
    article_title: str
    page_numbers: List[int]
    chunk_preview: str

class QuestionResponse(BaseModel):
    success: bool
    answer: str
    sources: List[SourceInfo]
    collection_name: str
    sources_count: int
    question: str
    error: Optional[str] = None

class CollectionSummaryResponse(BaseModel):
    success: bool
    collection_name: str
    collection_id: int
    pdf_count: int
    total_chunks_in_chroma: int
    created_at: datetime
    description: Optional[str] = None
    error: Optional[str] = None

class RecentQuery(BaseModel):
    id: int
    question: str
    answer: str
    sources_count: int
    timestamp: datetime

class RecentQueriesResponse(BaseModel):
    collection_id: int
    queries: List[RecentQuery]
    count: int

class ReindexResponse(BaseModel):
    success: bool
    collection_name: Optional[str] = None
    pdfs_processed: Optional[int] = None
    total_pdfs: Optional[int] = None
    chunks_created: Optional[int] = None
    errors: Optional[List[str]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class SystemStats(BaseModel):
    success: bool
    sqlite_stats: dict
    chromadb_stats: dict
    embedding_model: str
    chroma_db_path: str
    error: Optional[str] = None
