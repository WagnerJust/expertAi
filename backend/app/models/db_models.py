from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)  # Explicit length for PostgreSQL
    description = Column(Text)  # Added description field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated_at
    pdfs = relationship("PDFDocument", back_populates="collection")
    queries = relationship("QueryHistory", back_populates="collection")

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)  # Explicit length for PostgreSQL
    title = Column(String(500))  # Explicit length for PostgreSQL
    file_path = Column(String(1000))  # Added file_path field with explicit length
    status = Column(String(50), default="pending")  # Explicit length for PostgreSQL
    created_at = Column(DateTime, default=datetime.utcnow)  # Added created_at
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated_at
    collection_id = Column(Integer, ForeignKey("collections.id"))
    collection = relationship("Collection", back_populates="pdfs")

# Create an alias for compatibility
PDF = PDFDocument

class QueryHistory(Base):
    __tablename__ = "query_history"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)  # Renamed from 'text' to 'question_text'
    answer_text = Column(Text)  # Added answer_text field
    sources_count = Column(Integer, default=0)  # Added sources_count field
    collection_id = Column(Integer, ForeignKey("collections.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    collection = relationship("Collection", back_populates="queries")
    answers = relationship("Answer", back_populates="query")

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("query_history.id"))
    text = Column(Text, nullable=False)
    context_used = Column(Text)
    sources = Column(Text)  # JSON or comma-separated list
    query = relationship("QueryHistory", back_populates="answers")
    feedbacks = relationship("AnswerFeedback", back_populates="answer")

class AnswerFeedback(Base):
    __tablename__ = "answer_feedback"
    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"))
    rating = Column(String(20))  # Explicit length for PostgreSQL (e.g., 'good', 'bad')
    comment = Column(Text)
    answer = relationship("Answer", back_populates="feedbacks")
