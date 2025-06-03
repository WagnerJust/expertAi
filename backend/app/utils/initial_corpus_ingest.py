import os
from pathlib import Path
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.services import pdf_ingestion_service, collection_service
from app.models import schemas

def ingest_initial_corpus():
    db: Session = SessionLocal()
    # Check if default collection exists
    default_collection = db.query(pdf_ingestion_service.db_models.Collection).filter_by(name=settings.default_collection_name).first()
    if not default_collection:
        # Create it
        default_collection = pdf_ingestion_service.db_models.Collection(name=settings.default_collection_name)
        db.add(default_collection)
        db.commit()
        db.refresh(default_collection)
    # Scan initial corpus dir
    corpus_dir = Path(settings.initial_corpus_dir)
    if not corpus_dir.exists():
        print(f"Initial corpus dir {corpus_dir} does not exist.")
        return
    for file in corpus_dir.glob("*.pdf"):
        # Check if already registered
        exists = db.query(pdf_ingestion_service.db_models.PDFDocument).filter_by(filename=file.name, collection_id=default_collection.id).first()
        if not exists:
            title = pdf_ingestion_service.filename_to_title(file.name)
            pdf_ingestion_service.add_pdf_record_to_db(db, title, file.name, str(file), default_collection.id)
    db.close()

def register_startup_event(app: FastAPI):
    @app.on_event("startup")
    def startup_ingest():
        ingest_initial_corpus()
