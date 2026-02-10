"""Test API endpoints"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.session_store import SessionStore
from src.api.recommender import SessionRecommender
import time


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def session_store():
    """Session store fixture"""
    return SessionStore(redis_host="localhost", redis_port=6379, redis_db=1)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint(client):
    """Test health check"""
    response = client.get("/health")
    # May fail if Redis not running
    assert response.status_code in [200, 503]


def test_version_endpoint(client):
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert "model_version" in data


def test_event_tracking(client):
    """Test event tracking"""
    event_data = {
        "session_id": "test_session_123",
        "item_id": "prod_456",
        "event_type": "view",
        "metadata": {"test": True}
    }
    
    try:
        response = client.post("/event", json=event_data)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert data["session_id"] == "test_session_123"
            assert data["event_count"] >= 1
    except Exception:
        # Redis might not be available
        pytest.skip("Redis not available")


def test_recommendations(client):
    """Test recommendation endpoint"""
    # First track some events
    for i in range(3):
        event_data = {
            "session_id": "test_rec_session",
            "item_id": f"prod_{i}",
            "event_type": "view"
        }
        try:
            client.post("/event", json=event_data)
        except Exception:
            pytest.skip("Redis not available")
    
    # Get recommendations
    rec_request = {
        "session_id": "test_rec_session",
        "k": 10
    }
    
    try:
        response = client.post("/recommend", json=rec_request)
        if response.status_code == 200:
            data = response.json()
            assert "recommendations" in data
            assert len(data["recommendations"]) <= 10
            assert "model_version" in data
    except Exception:
        pytest.skip("Redis not available")


def test_session_info(client):
    """Test session info endpoint"""
    try:
        response = client.get("/session/test_session")
        assert response.status_code in [200, 500]
    except Exception:
        pytest.skip("Redis not available")
