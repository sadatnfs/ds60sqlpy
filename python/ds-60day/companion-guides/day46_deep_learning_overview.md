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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 46 learner notebook from this guide's **Next
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

## Concept deep dive — tensors, computation graphs, gradients, and the optimizer cycle

### The mental model

A neural network is a parameterized function composed from tensor
operations. The **forward pass** produces predictions and a loss.
Autograd records the computation graph and `backward()` applies the
chain rule to accumulate gradients in parameter `.grad` fields.
`optimizer.step()` then updates parameters according to those gradients.

Gradients accumulate by default, so a training step normally follows
`zero_grad → forward → loss → backward → step`. Evaluation additionally
switches training-specific module behavior off and disables gradient
tracking. A falling training loss is evidence of optimization, not of
generalization.

### Worked examples and syntax anatomy

- **`tensor.requires_grad_(True)`:** marks a leaf tensor whose derivative should be accumulated.
- **`loss.backward()`:** computes derivatives through the recorded graph and adds them to existing `.grad` values.
- **`optimizer.zero_grad(); ...; optimizer.step()`:** clears old gradients, computes a new step, and updates registered parameters.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — differentiate a scalar function by autograd

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import torch

x = torch.tensor(3.0, requires_grad=True)
y = x**2 + 2 * x
y.backward()
print({"y": y.item(), "dy_dx": x.grad.item()})
assert x.grad.item() == 8.0  # derivative: 2*x + 2 at x=3
```

**Expected observation:** Autograd returns derivative 8.0, matching the hand-derived chain rule.

**Assumption to name:** `x` is a scalar leaf and only one backward pass has contributed to its gradient.

### Focused example B — see gradient accumulation explicitly

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import torch

weight = torch.tensor(2.0, requires_grad=True)
(weight**2).backward()
first = weight.grad.item()
(weight**2).backward()
accumulated = weight.grad.item()
weight.grad.zero_()
cleared = weight.grad.item()
print({"first": first, "accumulated": accumulated, "cleared": cleared})
assert (first, accumulated, cleared) == (4.0, 8.0, 0.0)
```

**Expected observation:** A second backward call adds another gradient; clearing is an explicit part of each ordinary optimization step.

**Assumption to name:** Gradient accumulation is not intentionally being used to combine microbatches.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define tensors, computation graphs, gradients, and the optimizer cycle in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Forgetting `zero_grad`, calling `step` before `backward`, or evaluating with dropout active and gradient tracking enabled.

**Debug it deliberately:** Print tensor shape/dtype/device, `requires_grad`, loss value, gradient norms, parameter deltas, and train/validation curves for one tiny batch.

**Stop condition:** Stop training when loss is non-finite, gradients explode/vanish, validation degrades, or the data/label shape contract is uncertain.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Plot the loss over epochs.

**Verify:** For task `Plot the loss over epochs`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check.






2. Replace SGD with Adam and compare convergence.

**Verify:** For task `Replace SGD with Adam and compare convergence`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






3. Add one hidden layer and a ReLU activation.

**Verify:** For task `Add one hidden layer and a ReLU activation`, demonstrate the concrete requirement “3. Add one hidden layer and a ReLU activation” with explicit inputs, observable output, and one counterexample.







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

### Additional mastery practice

Trace tensor shapes, gradients, modes, and loss aggregation through a complete training step. Deep-learning code is correct only when its state transitions are explicit.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Autograd tracing:** For one scalar regression batch, annotate every line from `zero_grad()` through `step()`: which tensors receive gradients, when are they accumulated, and when do parameters change?
   **Progressive hint:** Gradients accumulate in parameter `.grad` fields during backward; the optimizer reads them during step. zero_grad clears the previous batch.

**Verify:** For task `Autograd tracing: For one scalar regression batch, annotate every line from zerograd() throug...`, demonstrate the concrete requirement “4. Autograd tracing: For one scalar regression batch, annotate every line from zero grad through step : which tensors receive gradients, when are they accumulated, and when do para” with explicit inputs, observable output, and one counterexample.







5. **Mode debugging:** Build a model with Dropout and BatchNorm, then compare repeated predictions in `train()` and `eval()` modes. Explain why `torch.no_grad()` is related but not interchangeable.
   **Progressive hint:** Mode changes module behavior; no_grad disables graph recording. Validation usually needs both `model.eval()` and `with torch.no_grad()`.

**Verify:** For task `Mode debugging: Build a model with Dropout and BatchNorm, then compare repeated predictions i...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







6. **Loss-aggregation edge case:** Compare averaging per-batch losses with a sample-weighted epoch loss when the final batch is smaller. Implement the correct aggregation.
   **Progressive hint:** Multiply each mean batch loss by batch size, sum, then divide by the number of examples.

**Verify:** For task `Loss-aggregation edge case: Compare averaging per-batch losses with a sample-weighted epoch l...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-46` — Day 46 — Deep Learning Overview.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize tensors, computation graphs, gradients, and the optimizer cycle. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day46_deep_learning_overview.md`
- learner artifact: `python/ds-60day/notebooks/day46_deep_learning_overview.ipynb`

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
