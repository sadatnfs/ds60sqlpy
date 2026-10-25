# torch-030: Distributed gradients and accumulation semantics on CPU

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-029`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Distributed and accumulated gradients should represent a declared global objective. The central investigation is concrete: Combine means 2, 6 with counts 1, 3. The finish condition is global mean 5; unweighted shard mean 4. empty shard contributes 0; global mean 5. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-030`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-030.py` under `.learning/expansion/torch-030/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use reduction='sum' for each microbatch, call backward without stepping, then divide accumulated gradients by the total count before one step. Clear gradients before starting the accumulation group. Count active masked targets when appropriate, not merely tensor storage size. If a distributed backend averages gradients across ranks, the local loss scaling must account for that reduction and unequal local counts.

## Derive the global gradient and the reduction factor

Let rank or shard r contain n_r participating examples, local gradient sum S_r and local mean \(g_{r}=\frac{S_{r}}{n_{r}}\) when \(n_{r}>0\). The global example-mean gradient is \(\frac{\sum_r S_r}{\sum_r n_r}\), equivalently \(\frac{\sum_r n_rg_r}{N}\). For means 2 and 6 with counts 1 and 3, the numerator is \(2+18=20\) and \(N=4\), giving five. Averaging the two means gives four and defines a different objective with equal shard weight.

The vector[2, 4, 6, 8] is an independent four-example oracle. Splitting it 1:3 gives sums 2 and 18, which recombine to \(\frac{20}{4}=5\). An empty shard contributes sum zero and count zero; its local mean need not be evaluated at all. A globally empty collection has \(N=0\) and must not be divided by zero or described as a valid zero-gradient batch without an explicit skip policy.

For the actual squared-loss fixture, x=[1, 2, 3, 4], y=2x and \(w=0\). The per-example derivatives are \(-4x^2\), or[-4, -16, -36, -64]. Their sum is-120 and global mean-30. The two backward calls in Example C accumulate the summed objectives at the same unchanged w, then divide once by four. One SGD update at 0.01 gives \(w=0.3\).

Stepping after each microbatch changes both normalization and evaluation state. The first one-row mean has gradient-4, so w becomes 0.04. The second three-row mean is then evaluated at that new value and has derivative(58/3)(0.04-2), approximately-37.893333. Its second update ends at approximately 0.418933, not 0.3. This discrepancy is expected because it is a different optimization trajectory, not an accumulation bug to hide with a tolerance.

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

means=torch.tensor([2.,6.]); counts=torch.tensor([1.,3.])
assert (means*counts).sum().div(counts.sum()).item()==5 and means.mean().item()==4
```

**Expected:** global mean 5; unweighted shard mean 4.

### Example B: Reconstruct an example mean

The per-example vector is an independent oracle for the shard formula. It catches a checker that merely repeats a wrong averaging assumption.

```python
values=torch.tensor([2.,4.,6.,8.]); parts=[values[:1],values[1:]]
assert sum(part.sum() for part in parts).div(sum(part.numel() for part in parts)).item()==values.mean().item()==5
```

**Expected:** global mean 5.

### Example C: Accumulate one full-batch gradient

The weight remains fixed across both backward calls. Accumulation is intentional here, and its denominator is applied exactly once.

```python
x=torch.arange(1,5,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
for start,end in [(0,1),(1,4)]: ((w*x[start:end]-y[start:end])**2).sum().backward()
w.grad.div_(4)
assert w.grad.item()==-30
oracle=torch.tensor(0.,dtype=torch.float64,requires_grad=True); full=((oracle*x-y)**2).mean(); assert torch.autograd.grad(full,oracle)[0].item()==-30
```

**Expected:** gradient-30, matching full-batch mean.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: global mean 5; unweighted shard mean 4. empty shard contributes 0; global mean 5. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Weight unequal shard means.** Combine means 2, 6 with counts 1, 3.
   **Expected:** global mean 5; unweighted shard mean 4.
   **Verify:** Save the assertion results for exercise 1, including global mean 5; unweighted shard mean 4.

2. **Reconstruct an example mean.** Split gradients 2, 4, 6, 8 into one and three elements and recombine sums/counts.
   **Expected:** global mean 5.
   **Verify:** Save the assertion results for exercise 2, including global mean 5.

3. **Accumulate one full-batch gradient.** At \(w=0\), use x 1..4, y = 2x, accumulate squared-loss sums for shards 1 and 3, and divide by 4.
   **Expected:** gradient-30, matching full-batch mean.
   **Verify:** Save the assertion results for exercise 3, including gradient-30, matching full-batch mean.

4. **Apply one accumulated update.** Take SGD.01 after the global gradient is formed.
   **Expected:** new weight.3.
   **Verify:** Save the assertion results for exercise 4, including new weight.3.

5. **Contrast separate microbatch updates.** Reset w0and step after each shard mean instead.
   **Expected:** endpoint differs from.3.
   **Verify:** Save the assertion results for exercise 5, including endpoint differs from.3.

6. **Represent empty-shard contributions.** Combine an empty shard and the four real gradients using sums and counts.
   **Expected:** empty shard contributes 0; global mean 5.
   **Verify:** Save the assertion results for exercise 6, including empty shard contributes 0; global mean 5.

## Common pitfalls and diagnosis

If gradients differ by a constant factor, inspect local loss reduction, global valid count and the backend's sum-versus-average rule. If only unequal batches fail, compare n_r explicitly instead of assuming rank means have equal denominators. If the endpoint differs after microbatching, check whether parameters were stepped between contributions.

If an empty shard hangs a distributed experiment, the arithmetic zero contribution is not the whole participation contract; inspect collective ordering and the chosen uneven-input mechanism. If accumulation changes results despite correct weighting, inspect BatchNorm, dropout and cross-example objectives. Keep regularization and optimizer-step frequency visible. A successful CPU mean calculation is not evidence of multi-process setup, device behavior or scaling.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Global objective, Microbatch accumulation, Sha rd weighting using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-029` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

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
