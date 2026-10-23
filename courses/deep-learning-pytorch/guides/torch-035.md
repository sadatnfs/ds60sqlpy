# torch-035: Paired model comparisons and uncertainty

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-034`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Model comparisons should preserve the pairing between predictions on the same held-out identities. The central investigation is concrete: Use truth a0, b1, c2 with A0, 2, 2 andB1, 2, 3 in different dictionary order. The finish condition is paired squared-loss differences-1, 0, -1. test selection violates the declared boundary. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Model comparisons should preserve the pairing between predictions on the same held-out identities. Subtract per-record losses before averaging, so shared case difficulty remains represented. A bootstrap resamples observed units with replacement and estimates variability under a stated sampling model. It cannot repair biased data or create independent units from many duplicates. Related records may need group-level resampling rather than row-level draws.

PyTorch generators provide a local reproducible random stream for this calculation. A seed makes an implementation repeatable in the tested runtime, but does not make the inference assumptions valid. Keep model selection on validation data and freeze the final test before choosing a winner. A confidence interval or mean loss difference is one piece of evidence, not a complete release policy.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-035](../../deep-learning-tensorflow/guides/tf-035.md) after deriving the shared numerical contract.

The paired TensorFlow route uses NumPy resampling over the same paired loss contract. PyTorch's local Generator offers an idiomatic tensor implementation, but framework agreement does not validate the bootstrap'sin dependence or representativeness assumptions.

## Vocabulary and concepts

**Paired difference:** The loss contrast for the same identified observation.

**Resampling unit:** The independent entity selected during a bootstrap draw.

**Selection bias:** Optimism introduced when evaluation results guide configuration choices.

**Local generator:** An explicit random-state object separate from unrelated global draws.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-035/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-035.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-035.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Align prediction dictionaries by stable IDs and check equal keysets. Calculate squared-error A minus squared-errorB for each ID. Sample indices with torch.rand int and an explicit Generator, then index the paired difference vector. Use the same resampling unit for both systems by resampling the already-paired values. Report independent count and selection history beside the estimate.

## Worked example / walkthrough

### Example A: Align predictions by ID

Dictionary insertion order is not an identity join. The contrast must keep each prediction attached to its own target.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

truth={'a':0.,'b':1.,'c':2.}; a={'a':0.,'b':2.,'c':2.}; b={'c':3.,'a':1.,'b':2.}; ids=sorted(truth)
difference=torch.tensor([(a[i]-truth[i])**2-(b[i]-truth[i])**2 for i in ids],dtype=torch.float64)
assert difference.tolist()==[-1.,0.,-1.]
```

**Expected:** paired squared-loss differences-1, 0, -1.

### Example B: Interpret the average contrast

The sign follows the declared A-minus-Blossorder. A negative value favors A only for this metric and assessment set.

```python
np.testing.assert_allclose(difference.mean().item(),-2/3,atol=1e-12,rtol=0)
```

**Expected:** mean-2/3, favoring A on this loss fixture.

### Example C: Resample pairs reproducibly

The known range of per-record differences bounds every resampled mean. That independent bound can expose an indexing or reduction error.

```python
generator=torch.Generator().manual_seed(7); indices=torch.randint(0,3,(1000,3),generator=generator); estimates=difference[indices].mean(1)
assert tuple(estimates.shape)==(1000,) and torch.isfinite(estimates).all() and estimates.min()>=-1 and estimates.max()<=0
```

**Expected:** 1000 finite estimates within-1..0.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: paired squared-loss differences-1, 0, -1. test selection violates the declared boundary. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Align predictions by ID.** Use truth a0, b1, c2 with A0, 2, 2 andB1, 2, 3 in different dictionary order.
   **Expected:** paired squared-loss differences-1, 0, -1.
   **Verify:** Save the assertion results for exercise 1, including paired squared-loss differences-1, 0, -1.

2. **Interpret the average contrast.** Average the three paired differences.
   **Expected:** mean-2/3, favoring A on this loss fixture.
   **Verify:** Save the assertion results for exercise 2, including mean-2/3, favoring A on this loss fixture.

3. **Resample pairs reproducibly.** Draw1000 three-index bootstrap samples with local Generator seed 7.
   **Expected:** 1000 finite estimates within-1..0.
   **Verify:** Save the assertion results for exercise 3, including 1000 finite estimates within-1..0.

4. **Replay the local random stream.** Create a new Generator with seed 7 and compare the index matrix.
   **Expected:** exact match.
   **Verify:** Save the assertion results for exercise 4, including exact match.

5. **Reject missing assessment identities.** Remove c from one prediction dictionary and check the keyset.
   **Expected:** mismatch detected before comparison.
   **Verify:** Save the assertion results for exercise 5, including mismatch detected before comparison.

6. **Preserve a final-test boundary.** Record configuration choice on validation and assessment on test; flag a test-driven new choice.
   **Expected:** test selection violates the declared boundary.
   **Verify:** Save the assertion results for exercise 6, including test selection violates the declared boundary.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Paired difference, Resampling unit, Selection bias using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-034` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why resample differences rather than each model separately?**

The models were evaluated on the same cases. Separate resampling discards their dependence and answers a different uncertainty question.

**Can more bootstrap draws compensate for only three assessment units?**

No. More draws approximate the empirical resampling distribution more closely; they do not add new independent evidence.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-035, Paired model comparisons and uncertainty.
Read courses/deep-learning-pytorch/guides/torch-035.md and courses/deep-learning-pytorch/lessons/torch-035.py. Direct prerequisites: `torch-034`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
