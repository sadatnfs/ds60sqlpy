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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 47 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — logits, minibatches, modes, and a correct PyTorch training loop

### The mental model

`nn.Module` composes registered parameters and operations. For
multiclass classification, the final layer returns one **logit** per
class; `CrossEntropyLoss` combines log-softmax and negative
log-likelihood, so the model should not apply softmax first. Targets are
integer class indices with `torch.long` dtype.

A `DataLoader` defines batch and shuffle behavior. Training mode enables
dropout and batch-normalization updates; evaluation mode disables those
training behaviors but does not itself disable gradients. Use
`model.eval()` together with `torch.no_grad()` for validation.

### Worked examples and syntax anatomy

- **`DataLoader(dataset, batch_size=..., shuffle=...)`:** yields bounded feature/target batches and controls training order.
- **`model(features)`:** returns logits shaped `(batch, classes)` for multiclass classification.
- **`CrossEntropyLoss(logits, labels)`:** expects floating logits and `long` class indices shaped `(batch,)`.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — make the logits-and-label contract executable

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import torch
from torch import nn

model = nn.Linear(3, 2)
features = torch.tensor([[1.0, 0.0, -1.0], [0.5, 2.0, 1.0]])
labels = torch.tensor([0, 1], dtype=torch.long)
logits = model(features)
loss = nn.CrossEntropyLoss()(logits, labels)
print({"logit_shape": tuple(logits.shape),
       "label_shape": tuple(labels.shape), "loss": loss.item()})
assert logits.shape == (2, 2) and loss.ndim == 0
```

**Expected observation:** Two rows and two classes produce a `(2, 2)` logit tensor and one scalar batch loss.

**Assumption to name:** Class labels are zero-based indices and no softmax was applied before the loss.

### Focused example B — observe dropout differ between train and eval modes

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import torch
from torch import nn

torch.manual_seed(4702)
layer = nn.Dropout(p=0.5)
values = torch.ones(12)
layer.train()
train_output = layer(values)
layer.eval()
with torch.no_grad():
    eval_output = layer(values)
print({"train_zeros": int((train_output == 0).sum()),
       "eval_unchanged": bool(torch.equal(eval_output, values))})
assert torch.equal(eval_output, values)
```

**Expected observation:** Dropout randomly masks/scales values in training but becomes an identity operation in evaluation.

**Assumption to name:** A fixed seed controls the demonstration; production quality is not inferred from one mask.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define logits, minibatches, modes, and a correct PyTorch training loop in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Passing probabilities to `CrossEntropyLoss`, float labels, or evaluating while the model remains in training mode.

**Debug it deliberately:** Assert every batch's shape/dtype/device, inspect one loss and gradient norm, and compare repeated predictions in train versus eval mode.

**Stop condition:** Do not add schedulers, early stopping, or mixed precision until the basic loop overfits one tiny batch and validates correctly.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Add dropout to the MLP and compare results.

**Verify:** For task `Add dropout to the MLP and compare results`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






2. Implement a small minibatch training loop with `DataLoader`.

**Verify:** For task `Implement a small minibatch training loop with DataLoader`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







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

**Verify:** For task `Shape and dtype contract: Write assertions at the start of a classification training step for...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







4. **Validation implementation:** Implement an evaluation function that returns sample-weighted loss and accuracy, restores the caller's prior train/eval mode, and never retains an autograd graph.
   **Progressive hint:** Remember `was_training = model.training`, call eval and no_grad, aggregate counts, then restore train mode only if it was previously active.

**Verify:** For task `Validation implementation: Implement an evaluation function that returns sample-weighted loss...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.







5. **DataLoader reproducibility:** Run two shuffled DataLoaders with the same seed and compare batch order. Then state what changes when using worker processes.
   **Progressive hint:** Pass a seeded `torch.Generator`; worker initialization and external NumPy/Python randomness need their own deliberate seeds.

**Verify:** For task `DataLoader reproducibility: Run two shuffled DataLoaders with the same seed and compare batch...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







6. **Portable checkpoint:** Save model, optimizer, epoch, metric history, and configuration, then reload on CPU and resume one step. Explain `state_dict` versus serializing the entire model object.
   **Progressive hint:** Save plain state dictionaries plus architecture/config metadata. Use `map_location='cpu'` and recreate the model class before loading.

**Verify:** For task `Portable checkpoint: Save model, optimizer, epoch, metric history, and configuration, then re...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-47` — Day 47 — PyTorch Tensors, Modules, and Training Loops.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize logits, minibatches, modes, and a correct PyTorch training loop. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day47_pytorch_basics_nn_training_loop.md`
- learner artifact: `python/ds-60day/notebooks/day47_pytorch_basics_nn_training_loop.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
