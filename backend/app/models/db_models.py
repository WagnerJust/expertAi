from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    pdfs = relationship("PDFDocument", back_populates="collection")
    queries = relationship("QueryHistory", back_populates="collection")

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    title = Column(String)
    status = Column(String, default="pending")
    collection_id = Column(Integer, ForeignKey("collections.id"))
    collection = relationship("Collection", back_populates="pdfs")

class QueryHistory(Base):
    __tablename__ = "query_history"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
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
    sources = Column(Text)  # Comma-separated list
    query = relationship("QueryHistory", back_populates="answers")
    feedbacks = relationship("AnswerFeedback", back_populates="answer")

class AnswerFeedback(Base):
    __tablename__ = "answer_feedback"
    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"))
    rating = Column(String)
    comment = Column(Text)
    answer = relationship("Answer", back_populates="feedbacks")
