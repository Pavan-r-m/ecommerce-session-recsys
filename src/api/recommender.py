"""Recommendation engine - candidate generation + ranking"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path
from loguru import logger
import pickle


class SessionRecommender:
    """Session-based recommender with candidate generation + ranking"""
    
    def __init__(self, artifacts_path: str = "src/artifacts"):
        self.artifacts_path = Path(artifacts_path)
        self.model = None
        self.item_similarity = None
        self.item_popularity = None
        self.feature_config = None
        self.model_version = "unloaded"
        
        self._load_artifacts()
    
    def _load_artifacts(self):
        """Load model artifacts (ranker, embeddings, popularity, config)"""
        try:
            # Load ranker model
            model_path = self.artifacts_path / "ranker_model.pkl"
            if model_path.exists():
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded ranker model from {model_path}")
            else:
                logger.warning(f"Ranker model not found at {model_path}, using fallback")
            
            # Load item similarity (for candidate generation)
            similarity_path = self.artifacts_path / "item_similarity.parquet"
            if similarity_path.exists():
                self.item_similarity = pd.read_parquet(similarity_path)
                logger.info(f"Loaded item similarity from {similarity_path}")
            
            # Load item popularity
            popularity_path = self.artifacts_path / "item_popularity.json"
            if popularity_path.exists():
                with open(popularity_path, "r") as f:
                    self.item_popularity = json.load(f)
                logger.info(f"Loaded item popularity from {popularity_path}")
            else:
                # Fallback popularity
                self.item_popularity = {}
            
            # Load feature config
            config_path = self.artifacts_path / "feature_config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.feature_config = json.load(f)
                self.model_version = self.feature_config.get("version", "unknown")
                logger.info(f"Loaded feature config, version: {self.model_version}")
            
        except Exception as e:
            logger.error(f"Error loading artifacts: {e}")
            self.model_version = "error"
    
    def generate_candidates(
        self,
        session_context: Dict,
        k: int = 100,
        exclude_items: Optional[List[str]] = None
    ) -> List[str]:
        """Generate candidate items from session context"""
        candidates = set()
        recent_items = session_context.get("recent_items", [])
        exclude_set = set(exclude_items or [])
        
        # Strategy 1: Item-to-item similarity (if available)
        if self.item_similarity is not None and len(recent_items) > 0:
            for item_id in recent_items[:5]:  # Use last 5 items
                similar = self._get_similar_items(item_id, n=20)
                candidates.update(similar)
        
        # Strategy 2: Popular items (always available)
        if self.item_popularity:
            popular_items = sorted(
                self.item_popularity.items(),
                key=lambda x: x[1],
                reverse=True
            )[:50]
            candidates.update([item_id for item_id, _ in popular_items])
        
        # Remove items already in session
        candidates -= set(recent_items)
        candidates -= exclude_set
        
        # Fallback if no candidates
        if len(candidates) == 0:
            logger.warning("No candidates generated, using popular items")
            candidates = set(list(self.item_popularity.keys())[:k])
        
        return list(candidates)[:k]
    
    def _get_similar_items(self, item_id: str, n: int = 20) -> List[str]:
        """Get similar items using precomputed similarity matrix"""
        if self.item_similarity is None:
            return []
        
        # Filter similarity dataframe
        similar_df = self.item_similarity[
            self.item_similarity["item_id_1"] == item_id
        ].sort_values("similarity", ascending=False).head(n)
        
        return similar_df["item_id_2"].tolist()
    
    def build_features(
        self,
        candidates: List[str],
        session_context: Dict
    ) -> pd.DataFrame:
        """Build features for candidate ranking"""
        features = []
        
        recent_items = session_context.get("recent_items", [])
        event_counts = session_context.get("event_counts", {})
        
        for item_id in candidates:
            feat = {
                "item_id": item_id,
                # Popularity features
                "item_popularity": self.item_popularity.get(item_id, 0),
                "item_popularity_log": np.log1p(self.item_popularity.get(item_id, 0)),
                
                # Session features
                "session_length": len(recent_items),
                "session_views": event_counts.get("view", 0),
                "session_clicks": event_counts.get("click", 0),
                "session_add_to_cart": event_counts.get("add_to_cart", 0),
                
                # Co-occurrence features
                "in_recent_items": int(item_id in recent_items),
                "position_in_session": recent_items.index(item_id) if item_id in recent_items else -1,
            }
            features.append(feat)
        
        return pd.DataFrame(features)
    
    def rank_candidates(
        self,
        candidates: List[str],
        session_context: Dict
    ) -> List[Tuple[str, float, str]]:
        """Rank candidates using trained model or fallback scoring"""
        
        # Build features
        features_df = self.build_features(candidates, session_context)
        
        # Score with model or fallback
        if self.model is not None:
            # Use trained ranker
            feature_cols = [c for c in features_df.columns if c != "item_id"]
            X = features_df[feature_cols].fillna(0)
            scores = self.model.predict(X)
        else:
            # Fallback: popularity-based scoring
            scores = features_df["item_popularity"].values
            logger.debug("Using fallback popularity scoring")
        
        # Combine and sort
        results = []
        for idx, (item_id, score) in enumerate(zip(candidates, scores)):
            reason = self._get_reason(features_df.iloc[idx])
            results.append((item_id, float(score), reason))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _get_reason(self, feature_row: pd.Series) -> str:
        """Generate explanation for recommendation"""
        if feature_row["in_recent_items"] == 1:
            return "viewed_recently"
        elif feature_row["item_popularity"] > 1000:
            return "popular"
        else:
            return "recommended"
    
    def recommend(
        self,
        session_context: Dict,
        k: int = 20,
        exclude_items: Optional[List[str]] = None
    ) -> List[Dict]:
        """Main recommendation method"""
        
        # Step 1: Generate candidates
        candidates = self.generate_candidates(
            session_context,
            k=max(k * 5, 100),  # Generate more candidates to rank
            exclude_items=exclude_items
        )
        
        if len(candidates) == 0:
            logger.warning("No candidates available")
            return []
        
        # Step 2: Rank candidates
        ranked = self.rank_candidates(candidates, session_context)
        
        # Step 3: Return top-k
        recommendations = []
        for rank, (item_id, score, reason) in enumerate(ranked[:k], start=1):
            recommendations.append({
                "item_id": item_id,
                "score": score,
                "reason": reason,
                "rank": rank
            })
        
        return recommendations
