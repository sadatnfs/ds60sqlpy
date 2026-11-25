# torch-009: Batches, zero_grad and repeated updates

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-008`.

## Learning objectives

Relate epochs, batches and optimizer steps, and combine unequal batch means with record-count weights.

Central investigation: Partition record IDs into batches, train three cleared updates on x = 1..6 and repeat the loop without zero_grad.

Finish condition: Six IDs give three batches, five give sizes 2, 2, 1, the cleared run produces three distinct finite weights, omitting zero_grad changes the endpoint, and batch means 2 and 8 over 2 and 1 records combine to 4, not 5.

## Purpose and mental model

An epoch is a traversal of selected records; a batch is the set reduced before an update; an optimizer step changes parameters once. These counts differ. Six records with batch size 2 produce three updates per epoch, while batch size 1 produces six. Later batches see weights changed by earlier updates, so equal epochs do not imply equal trajectories. PyTorch also accumulates gradients unless they are cleared, which can accidentally turn a minibatch loop into an unplanned accumulation scheme.

Record IDs should travel with features and targets. A final short batch is retained unless drop_last is explicitly chosen. Its mean loss uses its own number of examples. To report an epoch mean from unequal batches, accumulate loss sums and counts rather than averaging batch means equally. This lesson makes the loop explicit before introducing DataLoader configuration.

## Design decisions and when to use this method

Choose batch size together with the intended update budget, memory budget and statistical unit. Equal epochs do not imply equal optimizer-step counts, and equal step counts do not imply equal numbers of observed records. Record both when comparing runs. Keep a short final batch unless a documented shape or algorithm requirement justifies dropping it.

Use zero_grad between independent minibatch updates. If memory constraints require accumulation, define a separate policy that holds parameters fixed while accumulating correctly weighted contributions and steps once at the intended boundary. Do not treat a loop that steps repeatedly on an uncleared gradient as an equivalent large-batch implementation.

## Paired TensorFlow comparison

Compare [tf-009](../../deep-learning-tensorflow/guides/tf-009.md) after deriving the shared numerical contract.

TensorFlow and PyTorch share batch/epoch/step semantics, but PyTorch `leaf.grad` accumulation makes the zero_grad policy explicit in a standard loop. In either framework, a short batch changes the correct weighting of per-batch metrics.

## Vocabulary and concepts

**Epoch:** One traversal of the chosen observation set.

**Batch:** The observations contributing to one gradient reduction.

**Gradient reset:** Clearing stored derivatives before an independent update.

## How to run this lesson

Run `torch-009` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C need only the imports at the top of Example A.

## Syntax anatomy and reasoning sequence

Slice the leading observation axis into batches. For each independent update, call `zero_grad(set_to_none=True)`, compute the current mean loss, backward and step. Log parameter values after each step and counts separately from epochs. A shared index permutation preserves x/y pairing. Changing only one side creates a different learning task even when marginal distributions remain unchanged.

## Trace every update at the state where its gradient was computed

Six records with batch size two produce three batches per epoch: IDs [1, 2], [3, 4], [5, 6]. With one optimizer step per batch, one epoch means three updates. At batch size one, the same epoch means six updates. Neither count identifies the resulting parameter trajectory without the data order, loss reduction and learning rate.

For this scalar fixture, \(y=2x\) and each batch mean loss has derivative \(2\operatorname{mean}(x^2)(w-2)\). With learning rate \(\eta=0.01\), the exact correct trajectory is:

| Batch inputs | \(\operatorname{mean}({x}^{2})\) | Weight before | Fresh gradient | Weight after |
| --- | --- | --- | --- | --- |
| [1, 2] | 2.5 | 0 | -10 | 0.1 |
| [3, 4] | 12.5 | 0.1 | -47.5 | 0.575 |
| [5, 6] | 30.5 | 0.575 | -86.925 | 1.44425 |

Each gradient uses the latest weight. Clearing the buffer before each backward ensures that the applied gradient is precisely the one shown in its row. The same records in a different order can yield another trajectory because their local curvature and current parameter state differ.

Without clearing, the first step is still 0.1. The next backward adds -47.5 to the stored -10, giving -57.5, and the second weight becomes 0.675. The final fresh derivative is -80.825, but the accumulated buffer becomes -138.325 and the final weight 2.05825. These are derivatives evaluated at different historical weights. A single constant learning-rate adjustment does not turn this procedure into the intended minibatch algorithm.

Interestingly, the incorrect endpoint happens to lie closer to the known optimum two on this tiny sequence. That does not make the implementation correct. It violated the declared update rule, and another sequence can behave very differently. An acceptance test must inspect the mechanism and state trace rather than reward whichever accidental final training loss is smaller.

Intentional accumulation is different. Hold w fixed, compute each microbatch's contribution to one declared objective, accumulate the scaled gradients, and call step once. For the full six-record mean at \(w=0\), the gradient is 2 \(\operatorname{mean}({x}^{2})\)(-2)=-182/3. One rate 0.01 step gives \(\frac{91}{150}\), about 0.606667. This differs from the three-step minibatch result because it is one update from one fixed state. When microbatch sizes differ, weight each microbatch mean by its participating count divided by the total count.

Metric reporting needs the same denominator discipline. A mean loss two from two records contributes numerator four; mean loss eight from one record contributes numerator eight. The record-weighted mean is (4+8)/3=4, not the unweighted batch-mean average five. But there is another interpretation boundary: losses measured before successive updates belong to different model states. Their weighted average is an online training statistic, not necessarily the loss of the final model. A final-model metric requires a separate fixed-state evaluation pass.

Record identities protect the training population. A shared permutation of x and y preserves y=2x after shuffling. Independently permuting either side changes the prediction task while leaving each marginal array plausible. For five records at batch size two, the tail has one record; dropping it changes which observations participated in the epoch. The loop should retain that decision in its budget and denominator report.

## Worked example / walkthrough

### Example A: Count batches and updates

The update count is the number of batches when there is one step per batch. It is neither the number of examples nor the number of epochs.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

ids = list(range(1, 7))
batches = [ids[i : i + 2] for i in range(0, len(ids), 2)]
assert batches == [[1, 2], [3, 4], [5, 6]]
```

