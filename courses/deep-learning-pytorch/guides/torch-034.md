# torch-034: Robustness, privacy and evidence beyond a score

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-033`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A reliability report should preserve the conditions and denominators behind a score. The central investigation is concrete: Use groups A, A, B with truth 1, 1, 0 and prediction 1, 0, 0. The finish condition is A1/2errors; B0/1. card explicitly has no privacy guarantee. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A reliability report should preserve the conditions and denominators behind a score. Group A with zero errors in one case does not provide the same evidence as zero errors in hundreds of independent cases. Duplicate records can improve an apparent rate without testing new conditions. Perturbation tests need a label policy: crossing a legitimate decision boundary may change the correct target rather than reveal a robustness failure.

Privacy and safety claims require their own mechanisms and evidence. A synthetic fixture containing no personal data does not establish differential privacy. A finite set of successful adversarial checks does not prove all future inputs are safe. This chapter uses Torch tensors for error accounting and controlled perturbations, then writes a bounded model-card record with untested conditions and failure severity.

## Design decisions and when to use this method

Define the evaluation unit, conditions and failure severity before aggregating a score. Preserve numerator and denominator for each declared group, and distinguish an untested group from a tested group with zero observed errors. Choose any deduplication or weighting rule from the intended unit of analysis rather than deleting repeated-looking rows automatically.

Use perturbations only under an explicit target interpretation. Record privacy claims only when an actual mechanism and its analysis support them. The synthetic arrays are suitable for learning evidence accounting; they establish no privacy mechanism or universal robustness guarantee.

## Paired TensorFlow comparison

Compare [tf-034](../../deep-learning-tensorflow/guides/tf-034.md) after deriving the shared numerical contract.

The paired TensorFlow lesson uses the same evidence principles. Framework choice does not change the independence unit, duplicate policy or meaning of a privacy claim. Compare model behavior under identical conditions and keep framework runtime acceptance separate from task reliability.

## Vocabulary and concepts

**Subgroup denominator:** The observation count supporting a group metric.

**Robustness condition:** A specified input change under a declared label policy.

**Finite safety evidence:** Observed results on bounded cases without a universal guarantee.

**Model card:** A record of intended use, evidence and limitations.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-034/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-034.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-034.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Compute boolean error vectors before aggregation. Groupby declared labels and retain integer error/count pairs. Compare row count with unique ID count to expose duplicates. Use None for an untested group rather than a rate of zero. Keep severity categories separate from overall pass rate, and make the decision gate explicit before inspecting results.

## Keep population, perturbation and mechanism claims separate

The original three records contain one error: groupA has \(\frac{1}{2}\) and groupB has 0/1. Overall error is \(\frac{1}{3}\). Repeating the correct record c five additional times creates eight rows but only three unique IDs. A naive row-weighted error becomes \(\frac{1}{8}\) even though no new case was tested. The apparent improvement comes entirely from changing the weight of one existing success.

This counterexample does not imply that every repeated identity should be removed. A longitudinal task may legitimately contain several observations from one person or device. The question is which unit the reported quantity is intended to average over, and whether dependence is modeled. Exact duplicate detection, source-family grouping and a weighting policy are related but different controls. A set of three IDs alone also does not prove those units are statistically independent.

Zero errors among one observation is weak evidence about an unknown error probability. Under a deliberately stated independent Bernoulli sampling model, the chance of observing zero errors in n cases is \((1-p)^n\). Solving \((1-p)^n=0.05\) gives a one-sided 95% upper bound \(1-{0.05}^{\frac{1}{n}}\):0.95 at \(n=1\) and approximately 0.0295 at \(n=100\). This arithmetic illustrates why denominators matter. The hand-selected synthetic cases do not automatically satisfy the random-sampling assumptions needed to interpret that bound as a population claim.

An empty group has no measured rate. Returning None preserves that absence; returning zero invents a successful observation. A report or chart should not replace missing rates with zero merely to fill a display. Likewise, a confidence calculation cannot create coverage for a group or condition that never appeared in the data. Keep coverage counts and the intended target population beside every aggregate.

The perturbation rule here is f(x)=1 when \(x\ge 0\). Starting at one, the shifts-0.1, -0.9, -1.1 produce 0.9, 0.1, -0.1 and therefore labels 1, 1, 0. If the target itself is defined by the observed sign, the final change is correct behavior after crossing the decision boundary. Calling it a robustness failure would assume an invariant label that the task definition does not support.

A different application might model these shifts as measurement noise while the latent class remains fixed. That is a different target policy and needs its own oracle. For this simple sign rule, perturbations with magnitude strictly below one cannot cross from the starting point to the negative side. That analytic statement is local to this scalar rule and declared perturbation set; it is not evidence that an arbitrary neural classifier is robust to all small changes.

Severity is another independent axis. Nine minor passes and one severe failure yield a90% overall pass rate. If the predeclared release rule blocks on any severe failure, the correct decision remains no-go. Choosing a favorable aggregate after observing the severe failure changes the decision policy. Preserve case-level identity, severity and the actual failed condition so a summary cannot erase it.

Privacy is not established by removing names from an example or by obtaining a good accuracy score. Differential privacy describes a randomized mechanism's output behavior under a defined change to a dataset. Its guarantee depends on the neighboring-dataset unit, privacy parameters and the mechanism/accounting assumptions. Record-level adjacency and person-level adjacency are different promises when a person contributes multiple rows. Clipping, noise, sampling and repeated releases require a coherent analysis; this chapter implements none of them. [NIST SP 800-226](https://csrc.nist.gov/pubs/sp/800/226/final) discusses evaluation of such guarantees and implementation hazards.

An empirical privacy attack test and a mathematical privacy guarantee answer different questions. Failing to observe leakage in a few attempts does not prove a bound over all neighboring datasets and outputs. Conversely, a claimed formal bound does not remove the need to inspect the actual implementation, access controls and intended release. The lesson's model card therefore records synthetic teaching use and no privacy guarantee rather than promoting absence of personal data into a property of the training algorithm.

A useful card joins intended use, data/version identity, evaluation units, group counts, perturbation policy, severity results and untested conditions. It can summarize existing evidence but does not create it. The paired TensorFlow route uses the same reasoning fixtures, so framework choice does not change the denominator, independence or privacy interpretation.

## Worked example / walkthrough

### Example A: Count group errors

Counts keep the evidence visible. Equal rates with different denominators do not imply equal uncertainty.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

truth=torch.tensor([1,1,0]); prediction=torch.tensor([1,0,0]); groups=['A','A','B']; errors=prediction!=truth
report={group:(int(errors[torch.tensor([g==group for g in groups])].sum()),groups.count(group)) for group in ['A','B']}
assert report=={'A':(1,2),'B':(0,1)}
```

