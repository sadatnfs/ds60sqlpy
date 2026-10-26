# torch-009: Batches, zero_grad and repeated updates

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: `torch-008`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

An epoch is a traversal of selected records; a batch is the set reduced before an update; an optimizer step changes parameters once. The central investigation is concrete: Partition IDs 1..6 into batches of 2. The finish condition is three batches[[1, 2], [3, 4], [5, 6]]. epoch mean 4, not 5. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-009`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-009.py` under `.learning/expansion/torch-009/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Slice the leading observation axis into batches. For each independent update, call `zero_grad(set_to_none=True)`, compute the current mean loss, backward and step. Log parameter values after each step and counts separately from epochs. A shared index permutation preserves x/y pairing. Changing only one side creates a different learning task even when marginal distributions remain unchanged.

## Trace every update at the state where its gradient was computed

Six records with batch size two produce three batches per epoch: IDs[1, 2], [3, 4], [5, 6]. With one optimizer step per batch, one epoch means three updates. At batch size one, the same epoch means six updates. Neither count identifies the resulting parameter trajectory without the data order, loss reduction and learning rate.

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

Metric reporting needs the same denominator discipline. A mean loss two from two records contributes numerator four; mean loss eight from one record contributes numerator eight. The record-weighted mean is(4+8)/3=4, not the unweighted batch-mean average five. But there is another interpretation boundary: losses measured before successive updates belong to different model states. Their weighted average is an online training statistic, not necessarily the loss of the final model. A final-model metric requires a separate fixed-state evaluation pass.

Record identities protect the training population. A shared permutation of x and y preserves y=2x after shuffling. Independently permuting either side changes the prediction task while leaving each marginal array plausible. For five records at batch size two, the tail has one record; dropping it changes which observations participated in the epoch. The loop should retain that decision in its budget and denominator report.

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

**Expected:** batch sizes 2, 2, 1.

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

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: three batches[[1, 2], [3, 4], [5, 6]]. epoch mean 4, not 5. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Count batches and updates.** Partition IDs 1..6 into batches of 2.
   **Expected:** three batches[[1, 2], [3, 4], [5, 6]].
   **Verify:** Save the assertion results for exercise 1, including three batches[[1, 2], [3, 4], [5, 6]].

2. **Retain a short tail.** Partition five IDs with batch size 2.
   **Expected:** batch sizes 2, 2, 1.
   **Verify:** Save the assertion results for exercise 2, including batch sizes 2, 2, 1.

3. **Run three independent updates.** Train x = 1..6, y = 2x, w = 0 with batch size 2, rate 0.01, clearing gradients each batch.
   **Expected:** three finite distinct weights.
   **Verify:** Save the assertion results for exercise 3, including three finite distinct weights.

4. **Expose accidental accumulation.** Repeat the loop without zero_grad and compare its final weight with the correct run.
   **Expected:** different endpoint.
   **Verify:** Save the assertion results for exercise 4, including different endpoint.

5. **Shuffle paired records together.** Use permutation 5, 0, 4, 1, 3, 2 for both x and y.
   **Expected:** every shuffled target equals twice its input.
   **Verify:** Save the assertion results for exercise 5, including every shuffled target equals twice its input.

6. **Aggregate unequal batch means.** Combine mean loss 2 over 2 examples and mean loss 8 over 1 example.
   **Expected:** epoch mean 4, not 5.
   **Verify:** Save the assertion results for exercise 6, including epoch mean 4, not 5.

## Common pitfalls and diagnosis

If the number of steps is wrong, inspect the batch slices and tail policy before looking at the optimizer. If a second step is too large, inspect whether the gradient buffer still contains a prior contribution. Compare the exact 0.1, 0.575, 1.44425 trace with the incorrect uncleared trajectory rather than accepting only a finite endpoint.

If batch-size changes appear to improve a model, compare examples seen, update count and ordering before attributing the result to batch size alone. If an epoch metric depends on how records are partitioned into batches, reconstruct loss sums and counts. If it is reported as a final-model score, check whether all records were evaluated at one fixed final state. Finally, keep record IDs through shuffling so a correct-looking tensor shape cannot hide broken target pairing.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Epoch, Batch, Gradient reset using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-008` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

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
