import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import schemas
from unittest.mock import patch

client = TestClient(app)

@patch("app.services.collection_service.create_collection")
def test_create_collection_api(mock_create):
    mock_create.return_value = schemas.Collection(id=1, name="Test", created_at="2025-06-02T00:00:00Z")
    response = client.post("/collections/", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"

@patch("app.services.collection_service.get_collections")
def test_list_collections_api(mock_list):
    mock_list.return_value = [schemas.Collection(id=1, name="Test", created_at="2025-06-02T00:00:00Z")]
    response = client.get("/collections/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("app.services.collection_service.get_collection")
def test_get_collection_api_found(mock_get):
    mock_get.return_value = schemas.Collection(id=1, name="Test", created_at="2025-06-02T00:00:00Z")
    response = client.get("/collections/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

@patch("app.services.collection_service.get_collection")
def test_get_collection_api_not_found(mock_get):
    mock_get.return_value = None
    response = client.get("/collections/999")
    assert response.status_code == 404

@patch("app.services.collection_service.update_collection")
def test_update_collection_api(mock_update):
    mock_update.return_value = schemas.Collection(id=1, name="Renamed", created_at="2025-06-02T00:00:00Z")
    response = client.put("/collections/1", json={"name": "Renamed"})
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"

@patch("app.services.collection_service.update_collection")
def test_update_collection_api_not_found(mock_update):
    mock_update.return_value = None
    response = client.put("/collections/999", json={"name": "Renamed"})
    assert response.status_code == 404

@patch("app.services.collection_service.delete_collection")
def test_delete_collection_api(mock_delete):
    mock_delete.return_value = schemas.Collection(id=1, name="Test", created_at="2025-06-02T00:00:00Z")
    response = client.delete("/collections/1")
    assert response.status_code == 200

@patch("app.services.collection_service.delete_collection")
def test_delete_collection_api_not_found(mock_delete):
    mock_delete.return_value = None
    response = client.delete("/collections/999")
    assert response.status_code == 404
