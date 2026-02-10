"""Test recommender logic"""
import pytest
from src.api.recommender import SessionRecommender
import numpy as np


@pytest.fixture
def recommender():
    """Recommender fixture"""
    return SessionRecommender(artifacts_path="src/artifacts")


def test_recommender_initialization(recommender):
    """Test recommender loads"""
    assert recommender is not None
    assert recommender.model_version is not None


def test_generate_candidates(recommender):
    """Test candidate generation"""
    session_context = {
        "recent_items": ["prod_1", "prod_2"],
        "event_counts": {"view": 2}
    }
    
    candidates = recommender.generate_candidates(session_context, k=50)
    assert len(candidates) > 0
    assert len(candidates) <= 50
    # Should not include items already in session
    assert "prod_1" not in candidates
    assert "prod_2" not in candidates


def test_build_features(recommender):
    """Test feature building"""
    candidates = ["prod_a", "prod_b", "prod_c"]
    session_context = {
        "recent_items": ["prod_x"],
        "event_counts": {"view": 1, "click": 0}
    }
    
    features_df = recommender.build_features(candidates, session_context)
    assert len(features_df) == 3
    assert "item_id" in features_df.columns
    assert "item_popularity" in features_df.columns
    assert "session_length" in features_df.columns


def test_recommend(recommender):
    """Test end-to-end recommendation"""
    session_context = {
        "recent_items": ["prod_1"],
        "event_counts": {"view": 1}
    }
    
    recommendations = recommender.recommend(session_context, k=10)
    assert len(recommendations) <= 10
    
    if len(recommendations) > 0:
        rec = recommendations[0]
        assert "item_id" in rec
        assert "score" in rec
        assert "reason" in rec
        assert "rank" in rec
        assert rec["rank"] == 1


def test_recommend_with_exclusions(recommender):
    """Test recommendations with excluded items"""
    session_context = {
        "recent_items": ["prod_1"],
        "event_counts": {"view": 1}
    }
    
    exclude_items = ["prod_exclude_1", "prod_exclude_2"]
    recommendations = recommender.recommend(
        session_context,
        k=20,
        exclude_items=exclude_items
    )
    
    rec_items = [r["item_id"] for r in recommendations]
    for excluded in exclude_items:
        assert excluded not in rec_items