**Expected:** three batches [[1, 2], [3, 4], [5, 6]].

### Example B: Retain a short tail

Dropping the last singleton would change the effective training set. Record that choice explicitly when fixed batch shapes are required.

```python
short = [list(range(5))[i : i + 2] for i in range(0, 5, 2)]
assert [len(batch) for batch in short] == [2, 2, 1]
```

**Expected:** batch sizes 2, 2, 1.

### Example C: Run three independent updates

Each derivative is evaluated at the latest weight. Clearing the gradient prevents earlier batches from being counted again accidentally.

```python
x = torch.arange(1, 7, dtype=torch.float64)
y = 2 * x
w = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
optimizer = torch.optim.SGD([w], lr=0.01)
history = []
for start in range(0, 6, 2):
    optimizer.zero_grad(set_to_none=True)
    loss = ((w * x[start : start + 2] - y[start : start + 2]) ** 2).mean()
    loss.backward()
    optimizer.step()
    history.append(w.item())
assert len(history) == 3 and np.isfinite(history).all() and len(set(history)) == 3
```

**Expected:** three finite distinct weights.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Count batches and updates. Predict exercise 6, Aggregate unequal batch means, from its prompt alone: Combine mean loss 2 over 2 examples and mean loss 8 over 1 example. Then explain why this finish condition holds: Six IDs give three batches, five give sizes 2, 2, 1, the cleared run produces three distinct finite weights, omitting zero_grad changes the endpoint, and batch means 2 and 8 over 2 and 1 records combine to 4, not 5. Keep each prediction beside the observed value.

## Exercises

