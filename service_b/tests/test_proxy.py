import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from service_b.app.main import app

# Create a test client
client = TestClient(app)

@pytest.fixture
def mock_get_items():
    """Fixture to mock the get_items function"""
    with patch("service_b.app.client.get_items") as mock:
        # Create a mock response
        mock.return_value = AsyncMock(return_value={"items": [
            {"id": 1, "value": "test item 1"},
            {"id": 2, "value": "test item 2"}
        ]})
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
    with patch("service_b.app.client.get_items") as mock:
        mock.return_value = AsyncMock(side_effect=Exception("Service A is down"))
        yield mock

def test_proxy_items_error(mock_get_items_error):
    """Test the proxy-items endpoint when Service A is down"""
    response = client.get("/proxy-items")
    assert response.status_code == 503
    assert "Error communicating with Service A" in response.json()["detail"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}