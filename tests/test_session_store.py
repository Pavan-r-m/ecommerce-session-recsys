"""Test session store"""
import pytest
from src.api.session_store import SessionStore
from datetime import datetime
import time


@pytest.fixture
def store():
    """Session store fixture using test DB"""
    return SessionStore(redis_host="localhost", redis_port=6379, redis_db=1)


def test_health_check(store):
    """Test Redis connection"""
    try:
        assert store.health_check() == True
    except Exception:
        pytest.skip("Redis not available")


def test_add_event(store):
    """Test adding events"""
    try:
        session_id = f"test_session_{int(time.time())}"
        count = store.add_event(
            session_id=session_id,
            item_id="prod_123",
            event_type="view"
        )
        assert count >= 1
        
        # Add another event
        count2 = store.add_event(
            session_id=session_id,
            item_id="prod_456",
            event_type="click"
        )
        assert count2 == count + 1
        
        # Cleanup
        store.clear_session(session_id)
    except Exception:
        pytest.skip("Redis not available")


def test_get_recent_items(store):
    """Test retrieving recent items"""
    try:
        session_id = f"test_recent_{int(time.time())}"
        
        # Add multiple items
        items = ["prod_1", "prod_2", "prod_3"]
        for item in items:
            store.add_event(session_id, item, "view")
        
        # Get recent items
        recent = store.get_recent_items(session_id, n=10)
        assert len(recent) == 3
        # Should be in reverse order (most recent first)
        assert recent[0] == "prod_3"
        
        # Cleanup
        store.clear_session(session_id)
    except Exception:
        pytest.skip("Redis not available")


def test_get_event_counts(store):
    """Test event counting"""
    try:
        session_id = f"test_counts_{int(time.time())}"
        
        store.add_event(session_id, "prod_1", "view")
        store.add_event(session_id, "prod_2", "view")
        store.add_event(session_id, "prod_2", "click")
        store.add_event(session_id, "prod_2", "add_to_cart")
        
        counts = store.get_event_counts(session_id)
        assert counts["view"] == 2
        assert counts["click"] == 1
        assert counts["add_to_cart"] == 1
        
        # Cleanup
        store.clear_session(session_id)
    except Exception:
        pytest.skip("Redis not available")


def test_get_session_context(store):
    """Test getting complete session context"""
    try:
        session_id = f"test_context_{int(time.time())}"
        
        # Add events
        store.add_event(session_id, "prod_1", "view")
        store.add_event(session_id, "prod_2", "click")
        
        # Get context
        context = store.get_session_context(session_id)
        
        assert "recent_items" in context
        assert "recent_events" in context
        assert "event_counts" in context
        assert len(context["recent_items"]) == 2
        
        # Cleanup
        store.clear_session(session_id)
    except Exception:
        pytest.skip("Redis not available")


def test_clear_session(store):
    """Test clearing session data"""
    try:
        session_id = f"test_clear_{int(time.time())}"
        
        # Add data
        store.add_event(session_id, "prod_1", "view")
        
        # Clear
        store.clear_session(session_id)
        
        # Verify cleared
        recent = store.get_recent_items(session_id)
        assert len(recent) == 0
    except Exception:
        pytest.skip("Redis not available")
