"""
utils.py

Helper functions for evaluation metrics and misc utilities.

Functions:
- accuracy(y_pred, y_true, threshold): Compute binary classification accuracy.
"""

import numpy as np

def accuracy(y_pred: np.ndarray, y_true: np.ndarray, threshold: float = 0.5) -> float:
    """
    Calculate classification accuracy for binary predictions.

    Args:
        y_pred (np.ndarray): Predicted probabilities or scores.
        y_true (np.ndarray): True binary labels.
        threshold (float): Threshold for converting scores to binary labels.

    Returns:
        float: Accuracy score between 0 and 1.
    """
    preds = (y_pred > threshold).astype(int)
    return np.mean(preds == y_true)
