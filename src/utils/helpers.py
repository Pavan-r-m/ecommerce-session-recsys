"""Utility functions for the recommender system"""
import time
import functools
from typing import Callable, Any, List, Dict
from loguru import logger
import hashlib
import json


def timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000
        logger.debug(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    return wrapper


def cache_result(ttl_seconds: int = 300):
    """Decorator to cache function results with TTL"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from args and kwargs
            cache_key = hashlib.md5(
                json.dumps((args, kwargs), sort_keys=True, default=str).encode()
            ).hexdigest()
            
            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Execute and cache
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            # Clean old entries
            current_time = time.time()
            cache_keys_to_delete = [
                k for k, (_, ts) in cache.items()
                if current_time - ts >= ttl_seconds
            ]
            for k in cache_keys_to_delete:
                del cache[k]
            
            return result
        
        wrapper.clear_cache = lambda: cache.clear()
        return wrapper
    
    return decorator


def batch_items(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
    """Split list into batches"""
    return [
        items[i:i + batch_size]
        for i in range(0, len(items), batch_size)
    ]


def normalize_scores(scores: List[float]) -> List[float]:
    """Normalize scores to 0-1 range"""
    if not scores or max(scores) == min(scores):
        return [0.5] * len(scores)
    
    min_score = min(scores)
    max_score = max(scores)
    return [
        (score - min_score) / (max_score - min_score)
        for score in scores
    ]


def diversify_recommendations(
    recommendations: List[Dict],
    diversity_weight: float = 0.3,
    category_key: str = 'category'
) -> List[Dict]:
    """
    Re-rank recommendations to promote diversity
    
    Args:
        recommendations: List of recommendation dicts with 'score' and category
        diversity_weight: Weight for diversity penalty (0-1)
        category_key: Key for category field
        
    Returns:
        Re-ranked recommendations
    """
    if not recommendations or diversity_weight <= 0:
        return recommendations
    
    selected = []
    remaining = recommendations.copy()
    seen_categories = set()
    
    while remaining:
        # Score with diversity penalty
        scores = []
        for rec in remaining:
            base_score = rec.get('score', 0)
            category = rec.get(category_key, 'unknown')
            
            # Penalty for already-seen categories
            diversity_penalty = (
                diversity_weight if category in seen_categories else 0
            )
            
            final_score = base_score * (1 - diversity_penalty)
            scores.append(final_score)
        
        # Select best
        best_idx = scores.index(max(scores))
        best_rec = remaining.pop(best_idx)
        selected.append(best_rec)
        
        # Track category
        category = best_rec.get(category_key, 'unknown')
        seen_categories.add(category)
    
    return selected


def calculate_recall_at_k(actual: List[str], predicted: List[str], k: int) -> float:
    """Calculate Recall@K metric"""
    if len(actual) == 0:
        return 0.0
    
    predicted_k = set(predicted[:k])
    actual_set = set(actual)
    
    hits = len(predicted_k & actual_set)
    return hits / len(actual_set)


def calculate_precision_at_k(actual: List[str], predicted: List[str], k: int) -> float:
    """Calculate Precision@K metric"""
    if k == 0:
        return 0.0
    
    predicted_k = set(predicted[:k])
    actual_set = set(actual)
    
    hits = len(predicted_k & actual_set)
    return hits / k


def exponential_decay_weights(n: int, decay_rate: float = 0.5) -> List[float]:
    """
    Generate exponential decay weights for time-based importance
    
    Args:
        n: Number of weights to generate
        decay_rate: Decay rate (higher = faster decay)
        
    Returns:
        List of weights (most recent = highest weight)
    """
    import numpy as np
    weights = [np.exp(-decay_rate * i) for i in range(n)]
    # Reverse so most recent is first
    return weights[::-1]


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []
    
    def allow_request(self) -> bool:
        """Check if request is allowed"""
        current_time = time.time()
        
        # Remove old calls
        self.calls = [
            t for t in self.calls
            if current_time - t < self.period_seconds
        ]
        
        # Check limit
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        
        return False
    
    def wait_time(self) -> float:
        """Get seconds to wait before next allowed request"""
        if not self.calls:
            return 0
        
        current_time = time.time()
        oldest_call = min(self.calls)
        wait = max(0, self.period_seconds - (current_time - oldest_call))
        return wait
