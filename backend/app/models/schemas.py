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
