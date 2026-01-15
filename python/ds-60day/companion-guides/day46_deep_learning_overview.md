# Day 46 — Deep Learning Overview (Companion Guide)

## Learning objectives
- Understand tensors, computation graphs, and automatic differentiation
- Compare classic ML vs deep learning; when to use which
- Know common architectures: MLPs, CNNs, RNNs/Transformers (high level)

## Why this matters
Deep learning powers state-of-the-art results in vision, language, and speech. A big-picture map helps you choose the right tool and avoid common traps.

## Mental models
- A model is a function with parameters; training adjusts parameters to minimize loss via gradient descent
- Depth = stacked nonlinear transforms that learn hierarchical features

## Core concepts and examples
### Tensors and autograd (PyTorch flavor)
```python
import torch
x = torch.randn(4, 3, requires_grad=True)
w = torch.randn(3, 2, requires_grad=True)
y = x @ w
loss = y.pow(2).mean()
loss.backward()  # populates x.grad and w.grad
```

### Optimization loop (concept)
- Forward pass → compute loss
- Backward pass → compute grads
- Optimizer step → update params

### Common architectures
- MLP: fully connected layers for tabular/simple signals
- CNN: local receptive fields and weight sharing for images
- RNN/LSTM/GRU: sequence modeling (now often replaced by Transformers)
- Transformers: attention mechanisms for long-range dependencies

## Common pitfalls
- Not tracking data/label leakage and distribution shift
- Using too large/complex models for the dataset size
- Ignoring proper splits and cross-validation

## Practice exercises
1) Build a tiny MLP on a toy dataset; vary depth/width and observe overfitting
2) Compare SGD vs Adam on convergence speed
3) Explain vanishing/exploding gradients and mitigation strategies

## Further reading
- Dive into DL: https://d2l.ai
- Transformers: https://arxiv.org/abs/1706.03762
