"""
Admin Service - Administrative operations for the RAG system
Handles re-indexing, maintenance, and system administration tasks.
"""

from sqlalchemy.orm import Session
from typing import Dict, List
import logging
import os
from datetime import datetime
import os

from ..models.db_models import Collection, PDF
from ..rag_components.vector_store_interface import (
    delete_collection_data_from_vector_store,
    delete_pdf_chunks_from_vector_store,
    add_chunks_to_vector_store
)
from ..rag_components.chunker import chunk_text
from ..rag_components.embedder import generate_embeddings_for_chunks
from ..services.pdf_ingestion_service import extract_text_from_pdf
from ..core.config import settings

logger = logging.getLogger(__name__)

async def reindex_collection(db: Session, collection_id: int) -> Dict:
    """
    Completely re-index a collection by re-processing all PDFs.
    This clears existing ChromaDB data and rebuilds it from scratch.
    
    Args:
        db: SQLAlchemy database session
        collection_id: Database collection ID to re-index
        
    Returns:
        Dictionary with re-indexing results
    """
    try:
        # Step 1: Get collection info from database
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return {
                "success": False,
                "error": f"Collection with ID {collection_id} not found"
            }
        
        collection_name = collection.name
        collection_id_string = str(collection.id)
        
        logger.info(f"Starting re-indexing for collection '{collection_name}' (ID: {collection_id})")
        
        # Step 2: Clear existing ChromaDB data for this collection
        delete_collection_data_from_vector_store(
            chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
            filter_collection_id=collection_id_string
        )
        
        # Step 3: Get all PDFs in this collection
        pdfs = db.query(PDF).filter(PDF.collection_id == collection_id).all()
        
        if not pdfs:
            logger.info(f"No PDFs found in collection '{collection_name}'")
            return {
                "success": True,
                "message": f"Collection '{collection_name}' has no PDFs to re-index",
                "pdfs_processed": 0,
                "chunks_created": 0
            }
        
        total_chunks = 0
        processed_pdfs = 0
        errors = []
        
        # Step 4: Re-process each PDF
        for pdf in pdfs:
            try:
                logger.info(f"Re-processing PDF: {pdf.filename}")
                
                # Extract text from PDF
                text_content, page_info = extract_text_from_pdf(pdf.file_path)
                
                if not text_content:
                    errors.append(f"No text extracted from {pdf.filename}")
                    continue
                
                # Chunk the text
                chunks = chunk_text(
                    text_content=text_content,
                    article_title=pdf.title or pdf.filename,
                    pdf_filename=pdf.filename,
                    collection_id=collection_id_string,
                    pdf_db_id=pdf.id,
                    page_info=page_info
                )
                
                if not chunks:
                    errors.append(f"No chunks created from {pdf.filename}")
                    continue
                
                # Generate embeddings
                chunks_with_embeddings = generate_embeddings_for_chunks(chunks)
                
                # Add to ChromaDB
                add_chunks_to_vector_store(
                    chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
                    chunks_with_embeddings=chunks_with_embeddings
                )
                
                total_chunks += len(chunks)
                processed_pdfs += 1
                
                logger.info(f"Successfully re-processed {pdf.filename}: {len(chunks)} chunks")
                
            except Exception as e:
                error_msg = f"Error processing {pdf.filename}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Step 5: Update collection timestamp
        collection.updated_at = datetime.utcnow()
        db.commit()
        
        result = {
            "success": True,
            "collection_name": collection_name,
            "pdfs_processed": processed_pdfs,
            "total_pdfs": len(pdfs),
            "chunks_created": total_chunks,
            "errors": errors
        }
        
        if errors:
            result["message"] = f"Re-indexing completed with {len(errors)} errors"
        else:
            result["message"] = "Re-indexing completed successfully"
        
        logger.info(f"Re-indexing completed for collection '{collection_name}': {processed_pdfs}/{len(pdfs)} PDFs, {total_chunks} chunks")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during re-indexing: {str(e)}")
        return {
            "success": False,
            "error": f"Re-indexing failed: {str(e)}"
        }

