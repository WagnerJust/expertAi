import io
import pytest
from unittest.mock import MagicMock, patch
from app.services import pdf_ingestion_service
from app.models import db_models
from fastapi import UploadFile

class DummyUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = io.BytesIO(content)

def test_store_uploaded_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_ingestion_service.settings, "pdf_dir", str(tmp_path))
    upload = DummyUploadFile("test.pdf", b"PDFDATA")
    path = pdf_ingestion_service.store_uploaded_pdf(1, upload)
    assert path.exists()
    assert path.read_bytes() == b"PDFDATA"

def test_store_uploaded_pdf_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_ingestion_service.settings, "pdf_dir", str(tmp_path))
    upload = DummyUploadFile("test.pdf", b"")
    with pytest.raises(ValueError, match="Empty file provided"):
        pdf_ingestion_service.store_uploaded_pdf(1, upload)

def test_download_pdf_from_url_success(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_ingestion_service.settings, "pdf_dir", str(tmp_path))
    with patch("httpx.stream") as mock_stream:
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.iter_bytes.return_value = [b"PDFDATA"]
        mock_resp.raise_for_status.return_value = None
        mock_stream.return_value = mock_resp
        path = pdf_ingestion_service.download_pdf_from_url(1, "http://example.com/test.pdf", "test.pdf")
        assert path.exists()
        assert path.read_bytes() == b"PDFDATA"

def test_download_pdf_from_url_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_ingestion_service.settings, "pdf_dir", str(tmp_path))
    with patch("httpx.stream", side_effect=Exception("fail")):
        path = pdf_ingestion_service.download_pdf_from_url(1, "badurl", "fail.pdf")
        assert path is None

def test_add_pdf_record_to_db():
    db = MagicMock()
    db_models.PDFDocument.return_value = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = pdf_ingestion_service.add_pdf_record_to_db(db, "title", "file.pdf", "/path/file.pdf", 1)
    db.add.assert_called()
    db.commit.assert_called()
    db.refresh.assert_called()
    assert result is not None

def test_extract_text_from_pdf(tmp_path):
    import fitz
    # Create a simple PDF
    pdf_path = tmp_path / "simple.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello World!")
    doc.save(str(pdf_path))
    doc.close()
    result = pdf_ingestion_service.extract_text_from_pdf(pdf_path)
    assert result is not None
    text, page_info = result
    assert "Hello World!" in text
    assert isinstance(page_info, dict)

def test_extract_text_from_pdf_error(tmp_path):
    # Pass a non-PDF file
    bad_path = tmp_path / "bad.pdf"
    bad_path.write_bytes(b"not a pdf")
    result = pdf_ingestion_service.extract_text_from_pdf(bad_path)
    assert result is None

def test_filename_to_title():
    assert pdf_ingestion_service.filename_to_title("My_Document-Name.pdf") == "My Document Name"
