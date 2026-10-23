# torch-017: Dropout, regularization, train and eval modes

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-016`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Regularization and training mode affect different parts of the experiment. The central investigation is concrete: Use weights1, -2 and compute L1and squared L2sums. The finish condition is L1=3; squared L2=5. output still requires grad; backward gives ones. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Regularization and training mode affect different parts of the experiment. An explicit L1orL2penalty adds a term to the objective. Dropout randomly zeroes activations during training and rescales retained values; in evaluation it returns the unmodified input. model.train and model.eval recursively set module behavior, but neither changes whether autograd records operations. Optimizer weight decay and an explicit penalty can have different semantics, especially for adaptive optimizers, so their names do not establish equivalence.

The fixture uses weights1, -2 and unit activations. It separates data loss from penalty, checks stochastic outputs by allowed values rather than a fixed random mask, and confirms deterministic evaluation. None of these checks proves that regularization improves held-out quality; that requires a controlled validation comparison.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-017](../../deep-learning-tensorflow/guides/tf-017.md) after deriving the shared numerical contract.

Keras commonly receives training=True/False per call; PyTorch modules store train/eval mode. Both need explicit stochastic-layer behavior. Keras regularizers and PyTorch optimizer weight_decay are not automatically identical; compare the actual objective or update rule.

## Vocabulary and concepts

**Regularization penalty:** A parameter-dependent term added to the training objective.

**Dropout mode:** Whether stochastic activation masking is applied.

**Weight decay:** An optimizer-specific parameter update policy requiring its own contract.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-017/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-017.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-017.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

nn.Dropout(p=.5) scales retained training activations by 1/(1-p). Call train or eval to select behavior. Compute sum(abs(w)) and sum(w²) for declared penalty conventions, then multiply by an explicit coefficient. A half-scaled squared penalty would have a different derivative. Keep metrics and penalty components separate in logs.

## Worked example / walkthrough

### Example A: Calculate two penalties

The squared L2penalty is not the square root norm. Naming the convention avoids a factor or square-root mismatch when comparing implementations.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

w=torch.tensor([1.,-2.]); assert w.abs().sum().item()==3 and w.square().sum().item()==5
```

**Expected:** L1=3; squared L2=5.

### Example B: Check evaluation dropout

The local inference behavior is deterministic. Other pipeline components can still be random, so a full model needs its own evaluation contract.

```python
drop=nn.Dropout(.5); drop.eval(); x=torch.ones((4,8))
assert torch.equal(drop(x),x) and torch.equal(drop(x),x)
```

**Expected:** both outputs exactly ones.

### Example C: Check training invariants

The test does not require a particular mask or count of zeros. Such a pattern would overfit the random implementation rather than the Dropout contract.

```python
drop.train(); sampled=drop(x)
assert tuple(sampled.shape)==(4,8) and set(sampled.unique().tolist())<={0.,2.}
```

**Expected:** shape(4, 8); only0or2.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: L1=3; squared L2=5. output still requires grad; backward gives ones. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate two penalties.** Use weights1, -2 and compute L1and squared L2sums.
   **Expected:** L1=3; squared L2=5.
   **Verify:** Save the assertion results for exercise 1, including L1=3; squared L2=5.

2. **Check evaluation dropout.** Apply Dropout.5 in eval mode to ones twice.
   **Expected:** both outputs exactly ones.
   **Verify:** Save the assertion results for exercise 2, including both outputs exactly ones.

3. **Check training invariants.** Switch the same layer to train mode and inspect output values.
   **Expected:** shape(4, 8); only0or2.
   **Verify:** Save the assertion results for exercise 3, including shape(4, 8); only0or2.

4. **Separate data and penalty terms.** Combine data loss2 with coefficient.1 times squared L2.
   **Expected:** penalty.5; total2.5.
   **Verify:** Save the assertion results for exercise 4, including penalty.5; total2.5.

5. **Differentiate the explicit penalty.** Differentiate .1*sum(v*v) at v=[1, -2].
   **Expected:** gradient [.2, -.4].
   **Verify:** Save the assertion results for exercise 5, including gradient [.2, -.4].

6. **Keep mode separate from gradients.** Set Dropout to eval and pass a requires_grad input.
   **Expected:** output still requires grad; backward gives ones.
   **Verify:** Save the assertion results for exercise 6, including output still requires grad; backward gives ones.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Regularization penalty, Dropout mode, Weight decay using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-016` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does Dropout make each training batch mean exactly unchanged?**

No. It preserves an expectation under its random masking policy. A finite batch can have a different mean.

**Is weight decay always L2regularization?**

No. Equivalence depends on the optimizer and implementation. For adaptive optimizers, de coupled weight decay is not generally the same as adding a squared penalty to the gradient.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-017, Dropout, regularization, train and eval modes.
Read courses/deep-learning-pytorch/guides/torch-017.md and courses/deep-learning-pytorch/lessons/torch-017.py. Direct prerequisites: `torch-016`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
