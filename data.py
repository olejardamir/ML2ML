"""
data.py

Handles input data loading and preprocessing.

Functions:
- load_data(): Load or generate dataset.
- preprocess(inputs): Normalize or encode input features.
"""

import numpy as np

def preprocess(inputs: np.ndarray) -> np.ndarray:
    """
    Normalize inputs to zero mean and unit variance.

    Args:
        inputs (np.ndarray): Raw input data.

    Returns:
        np.ndarray: Normalized data.
    """
    return (inputs - np.mean(inputs, axis=0)) / np.std(inputs, axis=0)

def load_data():
    """
    Load or generate dataset for training/testing.

    Returns:
        tuple: (features, labels) as numpy arrays.
    """
    # Placeholder: synthetic binary classification data
    X = np.random.randn(100, 10)  # 100 samples, 10 features
    y = np.random.randint(0, 2, size=(100,))  # binary labels 0 or 1
    X = preprocess(X)
    return X, y