async def reindex_single_pdf(db: Session, pdf_id: int) -> Dict:
    """
    Re-index a single PDF by re-processing it.
    
    Args:
        db: SQLAlchemy database session
        pdf_id: PDF ID to re-index
        
    Returns:
        Dictionary with re-indexing results
    """
    try:
        # Get PDF info
        pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
        if not pdf:
            return {
                "success": False,
                "error": f"PDF with ID {pdf_id} not found"
            }
        
        logger.info(f"Re-indexing single PDF: {pdf.filename}")
        
        # Clear existing chunks for this PDF from ChromaDB
        delete_pdf_chunks_from_vector_store(
            chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
            pdf_db_id=pdf_id
        )
        
        # Re-process the PDF
        text_content, page_info = extract_text_from_pdf(pdf.file_path)
        
        if not text_content:
            return {
                "success": False,
                "error": f"No text could be extracted from {pdf.filename}"
            }
        
        # Chunk the text
        chunks = chunk_text(
            text_content=text_content,
            article_title=pdf.title or pdf.filename,
            pdf_filename=pdf.filename,
            collection_id=str(pdf.collection_id),
            pdf_db_id=pdf.id,
            page_info=page_info
        )
        
        if not chunks:
            return {
                "success": False,
                "error": f"No chunks could be created from {pdf.filename}"
            }
        
        # Generate embeddings and add to ChromaDB
        chunks_with_embeddings = generate_embeddings_for_chunks(chunks)
        add_chunks_to_vector_store(
            chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
            chunks_with_embeddings=chunks_with_embeddings
        )
        
        # Update PDF timestamp
        pdf.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Successfully re-indexed PDF {pdf.filename}: {len(chunks)} chunks")
        
        return {
            "success": True,
            "pdf_filename": pdf.filename,
            "chunks_created": len(chunks),
            "message": f"Successfully re-indexed {pdf.filename}"
        }
        
    except Exception as e:
        logger.error(f"Error re-indexing PDF {pdf_id}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to re-index PDF: {str(e)}"
        }

def get_system_stats(db: Session) -> Dict:
    """
    Get system statistics for admin dashboard.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        Dictionary with system statistics
    """
    try:
        from ..rag_components.vector_store_interface import get_collection_stats
        
        # Get database stats
        total_collections = db.query(Collection).count()
        total_pdfs = db.query(PDF).count()
        
        # Get ChromaDB stats
        chroma_stats = get_collection_stats(settings.CHROMA_DEFAULT_COLLECTION_NAME)
        
        return {
            "success": True,
            "database_stats": {
                "total_collections": total_collections,
                "total_pdfs": total_pdfs
            },
            "chromadb_stats": chroma_stats,
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "chroma_db_path": settings.CHROMA_DB_PATH
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get system stats: {str(e)}"
        }

