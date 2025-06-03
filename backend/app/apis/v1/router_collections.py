from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...models import schemas
from ...db.session import get_db
from ...services import collection_service
from typing import List

router = APIRouter(prefix="/collections", tags=["collections"])

@router.post("/", response_model=schemas.Collection, status_code=status.HTTP_201_CREATED)
def create_collection(collection: schemas.CollectionCreate, db: Session = Depends(get_db)):
    db_collection = collection_service.create_collection(db, collection)
    return db_collection

@router.get("/", response_model=List[schemas.Collection])
def list_collections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return collection_service.get_collections(db, skip=skip, limit=limit)

@router.get("/{collection_id}", response_model=schemas.Collection)
def get_collection(collection_id: int, db: Session = Depends(get_db)):
    db_collection = collection_service.get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return db_collection

@router.put("/{collection_id}", response_model=schemas.Collection)
def update_collection(collection_id: int, collection_update: schemas.CollectionUpdate, db: Session = Depends(get_db)):
    db_collection = collection_service.update_collection(db, collection_id, collection_update)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found or update failed")
    return db_collection

@router.delete("/{collection_id}", response_model=schemas.Collection)
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    db_collection = collection_service.delete_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found or cannot be deleted (PDFs exist)")
    return db_collection
