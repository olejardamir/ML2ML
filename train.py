"""
train.py

Training loop to optimize the model parameters.

Functions:
- train(): Load data, initialize model, run training loop with gradient updates.
"""

import numpy as np
from ml_core_algorithm.data import load_data
from ml_core_algorithm.model import SimpleModel
from ml_core_algorithm.loss import mse_loss, mse_grad

def train(epochs: int = 100, lr: float = 0.01):
    """
    Train the SimpleModel using Mean Squared Error loss.

    Args:
        epochs (int): Number of training iterations.
        lr (float): Learning rate for gradient updates.
    """
    X, y = load_data()
    model = SimpleModel(input_dim=X.shape[1], output_dim=1)

    for epoch in range(epochs):
        # Forward pass
        preds = model.forward(X).flatten()

        # Compute loss
        loss = mse_loss(preds, y)

        # Compute gradient w.r.t predictions
        grad_preds = mse_grad(preds, y).reshape(-1, 1)

        # Compute gradients w.r.t weights and bias
        grad_W = X.T @ grad_preds
        grad_b = np.sum(grad_preds, axis=0)

        # Parameter update (gradient descent)
        model.W -= lr * grad_W
        model.b -= lr * grad_b

        if epoch % 10 == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch+1}/{epochs}: Loss = {loss:.4f}")

if __name__ == "__main__":
    train()
