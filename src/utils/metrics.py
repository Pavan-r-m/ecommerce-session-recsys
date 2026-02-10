"""Metrics collection and monitoring"""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional
import time


# Request metrics
request_count = Counter(
    'recommendation_requests_total',
    'Total number of recommendation requests',
    ['endpoint', 'status']
)

request_latency = Histogram(
    'recommendation_request_duration_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Recommendation metrics
recommendations_returned = Histogram(
    'recommendations_count',
    'Number of recommendations returned per request',
    buckets=[0, 5, 10, 20, 50, 100]
)

# Session metrics
active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

events_processed = Counter(
    'events_processed_total',
    'Total number of events processed',
    ['event_type']
)

# Model metrics
model_info = Info(
    'model_info',
    'Information about the recommendation model'
)

candidate_generation_time = Histogram(
    'candidate_generation_seconds',
    'Time spent generating candidates',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
)

ranking_time = Histogram(
    'ranking_duration_seconds',
    'Time spent ranking candidates',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
)


class MetricsCollector:
    """Helper class for collecting metrics"""
    
    @staticmethod
    def record_request(endpoint: str, status: str, duration: float):
        """Record API request metrics"""
        request_count.labels(endpoint=endpoint, status=status).inc()
        request_latency.labels(endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_event(event_type: str):
        """Record event processing"""
        events_processed.labels(event_type=event_type).inc()
    
    @staticmethod
    def record_recommendations(count: int):
        """Record number of recommendations returned"""
        recommendations_returned.observe(count)
    
    @staticmethod
    def update_active_sessions(count: int):
        """Update active session count"""
        active_sessions.set(count)
    
    @staticmethod
    def set_model_info(version: str, trained_at: str, features_count: int):
        """Set model information"""
        model_info.info({
            'version': version,
            'trained_at': trained_at,
            'features_count': str(features_count)
        })
    
    @staticmethod
    def record_candidate_generation_time(duration: float):
        """Record candidate generation time"""
        candidate_generation_time.observe(duration)
    
    @staticmethod
    def record_ranking_time(duration: float):
        """Record ranking time"""
        ranking_time.observe(duration)


def timed_operation(metric: Histogram):
    """Decorator to time operations and record in histogram"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            metric.observe(duration)
            return result
        return wrapper
    return decorator