async def reindex_collection_batch(db: Session, collection_id: int, batch_size: int = 10) -> Dict:
    """
    Re-index a collection by processing PDFs in batches for better performance and error handling.
    
    Args:
        db: SQLAlchemy database session
        collection_id: Database collection ID to re-index
        batch_size: Number of PDFs to process in each batch
        
    Returns:
        Dictionary with re-indexing results
    """
    try:
        # Step 1: Get collection info from database
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return {
                "success": False,
                "error": f"Collection with ID {collection_id} not found"
            }
        
        collection_name = collection.name
        collection_id_string = str(collection.id)
        
        logger.info(f"Starting batch re-indexing for collection '{collection_name}' (ID: {collection_id})")
        
        # Step 2: Clear existing ChromaDB data for this collection
        try:
            delete_collection_data_from_vector_store(
                chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
                filter_collection_id=collection_id_string
            )
            logger.info("Cleared existing ChromaDB data for collection")
        except Exception as e:
            logger.warning(f"Error clearing ChromaDB data: {str(e)} - continuing anyway")
        
        # Step 3: Get all PDFs in this collection
        pdfs = db.query(PDF).filter(PDF.collection_id == collection_id).all()
        
        if not pdfs:
            logger.info(f"No PDFs found in collection '{collection_name}'")
            return {
                "success": True,
                "message": f"Collection '{collection_name}' has no PDFs to re-index",
                "pdfs_processed": 0,
                "chunks_created": 0
            }
        
        total_pdfs = len(pdfs)
        total_chunks = 0
        processed_pdfs = 0
        errors = []
        
        logger.info(f"Processing {total_pdfs} PDFs in batches of {batch_size}")
        
        # Step 4: Process PDFs in batches
        for i in range(0, total_pdfs, batch_size):
            batch = pdfs[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_pdfs + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} PDFs)")
            
            batch_errors = []
            batch_chunks = 0
            
            for pdf in batch:
                try:
                    logger.info(f"Processing PDF: {pdf.filename}")
                    
                    # Check if file exists
                    if not os.path.exists(pdf.file_path):
                        error_msg = f"File not found: {pdf.file_path}"
                        logger.error(error_msg)
                        batch_errors.append(error_msg)
                        continue
                    
                    # Extract text from PDF
                    text_result = extract_text_from_pdf(pdf.file_path)
                    
                    if not text_result:
                        error_msg = f"No text extracted from {pdf.filename}"
                        logger.error(error_msg)
                        batch_errors.append(error_msg)
                        continue
                    
                    text_content, page_info = text_result
                    
                    if not text_content.strip():
                        error_msg = f"Empty text content from {pdf.filename}"
                        logger.warning(error_msg)
                        batch_errors.append(error_msg)
                        continue
                    
                    # Chunk the text
                    chunks = chunk_text(
                        text_content=text_content,
                        article_title=pdf.title or pdf.filename,
                        pdf_filename=pdf.filename,
                        collection_id=collection_id_string,
                        pdf_db_id=pdf.id,
                        page_info=page_info
                    )
                    
                    if not chunks:
                        error_msg = f"No chunks created from {pdf.filename}"
                        logger.error(error_msg)
                        batch_errors.append(error_msg)
                        continue
                    
                    # Generate embeddings
                    try:
                        chunks_with_embeddings = generate_embeddings_for_chunks(chunks)
                    except Exception as e:
                        error_msg = f"Embedding generation failed for {pdf.filename}: {str(e)}"
                        logger.error(error_msg)
                        batch_errors.append(error_msg)
                        continue
                    
                    # Add to ChromaDB
                    try:
                        add_chunks_to_vector_store(
                            chroma_collection_name=settings.CHROMA_DEFAULT_COLLECTION_NAME,
                            chunks_with_embeddings=chunks_with_embeddings
                        )
                    except Exception as e:
                        error_msg = f"ChromaDB storage failed for {pdf.filename}: {str(e)}"
                        logger.error(error_msg)
                        batch_errors.append(error_msg)
                        continue
                    
                    batch_chunks += len(chunks)
                    processed_pdfs += 1
                    
                    logger.info(f"Successfully processed {pdf.filename}: {len(chunks)} chunks")
                    
                except Exception as e:
                    error_msg = f"Unexpected error processing {pdf.filename}: {str(e)}"
                    logger.error(error_msg)
                    batch_errors.append(error_msg)
            
            total_chunks += batch_chunks
            errors.extend(batch_errors)
            
            logger.info(f"Batch {batch_num} completed: {batch_chunks} chunks, {len(batch_errors)} errors")
            
            # Small delay between batches to prevent overwhelming the system
            if batch_num < total_batches:
                import asyncio
                await asyncio.sleep(0.1)
        
        # Step 5: Update collection timestamp
        collection.updated_at = datetime.utcnow()
        db.commit()
        
        result = {
            "success": True,
            "collection_name": collection_name,
            "pdfs_processed": processed_pdfs,
            "total_pdfs": total_pdfs,
            "chunks_created": total_chunks,
            "errors": errors,
            "batch_size": batch_size
        }
        
        if errors:
            result["message"] = f"Re-indexing completed with {len(errors)} errors out of {total_pdfs} PDFs"
        else:
            result["message"] = "Re-indexing completed successfully"
        
        logger.info(f"Re-indexing completed for collection '{collection_name}': {processed_pdfs}/{total_pdfs} PDFs, {total_chunks} chunks, {len(errors)} errors")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during batch re-indexing: {str(e)}")
        return {
            "success": False,
            "error": f"Re-indexing failed: {str(e)}"
        }

# Placeholder for future admin API endpoints
async def clear_all_embeddings() -> Dict:
    """
    DANGEROUS: Clear all embeddings from ChromaDB.
    This is a placeholder for a future admin endpoint.
    """
    # This would be implemented when needed
    return {
        "success": False,
        "error": "Not implemented - placeholder function"
    }
