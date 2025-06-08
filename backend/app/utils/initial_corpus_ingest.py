import os
import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from ..core.config import settings
from ..services import collection_service
from ..models import schemas, db_models
import logging

logger = logging.getLogger(__name__)

def ingest_initial_corpus(db: Session) -> dict:
    """
    Ingest PDFs from the initial corpus directory into the default collection.
    This copies files to the proper storage location and creates database records.
    
    Returns:
        dict: Summary of ingestion results
    """
    logger.info("Starting initial corpus ingestion...")
    results = {
        "processed": 0,
        "skipped": 0,
        "errors": 0,
        "files": []
    }
    
    try:
        # Check if default collection exists, create if not
        default_collection = db.query(db_models.Collection).filter_by(
            name=settings.default_collection_name
        ).first()
        
        if not default_collection:
            logger.info("Creating default collection...")
            collection_create = schemas.CollectionCreate(
                name=settings.default_collection_name,
                description="Default collection for initial corpus"
            )
            default_collection = collection_service.create_collection(db, collection_create)
            logger.info(f"Created default collection with ID: {default_collection.id}")
        
        # Check if initial corpus directory exists
        corpus_dir = Path(settings.initial_corpus_dir)
        if not corpus_dir.exists():
            logger.warning(f"Initial corpus directory does not exist: {corpus_dir}")
            return results
        
        # Create storage directory for the collection
        storage_dir = Path(settings.pdf_dir) / str(default_collection.id)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each PDF file in the corpus directory
        pdf_files = list(corpus_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in corpus directory")
        
        for pdf_file in pdf_files:
            try:
                # Check if already registered
                existing_pdf = db.query(db_models.PDFDocument).filter_by(
                    filename=pdf_file.name,
                    collection_id=default_collection.id
                ).first()
                
                if existing_pdf:
                    logger.debug(f"PDF already exists in collection: {pdf_file.name}")
                    results["skipped"] += 1
                    results["files"].append({
                        "filename": pdf_file.name,
                        "status": "skipped",
                        "reason": "already_exists"
                    })
                    continue
                
                # Copy file to storage directory
                destination = storage_dir / pdf_file.name
                shutil.copy2(pdf_file, destination)
                
                # Create database record
                title = pdf_file.stem.replace('_', ' ').replace('-', ' ').title()
                pdf_doc = db_models.PDFDocument(
                    title=title,
                    filename=pdf_file.name,
                    file_path=str(destination),
                    status="pending",
                    collection_id=default_collection.id
                )
                
                db.add(pdf_doc)
                db.commit()
                db.refresh(pdf_doc)
                
                logger.info(f"Successfully ingested: {pdf_file.name}")
                results["processed"] += 1
                results["files"].append({
                    "filename": pdf_file.name,
                    "status": "success",
                    "pdf_id": pdf_doc.id
                })
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                results["errors"] += 1
                results["files"].append({
                    "filename": pdf_file.name,
                    "status": "error",
                    "reason": str(e)
                })
                # Continue processing other files
                continue
        
        logger.info(
            f"Initial corpus ingestion complete. "
            f"Processed: {results['processed']}, "
            f"Skipped: {results['skipped']}, "
            f"Errors: {results['errors']}"
        )
        
    except Exception as e:
        logger.error(f"Fatal error during initial corpus ingestion: {str(e)}")
        results["fatal_error"] = str(e)
    
    return results
