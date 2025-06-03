import os
import sqlite3
import pytest
from app.core.config import settings
import tempfile
import shutil
import importlib
from app.db import session as db_session

def test_db_tables_exist(tmp_path, monkeypatch):
    # Use a temp DB path
    db_path = tmp_path / "test_db.sqlite"
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{db_path}")
    # Re-import and init DB
    importlib.reload(db_session)
    db_session.init_db()
    assert os.path.exists(db_path), f"Database file {db_path} does not exist."
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check for required tables
    for table in ["collections", "pdf_documents"]:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        assert cursor.fetchone(), f"Table '{table}' does not exist in the database."
    conn.close()
