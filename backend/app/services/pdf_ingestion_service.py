import os
from pathlib import Path
from fastapi import UploadFile
import httpx
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models import db_models
from typing import Optional, Dict, Tuple
import fitz  # PyMuPDF
import logging

# Import RAG components
from ..rag_components.chunker import chunk_text
from ..rag_components.embedder import generate_embeddings_for_chunks
from ..rag_components.vector_store_interface import add_chunks_to_vector_store

logger = logging.getLogger(__name__)

def store_uploaded_pdf(collection_id: int, pdf_file: UploadFile) -> Path:
    """Store uploaded PDF file in the designated directory structure."""
    try:
        base_path = Path(settings.pdf_dir) / str(collection_id)
        base_path.mkdir(parents=True, exist_ok=True)
        file_path = base_path / pdf_file.filename
        
        # Reset file pointer to beginning
        pdf_file.file.seek(0)
        
        with open(file_path, "wb") as f:
            content = pdf_file.file.read()
            if not content:
                raise ValueError(f"Empty file provided: {pdf_file.filename}")
            f.write(content)
        
        logger.info(f"Successfully stored PDF: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error storing uploaded PDF {pdf_file.filename}: {str(e)}")
        raise

def download_pdf_from_url(collection_id: int, url: str, filename: str) -> Optional[Path]:
    """Download PDF from URL and store it in the designated directory structure."""
    base_path = Path(settings.pdf_dir) / str(collection_id)
    base_path.mkdir(parents=True, exist_ok=True)
    file_path = base_path / filename
    
    try:
        logger.info(f"Downloading PDF from URL: {url}")
        with httpx.stream("GET", url, timeout=30.0, follow_redirects=True) as r:
            r.raise_for_status()
            
            # Check if it's actually a PDF by content type
            content_type = r.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not filename.lower().endswith('.pdf'):
                logger.warning(f"Downloaded content may not be PDF. Content-Type: {content_type}")
            
            with open(file_path, "wb") as f:
                total_size = 0
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    total_size += len(chunk)
                    # Basic size check to prevent huge downloads
                    if total_size > 100 * 1024 * 1024:  # 100MB limit
                        raise ValueError("PDF file too large (>100MB)")
        
        logger.info(f"Successfully downloaded PDF: {file_path} ({total_size} bytes)")
        return file_path
        
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {str(e)}")
        if file_path.exists():
            file_path.unlink()  # Clean up partial download
        return None

def add_pdf_record_to_db(db: Session, title: str, filename: str, file_path: str, collection_id: int, status: str = "pending") -> db_models.PDFDocument:
    pdf_doc = db_models.PDFDocument(
        title=title,
        filename=filename,
        file_path=file_path,
        status=status,
        collection_id=collection_id
    )
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    return pdf_doc

def extract_text_from_pdf(pdf_path: Path) -> Optional[Tuple[str, Dict]]:
    """
    Extract text from PDF and return text content with page information.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (text_content, page_info_dict) or None if extraction fails
    """
    try:
        doc = fitz.open(pdf_path)
        
        text_parts = []
        page_info = {}
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():  # Only add non-empty pages
                text_parts.append(page_text)
                # Store page info for chunking (simple approach)
                page_info[len(text_parts) - 1] = [page_num + 1]  # 1-indexed page numbers
        
        full_text = "\n".join(text_parts)
        doc.close()
        
        return full_text, page_info
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return None

def filename_to_title(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    return name.replace('_', ' ').replace('-', ' ').title()

async def process_pdf_with_rag_pipeline(
    db: Session,
    pdf_record: db_models.PDFDocument,
    pdf_path: Path
) -> Dict:
    """
    Process a PDF through the complete RAG pipeline.
    This includes text extraction, chunking, embedding generation, and ChromaDB storage.
    
    Args:
        db: SQLAlchemy database session
        pdf_record: The PDF database record
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Starting RAG pipeline processing for: {pdf_record.filename}")
        
        # Step 1: Extract text from PDF
        extraction_result = extract_text_from_pdf(pdf_path)
        if not extraction_result:
            pdf_record.status = "failed"
            db.commit()
            return {
                "success": False,
                "error": "Failed to extract text from PDF",
                "pdf_id": pdf_record.id
            }
        
        text_content, page_info = extraction_result
        
        if not text_content.strip():
            pdf_record.status = "failed"
            db.commit()
            return {
                "success": False,
                "error": "No text content found in PDF",
                "pdf_id": pdf_record.id
            }
        
        # Step 2: Chunk the text
        chunks = chunk_text(
            text_content=text_content,
            article_title=pdf_record.title or pdf_record.filename,
            pdf_filename=pdf_record.filename,
            collection_id=str(pdf_record.collection_id),
            pdf_db_id=pdf_record.id,
            page_info=page_info
        )
        
        if not chunks:
            pdf_record.status = "failed"
            db.commit()
            return {
                "success": False,
                "error": "Failed to create chunks from PDF text",
                "pdf_id": pdf_record.id
            }
        
        logger.info(f"Created {len(chunks)} chunks from {pdf_record.filename}")
        
        # Step 3: Generate embeddings
        chunks_with_embeddings = generate_embeddings_for_chunks(chunks)
        
        # Step 4: Store in ChromaDB
        add_chunks_to_vector_store(
            chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
            chunks_with_embeddings=chunks_with_embeddings
        )
        
        # Step 5: Update PDF status
        pdf_record.status = "processed"
        db.commit()
        
        logger.info(f"Successfully processed {pdf_record.filename} through RAG pipeline")
        
        return {
            "success": True,
            "pdf_id": pdf_record.id,
            "filename": pdf_record.filename,
            "chunks_created": len(chunks),
            "text_length": len(text_content),
            "message": f"Successfully processed {pdf_record.filename}"
        }
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline processing for {pdf_record.filename}: {str(e)}")
        pdf_record.status = "failed"
        db.commit()
        
        return {
            "success": False,
            "error": f"RAG pipeline processing failed: {str(e)}",
            "pdf_id": pdf_record.id
        }
