"""Session state management with Redis"""
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import redis
from loguru import logger


class SessionStore:
    """Manages session state in Redis"""
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        ttl_hours: int = 24
    ):
        self.client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.ttl_seconds = ttl_hours * 3600
        
    def add_event(
        self,
        session_id: str,
        item_id: str,
        event_type: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ) -> int:
        """Add event to session and return total event count"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        event = {
            "item_id": item_id,
            "event_type": event_type,
            "timestamp": timestamp.isoformat(),
            "metadata": metadata or {}
        }
        
        # Store event in sorted set (scored by timestamp)
        key = f"session:{session_id}:events"
        score = timestamp.timestamp()
        
        self.client.zadd(key, {json.dumps(event): score})
        self.client.expire(key, self.ttl_seconds)
        
        # Also maintain recent items list (for quick access)
        items_key = f"session:{session_id}:items"
        self.client.lpush(items_key, item_id)
        self.client.ltrim(items_key, 0, 99)  # Keep last 100 items
        self.client.expire(items_key, self.ttl_seconds)
        
        # Update event type counters
        counter_key = f"session:{session_id}:counters"
        self.client.hincrby(counter_key, event_type, 1)
        self.client.expire(counter_key, self.ttl_seconds)
        
        return self.client.zcard(key)
    
    def get_recent_items(self, session_id: str, n: int = 20) -> List[str]:
        """Get N most recent items in session"""
        key = f"session:{session_id}:items"
        items = self.client.lrange(key, 0, n - 1)
        return items
    
    def get_session_events(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get recent session events"""
        key = f"session:{session_id}:events"
        events_raw = self.client.zrevrange(key, 0, limit - 1)
        
        events = []
        for event_str in events_raw:
            try:
                events.append(json.loads(event_str))
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse event: {event_str}")
                
        return events
    
    def get_event_counts(self, session_id: str) -> Dict[str, int]:
        """Get event type counts for session"""
        key = f"session:{session_id}:counters"
        counters = self.client.hgetall(key)
        return {k: int(v) for k, v in counters.items()}
    
    def get_session_context(self, session_id: str) -> Dict:
        """Get complete session context for recommendation"""
        return {
            "recent_items": self.get_recent_items(session_id, n=20),
            "recent_events": self.get_session_events(session_id, limit=50),
            "event_counts": self.get_event_counts(session_id)
        }
    
    def clear_session(self, session_id: str):
        """Clear all session data"""
        keys_to_delete = [
            f"session:{session_id}:events",
            f"session:{session_id}:items",
            f"session:{session_id}:counters"
        ]
        self.client.delete(*keys_to_delete)
    
    def health_check(self) -> bool:
        """Check if Redis is accessible"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
