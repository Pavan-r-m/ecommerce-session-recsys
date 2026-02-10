"""FastAPI application - Session-based Recommendation API"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from loguru import logger
import time
import os

from .schemas import (
    EventRequest,
    EventResponse,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationItem,
    HealthResponse,
    VersionResponse
)
from .session_store import SessionStore
from .recommender import SessionRecommender

# Configuration
API_VERSION = "0.1.0"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
ARTIFACTS_PATH = os.getenv("ARTIFACTS_PATH", "src/artifacts")

# Global state
session_store: SessionStore = None
recommender: SessionRecommender = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    global session_store, recommender
    
    logger.info("Starting up recommendation API...")
    
    # Initialize session store
    session_store = SessionStore(
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT
    )
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    
    # Initialize recommender
    recommender = SessionRecommender(artifacts_path=ARTIFACTS_PATH)
    logger.info(f"Loaded recommender, model version: {recommender.model_version}")
    
    yield
    
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="E-Commerce Session-Based Recommender API",
    description="Real-time product recommendations based on user session behavior",
    version=API_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "E-Commerce Recommendation API",
        "version": API_VERSION,
        "endpoints": {
            "health": "/health",
            "version": "/version",
            "event": "POST /event",
            "recommend": "GET /recommend"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    redis_healthy = session_store.health_check() if session_store else False
    
    if not redis_healthy:
        raise HTTPException(status_code=503, detail="Redis not accessible")
    
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        model_version=recommender.model_version if recommender else "unknown",
        timestamp=datetime.utcnow()
    )


@app.get("/version", response_model=VersionResponse, tags=["Health"])
async def get_version():
    """Get version information"""
    feature_config = recommender.feature_config if recommender else {}
    
    return VersionResponse(
        api_version=API_VERSION,
        model_version=recommender.model_version if recommender else "unknown",
        model_trained_at=feature_config.get("trained_at"),
        features_count=feature_config.get("features_count", 0)
    )


@app.post("/event", response_model=EventResponse, tags=["Events"])
async def track_event(event: EventRequest):
    """Track user interaction event"""
    try:
        timestamp = event.timestamp or datetime.utcnow()
        
        event_count = session_store.add_event(
            session_id=event.session_id,
            item_id=event.item_id,
            event_type=event.event_type,
            timestamp=timestamp,
            metadata=event.metadata
        )
        
        return EventResponse(
            status="success",
            session_id=event.session_id,
            event_count=event_count
        )
        
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(req: RecommendationRequest):
    """Get personalized recommendations for session"""
    start_time = time.time()
    
    try:
        # Get session context
        session_context = session_store.get_session_context(req.session_id)
        
        # Generate recommendations
        recommendations = recommender.recommend(
            session_context=session_context,
            k=req.k,
            exclude_items=req.exclude_items
        )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Format response
        rec_items = [
            RecommendationItem(**rec)
            for rec in recommendations
        ]
        
        return RecommendationResponse(
            session_id=req.session_id,
            recommendations=rec_items,
            model_version=recommender.model_version,
            latency_ms=round(latency_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}", tags=["Debug"])
async def get_session_info(session_id: str):
    """Get session information (debug endpoint)"""
    try:
        context = session_store.get_session_context(session_id)
        return {
            "session_id": session_id,
            "context": context
        }
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
