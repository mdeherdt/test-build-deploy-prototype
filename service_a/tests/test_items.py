import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from service_a.app.main import app
from service_a.app.db import Base, get_db
from service_a.app.models import Item

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
@pytest.fixture
def test_db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop the tables after the test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as c:
        yield c
    
    # Reset the dependency override
    app.dependency_overrides = {}

def test_create_item(client):
    """Test creating an item"""
    response = client.post("/items", json={"value": "test item"})
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "test item"
    assert "id" in data

def test_read_items(client, test_db):
    """Test reading all items"""
    # Add some test items
    test_db.add(Item(value="test item 1"))
    test_db.add(Item(value="test item 2"))
    test_db.commit()
    
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["value"] == "test item 1"
    assert data["items"][1]["value"] == "test item 2"

def test_read_item(client, test_db):
    """Test reading a specific item"""
    # Add a test item
    item = Item(value="test item")
    test_db.add(item)
    test_db.commit()
    
    response = client.get(f"/items/{item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "test item"
    assert data["id"] == item.id

def test_delete_item(client, test_db):
    """Test deleting an item"""
    # Add a test item
    item = Item(value="test item")
    test_db.add(item)
    test_db.commit()
    
    response = client.delete(f"/items/{item.id}")
    assert response.status_code == 204
    
    # Verify the item was deleted
    response = client.get(f"/items/{item.id}")
    assert response.status_code == 404

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}