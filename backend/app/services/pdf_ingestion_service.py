import os
from pathlib import Path
from fastapi import UploadFile
import httpx
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models import db_models
from typing import Optional
import fitz  # PyMuPDF

def store_uploaded_pdf(collection_id: int, pdf_file: UploadFile) -> Path:
    base_path = Path(settings.pdf_dir) / str(collection_id)
    base_path.mkdir(parents=True, exist_ok=True)
    file_path = base_path / pdf_file.filename
    with open(file_path, "wb") as f:
        f.write(pdf_file.file.read())
    return file_path

def download_pdf_from_url(collection_id: int, url: str, filename: str) -> Optional[Path]:
    base_path = Path(settings.pdf_dir) / str(collection_id)
    base_path.mkdir(parents=True, exist_ok=True)
    file_path = base_path / filename
    try:
        with httpx.stream("GET", url, timeout=10.0) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
        return file_path
    except Exception:
        return None

def add_pdf_record_to_db(db: Session, title: str, filename: str, file_path: str, collection_id: int, status: str = "pending") -> db_models.PDFDocument:
    pdf_doc = db_models.PDFDocument(
        title=title,
        filename=filename,
        status=status,
        collection_id=collection_id
    )
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    return pdf_doc

def extract_text_from_pdf(pdf_path: Path) -> Optional[tuple[str, int]]:
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        page_count = doc.page_count
        doc.close()
        return text, page_count
    except Exception:
        return None

def filename_to_title(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    return name.replace('_', ' ').replace('-', ' ').title()
