# torch-035: Paired model comparisons and uncertainty

## Level and prerequisites

Advanced; approximately 135 minutes. Direct prerequisites: `torch-034`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Model comparisons should preserve the pairing between predictions on the same held-out identities. The central investigation is concrete: Use truth a0, b1, c2 with A0, 2, 2 and B 1, 2, 3 in different dictionary order. The finish condition is paired squared-loss differences-1, 0, -1. test selection violates the declared boundary. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Model comparisons should preserve the pairing between predictions on the same held-out identities. Subtract per-record losses before averaging, so shared case difficulty remains represented. A bootstrap resamples observed units with replacement and estimates variability under a stated sampling model. It cannot repair biased data or create independent units from many duplicates. Related records may need group-level resampling rather than row-level draws.

PyTorch generators provide a local reproducible random stream for this calculation. A seed makes an implementation repeatable in the tested runtime, but does not make the inference assumptions valid. Keep model selection on validation data and freeze the final test before choosing a winner. A confidence interval or mean loss difference is one piece of evidence, not a complete release policy.

## Design decisions and when to use this method

Compare models on the same identified assessment units using a predeclared loss and subtraction order. Preserve the pairing before any resampling. Choose row, family or temporal-block resampling according to the unit whose variability the inference is meant to represent.

Treat a bootstrap over saved predictions as conditional on those fitted models and observed data. More resampling draws can reduce Monte Carlo approximation error, but cannot increase the number of independent assessment units or undo model selection on the final test. Combine uncertainty with practical effect size and other release gates rather than treating one interval as automatic approval.

## Paired TensorFlow comparison

Compare [tf-035](../../deep-learning-tensorflow/guides/tf-035.md) after deriving the shared numerical contract.

The paired TensorFlow route uses NumPy resampling over the same paired loss contract. PyTorch's local Generator offers an idiomatic tensor implementation, but framework agreement does not validate the bootstrap'sin dependence or representativeness assumptions.

## Vocabulary and concepts

**Paired difference:** The loss contrast for the same identified observation.

**Resampling unit:** The independent entity selected during a bootstrap draw.

**Selection bias:** Optimism introduced when evaluation results guide configuration choices.

**Local generator:** An explicit random-state object separate from unrelated global draws.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-035/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-035.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-035.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Align prediction dictionaries by stable IDs and check equal keysets. Calculate squared-error A minus squared-errorB for each ID. Sample indices with torch.rand int and an explicit Generator, then index the paired difference vector. Use the same resampling unit for both systems by resampling the already-paired values. Report independent count and selection history beside the estimate.

## Derive the paired contrast and the finite bootstrap law

Align by stable ID before calculating losses. The fixture's dictionary insertion orders differ, so zipping values would compare unrelated targets and predictions. The correct table is:

| ID | Truth | A prediction | B prediction | A squared loss | B squared loss | A minus B |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0 | 0 | 1 | 0 | 1 | -1 |
| b | 1 | 2 | 2 | 1 | 1 | 0 |
| c | 2 | 2 | 3 | 0 | 1 | -1 |

The mean contrast is \(\frac{-2}{3}\) in squared-target units. Its sign favors A for this loss and these three cases. It does not mean A wins on every possible metric, group or deployment condition. Equal key sets are required before indexing; silently dropping missing predictions can select an easier assessment subset.

Pairing preserves shared case difficulty. In general, \(\operatorname{Var}(\ell_A-\ell_B)=\operatorname{Var}(\ell_A)+\operatorname{Var}(\ell_B)-2\operatorname{Cov}(\ell_A,\ell_B)\). Independently resampling the two models discards that covariance and answers a different question. The particular fixture has B losses all equal to one, so its covariance term is zero; it is not by itself a strong counterexample for every unpaired bootstrap mistake.

A separate analytic example makes the dependence visible. Suppose two cases have losses A=[1, 11] and B=[0, 10]. Every paired difference is one, so every paired resampled mean is one. Independent resampling can pair the easy A loss with the hard B loss or vice versa and create variation that was absent from the paired contrast. This explains the method without claiming that the original three-case code exercised that different fixture.

For the actual differences[-1, 0, -1], an empirical draw has probability \(\frac{2}{3}\) of-1 and \(\frac{1}{3}\) of zero. Each bootstrap estimate averages three independent draws from that empirical distribution. Let K count the selected-1 values; then K has a Binomial(3, \(\frac{2}{3}\)) law and the estimate is-K/3:

