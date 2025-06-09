#!/usr/bin/env python3
"""
Test script to verify single PDF processing works correctly.
This helps debug PDF processing issues before running full re-indexing.
"""

import os
import sys
from pathlib import Path

# Add the backend app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.pdf_ingestion_service import extract_text_from_pdf
from app.rag_components.chunker import chunk_text
from app.rag_components.embedder import generate_embeddings_for_chunks
from app.db.session import SessionLocal
from app.models.db_models import PDF
from sqlalchemy import desc

def test_single_pdf_processing():
    """Test processing a single PDF from the database."""
    db = SessionLocal()
    
    try:
        # Get the first PDF from the database
        pdf = db.query(PDF).order_by(desc(PDF.id)).first()
        
        if not pdf:
            print("No PDFs found in database")
            return False
            
        print(f"Testing PDF: {pdf.filename}")
        print(f"File path: {pdf.file_path}")
        
        # Check if file exists
        if not os.path.exists(pdf.file_path):
            print(f"ERROR: File not found at {pdf.file_path}")
            return False
            
        print("✓ File exists")
        
        # Step 1: Extract text
        print("Testing text extraction...")
        result = extract_text_from_pdf(Path(pdf.file_path))
        
        if not result:
            print("ERROR: Text extraction failed")
            return False
            
        text_content, page_info = result
        print(f"✓ Extracted {len(text_content)} characters from {len(page_info)} pages")
        print(f"First 200 chars: {text_content[:200]}...")
        
        # Step 2: Test chunking
        print("Testing chunking...")
        chunks = chunk_text(
            text_content=text_content,
            article_title=pdf.title or pdf.filename,
            pdf_filename=pdf.filename,
            collection_id=str(pdf.collection_id),
            pdf_db_id=pdf.id,
            page_info=page_info
        )
        
        if not chunks:
            print("ERROR: Chunking failed")
            return False
            
        print(f"✓ Created {len(chunks)} chunks")
        
        # Step 3: Test embedding generation (just first chunk)
        print("Testing embedding generation...")
        test_chunks = chunks[:1]  # Test with just one chunk
        chunks_with_embeddings = generate_embeddings_for_chunks(test_chunks)
        
        if not chunks_with_embeddings:
            print("ERROR: Embedding generation failed")
            return False
            
        print(f"✓ Generated embeddings for test chunk")
        print(f"Embedding dimensions: {len(chunks_with_embeddings[0].embedding)}")
        
        print("\n🎉 All PDF processing steps successful!")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_single_pdf_processing()
    sys.exit(0 if success else 1)
