# torch-030: Distributed gradients and accumulation semantics on CPU

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-029`.

## Learning objectives

Combine gradients across shards and microbatches so that they represent the declared global mean objective.

Central investigation: Weight shard means by their counts, accumulate summed squared-loss gradients over shards of sizes 1 and 3, and contrast separate microbatch steps.

Finish condition: Shard means 2 and 6 with counts 1 and 3 give 5 rather than 4, the accumulated gradient is -30 like the full batch, one SGD step gives \(w=0\).3, separate steps end elsewhere, and an empty shard contributes 0.

Exercises 1-3 repeat the worked examples as guided reconstructions; exercises 4-6 change the fixture or expose a failure.

## Purpose and mental model

Distributed and accumulated gradients should represent a declared global objective. Equal averaging of shard means weights shards equally, not examples. If one shard contains one observation with mean gradient 2 and another contains three with mean 6, the global example mean is 5 rather than 4. The same issue appears with unequal microbatches on one CPU.

To reproduce a full-batch mean through accumulation, hold parameters fixed while adding gradient sums, divide by the total active count, and apply one optimizer update. Stepping after each microbatch is a different trajectory because later gradients use changed weights. Distributed Data Parallel has its own reduction semantics; this lesson does not launch multiple processes or claim scaling. It derives the weighting rule that a real distributed implementation must preserve and explains which additional runtime evidence would be required.

## Design decisions and when to use this method

Define the global statistical objective before choosing communication or accumulation mechanics. Decide whether examples, tokens, weights or groups receive equal influence, and carry the corresponding denominator alongside every local numerator. Equal rank weight is correct only when that is the intended objective or local denominators agree.

Use the one-CPU fixture to validate the algebra and one-update boundary. A real distributed run additionally needs compatible process participation, collective ordering, parameter state and failure handling. Do not infer those operational properties from a correct scalar weighted mean.

## Paired TensorFlow comparison

Compare [tf-030](../../deep-learning-tensorflow/guides/tf-030.md) after deriving the shared numerical contract.

TensorFlow distributed strategies and PyTorchDDP can use different default reduction conventions. The paired CPU arithmetic establishes the intended example-weighted result; it does not demonstrate either backend's communication, scaling or failure behavior.

## Vocabulary and concepts

**Global objective:** The loss definition over all participating examples.

**Microbatch accumulation:** Combining derivatives before one parameter update.

**Sha rd weighting:** The rule assigning contributions from differently sized partitions.

**Distributed acceptance:** Actual multi-process behavior and failure evidence beyond scalar arithmetic.

## How to run this lesson

Run `torch-030` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C need only the imports at the top of Example A.

## Syntax anatomy and reasoning sequence

Use reduction='sum' for each microbatch, call backward without stepping, then divide accumulated gradients by the total count before one step. Clear gradients before starting the accumulation group. Count active masked targets when appropriate, not merely tensor storage size. If a distributed backend averages gradients across ranks, the local loss scaling must account for that reduction and unequal local counts.

## Derive the global gradient and the reduction factor

Let rank or shard r contain n_r participating examples, local gradient sum S_r and local mean \(g_{r}=\frac{S_{r}}{n_{r}}\) when \(n_{r}>0\). The global example-mean gradient is \(\frac{\sum_r S_r}{\sum_r n_r}\), equivalently \(\frac{\sum_r n_rg_r}{N}\). For means 2 and 6 with counts 1 and 3, the numerator is \(2+18=20\) and \(N=4\), giving five. Averaging the two means gives four and defines a different objective with equal shard weight.

The vector [2, 4, 6, 8] is an independent four-example oracle. Splitting it 1:3 gives sums 2 and 18, which recombine to \(\frac{20}{4}=5\). An empty shard contributes sum zero and count zero; its local mean need not be evaluated at all. A globally empty collection has \(N=0\) and must not be divided by zero or described as a valid zero-gradient batch without an explicit skip policy.

For the actual squared-loss fixture, x=[1, 2, 3, 4], y=2x and \(w=0\). The per-example derivatives are \(-4x^2\), or [-4, -16, -36, -64]. Their sum is -120 and global mean -30. The two backward calls in Example C accumulate the summed objectives at the same unchanged w, then divide once by four. One SGD update at 0.01 gives \(w=0.3\).

Stepping after each microbatch changes both normalization and evaluation state. The first one-row mean has gradient -4, so w becomes 0.04. The second three-row mean is then evaluated at that new value and has derivative (58/3)(0.04-2), approximately -37.893333. Its second update ends at approximately 0.418933, not 0.3. This discrepancy is expected because it is a different optimization trajectory, not an accumulation bug to hide with a tolerance.

A distributed reducer introduces another factor. Under a fixed R-rank configuration that averages gradients across ranks, backpropagating a local summed loss divided by global N would produce only \(\frac{1}{R}\) of the intended global gradient after averaging. One appropriate local scaling for this stated convention is \(L_r=\frac{R}{N}\sum_i\ell_{ri}\). The reducer then returns \(\frac1R\sum_r\frac{RS_r}{N}=\frac{\sum_rS_r}{N}\). Equivalently, weight each nonempty local mean by R \(\frac{n_{r}}{N}\). When all n_r are equal, the ordinary mean of local means already has the intended weighting.

That derivation assumes the documented reducer behavior and a fixed participation set. Custom communication hooks, uneven-input mechanisms and changed divisors require a fresh derivation. PyTorch DDP documents that its gradient synchronization semantics depend on the loss reduction and participating processes. [PyTorch 2.9 DistributedDataParallel](https://docs.pytorch.org/docs/2.9/generated/torch.nn.parallel.DistributedDataParallel.html). The current lesson launches no process group and therefore verifies none of that communication behavior experimentally.

Padding and sample weights replace the simple n_r with the relevant valid weight mass. Counting tensor storage positions instead of supervised tokens can scale the gradient according to padding. A rank with no valid targets may still need to participate in the distributed protocol; simply skipping its backward while other ranks enter collectives can be an operational error. The CPU arithmetic handles an empty contribution, but a real implementation needs a separately tested participation policy.

Regularization also needs one global meaning. If the objective is mean data loss plus lambda R(theta), adding the full regularizer independently for every accumulated microbatch and then summing multiplies its contribution by the microbatch count. Add it once per intended update or distribute its coefficient deliberately. Optimizer weight decay has its own update semantics and likewise should not be assumed equivalent when the number of optimizer steps changes.

The equivalence requires more than denominators. Parameters and relevant model state must stay fixed while local contributions are formed. BatchNorm statistics, dropout draws, contrastive negative sets and cross-example losses can differ when a large batch is split. Even a mathematically correct reduction cannot make those different forward computations identical. For stateful optimizers, the one-step boundary preserves the intended momentum/adaptive update count; multiple steps change that history.

A future distributed acceptance packet should join the global objective, rank counts, actual reducer convention, parameter synchronization, cancellation and next-step parity. It should also report communication and throughput only after those quantities are measured. The paired TensorFlow chapter derives the same global arithmetic but does not qualify a TensorFlow strategy or a PyTorch backend merely by simulating shards on one CPU.

## Worked example / walkthrough

### Example A: Weight unequal shard means

Each mean must be multiplied by its denominator to recover a sum. Averaging means directly discards that information.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

means = torch.tensor([2.0, 6.0])
counts = torch.tensor([1.0, 3.0])
assert (means * counts).sum().div(counts.sum()).item() == 5 and means.mean().item() == 4
```

