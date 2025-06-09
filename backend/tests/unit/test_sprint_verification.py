#!/usr/bin/env python3
"""
Sprint 1 & 2 Verification Test
Tests the acceptance criteria for Sprints 1 and 2
"""

import sys
import os
import tempfile
from pathlib import Path

# Add backend to path
sys.path.append('/Users/justin/LLMS/App/backend')

def test_schemas():
    """Test Pydantic schemas"""
    print("Testing Pydantic Schemas...")
    
    from app.models import schemas
    
    # Test CollectionCreate schema
    collection_data = schemas.CollectionCreate(
        name="Test Collection",
        description="A test collection"
    )
    assert collection_data.name == "Test Collection"
    assert collection_data.description == "A test collection"
    print("✓ CollectionCreate schema works")
    
    # Test PDFDocumentBase schema
    pdf_data = schemas.PDFDocumentBase(
        filename="test.pdf",
        title="Test PDF"
    )
    assert pdf_data.filename == "test.pdf"
    assert pdf_data.title == "Test PDF"
    print("✓ PDFDocumentBase schema works")
    
    return True

def test_database_models():
    """Test database models"""
    print("Testing Database Models...")
    
    from app.models import db_models
    
    # Test that models are properly defined
    assert hasattr(db_models, 'Collection')
    assert hasattr(db_models, 'PDFDocument')
    assert hasattr(db_models, 'QueryHistory')
    assert hasattr(db_models, 'Answer')
    assert hasattr(db_models, 'AnswerFeedback')
    print("✓ All database models exist")
    
    return True

def test_pdf_filename_conversion():
    """Test PDF filename to title conversion"""
    print("Testing PDF filename conversion...")
    
    from app.services import pdf_ingestion_service
    
    # Test filename to title conversion
    assert pdf_ingestion_service.filename_to_title("My_Document-Name.pdf") == "My Document Name"
    assert pdf_ingestion_service.filename_to_title("another_test_file.pdf") == "Another Test File"
    print("✓ Filename to title conversion works")
    
    return True

def test_configuration():
    """Test configuration settings"""
    print("Testing Configuration...")
    
    from app.core.config import settings
    
    # Test that all required settings exist
    assert hasattr(settings, 'pdf_dir')
    assert hasattr(settings, 'db_url')
    assert hasattr(settings, 'postgres_db')
    assert hasattr(settings, 'postgres_user')
    assert hasattr(settings, 'postgres_password')
    assert hasattr(settings, 'CHROMA_DB_PATH')
    assert hasattr(settings, 'LLM_SERVICE_URL')
    print("✓ Configuration settings are properly defined")
    
    return True

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("SPRINT 1 & 2 ACCEPTANCE CRITERIA VERIFICATION")
    print("=" * 60)
    
    try:
        test_schemas()
        print()
        
        test_database_models()
        print()
        
        test_pdf_filename_conversion()
        print()
        
        test_configuration()
        print()
        
        print("=" * 60)
        print("✅ ALL SPRINT 1 & 2 VERIFICATION TESTS PASSED!")
        print("Core backend functionality is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
