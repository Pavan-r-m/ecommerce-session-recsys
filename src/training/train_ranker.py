"""Train LightGBM ranker model"""
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import pickle
import json
from datetime import datetime


class RankerTrainer:
    """Train ranking model for candidate scoring"""
    
    def __init__(self, artifacts_path: str = "src/artifacts"):
        self.artifacts_path = Path(artifacts_path)
        self.model = None
        
    def build_features(
        self,
        training_df: pd.DataFrame,
        item_features: pd.DataFrame,
        popularity: dict
    ) -> pd.DataFrame:
        """Build features for ranking"""
        logger.info("Building features for ranking...")
        
        features = []
        
        for _, row in training_df.iterrows():
            context_items = row['context_items']
            target_item = row['target_item']
            label = row['label']
            position = row['position']
            
            # Session features
            session_length = len(context_items)
            
            # Target item features
            target_popularity = popularity.get(target_item, 0)
            
            # Context features
            context_popularity_mean = np.mean([
                popularity.get(item, 0) for item in context_items
            ]) if len(context_items) > 0 else 0
            
            # Position features
            recency = position  # How recent is this interaction
            
            # Co-occurrence with last item (simple proxy)
            last_item_same_category = 0  # Would need category info
            
            feat = {
                'target_item': target_item,
                'session_length': session_length,
                'target_popularity': target_popularity,
                'target_popularity_log': np.log1p(target_popularity),
                'context_popularity_mean': context_popularity_mean,
                'context_popularity_log': np.log1p(context_popularity_mean),
                'position': position,
                'in_context': int(target_item in context_items),
                'label': label
            }
            
            features.append(feat)
        
        features_df = pd.DataFrame(features)
        logger.info(f"Built {len(features_df)} feature rows with {len(features_df.columns)-2} features")
        
        return features_df
    
    def train(
        self,
        training_pairs_path: str = None,
        item_features_path: str = None,
        popularity_path: str = None,
        test_size: float = 0.2
    ):
        """Train LightGBM ranker"""
        
        # Load data
        if training_pairs_path is None:
            training_pairs_path = self.artifacts_path / "training_pairs.parquet"
        if item_features_path is None:
            item_features_path = self.artifacts_path / "item_features.parquet"
        if popularity_path is None:
            popularity_path = self.artifacts_path / "item_popularity.json"
        
        logger.info("Loading training data...")
        training_df = pd.read_parquet(training_pairs_path)
        item_features = pd.read_parquet(item_features_path)
        
        with open(popularity_path, 'r') as f:
            popularity = json.load(f)
        
        # Build features
        features_df = self.build_features(training_df, item_features, popularity)
        
        # Split train/test
        train_df, test_df = train_test_split(
            features_df,
            test_size=test_size,
            random_state=42,
            stratify=features_df['label']
        )
        
        logger.info(f"Train size: {len(train_df)}, Test size: {len(test_df)}")
        
        # Prepare features
        feature_cols = [
            'session_length',
            'target_popularity',
            'target_popularity_log',
            'context_popularity_mean',
            'context_popularity_log',
            'position',
            'in_context'
        ]
        
        X_train = train_df[feature_cols]
        y_train = train_df['label']
        
        X_test = test_df[feature_cols]
        y_test = test_df['label']
        
        # Train LightGBM
        logger.info("Training LightGBM ranker...")
        
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 0
        }
        
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[train_data, test_data],
            valid_names=['train', 'test'],
            callbacks=[lgb.log_evaluation(10)]
        )
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        from sklearn.metrics import roc_auc_score, average_precision_score
        
        train_auc = roc_auc_score(y_train, train_pred)
        test_auc = roc_auc_score(y_test, test_pred)
        test_ap = average_precision_score(y_test, test_pred)
        
        logger.info(f"Train AUC: {train_auc:.4f}")
        logger.info(f"Test AUC: {test_auc:.4f}")
        logger.info(f"Test AP: {test_ap:.4f}")
        
        # Feature importance
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importance()
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature importance:")
        logger.info(f"\n{importance_df.to_string()}")
        
        # Save model
        self.save_model(feature_cols)
        
        return {
            'train_auc': train_auc,
            'test_auc': test_auc,
            'test_ap': test_ap
        }
    
    def save_model(self, feature_cols: list):
        """Save trained model and config"""
        # Save model
        model_path = self.artifacts_path / "ranker_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"Saved model to {model_path}")
        
        # Save feature config
        config = {
            'version': datetime.now().strftime("%Y-%m-%d"),
            'trained_at': datetime.now().isoformat(),
            'features': feature_cols,
            'features_count': len(feature_cols),
            'model_type': 'lightgbm'
        }
        
        config_path = self.artifacts_path / "feature_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved config to {config_path}")


if __name__ == "__main__":
    trainer = RankerTrainer()
    metrics = trainer.train()
    logger.info(f"Training complete! Metrics: {metrics}")
