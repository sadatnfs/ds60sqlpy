# torch-009: Batches, zero_grad and repeated updates

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-008`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

An epoch is a traversal of selected records; a batch is the set reduced before an update; an optimizer step changes parameters once. The central investigation is concrete: Partition IDs1..6 into batches of 2. The finish condition is three batches[[1, 2], [3, 4], [5, 6]]. epoch mean4, not5. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

An epoch is a traversal of selected records; a batch is the set reduced before an update; an optimizer step changes parameters once. These counts differ. Six records with batch size 2 produce three updates per epoch, while batch size 1 produces six. Later batches see weights changed by earlier updates, so equal epochs do not imply equal trajectories. PyTorch also accumulates gradients unless they are clear e d, which can accidentally turn a minibatch loop into an unplanned accumulation scheme.

Record IDs should travel with features and targets. A final short batch is retained unless drop_last is explicitly chosen. Its mean loss uses its own number of examples. To report an epoch mean from unequal batches, accumulate loss sums and counts rather than averaging batch means equally. This lesson makes the loop explicit before introducing DataLoader configuration.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-009](../../deep-learning-tensorflow/guides/tf-009.md) after deriving the shared numerical contract.

TensorFlow and PyTorch share batch/epoch/step semantics, but PyTorch leaf.grad accumulation makes the zero_grad policy explicit in a standard loop. In either framework, a short batch changes the correct weighting of per-batch metrics.

## Vocabulary and concepts

**Epoch:** One traversal of the chosen observation set.

**Batch:** The observations contributing to one gradient reduction.

**Gradient reset:** Clearing stored derivatives before an independent update.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-009/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-009.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-009.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Slice the leading observation axis into batches. For each independent update, call zero_grad(set_to_none=True), compute the current mean loss, backward and step. Log parameter values after each step and counts separately from epochs. A shared index permutation preserves x/y pairing. Changing only one side creates a different learning task even when marginal distributions remain unchanged.

## Worked example / walkthrough

### Example A: Count batches and updates

The update count is the number of batches when there is one step per batch. It is neither the number of examples nor the number of epochs.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

ids=list(range(1,7)); batches=[ids[i:i+2] for i in range(0,len(ids),2)]
assert batches==[[1,2],[3,4],[5,6]]
```

**Expected:** three batches[[1, 2], [3, 4], [5, 6]].

### Example B: Retain a short tail

Dropping the last singleton would change the effective training set. Record that choice explicitly when fixed batch shapes are required.

```python
short=[list(range(5))[i:i+2] for i in range(0,5,2)]
assert [len(batch) for batch in short]==[2,2,1]
```

**Expected:** batch sizes2, 2, 1.

### Example C: Run three independent updates

Each derivative is evaluated at the latest weight. Clearing the gradient prevents earlier batches from being counted again accidentally.

```python
x=torch.arange(1,7,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); optimizer=torch.optim.SGD([w],lr=.01); history=[]
for start in range(0,6,2):
    optimizer.zero_grad(set_to_none=True); loss=((w*x[start:start+2]-y[start:start+2])**2).mean(); loss.backward(); optimizer.step(); history.append(w.item())
assert len(history)==3 and np.isfinite(history).all() and len(set(history))==3
```

**Expected:** three finite distinct weights.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: three batches[[1, 2], [3, 4], [5, 6]]. epoch mean4, not5. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Count batches and updates.** Partition IDs1..6 into batches of 2.
   **Expected:** three batches[[1, 2], [3, 4], [5, 6]].
   **Verify:** Save the assertion results for exercise 1, including three batches[[1, 2], [3, 4], [5, 6]].

2. **Retain a short tail.** Partition five IDs with batch size 2.
   **Expected:** batch sizes2, 2, 1.
   **Verify:** Save the assertion results for exercise 2, including batch sizes2, 2, 1.

3. **Run three independent updates.** Train x1..6, y2 x, w0 with batch size 2, rate.01, clearing gradients each batch.
   **Expected:** three finite distinct weights.
   **Verify:** Save the assertion results for exercise 3, including three finite distinct weights.

4. **Expose accidental accumulation.** Repeat the loop without zero_grad and compare its final weight with the correct run.
   **Expected:** different endpoint.
   **Verify:** Save the assertion results for exercise 4, including different endpoint.

5. **Shuffle paired records together.** Use permutation5, 0, 4, 1, 3, 2 for both x andy.
   **Expected:** every shuffled target equals twice its input.
   **Verify:** Save the assertion results for exercise 5, including every shuffled target equals twice its input.

6. **Aggregate unequal batch means.** Combine mean loss2 over2 examples and mean loss8 over1 example.
   **Expected:** epoch mean4, not5.
   **Verify:** Save the assertion results for exercise 6, including epoch mean4, not5.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Epoch, Batch, Gradient reset using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-008` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Is forgetting zero_grad a harmless learning-rate change?**

Usually not. The accumulated derivative mixes gradients evaluated at different parameter states, so it changes the trajectory rather than applying one constant scale.

**Can two batch sizes be compared by equal epochs alone?**

They process the same number of records but may perform different numbers of updates and use different state trajectories. Report both budgets.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-009, Batches, zero_grad and repeated updates.
Read courses/deep-learning-pytorch/guides/torch-009.md and courses/deep-learning-pytorch/lessons/torch-009.py. Direct prerequisites: `torch-008`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
