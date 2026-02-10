from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class EventRequest(BaseModel):
    """Event tracking request"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    item_id: str = Field(..., description="Product/item identifier")
    event_type: Literal["view", "click", "add_to_cart", "purchase"] = Field(
        ..., description="Type of user interaction"
    )
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional event data")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_123abc",
                "user_id": "user_456",
                "item_id": "prod_789",
                "event_type": "view",
                "timestamp": "2026-02-09T12:00:00Z",
                "metadata": {"category": "electronics", "price": 299.99}
            }
        }


class EventResponse(BaseModel):
    """Event tracking response"""
    status: str
    session_id: str
    event_count: int


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    item_id: str
    score: float
    reason: str
    rank: int


class RecommendationRequest(BaseModel):
    """Recommendation request"""
    session_id: str = Field(..., description="Session identifier")
    k: int = Field(default=20, ge=1, le=100, description="Number of recommendations")
    exclude_items: Optional[List[str]] = Field(
        default_factory=list, description="Items to exclude from recommendations"
    )


class RecommendationResponse(BaseModel):
    """Recommendation response"""
    session_id: str
    recommendations: List[RecommendationItem]
    model_version: str
    latency_ms: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model_version: str
    timestamp: datetime


class VersionResponse(BaseModel):
    """Version information"""
    api_version: str
    model_version: str
    model_trained_at: Optional[str]
    features_count: int
