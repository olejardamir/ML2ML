"""
loss.py

Implements loss functions and their gradients.

Functions:
- mse_loss(y_pred, y_true): Mean Squared Error loss.
- mse_grad(y_pred, y_true): Gradient of MSE w.r.t. predictions.
"""

import numpy as np

def mse_loss(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    """
    Compute Mean Squared Error loss.

    Args:
        y_pred (np.ndarray): Predicted values.
        y_true (np.ndarray): Ground truth values.

    Returns:
        float: Scalar loss.
    """
    return np.mean((y_pred - y_true) ** 2)

def mse_grad(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
    """
    Compute gradient of MSE loss w.r.t predictions.

    Args:
        y_pred (np.ndarray): Predicted values.
        y_true (np.ndarray): Ground truth values.

    Returns:
        np.ndarray: Gradient array same shape as inputs.
    """
    return 2 * (y_pred - y_true) / y_true.size
