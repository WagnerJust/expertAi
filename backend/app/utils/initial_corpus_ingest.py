import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal, init_db
from app.services import pdf_ingestion_service

def ingest_initial_corpus(db: Session):
    print("[ingest_initial_corpus] Starting initial corpus ingestion...")
    # init_db()  # No need to call here; already called in main.py before session creation
    print("[ingest_initial_corpus] DB session created.")
    # Check if default collection exists
    print("[ingest_initial_corpus] Checking for default collection...")
    default_collection = db.query(pdf_ingestion_service.db_models.Collection).filter_by(name=settings.default_collection_name).first()
    print(f"[ingest_initial_corpus] Default collection: {default_collection}")
    if not default_collection:
        print("[ingest_initial_corpus] Creating default collection...")
        default_collection = pdf_ingestion_service.db_models.Collection(name=settings.default_collection_name)
        db.add(default_collection)
        db.commit()
        db.refresh(default_collection)
        print("[ingest_initial_corpus] Default collection created.")
    # Scan initial corpus dir
    corpus_dir = Path(settings.initial_corpus_dir)
    if not corpus_dir.exists():
        print(f"[ingest_initial_corpus] Initial corpus dir {corpus_dir} does not exist.")
        return
    for file in corpus_dir.glob("*.pdf"):
        print(f"[ingest_initial_corpus] Checking PDF: {file.name}")
        # Check if already registered
        exists = db.query(pdf_ingestion_service.db_models.PDFDocument).filter_by(filename=file.name, collection_id=default_collection.id).first()
        if not exists:
            print(f"[ingest_initial_corpus] Registering PDF: {file.name}")
            title = pdf_ingestion_service.filename_to_title(file.name)
            pdf_ingestion_service.add_pdf_record_to_db(db, title, file.name, str(file), default_collection.id)
    print("[ingest_initial_corpus] Initial corpus ingestion complete.")
