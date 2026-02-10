"""Build training dataset from DuckDB"""
import duckdb
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import Tuple
import numpy as np


class DatasetBuilder:
    """Build training dataset for recommender system"""
    
    def __init__(self, db_path: str = "ecommerce_analytics.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path, read_only=True)
        
    def build_session_sequences(self) -> pd.DataFrame:
        """Extract session sequences from order history"""
        query = """
        WITH order_sequences AS (
            SELECT 
                o.customer_id as session_id,
                oi.product_id as item_id,
                o.order_purchase_timestamp as event_time,
                'purchase' as event_type,
                ROW_NUMBER() OVER (
                    PARTITION BY o.customer_id 
                    ORDER BY o.order_purchase_timestamp
                ) as seq_number,
                COUNT(*) OVER (PARTITION BY o.customer_id) as session_length
            FROM read_csv_auto('seeds/orders.csv') o
            JOIN read_csv_auto('seeds/order_items.csv') oi 
                ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
        )
        SELECT * FROM order_sequences
        WHERE session_length >= 2  -- Need at least 2 items for training
        ORDER BY session_id, event_time
        """
        
        df = self.conn.execute(query).df()
        logger.info(f"Extracted {len(df)} events from {df['session_id'].nunique()} sessions")
        return df
    
    def build_item_features(self) -> pd.DataFrame:
        """Extract item (product) features"""
        query = """
        SELECT 
            p.product_id as item_id,
            p.product_category_name as category,
            p.product_weight_g as weight,
            p.product_length_cm * p.product_height_cm * p.product_width_cm as volume,
            COUNT(DISTINCT oi.order_id) as purchase_count,
            AVG(oi.price) as avg_price,
            SUM(oi.price) as total_revenue
        FROM read_csv_auto('seeds/products.csv') p
        LEFT JOIN read_csv_auto('seeds/order_items.csv') oi
            ON p.product_id = oi.product_id
        GROUP BY 1, 2, 3, 4
        """
        
        df = self.conn.execute(query).df()
        logger.info(f"Extracted features for {len(df)} items")
        return df
    
    def build_training_pairs(
        self,
        min_session_length: int = 2,
        max_session_length: int = 50
    ) -> pd.DataFrame:
        """Build positive and negative training pairs"""
        
        # Get session sequences
        sessions = self.build_session_sequences()
        
        # Build positive pairs (next item prediction)
        positive_pairs = []
        
        for session_id, group in sessions.groupby('session_id'):
            items = group.sort_values('event_time')['item_id'].tolist()
            
            if len(items) < min_session_length or len(items) > max_session_length:
                continue
            
            # For each item except the last, predict next item
            for i in range(len(items) - 1):
                context_items = items[:i+1]  # Items seen so far
                target_item = items[i+1]  # Next item to predict
                
                positive_pairs.append({
                    'session_id': session_id,
                    'context_items': context_items,
                    'target_item': target_item,
                    'label': 1,
                    'position': i + 1
                })
        
        positive_df = pd.DataFrame(positive_pairs)
        logger.info(f"Created {len(positive_df)} positive pairs")
        
        # Sample negative pairs (items not purchased)
        all_items = sessions['item_id'].unique()
        negative_pairs = []
        
        for _, row in positive_df.iterrows():
            session_items = set(row['context_items']) | {row['target_item']}
            # Sample random item not in session
            candidate_negatives = list(set(all_items) - session_items)
            if len(candidate_negatives) > 0:
                neg_item = np.random.choice(candidate_negatives)
                negative_pairs.append({
                    'session_id': row['session_id'],
                    'context_items': row['context_items'],
                    'target_item': neg_item,
                    'label': 0,
                    'position': row['position']
                })
        
        negative_df = pd.DataFrame(negative_pairs)
        logger.info(f"Created {len(negative_df)} negative pairs")
        
        # Combine and shuffle
        training_df = pd.concat([positive_df, negative_df], ignore_index=True)
        training_df = training_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return training_df
    
    def build_popularity_index(self) -> dict:
        """Build item popularity index"""
        query = """
        SELECT 
            product_id as item_id,
            COUNT(*) as purchase_count
        FROM read_csv_auto('seeds/order_items.csv')
        GROUP BY product_id
        ORDER BY purchase_count DESC
        """
        
        df = self.conn.execute(query).df()
        popularity = dict(zip(df['item_id'], df['purchase_count']))
        logger.info(f"Built popularity index for {len(popularity)} items")
        return popularity
    
    def export_datasets(self, output_dir: str = "src/artifacts"):
        """Export all datasets needed for training"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Build and export
        logger.info("Building datasets...")
        
        # Training pairs
        training_df = self.build_training_pairs()
        training_df.to_parquet(output_path / "training_pairs.parquet")
        logger.info(f"Saved training pairs to {output_path / 'training_pairs.parquet'}")
        
        # Item features
        item_features = self.build_item_features()
        item_features.to_parquet(output_path / "item_features.parquet")
        logger.info(f"Saved item features to {output_path / 'item_features.parquet'}")
        
        # Popularity index
        popularity = self.build_popularity_index()
        import json
        with open(output_path / "item_popularity.json", "w") as f:
            json.dump(popularity, f)
        logger.info(f"Saved popularity index to {output_path / 'item_popularity.json'}")
        
        logger.info("Dataset export complete!")


if __name__ == "__main__":
    builder = DatasetBuilder()
    builder.export_datasets()