**Expected:** global mean 5; unweighted shard mean 4.

### Example B: Reconstruct an example mean

The per-example vector is an independent oracle for the shard formula. It catches a checker that merely repeats a wrong averaging assumption.

```python
values = torch.tensor([2.0, 4.0, 6.0, 8.0])
parts = [values[:1], values[1:]]
assert (
    sum(part.sum() for part in parts).div(sum(part.numel() for part in parts)).item()
    == values.mean().item()
    == 5
)
```

**Expected:** global mean 5.

### Example C: Accumulate one full-batch gradient

The weight remains fixed across both backward calls. Accumulation is intentional here, and its denominator is applied exactly once.

```python
x = torch.arange(1, 5, dtype=torch.float64)
y = 2 * x
w = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
for start, end in [(0, 1), (1, 4)]:
    ((w * x[start:end] - y[start:end]) ** 2).sum().backward()
w.grad.div_(4)
assert w.grad.item() == -30
oracle = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
full = ((oracle * x - y) ** 2).mean()
assert torch.autograd.grad(full, oracle)[0].item() == -30
```

**Expected:** gradient -30, matching full-batch mean.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Weight unequal shard means. Predict exercise 6, Represent empty-shard contributions, from its prompt alone: Combine an empty shard and the four real gradients using sums and counts. Then explain why this finish condition holds: Shard means 2 and 6 with counts 1 and 3 give 5 rather than 4, the accumulated gradient is -30 like the full batch, one SGD step gives \(w=0\).3, separate steps end elsewhere, and an empty shard contributes 0. Keep each prediction beside the observed value.

