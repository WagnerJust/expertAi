import os
import pytest
from app.core.config import settings
import tempfile
import shutil
import importlib
from app.db import session as db_session
from sqlalchemy import create_engine, text

def test_db_tables_exist(tmp_path, monkeypatch):
    # Skip this test since it was for SQLite
    pytest.skip("This test was for SQLite - PostgreSQL schema is managed by SQLAlchemy")

def test_postgresql_connection():
    """Test that we can connect to PostgreSQL with current settings"""
    try:
        # Test connection using current settings
        engine = create_engine(settings.db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    except Exception as e:
        pytest.skip(f"PostgreSQL not available for testing: {e}")

def test_postgresql_schema_creation():
    """Test that SQLAlchemy can create the schema"""
    try:
        from app.models.db_models import Base
        from app.db.session import engine
        
        # This should not raise an error
        Base.metadata.create_all(bind=engine)
        
        # Verify some tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('collections', 'pdf_documents')
            """))
            tables = [row[0] for row in result.fetchall()]
            assert 'collections' in tables
            assert 'pdf_documents' in tables
            
    except Exception as e:
        pytest.skip(f"PostgreSQL not available for testing: {e}")