1. **Partition with batch size 4.** Partition IDs 1..10 into batches of 4 without dropping the tail.
   **Expected:** batch sizes 4, 4, 2; the last batch is [9, 10].
   **Verify:** In a fresh process, the exercise checks confirm `[len(batch) for batch in quads] == [4, 4, 2]` and `quads[-1] == [9, 10]`.

2. **Count updates with a dropped tail.** With 10 records, batch size 4 and the short tail dropped, count optimizer steps per epoch and over 3 epochs.
   **Expected:** 2 steps per epoch and 6 in total; records 9 and 10 never contribute in unshuffled order.
   **Verify:** In a fresh process, the exercise checks confirm `steps_per_epoch == 2`; `3 * steps_per_epoch == 6` and `[i for batch in quads[:steps_per_epoch] for i in batch] == list(range(1, 9))`.

3. **Trace two single-record updates.** Train w from 0 on x = 1, 2 with y = 2x, batch size 1 and learning rate 0.1, clearing gradients before each step.
   **Expected:** weights 0.4 then 1.68.
   **Verify:** In a fresh process, the exercise checks confirm `trace` matches `[0.4, 1.68]` within 1e-12.

4. **Expose accidental accumulation.** Repeat the loop without zero_grad and compare its final weight with the correct run.
   **Expected:** different endpoint.
   **Verify:** In a fresh process, the exercise checks confirm `abs(bad.item() - history[-1]) > 1e-06`.

5. **Shuffle paired records together.** Use permutation 5, 0, 4, 1, 3, 2 for both x and y.
   **Expected:** every shuffled target equals twice its input.
   **Verify:** In a fresh process, the exercise checks confirm `sy` matches `2 * sx` exactly.

6. **Aggregate unequal batch means.** Combine mean loss 2 over 2 examples and mean loss 8 over 1 example.
   **Expected:** epoch mean 4, not 5.
   **Verify:** In a fresh process, the exercise checks confirm `(2 * 2 + 8 * 1) / 3 == 4` and `(2 + 8) / 2 == 5`.

## Common pitfalls and diagnosis

If the number of steps is wrong, inspect the batch slices and tail policy before looking at the optimizer. If a second step is too large, inspect whether the gradient buffer still contains a prior contribution. Compare the exact 0.1, 0.575, 1.44425 trace with the incorrect uncleared trajectory rather than accepting only a finite endpoint.

If batch-size changes appear to improve a model, compare examples seen, update count and ordering before attributing the result to batch size alone. If an epoch metric depends on how records are partitioned into batches, reconstruct loss sums and counts. If it is reported as a final-model score, check whether all records were evaluated at one fixed final state. Finally, keep record IDs through shuffling so a correct-looking tensor shape cannot hide broken target pairing.

## Progressive hints

Hint 1: Example B (Retain a short tail) alters one assumption of Example A (Count batches and updates). Hint 2: exercise 4, Expose accidental accumulation, should end at different endpoint. Work backward from it. Hint 3: exercise 5, Shuffle paired records together, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Run three independent updates, from its inputs alone. Predict whether exercise 3, Trace two single-record updates, survives one changed input. Then explain Epoch, Batch, Gradient reset in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Count batches and updates) cannot be rebuilt without help, revisit `torch-008` first. `torch-010` (Datasets, held-out families and leakage controls) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22 for the Epoch, Batch, Gradient reset behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Is forgetting zero_grad a harmless learning-rate change?**

Usually not. The accumulated derivative mixes gradients evaluated at different parameter states, so it changes the trajectory rather than applying one constant scale.

**Can two batch sizes be compared by equal epochs alone?**

They process the same number of records but may perform different numbers of updates and use different state trajectories. Report both budgets.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-009, Batches, zero_grad and repeated updates.
Read courses/deep-learning-pytorch/guides/torch-009.md and courses/deep-learning-pytorch/lessons/torch-009.py. Direct prerequisites: `torch-008`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