## Exercises

1. **Weight unequal shard means.** Combine means 2, 6 with counts 1, 3.
   **Expected:** global mean 5; unweighted shard mean 4.
   **Verify:** In a fresh process, the exercise checks confirm `(means * counts).sum().div(counts.sum()).item() == 5` and `means.mean().item() == 4`.

2. **Reconstruct an example mean.** Split gradients 2, 4, 6, 8 into one and three elements and recombine sums/counts.
   **Expected:** global mean 5.
   **Verify:** In a fresh process, the exercise checks confirm the combined assertion.

3. **Accumulate one full-batch gradient.** At \(w=0\), use \(x=(1, 2, 3, 4)\) and \(y=2x\), accumulate squared-loss sums for shards of sizes 1 and 3, and divide by the total sample count 4.
   **Expected:** gradient -30, matching full-batch mean.
   **Verify:** In a fresh process, the exercise checks confirm `w.grad.item() == -30` and `torch.autograd.grad(full, oracle)[0].item() == -30`.

4. **Apply one accumulated update.** Take one SGD step with learning rate 0.01 after the global gradient is formed.
   **Expected:** new weight 0.3.
   **Verify:** In a fresh process, the exercise checks confirm `w.item()` matches `0.3` within 1e-12.

5. **Contrast separate microbatch updates.** Reset w to 0 and step after each shard mean instead.
   **Expected:** endpoint differs from 0.3.
   **Verify:** In a fresh process, the exercise checks confirm `abs(other.item() - 0.3) > 1e-06`.

6. **Represent empty-shard contributions.** Combine an empty shard and the four real gradients using sums and counts.
   **Expected:** empty shard contributes 0; global mean 5.
   **Verify:** In a fresh process, the exercise checks confirm `denominator == 4` and `numerator.div(denominator).item() == 5`.

## Common pitfalls and diagnosis

If gradients differ by a constant factor, inspect local loss reduction, global valid count and the backend's sum-versus-average rule. If only unequal batches fail, compare n_r explicitly instead of assuming rank means have equal denominators. If the endpoint differs after microbatching, check whether parameters were stepped between contributions.

If an empty shard hangs a distributed experiment, the arithmetic zero contribution is not the whole participation contract; inspect collective ordering and the chosen uneven-input mechanism. If accumulation changes results despite correct weighting, inspect BatchNorm, dropout and cross-example objectives. Keep regularization and optimizer-step frequency visible. A successful CPU mean calculation is not evidence of multi-process setup, device behavior or scaling.

## Progressive hints

Hint 1: Example B (Reconstruct an example mean) alters one assumption of Example A (Weight unequal shard means). Hint 2: exercise 4, Apply one accumulated update, should end at new weight 0.3. Work backward from it. Hint 3: exercise 5, Contrast separate microbatch updates, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Accumulate one full-batch gradient, from its inputs alone. Predict whether exercise 3, Accumulate one full-batch gradient, survives one changed input. Then explain Global objective, Microbatch accumulation, Sha rd weighting in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Weight unequal shard means) cannot be rebuilt without help, revisit `torch-029` first. `torch-031` (Profiling, torch.compile and honest performance measurement) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22 for the Global objective, Microbatch accumulation, Sha rd weighting behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Why is an average of means sometimes wrong?**

The groups may have different denominators. It gives equal group weight rather than equal example weight unless that is the intended objective.

**What remains untested after this CPU lesson?**

Actual process-group setup, collective ordering, uneven-input handling, cancellation, device behavior and throughput. Those require a separate distributed runtime experiment.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-030, Distributed gradients and accumulation semantics on CPU.
Read courses/deep-learning-pytorch/guides/torch-030.md and courses/deep-learning-pytorch/lessons/torch-030.py. Direct prerequisites: `torch-029`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
