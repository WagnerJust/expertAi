from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ...models import schemas
from ...db.session import get_db
from ...services import pdf_ingestion_service, collection_service
from typing import List

router = APIRouter(prefix="/collections", tags=["pdfs"])

@router.post("/{collection_id}/pdfs/upload", status_code=status.HTTP_201_CREATED)
def upload_pdf(collection_id: int, pdf_file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check collection exists
    if not collection_service.get_collection(db, collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    file_path = pdf_ingestion_service.store_uploaded_pdf(collection_id, pdf_file)
    title = pdf_ingestion_service.filename_to_title(pdf_file.filename)
    pdf_doc = pdf_ingestion_service.add_pdf_record_to_db(db, title, pdf_file.filename, str(file_path), collection_id)
    return {"id": pdf_doc.id, "filename": pdf_doc.filename, "title": pdf_doc.title, "status": pdf_doc.status}

@router.post("/{collection_id}/pdfs/url", status_code=status.HTTP_201_CREATED)
def add_pdf_by_url(collection_id: int, url: str, filename: str, db: Session = Depends(get_db)):
    if not collection_service.get_collection(db, collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    file_path = pdf_ingestion_service.download_pdf_from_url(collection_id, url, filename)
    if not file_path:
        raise HTTPException(status_code=400, detail="Failed to download PDF from URL")
    title = pdf_ingestion_service.filename_to_title(filename)
    pdf_doc = pdf_ingestion_service.add_pdf_record_to_db(db, title, filename, str(file_path), collection_id)
    return {"id": pdf_doc.id, "filename": pdf_doc.filename, "title": pdf_doc.title, "status": pdf_doc.status}

@router.get("/{collection_id}/pdfs", response_model=List[schemas.PDFDocument])
def list_pdfs(collection_id: int, db: Session = Depends(get_db)):
    if not collection_service.get_collection(db, collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    return db.query(pdf_ingestion_service.db_models.PDFDocument).filter_by(collection_id=collection_id).all()

@router.delete("/pdfs/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
    pdf = db.query(pdf_ingestion_service.db_models.PDFDocument).filter_by(id=pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    db.delete(pdf)
    db.commit()
    return

__all__ = ["router"]
