# torch-018: BatchNorm, LayerNorm and stateful normalization

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-017`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Normalization can introduce both state and cross-observation dependencies. The central investigation is concrete: Apply BatchNorm momentum.5 to rows1, 3 and3, 5. The finish condition is running mean1, 2; batch counter1. finite zeros with default affine initialization. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Normalization can introduce both state and cross-observation dependencies. BatchNorm uses batch statistics during training and updates running statistics for later inference. LayerNorm normalizes feature values within each record and does not mix unrelated batch rows. PyTorch BatchNorm momentum specifies the weight of the new batch statistic, whereas Keras momentum specifies the retention weight of the old statistic. Equal numeric momentum arguments therefore usually mean different updates.

PyTorch BatchNorm also distinguishes the variance estimate used for training normalization from the unbiased estimate used in the running-variance update. A comparison must name both. The fixture uses a batch with mean2, 4 and momentum.5 to check running mean1, 2 from zero. Evaluation must leave running state unchanged. Tokenwise LayerNorm is checked with a future-row perturbation to expose wrong-axis leakage.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-018](../../deep-learning-tensorflow/guides/tf-018.md) after deriving the shared numerical contract.

The paired TensorFlow lesson uses momentum.5, where both old/new coefficients co incident all y match. Away from.5, the momentum conventions differ. Compare variance estimators, epsilon, affine parameters and training/evaluation behavior before expect in g parity.

## Vocabulary and concepts

**Running statistic:** Persistent state updated from training batches.

**Momentum convention:** Which coefficient weights the old versus new statistic.

**Batch coupling:** One observation influencing another through shared statistics.

**LayerNorm axis:** The feature dimensions normalized within one observation.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-018/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-018.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-018.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

nn.BatchNorm1d(2, momentum=.5) treats columns as features for an(N, C)input. train mode updates running_mean and running_var; eval mode uses stored state. nn.LayerNorm(2) reduces the last two-feature dimension independently for each row. Its default epsilon and affine parameters are part of the comparison. Track num_batches_tracked as a buffer, separate from trainable weight and bias.

## Worked example / walkthrough

### Example A: Update a running mean

The batch mean is2, 4 and the new-statistic weight is.5. The result is not yet the full batch mean.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

bn=nn.BatchNorm1d(2,momentum=.5); x=torch.tensor([[1.,3.],[3.,5.]])
bn.train(); bn(x)
torch.testing.assert_close(bn.running_mean,torch.tensor([1.,2.]),atol=1e-6,rtol=0); assert bn.num_batches_tracked.item()==1
```

**Expected:** running mean1, 2; batch counter1.

### Example B: Freeze state during evaluation

Evaluation must not adapt to assessment batch composition. A forgotten eval call can mutate state and change predictions based on neighboring records.

```python
before=bn.running_mean.clone(); count=bn.num_batches_tracked.clone(); bn.eval(); bn(torch.tensor([[100.,200.]]))
assert torch.equal(before,bn.running_mean) and torch.equal(count,bn.num_batches_tracked)
```

**Expected:** running mean and batch counter unchanged.

### Example C: Check LayerNorm row independence

LayerNorm uses only the current row's features in this configuration. A sequence-wide or batch-wide reduction would fail the perturbation test.

```python
ln=nn.LayerNorm(2); alone=ln(torch.tensor([[1.,3.]])); together=ln(torch.tensor([[1.,3.],[100.,200.]]))
torch.testing.assert_close(alone[0],together[0],atol=1e-6,rtol=0)
```

**Expected:** first row matches within1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: running mean1, 2; batch counter1. finite zeros with default affine initialization. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Update a running mean.** Apply BatchNorm momentum.5 to rows1, 3 and3, 5.
   **Expected:** running mean1, 2; batch counter1.
   **Verify:** Save the assertion results for exercise 1, including running mean1, 2; batch counter1.

2. **Freeze state during evaluation.** Call the trained layer in eval mode on100, 200.
   **Expected:** running mean and batch counter unchanged.
   **Verify:** Save the assertion results for exercise 2, including running mean and batch counter unchanged.

3. **Check LayerNorm row independence.** Normalize1, 3alone and beside100, 200.
   **Expected:** first row matches within1e-6.
   **Verify:** Save the assertion results for exercise 3, including first row matches within1e-6.

4. **Inspect running variance convention.** From initial running variance1, use batch values1, 3whose unbiased variance is2 and momentum.5.
   **Expected:** running variance1.5 for each feature.
   **Verify:** Save the assertion results for exercise 4, including running variance1.5 for each feature.

5. **Translate momentum explicitly.** Compute updates with old mean0, batch mean10 and PyTorch momentum.1versus Keras momentum.1.
   **Expected:** PyTorch1; Keras9 under their respective conventions.
   **Verify:** Save the assertion results for exercise 5, including PyTorch1; Keras9 under their respective conventions.

6. **Handle a constant feature row.** Apply LayerNorm to5, 5 and inspect finiteness.
   **Expected:** finite zeros with default affine initialization.
   **Verify:** Save the assertion results for exercise 6, including finite zeros with default affine initialization.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Running statistic, Momentum convention, Batch coupling using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-017` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 BatchNorm1d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BatchNorm1d.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why can BatchNorm predictions depend on batch neighbors?**

In training mode, the mean and variance a recomputed across batch observations. Changing a neighbor changes those shared statistics.

**Why state buffers rather than just weights must be saved?**

Running statistics and batch counter affect future inference even when all trainable parameters are the same. A weights-only mental model misses that state.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-018, BatchNorm, LayerNorm and stateful normalization.
Read courses/deep-learning-pytorch/guides/torch-018.md and courses/deep-learning-pytorch/lessons/torch-018.py. Direct prerequisites: `torch-017`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
