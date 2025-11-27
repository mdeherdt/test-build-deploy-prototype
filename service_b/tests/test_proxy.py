import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
import os
import httpx

# Add the parent directory to sys.path to allow imports from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# Create a test client
client = TestClient(app)

@pytest.fixture
def mock_get_items():
    """Fixture to mock the get_items function"""
    async def mock_get_items_impl():
        return {"items": [
            {"id": 1, "value": "test item 1"},
            {"id": 2, "value": "test item 2"}
        ]}

    with patch("app.client.get_items", mock_get_items_impl) as mock:
        yield mock

@pytest.fixture
def mock_get_item():
    """Fixture to mock the get_item function"""
    async def mock_get_item_impl(item_id):
        if item_id == 1:
            return {"id": 1, "value": "test item 1"}
        elif item_id == 2:
            return {"id": 2, "value": "test item 2"}
        else:
            raise httpx.HTTPStatusError(
                "Item not found",
                request=httpx.Request("GET", f"http://service-a/items/{item_id}"),
                response=httpx.Response(404, request=httpx.Request("GET", f"http://service-a/items/{item_id}"))
            )

    with patch("app.client.get_item", mock_get_item_impl) as mock:
        yield mock

@pytest.fixture
def mock_search_items():
    """Fixture to mock the search_items function"""
    async def mock_search_items_impl(query):
        if query == "test":
            return {"items": [
                {"id": 1, "value": "test item 1"},
                {"id": 2, "value": "test item 2"}
            ]}
        elif query == "item 1":
            return {"items": [
                {"id": 1, "value": "test item 1"}
            ]}
        else:
            return {"items": []}

    with patch("app.client.search_items", mock_search_items_impl) as mock:
        yield mock

@pytest.fixture
def mock_count_items():
    """Fixture to mock the count_items function"""
    async def mock_count_items_impl():
        return 2

    with patch("app.client.count_items", mock_count_items_impl) as mock:
        yield mock

def test_proxy_items(mock_get_items):
    """Test the proxy-items endpoint"""
    response = client.get("/proxy-items")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2

    # Check that the transformation was applied (source field added)
    assert data["items"][0]["source"] == "service_a"
    assert data["items"][1]["source"] == "service_a"

    # Check that the original data is preserved
    assert data["items"][0]["id"] == 1
    assert data["items"][0]["value"] == "test item 1"
    assert data["items"][1]["id"] == 2
    assert data["items"][1]["value"] == "test item 2"

@pytest.fixture
def mock_get_items_error():
    """Fixture to mock the get_items function with an error"""
    async def mock_get_items_error_impl():
        raise Exception("Service A is down")

    with patch("app.client.get_items", mock_get_items_error_impl) as mock:
        yield mock

def test_proxy_items_error(mock_get_items_error):
    """Test the proxy-items endpoint when Service A is down"""
    response = client.get("/proxy-items")
    assert response.status_code == 503
    assert "Error communicating with Service A" in response.json()["detail"]

def test_proxy_item(mock_get_item):
    """Test the proxy-item endpoint"""
    # Test getting an existing item
    response = client.get("/proxy-items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["value"] == "test item 1"
    assert data["source"] == "service_a"

    # Test getting a non-existent item
    response = client.get("/proxy-items/999")
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]

def test_proxy_search_items(mock_search_items):
    """Test the proxy-items/search endpoint"""
    # Test searching for "test"
    response = client.get("/proxy-items/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["source"] == "service_a"
    assert data["items"][1]["source"] == "service_a"

    # Test searching for "item 1"
    response = client.get("/proxy-items/search?q=item%201")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == 1
    assert data["items"][0]["value"] == "test item 1"
    assert data["items"][0]["source"] == "service_a"

    # Test searching for something that doesn't exist
    response = client.get("/proxy-items/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0

def test_proxy_count_items(mock_count_items):
    """Test the proxy-items/count endpoint"""
    response = client.get("/proxy-items/count")
    assert response.status_code == 200
    count = response.json()
    assert count == 2

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
