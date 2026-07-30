# Day 47 — PyTorch Tensors, Modules, and Training Loops

**Lesson ID:** `python-47` · **Level:** advanced · **Dependencies:** `deep-learning` · **Network:** offline

Day 46 exposed the core update sequence. Today you make the training procedure
more realistic with minibatches, explicit training/evaluation modes, and
validation-aware extensions.

## Learning objectives

By the end of the lesson, you can:

- convert NumPy feature arrays and labels to correctly typed tensors;
- build a classification MLP that returns logits;
- use `TensorDataset` and `DataLoader` for minibatches;
- switch correctly between `model.train()` and `model.eval()`; and
- reason about dropout, early stopping, schedulers, and optional mixed precision.

## Prerequisites

- Complete `python-46` (deep learning overview).
- Know stratified splitting and scaling from `python-34`–`python-35`.
- Use CPU by default; CUDA-specific acceleration is optional.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Logit | Unnormalized class score produced before softmax |
| Batch | Subset processed in one forward/backward update |
| `DataLoader` | Iterator that batches and optionally shuffles a dataset |
| Training mode | Enables training behavior such as dropout |
| Evaluation mode | Disables training-only behavior such as dropout |
| Dropout | Randomly zeros activations during training as regularization |
| Early stopping | Stops after validation performance fails to improve |
| Learning-rate scheduler | Changes the optimizer's rate over time |

`CrossEntropyLoss` expects logits shaped `(batch, classes)` and integer class
labels with dtype `torch.long`. Do not apply softmax before this loss.

## Worked example: one minibatch-safe epoch

```python
import torch


def train_one_epoch(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: torch.nn.Module,
) -> float:
    model.train()
    total_loss = 0.0
    total_rows = 0

    for features, labels in loader:
        optimizer.zero_grad()
        logits = model(features)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(features)
        total_rows += len(features)

    return total_loss / total_rows
```

Average by row rather than by batch so a smaller final batch does not receive
the same weight as every full batch. Evaluation should use `model.eval()` and
`torch.inference_mode()`.

The learner notebook scales before splitting for compactness. In your exercise,
improve the boundary: split first, fit `StandardScaler` only on training
features, then transform train and test separately.

## Learner exercises and progressive hints

1. Add dropout to the MLP and compare results.
2. Implement a small minibatch training loop with `DataLoader`.

### Progressive hints

1. Place `Dropout(p=...)` after an activation. Compare multiple seeded runs or
   validation curves, because one final accuracy is noisy.
2. Wrap float32 features and long labels in a `TensorDataset`; shuffle only the
   training loader. Move `zero_grad`, forward, loss, backward, and step inside
   the batch loop.

The separate solution proceeds to early stopping, `StepLR`, and CUDA mixed
precision. Mixed precision is an optional GPU optimization; the code path must
remain correct on CPU.

### Additional mastery practice

Build a training loop whose dtype, shape, mode, randomness, and checkpoint state can be inspected and resumed on CPU without hidden notebook state.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Shape and dtype contract:** Write assertions at the start of a classification training step for feature shape/dtype, target shape/dtype, and logits shape.
   **Progressive hint:** CrossEntropyLoss expects floating logits `(batch, classes)` and integer class indices `(batch,)` with dtype long.
4. **Validation implementation:** Implement an evaluation function that returns sample-weighted loss and accuracy, restores the caller's prior train/eval mode, and never retains an autograd graph.
   **Progressive hint:** Remember `was_training = model.training`, call eval and no_grad, aggregate counts, then restore train mode only if it was previously active.
5. **DataLoader reproducibility:** Run two shuffled DataLoaders with the same seed and compare batch order. Then state what changes when using worker processes.
   **Progressive hint:** Pass a seeded `torch.Generator`; worker initialization and external NumPy/Python randomness need their own deliberate seeds.
6. **Portable checkpoint:** Save model, optimizer, epoch, metric history, and configuration, then reload on CPU and resume one step. Explain `state_dict` versus serializing the entire model object.
   **Progressive hint:** Save plain state dictionaries plus architecture/config metadata. Use `map_location='cpu'` and recreate the model class before loading.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why are class labels `long` while input features are `float32`?
- What changes when `model.eval()` is omitted from a model with dropout?
- Why should the validation loader not shuffle for correctness or debugging?
- Where should a scheduler step occur, and why does the scheduler type matter?

Expected behavior: logits have two columns, validation accuracy is between 0 and
1, and minibatch loss generally decreases. Dropout is not guaranteed to improve
one small run.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| Target dtype error | Labels are float tensors | Convert labels with `dtype=torch.long` |
| Evaluation changes every call | Model left in training mode | Call `model.eval()` and use inference mode |
| Memory grows during evaluation | Graphs are still recorded | Use `torch.inference_mode()` |
| Scaling leaks test distribution | Scaler fit before split | Fit preprocessing on training data only |
| Windows worker process errors | Notebook multiprocessing behavior | Begin with `num_workers=0`; use a main guard in scripts |

Larger batches improve hardware throughput but use more memory and change
optimization dynamics. Smaller batches add gradient noise and more updates.

## Next step

- Work in the [Day 47 learner notebook](../notebooks/day47_pytorch_basics_nn_training_loop.ipynb).
- Then consult the
  [Day 47 solution](../solutions/day47_pytorch_basics_nn_training_loop/day47_solutions.md).
- Continue to [Day 48 — Transfer Learning](day48_transfer_learning_cnn.md).
