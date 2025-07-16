"""
model.py

Defines the ML model structure and forward pass.

Class:
- SimpleModel: Linear model with weight and bias parameters.
"""

import numpy as np

class SimpleModel:
    """
    Simple linear model: output = X @ W + b

    Attributes:
        W (np.ndarray): Weights matrix.
        b (np.ndarray): Bias vector.
    """
    def __init__(self, input_dim: int, output_dim: int):
        """
        Initialize weights and biases with small random values.

        Args:
            input_dim (int): Number of input features.
            output_dim (int): Number of output dimensions.
        """
        self.W = np.random.randn(input_dim, output_dim) * 0.01
        self.b = np.zeros(output_dim)

    def forward(self, X: np.ndarray) -> np.ndarray:
        """
        Compute forward pass.

        Args:
            X (np.ndarray): Input data matrix (samples x features).

        Returns:
            np.ndarray: Output predictions.
        """
        return X @ self.W + self.b
