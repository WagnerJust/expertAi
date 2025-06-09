#!/usr/bin/env python3
"""
Fix PDF file paths in the database.
This script updates existing PDF records to include the correct file paths.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/justin/LLMS/App/backend')

from app.db.session import get_db
from app.models.db_models import PDFDocument
from app.core.config import settings

def fix_pdf_paths():
    """Fix missing file paths in PDF records."""
    db = next(get_db())
    
    # Get all PDF records
    pdfs = db.query(PDFDocument).all()
    print(f"Found {len(pdfs)} PDF records")
    
    fixed_count = 0
    missing_files = []
    
    # The PDFs are mounted in Docker at /app/initial_corpus
    # But we need to check against the host path for verification
    host_corpus_dir = Path("/Users/justin/LLMS/Contexts/PromptEngineering/")
    container_corpus_dir = "/app/initial_corpus"
    
    for pdf in pdfs:
        if not pdf.file_path:
            # Check if file exists on host (for verification)
            host_path = host_corpus_dir / pdf.filename
            # Set container path for database
            container_path = f"{container_corpus_dir}/{pdf.filename}"
            
            if host_path.exists():
                pdf.file_path = container_path
                fixed_count += 1
                print(f"Fixed: {pdf.filename} -> {container_path}")
            else:
                missing_files.append(pdf.filename)
                print(f"Missing: {pdf.filename} (expected at {host_path})")
    
    # Commit changes
    if fixed_count > 0:
        db.commit()
        print(f"\nFixed {fixed_count} PDF file paths")
    
    if missing_files:
        print(f"\nWarning: {len(missing_files)} files not found:")
        for filename in missing_files[:10]:  # Show first 10
            print(f"  - {filename}")
        if len(missing_files) > 10:
            print(f"  ... and {len(missing_files) - 10} more")
    
    db.close()
    return fixed_count, len(missing_files)

if __name__ == "__main__":
    print("Fixing PDF file paths in database...")
    fixed, missing = fix_pdf_paths()
    print(f"\nSummary: Fixed {fixed} paths, {missing} files not found")
