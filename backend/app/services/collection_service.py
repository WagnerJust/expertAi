# Service for managing Collection CRUD operations
from sqlalchemy.orm import Session
from ..models import db_models, schemas
from typing import List, Optional

# Create a new collection
def create_collection(db: Session, collection: schemas.CollectionCreate) -> db_models.Collection:
    db_collection = db_models.Collection(name=collection.name)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

# Get a collection by ID
def get_collection(db: Session, collection_id: int) -> Optional[db_models.Collection]:
    return db.query(db_models.Collection).filter(db_models.Collection.id == collection_id).first()

# List collections with pagination
def get_collections(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.Collection]:
    return db.query(db_models.Collection).offset(skip).limit(limit).all()

# Update a collection (partial update)
def update_collection(db: Session, collection_id: int, collection_update: schemas.CollectionUpdate) -> Optional[db_models.Collection]:
    db_collection = db.query(db_models.Collection).filter(db_models.Collection.id == collection_id).first()
    if not db_collection:
        return None
    if collection_update.name is not None:
        db_collection.name = collection_update.name
    db.commit()
    db.refresh(db_collection)
    return db_collection

# Delete a collection (prevent deletion if PDFs exist)
def delete_collection(db: Session, collection_id: int) -> Optional[db_models.Collection]:
    db_collection = db.query(db_models.Collection).filter(db_models.Collection.id == collection_id).first()
    if not db_collection:
        return None
    if db_collection.pdfs and len(db_collection.pdfs) > 0:
        # Prevent deletion if PDFs exist
        return None
    db.delete(db_collection)
    db.commit()
    return db_collection
