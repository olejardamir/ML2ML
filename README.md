# Minimalist ML Core Code Checklist

**Scope:**  
This checklist focuses **strictly on functional code components** required to build an ML algorithm.

- Model definition  
- Forward pass (inference)  
- Loss calculation  
- Gradient updates (learning process)  
- Input/output handling (directly relevant to the algorithm)

---

## 1. Define Inputs

- **Input format specification**  
  - Raw data: vectors, matrices, images, text, etc.
  - Preprocessing code (normalization, tokenization, encoding)

## 2. Define Outputs

- **Output format specification**  
  - Class labels, regression values, probabilities, control signals
  - Postprocessing (e.g., softmax, argmax)

## 3. Model Definition

- **Model structure**  
  - Neural network layers, regression equations, tree structures, etc.
- **Parameter initialization**  
  - Weights, biases, stored examples (for k-NN), etc.

## 4. Forward Pass (Inference)

- **Transformation from input to output**  
  - Feedforward computation
  - Output generation (without gradient)

## 5. Performance Objective

- **Loss function / objective function**  
  - Mean squared error, cross-entropy, etc.
  - Custom domain-specific losses (if applicable)

## 6. Learning Process

- **Gradient calculation**  
  - Analytical gradients or autodiff (e.g., PyTorch, TensorFlow)
- **Parameter updates**  
  - Optimizer: SGD, Adam, etc.
  - Update rule: `θ = θ - α∇L`
- **Training loop**  
  - Batch iteration over data
  - Epoch control

---

## 7. Optional Algorithmic Features

| Feature               | Description                              | Status   |
|----------------------|------------------------------------------|----------|
| Memory-based learning | Stores examples (k-NN, case reasoning)   | 🟧 Optional |
| Structural adaptation | Modifies model structure (e.g., trees)   | 🟧 Optional |
| Online learning loop  | Streaming or per-sample updates          | 🟧 Optional |

---

## Summary of Core ML Components

| Component                        | Mandatory? |
|---------------------------------|------------|
| Input data pipeline (preprocessing only) | ✅ |
| Output formatting (postprocessing only)   | ✅ |
| Model definition & initialization        | ✅ |
| Forward pass (inference)                 | ✅ |
| Loss function                            | ✅ |
| Gradient calculation & update rule      | ✅ |
| Training loop (batch or online)          | ✅ |
| Optional algorithm extensions (k-NN, tree growth, etc.) | 🟧 |

---

## Visual Summary

```mermaid
graph TD
A[Input Data] --> B[Preprocessing]
B --> C[Model Forward Pass]
C --> D[Output Prediction]

D --> E[Loss Function]
E --> F[Gradient Calculation]
F --> G[Parameter Update]

G --> C