**Expected:** A1/2errors; B0/1.

### Example B: Expose repeated identities

Repeated rows can bias a metric without adding independent cases. Identity validation belongs before aggregation.

```python
ids=['a','b','c']+['c']*5
assert len(ids)==8 and len(set(ids))==3
```

**Expected:** 8rows but 3 unique IDs.

### Example C: Trace a controlled perturbation

The last shift crosses the defined boundary. Whether that counts as a robustness failure depends on the intended label semantics.

```python
base=torch.tensor(1.); shifts=torch.tensor([-.1,-.9,-1.1]); changed=(base+shifts>=0).long()
assert changed.tolist()==[1,1,0]
```

**Expected:** labels 1, 1, 0.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: A1/2errors; B0/1. card explicitly has no privacy guarantee. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Count group errors.** Use groups A, A, B with truth 1, 1, 0 and prediction 1, 0, 0.
   **Expected:** A1/2errors; B0/1.
   **Verify:** Save the assertion results for exercise 1, including A1/2errors; B0/1.

2. **Expose repeated identities.** Repeat correct record c five times and compare row count with unique IDs.
   **Expected:** 8rows but 3 unique IDs.
   **Verify:** Save the assertion results for exercise 2, including 8rows but 3 unique IDs.

3. **Trace a controlled perturbation.** Classify \(x\ge 0\) at base 1 after shifts-.1, -.9, -1.1.
   **Expected:** labels 1, 1, 0.
   **Verify:** Save the assertion results for exercise 3, including labels 1, 1, 0.

4. **Keep severe failures visible.** Use 9 minor passes and 1 severe failure.
   **Expected:** overall pass rate.9; severe failure count 1.
   **Verify:** Save the assertion results for exercise 4, including overall pass rate.9; severe failure count 1.

5. **Represent an untested group.** Define a rate helper with count 0.
   **Expected:** None for untested; 0for zero errors in one case.
   **Verify:** Save the assertion results for exercise 5, including None for untested; 0for zero errors in one case.

6. **Write a bounded card.** Record 3 unique units, synthetic teaching use and untested future conditions.
   **Expected:** card explicitly has no privacy guarantee.
   **Verify:** Save the assertion results for exercise 6, including card explicitly has no privacy guarantee.

## Common pitfalls and diagnosis

If a rate improves after adding duplicate rows, recompute it at the declared independent-unit or weighting level. If a zero-error group looks conclusive, inspect its count and sampling assumptions. If a missing group displays zero, repair the missing-value representation rather than accepting an invented measurement.

If a perturbation changes a prediction, first decide whether the correct label should change too. If one severe failure disappears inside a high pass percentage, restore the predeclared severity gate. If a card claims privacy, locate the actual mechanism, unit and accounting evidence. Synthetic data, redaction and a finite attack set should not be substituted for a guarantee they did not establish.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Subgroup denominator, Robustness condition, Finite safety evidence using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-033` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does zero observed failure mean zero risk?**

No. A finite sample can miss rare or unrepresented conditions. Report the tested population, count and coverage.

**Can a model card prove privacy?**

No. It can record a privacy mechanism and its analysis, but documentation does not replace a technical guarantee or empirical evidence.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-034, Robustness, privacy and evidence beyond a score.
Read courses/deep-learning-pytorch/guides/torch-034.md and courses/deep-learning-pytorch/lessons/torch-034.py. Direct prerequisites: `torch-033`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