| Resampled mean | Exact empirical probability |
| --- | --- |
| -1 | \(\frac{8}{27}\) |
| \(\frac{-2}{3}\) | \(\frac{12}{27}\) |
| \(\frac{-1}{3}\) | \(\frac{6}{27}\) |
| 0 | \(\frac{1}{27}\) |

The expected bootstrap mean is \(\frac{-2}{3}\) and its variance is \(\frac{2}{27}\) under this empirical resampling model. These are properties of resampling the three observed values, not a proof that the unknown population has this four-point distribution. The thousand generated estimates approximate these probabilities with random frequency variation. The reference checks shape, finiteness and the exact allowed range, not a guaranteed count for each value.

More draws refine the numerical approximation to that empirical distribution. They do not turn three cases into a thousand independent assessment observations. Even the ideal empirical percentile interval can be uninformative here: the lower tail includes-1 and the upper tail reaches zero. The code does not calculate or certify a particular confidence interval, and any interval method would still need its sampling assumptions and quantile convention stated.

If several rows come from one source family, resample families together when the intended independence is at that level. Define the estimand as well: equal family means and row-weighted population means differ when families have different sizes. Time dependence may require blocks or another design rather than an ordinary independent-row bootstrap. Stable row IDs alone do not resolve those dependencies.

The local torch.Generator makes this calculation reproducible without depending on unrelated global draws. A fresh generator seeded identically reproduces the index matrix in the tested environment. NumPy's generator in the paired TensorFlow route is a different random implementation; identical seed numbers do not require identical index matrices across the two libraries. Compare the statistical contract, allowed values and within-implementation replay rather than treating cross-library random bits as a shared oracle.

This resampling holds the fitted prediction vectors fixed. It does not include variation from retraining with a different initialization, batch order or training sample. If the decision concerns the whole fitting procedure, that uncertainty needs a broader experimental design. If test results are used to select another architecture, threshold or stopping rule, the test has become selection information. An unchanged filename cannot restore an untouched assessment boundary.

Finally, a negative point estimate is not a complete release decision. Record effect size, uncertainty, assessment coverage, severe failures and operating costs under their own evidence. The tiny fixture teaches pairing and resampling mechanics while making its limited independent sample size explicit.

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

**Expected:** mean \(\frac{-2}{3}\), favoring A on this loss fixture.

### Example C: Resample pairs reproducibly

The known range of per-record differences bounds every resampled mean. That independent bound can expose an indexing or reduction error.

```python
generator=torch.Generator().manual_seed(7); indices=torch.randint(0,3,(1000,3),generator=generator); estimates=difference[indices].mean(1)
assert tuple(estimates.shape)==(1000,) and torch.isfinite(estimates).all() and estimates.min()>=-1 and estimates.max()<=0
```

**Expected:** 1000finite estimates within-1..0.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: paired squared-loss differences-1, 0, -1. test selection violates the declared boundary. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Align predictions by ID.** Use truth a0, b1, c2 with A0, 2, 2 and B 1, 2, 3 in different dictionary order.
   **Expected:** paired squared-loss differences-1, 0, -1.
   **Verify:** Save the assertion results for exercise 1, including paired squared-loss differences-1, 0, -1.

2. **Interpret the average contrast.** Average the three paired differences.
   **Expected:** mean \(\frac{-2}{3}\), favoring A on this loss fixture.
   **Verify:** Save the assertion results for exercise 2, including mean \(\frac{-2}{3}\), favoring A on this loss fixture.

3. **Resample pairs reproducibly.** Draw 1000 three-index bootstrap samples with local Generator seed 7.
   **Expected:** 1000finite estimates within-1..0.
   **Verify:** Save the assertion results for exercise 3, including 1000finite estimates within-1..0.

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

If the contrast changes when dictionary order changes, repair the identity join. If a model lacks an assessment ID, stop instead of comparing a convenient intersection. If bootstrap draws exceed[-1, 0] here, inspect index bounds, axis reduction and whether the paired difference vector was actually sampled.

If an unpaired method gives different uncertainty, inspect the covariance and resampling unit rather than choosing the narrower result. If repeated seeds disagree, check generator ownership and preceding draws. If a thousand draws are presented as a thousand new test cases, restore the distinction between Monte Carlo approximation and independent evidence. If final-test feedback changed a configuration, record the selection history before interpreting the reported interval.

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
