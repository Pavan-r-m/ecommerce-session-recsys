"""Feature engineering for session-based recommendations"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter
import json


class FeatureBuilder:
    """Build features for recommendation ranking"""
    
    def __init__(self, item_metadata: Optional[pd.DataFrame] = None):
        self.item_metadata = item_metadata
        self.feature_cache = {}
        
    def build_session_features(
        self,
        session_items: List[str],
        event_counts: Dict[str, int],
        session_duration_mins: float = None
    ) -> Dict[str, float]:
        """
        Build features from session history
        
        Args:
            session_items: List of item IDs in session
            event_counts: Dictionary of event type counts
            session_duration_mins: Session duration in minutes
            
        Returns:
            Dictionary of session-level features
        """
        features = {}
        
        # Session length features
        features['session_length'] = len(session_items)
        features['session_length_log'] = np.log1p(len(session_items))
        features['unique_items'] = len(set(session_items))
        features['item_repetition_rate'] = 1 - (features['unique_items'] / max(len(session_items), 1))
        
        # Event type features
        features['view_count'] = event_counts.get('view', 0)
        features['click_count'] = event_counts.get('click', 0)
        features['add_to_cart_count'] = event_counts.get('add_to_cart', 0)
        features['purchase_count'] = event_counts.get('purchase', 0)
        
        # Event ratios
        total_events = sum(event_counts.values())
        if total_events > 0:
            features['click_through_rate'] = features['click_count'] / total_events
            features['add_to_cart_rate'] = features['add_to_cart_count'] / total_events
            features['conversion_rate'] = features['purchase_count'] / total_events
        else:
            features['click_through_rate'] = 0
            features['add_to_cart_rate'] = 0
            features['conversion_rate'] = 0
        
        # Session engagement
        features['engagement_score'] = (
            features['view_count'] * 1 +
            features['click_count'] * 2 +
            features['add_to_cart_count'] * 5 +
            features['purchase_count'] * 10
        )
        
        # Time-based features
        if session_duration_mins is not None:
            features['session_duration_mins'] = session_duration_mins
            features['session_duration_log'] = np.log1p(session_duration_mins)
            features['events_per_minute'] = total_events / max(session_duration_mins, 0.1)
        
        return features
    
    def build_item_features(
        self,
        item_id: str,
        popularity_dict: Dict[str, int],
        category_popularity: Optional[Dict[str, int]] = None
    ) -> Dict[str, float]:
        """
        Build features for a candidate item
        
        Args:
            item_id: Item identifier
            popularity_dict: Global item popularity scores
            category_popularity: Category-level popularity scores
            
        Returns:
            Dictionary of item-level features
        """
        features = {}
        
        # Popularity features
        popularity = popularity_dict.get(item_id, 0)
        features['item_popularity'] = popularity
        features['item_popularity_log'] = np.log1p(popularity)
        features['item_popularity_rank'] = self._get_popularity_rank(item_id, popularity_dict)
        
        # Percentile-based features
        all_popularity = list(popularity_dict.values())
        if len(all_popularity) > 0:
            features['item_popularity_percentile'] = (
                np.percentile(all_popularity, 
                             [(popularity - v) for v in all_popularity].count(True) / len(all_popularity) * 100)
            )
        else:
            features['item_popularity_percentile'] = 0
        
        # Category features (if metadata available)
        if self.item_metadata is not None and item_id in self.item_metadata.index:
            item_meta = self.item_metadata.loc[item_id]
            features['item_price'] = item_meta.get('price', 0)
            features['item_price_log'] = np.log1p(item_meta.get('price', 0))
            features['item_weight'] = item_meta.get('weight', 0)
            
            category = item_meta.get('category', 'unknown')
            if category_popularity and category in category_popularity:
                features['category_popularity'] = category_popularity[category]
        
        return features
    
    def build_interaction_features(
        self,
        item_id: str,
        session_items: List[str],
        item_similarity_matrix: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Build features based on item-session interactions
        
        Args:
            item_id: Candidate item
            session_items: Items in current session
            item_similarity_matrix: Pre-computed similarity scores
            
        Returns:
            Dictionary of interaction features
        """
        features = {}
        
        # Presence in session
        features['in_session'] = int(item_id in session_items)
        
        if item_id in session_items:
            # Recency features
            last_occurrence_idx = len(session_items) - 1 - session_items[::-1].index(item_id)
            features['last_seen_position'] = last_occurrence_idx
            features['recency_score'] = 1.0 / (len(session_items) - last_occurrence_idx)
            
            # Frequency
            features['item_frequency_in_session'] = session_items.count(item_id)
        else:
            features['last_seen_position'] = -1
            features['recency_score'] = 0
            features['item_frequency_in_session'] = 0
        
        # Similarity to session items
        if item_similarity_matrix is not None:
            similarity_scores = []
            for sess_item in set(session_items):
                if sess_item != item_id:
                    sim_score = self._get_similarity(
                        item_id, sess_item, item_similarity_matrix
                    )
                    similarity_scores.append(sim_score)
            
            if similarity_scores:
                features['max_similarity_to_session'] = max(similarity_scores)
                features['mean_similarity_to_session'] = np.mean(similarity_scores)
                features['sum_similarity_to_session'] = sum(similarity_scores)
            else:
                features['max_similarity_to_session'] = 0
                features['mean_similarity_to_session'] = 0
                features['sum_similarity_to_session'] = 0
        
        # Co-occurrence patterns
        if len(session_items) > 0:
            features['similarity_to_last_item'] = self._calculate_last_item_similarity(
                item_id, session_items[-1], item_similarity_matrix
            )
        
        return features
    
    def build_temporal_features(
        self,
        current_time: datetime,
        session_start_time: datetime
    ) -> Dict[str, float]:
        """
        Build time-based features
        
        Args:
            current_time: Current timestamp
            session_start_time: When session started
            
        Returns:
            Dictionary of temporal features
        """
        features = {}
        
        # Time of day
        features['hour_of_day'] = current_time.hour
        features['day_of_week'] = current_time.weekday()
        features['is_weekend'] = int(current_time.weekday() >= 5)
        features['is_business_hours'] = int(9 <= current_time.hour <= 17)
        
        # Cyclical encoding
        features['hour_sin'] = np.sin(2 * np.pi * current_time.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * current_time.hour / 24)
        features['day_sin'] = np.sin(2 * np.pi * current_time.weekday() / 7)
        features['day_cos'] = np.cos(2 * np.pi * current_time.weekday() / 7)
        
        # Session timing
        session_age = (current_time - session_start_time).total_seconds() / 60
        features['session_age_minutes'] = session_age
        features['session_age_log'] = np.log1p(session_age)
        
        return features
    
    def build_all_features(
        self,
        item_id: str,
        session_items: List[str],
        event_counts: Dict[str, int],
        popularity_dict: Dict[str, int],
        current_time: Optional[datetime] = None,
        session_start_time: Optional[datetime] = None,
        item_similarity_matrix: Optional[pd.DataFrame] = None,
        category_popularity: Optional[Dict[str, int]] = None
    ) -> Dict[str, float]:
        """
        Build complete feature set for ranking
        
        Returns:
            Complete feature dictionary
        """
        all_features = {}
        
        # Session features
        session_features = self.build_session_features(session_items, event_counts)
        all_features.update(session_features)
        
        # Item features
        item_features = self.build_item_features(
            item_id, popularity_dict, category_popularity
        )
        all_features.update(item_features)
        
        # Interaction features
        interaction_features = self.build_interaction_features(
            item_id, session_items, item_similarity_matrix
        )
        all_features.update(interaction_features)
        
        # Temporal features
        if current_time and session_start_time:
            temporal_features = self.build_temporal_features(
                current_time, session_start_time
            )
            all_features.update(temporal_features)
        
        return all_features
    
    @staticmethod
    def _get_popularity_rank(item_id: str, popularity_dict: Dict[str, int]) -> int:
        """Get rank of item by popularity"""
        sorted_items = sorted(
            popularity_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for rank, (iid, _) in enumerate(sorted_items, start=1):
            if iid == item_id:
                return rank
        return len(sorted_items) + 1
    
    @staticmethod
    def _get_similarity(
        item1: str,
        item2: str,
        similarity_matrix: pd.DataFrame
    ) -> float:
        """Get similarity score between two items"""
        if similarity_matrix is None:
            return 0.0
        
        try:
            mask = (
                (similarity_matrix['item_id_1'] == item1) &
                (similarity_matrix['item_id_2'] == item2)
            ) | (
                (similarity_matrix['item_id_1'] == item2) &
                (similarity_matrix['item_id_2'] == item1)
            )
            result = similarity_matrix[mask]
            if len(result) > 0:
                return result['similarity'].iloc[0]
        except Exception:
            pass
        return 0.0
    
    @staticmethod
    def _calculate_last_item_similarity(
        item_id: str,
        last_item: str,
        similarity_matrix: Optional[pd.DataFrame]
    ) -> float:
        """Calculate similarity to last viewed item"""
        if similarity_matrix is None:
            return 0.0
        return FeatureBuilder._get_similarity(item_id, last_item, similarity_matrix)


def create_feature_vector(
    candidate_items: List[str],
    session_context: Dict,
    popularity_dict: Dict[str, int],
    item_similarity_matrix: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Create feature matrix for multiple candidates
    
    Args:
        candidate_items: List of candidate item IDs
        session_context: Session state dictionary
        popularity_dict: Item popularity mapping
        item_similarity_matrix: Similarity scores
        
    Returns:
        DataFrame with features for all candidates
    """
    builder = FeatureBuilder()
    
    features_list = []
    for item_id in candidate_items:
        features = builder.build_all_features(
            item_id=item_id,
            session_items=session_context.get('recent_items', []),
            event_counts=session_context.get('event_counts', {}),
            popularity_dict=popularity_dict,
            item_similarity_matrix=item_similarity_matrix
        )
        features['item_id'] = item_id
        features_list.append(features)
    
    return pd.DataFrame(features_list)
