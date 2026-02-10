"""Feature definitions and metadata"""
from typing import List, Dict
from enum import Enum


class FeatureType(Enum):
    """Feature type enumeration"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    TEMPORAL = "temporal"


class FeatureDefinition:
    """Feature metadata and definition"""
    
    def __init__(
        self,
        name: str,
        feature_type: FeatureType,
        description: str,
        importance: float = 0.0,
        is_mandatory: bool = True
    ):
        self.name = name
        self.feature_type = feature_type
        self.description = description
        self.importance = importance
        self.is_mandatory = is_mandatory


# Session-level features
SESSION_FEATURES = [
    FeatureDefinition(
        name="session_length",
        feature_type=FeatureType.NUMERICAL,
        description="Number of items in session",
        importance=285.0
    ),
    FeatureDefinition(
        name="session_length_log",
        feature_type=FeatureType.NUMERICAL,
        description="Log-transformed session length",
        importance=120.0
    ),
    FeatureDefinition(
        name="unique_items",
        feature_type=FeatureType.NUMERICAL,
        description="Number of unique items in session",
        importance=95.0
    ),
    FeatureDefinition(
        name="item_repetition_rate",
        feature_type=FeatureType.NUMERICAL,
        description="Rate of item repetition in session",
        importance=68.0
    ),
    FeatureDefinition(
        name="view_count",
        feature_type=FeatureType.NUMERICAL,
        description="Number of view events",
        importance=142.0
    ),
    FeatureDefinition(
        name="click_count",
        feature_type=FeatureType.NUMERICAL,
        description="Number of click events",
        importance=156.0
    ),
    FeatureDefinition(
        name="add_to_cart_count",
        feature_type=FeatureType.NUMERICAL,
        description="Number of add-to-cart events",
        importance=198.0
    ),
    FeatureDefinition(
        name="engagement_score",
        feature_type=FeatureType.NUMERICAL,
        description="Weighted engagement score",
        importance=210.0
    ),
]

# Item-level features
ITEM_FEATURES = [
    FeatureDefinition(
        name="item_popularity",
        feature_type=FeatureType.NUMERICAL,
        description="Global item popularity (purchase count)",
        importance=420.0
    ),
    FeatureDefinition(
        name="item_popularity_log",
        feature_type=FeatureType.NUMERICAL,
        description="Log-transformed popularity",
        importance=385.0
    ),
    FeatureDefinition(
        name="item_popularity_rank",
        feature_type=FeatureType.NUMERICAL,
        description="Rank by popularity",
        importance=175.0
    ),
    FeatureDefinition(
        name="item_popularity_percentile",
        feature_type=FeatureType.NUMERICAL,
        description="Popularity percentile (0-100)",
        importance=145.0
    ),
]

# Interaction features
INTERACTION_FEATURES = [
    FeatureDefinition(
        name="in_session",
        feature_type=FeatureType.BINARY,
        description="Whether item is in current session",
        importance=210.0
    ),
    FeatureDefinition(
        name="recency_score",
        feature_type=FeatureType.NUMERICAL,
        description="Recency score (inverse of position from last)",
        importance=165.0
    ),
    FeatureDefinition(
        name="item_frequency_in_session",
        feature_type=FeatureType.NUMERICAL,
        description="How many times item appears in session",
        importance=125.0
    ),
    FeatureDefinition(
        name="max_similarity_to_session",
        feature_type=FeatureType.NUMERICAL,
        description="Max similarity to any session item",
        importance=245.0
    ),
    FeatureDefinition(
        name="mean_similarity_to_session",
        feature_type=FeatureType.NUMERICAL,
        description="Average similarity to session items",
        importance=198.0
    ),
    FeatureDefinition(
        name="similarity_to_last_item",
        feature_type=FeatureType.NUMERICAL,
        description="Similarity to most recent item",
        importance=312.0
    ),
]

# Temporal features
TEMPORAL_FEATURES = [
    FeatureDefinition(
        name="hour_of_day",
        feature_type=FeatureType.NUMERICAL,
        description="Hour of day (0-23)",
        importance=78.0
    ),
    FeatureDefinition(
        name="day_of_week",
        feature_type=FeatureType.NUMERICAL,
        description="Day of week (0-6)",
        importance=65.0
    ),
    FeatureDefinition(
        name="is_weekend",
        feature_type=FeatureType.BINARY,
        description="Whether it's weekend",
        importance=52.0
    ),
    FeatureDefinition(
        name="hour_sin",
        feature_type=FeatureType.NUMERICAL,
        description="Cyclical hour encoding (sin)",
        importance=42.0
    ),
    FeatureDefinition(
        name="hour_cos",
        feature_type=FeatureType.NUMERICAL,
        description="Cyclical hour encoding (cos)",
        importance=38.0
    ),
]


def get_all_features() -> List[FeatureDefinition]:
    """Get all feature definitions"""
    return (
        SESSION_FEATURES +
        ITEM_FEATURES +
        INTERACTION_FEATURES +
        TEMPORAL_FEATURES
    )


def get_feature_names() -> List[str]:
    """Get list of all feature names"""
    return [f.name for f in get_all_features()]


def get_mandatory_features() -> List[str]:
    """Get list of mandatory feature names"""
    return [f.name for f in get_all_features() if f.is_mandatory]


def get_feature_importance_dict() -> Dict[str, float]:
    """Get dictionary of feature importances"""
    return {f.name: f.importance for f in get_all_features()}


def get_features_by_type(feature_type: FeatureType) -> List[str]:
    """Get features of specific type"""
    return [f.name for f in get_all_features() if f.feature_type == feature_type]


# Feature groups for different model variants
MINIMAL_FEATURE_SET = [
    "item_popularity",
    "session_length",
    "in_session",
]

BASELINE_FEATURE_SET = [
    "item_popularity",
    "item_popularity_log",
    "session_length",
    "view_count",
    "click_count",
    "in_session",
    "recency_score",
]

FULL_FEATURE_SET = get_feature_names()
