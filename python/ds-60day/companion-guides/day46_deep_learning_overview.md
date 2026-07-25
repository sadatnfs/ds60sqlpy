# Day 46 — Deep Learning Overview

**Lesson ID:** `python-46` · **Level:** advanced · **Dependencies:** `deep-learning` · **Network:** offline

This survey introduces tensors, automatic differentiation, and a small PyTorch
training loop. CPU execution is the supported baseline. Other frameworks are
part of the broader ecosystem, but this course requires and installs only the
declared PyTorch stack.

## Learning objectives

By the end of the lesson, you can:

- distinguish tensors, parameters, activations, loss, and gradients;
- explain the forward pass, backward pass, and optimizer step;
- train a small linear or multilayer model with PyTorch;
- record and interpret a loss curve; and
- compare optimizer and capacity changes without claiming one run is universal.

## Prerequisites

- Complete `python-45` (end-to-end modeling project).
- Recall linear models, matrix multiplication, and train/validation boundaries.
- Install the `deep-learning` dependency group while connected. No model or
  dataset download is needed for this lesson.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Tensor | Multidimensional typed array used by PyTorch |
| Parameter | Tensor registered for optimization, usually with gradients enabled |
| Computation graph | Recorded operations connecting inputs, parameters, and output |
| Autograd | Automatic calculation of derivatives through the graph |
| Loss | Differentiable objective minimized during training |
| Gradient | Derivative of loss with respect to a parameter |
| Optimizer | Rule that updates parameters from gradients |
| Epoch | One pass through the training observations |
| Activation | Nonlinear function between learned linear layers |

The repeated training sequence is:
**clear gradients → forward pass → compute loss → backward pass → update**.
Changing that order can silently accumulate gradients or update the wrong state.

## Worked example: deterministic linear regression

```python
import torch

torch.manual_seed(42)
X = torch.linspace(-1, 1, 200).unsqueeze(1)
y = 2.0 * X - 0.5 + 0.1 * torch.randn_like(X)

model = torch.nn.Linear(1, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
loss_fn = torch.nn.MSELoss()
history: list[float] = []

for _ in range(200):
    optimizer.zero_grad()
    prediction = model(X)
    loss = loss_fn(prediction, y)
    loss.backward()
    optimizer.step()
    history.append(loss.item())
```

The seed controls parameter initialization and generated noise on this CPU path.
Hardware and library differences can still affect exact floating-point results,
so reproducibility means bounded, explainable variation—not bitwise identity
everywhere.

## Learner exercises

1. Plot the loss over epochs.
2. Replace SGD with Adam and compare convergence.
3. Add one hidden layer and a ReLU activation.

### Progressive hints

1. Append `loss.item()` once per epoch; use a logarithmic y-axis if early values
   obscure later improvement.
2. Recreate the model from the same seed for a fair comparison. Adam and SGD
   generally need different learning rates, so report both settings.
3. A one-input regression MLP can use
   `Linear(1, width) → ReLU() → Linear(width, 1)`.

The separate solution extends these ideas with train/validation curves,
capacity comparisons, and gradient-stability techniques. Treat those as deeper
reference material after completing the notebook's three exercises.

## Self-check

- Why must `optimizer.zero_grad()` run before `backward()` in this loop?
- What tensor shapes enter and leave `Linear(1, 1)`?
- Why can lower training loss accompany worse validation performance?
- What changes when ReLU is inserted between two linear layers?

Expected behavior: loss should generally decline and the learned slope/intercept
should approach the generated relationship. A single temporary increase does
not necessarily mean training failed.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| Loss is `nan` or explodes | Learning rate too large or unstable gradients | Lower the rate; inspect inputs/gradients |
| Loss never changes | No registered parameters, no backward call, or update omitted | Inspect `list(model.parameters())` and loop order |
| Results differ every run | Seed not set before data/model creation | Seed once before random operations |
| Hidden model memorizes training data | Excess capacity/no validation | Add a held-out curve and regularization |
| GPU assumed necessary | Survey confused with scale | Keep the toy workload on CPU |

Adam often converges quickly with little tuning; SGD can generalize well and is
easier to reason about, but may need momentum and schedules. Compare evidence,
not brand names.

## Next step

- Work in the [Day 46 learner notebook](../notebooks/day46_deep_learning_overview.ipynb).
- Then review the
  [Day 46 solution](../solutions/day46_deep_learning_overview/day46_solutions.md).
- Continue to [Day 47 — PyTorch Training Loops](day47_pytorch_basics_nn_training_loop.md).
