"""Offline evaluation metrics"""
import pandas as pd
import numpy as np
from typing import List, Dict
from loguru import logger


def recall_at_k(actual: List[str], predicted: List[str], k: int = 20) -> float:
    """Calculate Recall@K"""
    if len(actual) == 0:
        return 0.0
    
    predicted_k = predicted[:k]
    hits = len(set(actual) & set(predicted_k))
    return hits / len(actual)


def precision_at_k(actual: List[str], predicted: List[str], k: int = 20) -> float:
    """Calculate Precision@K"""
    if k == 0:
        return 0.0
    
    predicted_k = predicted[:k]
    hits = len(set(actual) & set(predicted_k))
    return hits / k


def ndcg_at_k(actual: List[str], predicted: List[str], k: int = 20) -> float:
    """Calculate NDCG@K"""
    predicted_k = predicted[:k]
    
    # DCG
    dcg = 0.0
    for i, item in enumerate(predicted_k):
        if item in actual:
            dcg += 1.0 / np.log2(i + 2)  # +2 because i is 0-indexed
    
    # IDCG (ideal)
    idcg = sum([1.0 / np.log2(i + 2) for i in range(min(len(actual), k))])
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def mean_average_precision_at_k(
    actual: List[str],
    predicted: List[str],
    k: int = 20
) -> float:
    """Calculate MAP@K"""
    if len(actual) == 0:
        return 0.0
    
    predicted_k = predicted[:k]
    
    score = 0.0
    num_hits = 0.0
    
    for i, p in enumerate(predicted_k):
        if p in actual:
            num_hits += 1.0
            score += num_hits / (i + 1.0)
    
    return score / min(len(actual), k)


def evaluate_recommendations(
    test_sessions: pd.DataFrame,
    recommender,
    k_values: List[int] = [5, 10, 20]
) -> Dict[str, float]:
    """
    Evaluate recommender on test sessions
    
    Args:
        test_sessions: DataFrame with columns [session_id, context_items, target_item]
        recommender: Recommender instance with recommend() method
        k_values: List of K values to evaluate
    
    Returns:
        Dictionary of metrics
    """
    logger.info(f"Evaluating on {len(test_sessions)} test sessions...")
    
    metrics = {f'recall@{k}': [] for k in k_values}
    metrics.update({f'ndcg@{k}': [] for k in k_values})
    metrics.update({f'map@{k}': [] for k in k_values})
    
    for idx, row in test_sessions.iterrows():
        if idx % 100 == 0:
            logger.info(f"Evaluated {idx}/{len(test_sessions)} sessions")
        
        # Build session context
        context = {
            'recent_items': row['context_items'],
            'event_counts': {'purchase': len(row['context_items'])}
        }
        
        # Get recommendations
        recs = recommender.recommend(context, k=max(k_values))
        predicted = [r['item_id'] for r in recs]
        
        # Actual next item(s)
        actual = [row['target_item']]
        
        # Calculate metrics for each k
        for k in k_values:
            metrics[f'recall@{k}'].append(recall_at_k(actual, predicted, k))
            metrics[f'ndcg@{k}'].append(ndcg_at_k(actual, predicted, k))
            metrics[f'map@{k}'].append(mean_average_precision_at_k(actual, predicted, k))
    
    # Average metrics
    results = {}
    for metric_name, values in metrics.items():
        results[metric_name] = np.mean(values) if len(values) > 0 else 0.0
    
    logger.info("Evaluation Results:")
    for metric_name, value in results.items():
        logger.info(f"  {metric_name}: {value:.4f}")
    
    return results


if __name__ == "__main__":
    # Example usage
    logger.info("Evaluation module loaded")
