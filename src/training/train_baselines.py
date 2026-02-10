"""Train baseline models: item-to-item similarity, matrix factorization"""
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from typing import Dict, List


class BaselineModels:
    """Baseline recommendation models"""
    
    def __init__(self, artifacts_path: str = "src/artifacts"):
        self.artifacts_path = Path(artifacts_path)
        
    def train_item_similarity(
        self,
        training_pairs_path: str = None,
        min_cooccurrence: int = 2,
        top_k: int = 50
    ) -> pd.DataFrame:
        """
        Train item-to-item collaborative filtering
        Based on co-purchase patterns
        """
        if training_pairs_path is None:
            training_pairs_path = self.artifacts_path / "training_pairs.parquet"
        
        logger.info("Training item-to-item similarity model...")
        
        # Load training data
        df = pd.read_parquet(training_pairs_path)
        df = df[df['label'] == 1]  # Only positive pairs
        
        # Build co-occurrence matrix
        item_pairs = []
        for _, row in df.iterrows():
            context = row['context_items']
            target = row['target_item']
            
            # Add all pairs of (context_item, target)
            for ctx_item in context:
                item_pairs.append({
                    'item_id_1': ctx_item,
                    'item_id_2': target
                })
        
        pairs_df = pd.DataFrame(item_pairs)
        
        # Count co-occurrences
        cooccurrence = pairs_df.groupby(
            ['item_id_1', 'item_id_2']
        ).size().reset_index(name='count')
        
        # Filter by minimum co-occurrence
        cooccurrence = cooccurrence[cooccurrence['count'] >= min_cooccurrence]
        
        # Calculate similarity (normalized co-occurrence)
        # Get item purchase counts
        item_counts = pairs_df['item_id_1'].value_counts()
        
        cooccurrence['item_1_count'] = cooccurrence['item_id_1'].map(item_counts)
        cooccurrence['similarity'] = (
            cooccurrence['count'] / np.sqrt(cooccurrence['item_1_count'])
        )
        
        # Keep top-k similar items per item
        similarity_df = (
            cooccurrence
            .sort_values(['item_id_1', 'similarity'], ascending=[True, False])
            .groupby('item_id_1')
            .head(top_k)
            [['item_id_1', 'item_id_2', 'similarity']]
        )
        
        logger.info(
            f"Built similarity index: {len(similarity_df)} pairs "
            f"for {similarity_df['item_id_1'].nunique()} items"
        )
        
        # Save
        output_path = self.artifacts_path / "item_similarity.parquet"
        similarity_df.to_parquet(output_path, index=False)
        logger.info(f"Saved similarity matrix to {output_path}")
        
        return similarity_df
    
    def evaluate_item_similarity(
        self,
        similarity_df: pd.DataFrame,
        test_sessions: pd.DataFrame,
        k: int = 20
    ) -> Dict[str, float]:
        """Evaluate item-to-item on test sessions"""
        logger.info(f"Evaluating item-to-item model on {len(test_sessions)} sessions...")
        
        hits = 0
        total = 0
        
        for _, row in test_sessions.iterrows():
            if row['label'] == 0:  # Only evaluate on positive pairs
                continue
            
            context_items = row['context_items']
            target_item = row['target_item']
            
            # Get recommendations based on last item in context
            if len(context_items) == 0:
                continue
            
            last_item = context_items[-1]
            candidates = similarity_df[
                similarity_df['item_id_1'] == last_item
            ].head(k)['item_id_2'].tolist()
            
            # Check if target is in recommendations
            if target_item in candidates:
                hits += 1
            total += 1
        
        recall_at_k = hits / total if total > 0 else 0
        
        metrics = {
            'recall@20': recall_at_k,
            'hits': hits,
            'total': total
        }
        
        logger.info(f"Item-to-item metrics: {metrics}")
        return metrics


if __name__ == "__main__":
    trainer = BaselineModels()
    
    # Train item similarity
    similarity_df = trainer.train_item_similarity()
    
    logger.info("Baseline models training complete!")
