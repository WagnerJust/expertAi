import pytest
from unittest.mock import MagicMock
from app.services import collection_service
from app.models import schemas, db_models

def test_create_collection():
    db = MagicMock()
    collection_in = schemas.CollectionCreate(name="Test Collection")
    db_models.Collection.return_value = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = collection_service.create_collection(db, collection_in)
    db.add.assert_called()
    db.commit.assert_called()
    db.refresh.assert_called()
    assert result is not None

def test_get_collection_found():
    db = MagicMock()
    db.query().filter().first.return_value = "collection_obj"
    result = collection_service.get_collection(db, 1)
    assert result == "collection_obj"

def test_get_collection_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    result = collection_service.get_collection(db, 1)
    assert result is None

def test_get_collections():
    db = MagicMock()
    db.query().offset().limit().all.return_value = ["c1", "c2"]
    result = collection_service.get_collections(db)
    assert result == ["c1", "c2"]

def test_update_collection_found():
    db = MagicMock()
    db_collection = MagicMock()
    db.query().filter().first.return_value = db_collection
    update = schemas.CollectionUpdate(name="New Name")
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = collection_service.update_collection(db, 1, update)
    db.commit.assert_called()
    db.refresh.assert_called()
    assert db_collection.name == "New Name"
    assert result == db_collection

def test_update_collection_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    update = schemas.CollectionUpdate(name="New Name")
    result = collection_service.update_collection(db, 1, update)
    assert result is None

def test_delete_collection_found_and_no_pdfs():
    db = MagicMock()
    db_collection = MagicMock()
    db_collection.pdfs = []
    db.query().filter().first.return_value = db_collection
    db.delete = MagicMock()
    db.commit = MagicMock()
    result = collection_service.delete_collection(db, 1)
    db.delete.assert_called_with(db_collection)
    db.commit.assert_called()
    assert result == db_collection

def test_delete_collection_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    result = collection_service.delete_collection(db, 1)
    assert result is None

def test_delete_collection_with_pdfs():
    db = MagicMock()
    db_collection = MagicMock()
    db_collection.pdfs = ["pdf1"]
    db.query().filter().first.return_value = db_collection
    result = collection_service.delete_collection(db, 1)
    assert result is None
