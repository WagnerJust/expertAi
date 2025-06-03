import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("app.services.collection_service.get_collection")
@patch("app.services.pdf_ingestion_service.store_uploaded_pdf")
@patch("app.services.pdf_ingestion_service.filename_to_title")
@patch("app.services.pdf_ingestion_service.add_pdf_record_to_db")
def test_upload_pdf_api(mock_add, mock_title, mock_store, mock_get):
    mock_get.return_value = True
    mock_store.return_value = "/tmp/test.pdf"
    mock_title.return_value = "Test Title"
    mock_add.return_value = MagicMock(id=1, filename="test.pdf", title="Test Title", status="pending")
    response = client.post("/collections/1/pdfs/upload", files={"pdf_file": ("test.pdf", b"PDFDATA", "application/pdf")})
    assert response.status_code == 201
    assert response.json()["filename"] == "test.pdf"

@patch("app.services.collection_service.get_collection")
@patch("app.services.pdf_ingestion_service.download_pdf_from_url")
@patch("app.services.pdf_ingestion_service.filename_to_title")
@patch("app.services.pdf_ingestion_service.add_pdf_record_to_db")
def test_add_pdf_by_url_api(mock_add, mock_title, mock_download, mock_get):
    mock_get.return_value = True
    mock_download.return_value = "/tmp/test.pdf"
    mock_title.return_value = "Test Title"
    mock_add.return_value = MagicMock(id=2, filename="test.pdf", title="Test Title", status="pending")
    response = client.post("/collections/1/pdfs/url?url=http://example.com/test.pdf&filename=test.pdf")
    assert response.status_code == 201
    assert response.json()["filename"] == "test.pdf"

@patch("app.services.collection_service.get_collection")
def test_upload_pdf_api_collection_not_found(mock_get):
    mock_get.return_value = False
    response = client.post("/collections/999/pdfs/upload", files={"pdf_file": ("test.pdf", b"PDFDATA", "application/pdf")})
    assert response.status_code == 404

@patch("app.services.collection_service.get_collection")
def test_add_pdf_by_url_api_collection_not_found(mock_get):
    mock_get.return_value = False
    response = client.post("/collections/999/pdfs/url?url=http://example.com/test.pdf&filename=test.pdf")
    assert response.status_code == 404
