# torch-034: Robustness, privacy and evidence beyond a score

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-033`.

## Learning objectives

Report model reliability with group denominators, repeated identities, controlled perturbations and severe failures kept visible.

Central investigation: Count group errors on three records, repeat one record, shift a threshold input and summarize nine minor passes with one severe failure.

Finish condition: Group A has 1 error of 2 and group B 0 of 1, 8 rows contain only 3 unique IDs, the shifts give labels 1, 1, 0, the 0.9 pass rate still reports 1 severe failure, and an untested group is None rather than 0.

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

Run `torch-034` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C need only the imports at the top of Example A.

## Syntax anatomy and reasoning sequence

Compute boolean error vectors before aggregation. Groupby declared labels and retain integer error/count pairs. Compare row count with unique ID count to expose duplicates. Use None for an untested group rather than a rate of zero. Keep severity categories separate from overall pass rate, and make the decision gate explicit before inspecting results.

## Keep population, perturbation and mechanism claims separate

The original three records contain one error: group A has \(\frac{1}{2}\) and group B has 0/1. Overall error is \(\frac{1}{3}\). Repeating the correct record c five additional times creates eight rows but only three unique IDs. A naive row-weighted error becomes \(\frac{1}{8}\) even though no new case was tested. The apparent improvement comes entirely from changing the weight of one existing success.

This counterexample does not imply that every repeated identity should be removed. A longitudinal task may legitimately contain several observations from one person or device. The question is which unit the reported quantity is intended to average over, and whether dependence is modeled. Exact duplicate detection, source-family grouping and a weighting policy are related but different controls. A set of three IDs alone also does not prove those units are statistically independent.

Zero errors among one observation is weak evidence about an unknown error probability. Under a deliberately stated independent Bernoulli sampling model, the chance of observing zero errors in n cases is \((1-p)^n\). Solving \((1-p)^n=0.05\) gives a one-sided 95% upper bound \(1-{0.05}^{\frac{1}{n}}\):0.95 at \(n=1\) and approximately 0.0295 at \(n=100\). This arithmetic illustrates why denominators matter. The hand-selected synthetic cases do not automatically satisfy the random-sampling assumptions needed to interpret that bound as a population claim.

An empty group has no measured rate. Returning None preserves that absence; returning zero invents a successful observation. A report or chart should not replace missing rates with zero merely to fill a display. Likewise, a confidence calculation cannot create coverage for a group or condition that never appeared in the data. Keep coverage counts and the intended target population beside every aggregate.

The perturbation rule here is f(x)=1 when \(x\ge 0\). Starting at one, the shifts -0.1, -0.9, -1.1 produce 0.9, 0.1, -0.1 and therefore labels 1, 1, 0. If the target itself is defined by the observed sign, the final change is correct behavior after crossing the decision boundary. Calling it a robustness failure would assume an invariant label that the task definition does not support.

A different application might model these shifts as measurement noise while the latent class remains fixed. That is a different target policy and needs its own oracle. For this simple sign rule, perturbations with magnitude strictly below one cannot cross from the starting point to the negative side. That analytic statement is local to this scalar rule and declared perturbation set; it is not evidence that an arbitrary neural classifier is robust to all small changes.

Severity is another independent axis. Nine minor passes and one severe failure yield a 90% overall pass rate. If the predeclared release rule blocks on any severe failure, the correct decision remains no-go. Choosing a favorable aggregate after observing the severe failure changes the decision policy. Preserve case-level identity, severity and the actual failed condition so a summary cannot erase it.

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

truth = torch.tensor([1, 1, 0])
prediction = torch.tensor([1, 0, 0])
groups = ["A", "A", "B"]
errors = prediction != truth
report = {
    group: (int(errors[torch.tensor([g == group for g in groups])].sum()), groups.count(group))
    for group in ["A", "B"]
}
assert report == {"A": (1, 2), "B": (0, 1)}
```

**Expected:** group A: 1 of 2 wrong; group B: 0 of 1 wrong.

### Example B: Expose repeated identities

Repeated rows can bias a metric without adding independent cases. Identity validation belongs before aggregation.

```python
ids = ["a", "b", "c"] + ["c"] * 5
assert len(ids) == 8 and len(set(ids)) == 3
```

**Expected:** 8 rows but 3 unique IDs.

### Example C: Trace a controlled perturbation

The last shift crosses the defined boundary. Whether that counts as a robustness failure depends on the intended label semantics.

```python
base = torch.tensor(1.0)
shifts = torch.tensor([-0.1, -0.9, -1.1])
changed = (base + shifts >= 0).long()
assert changed.tolist() == [1, 1, 0]
```

**Expected:** labels 1, 1, 0.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Count group errors. Predict exercise 6, Write a bounded card, from its prompt alone: Record 3 unique units, synthetic teaching use and untested future conditions. Then explain why this finish condition holds: Group A has 1 error of 2 and group B 0 of 1, 8 rows contain only 3 unique IDs, the shifts give labels 1, 1, 0, the 0.9 pass rate still reports 1 severe failure, and an untested group is None rather than 0. Keep each prediction beside the observed value.

## Exercises

1. **Count errors for three groups.** Use groups A, B, B, C with truth 0, 1, 1, 0 and predictions 0, 0, 1, 1.
   **Expected:** A: 0 of 1 wrong; B: 1 of 2; C: 1 of 1.
   **Verify:** In a fresh process, the exercise checks confirm `summary == {'A': (0, 1), 'B': (1, 2), 'C': (1, 1)}`.

2. **Deduplicate repeated identities.** Use row identities p, q, q, r, r, r and count rows, unique identities and the largest repeat.
   **Expected:** 6 rows, 3 unique identities, largest repeat 3.
   **Verify:** In a fresh process, the exercise checks confirm `len(rows_t) == 6`, `len(set(rows_t)) == 3` and `max((rows_t.count(i) for i in set(rows_t))) == 3`.

3. **Trace a new perturbation.** Classify \(x\ge 0\) at base 0.5 after shifts -0.4, -0.5 and -0.6.
   **Expected:** labels 1, 1, 0; the shift of -0.5 lands exactly on the boundary.
   **Verify:** In a fresh process, the exercise checks confirm `(start + moves >= 0).long().tolist() == [1, 1, 0]`.

4. **Keep severe failures visible.** Use 9 minor passes and 1 severe failure.
   **Expected:** overall pass rate 0.9; severe failure count 1.
   **Verify:** In a fresh process, the exercise checks confirm `passed.float().mean().item()` matches `0.9` within 1e-06 and `int((~passed & severe).sum()) == 1`.

5. **Represent an untested group.** Define a rate helper with count 0.
   **Expected:** None for untested; 0 for zero errors in one case.
   **Verify:** In a fresh process, the exercise checks confirm `rate(0, 0) is None` and `rate(0, 1) == 0`.

6. **Write a bounded card.** Record 3 unique units, synthetic teaching use and untested future conditions.
   **Expected:** card explicitly has no privacy guarantee.
   **Verify:** In a fresh process, the exercise checks confirm `card['unique_units'] == 3` and `not card['differential_privacy_established']`.

## Common pitfalls and diagnosis

If a rate improves after adding duplicate rows, recompute it at the declared independent-unit or weighting level. If a zero-error group looks conclusive, inspect its count and sampling assumptions. If a missing group displays zero, repair the missing-value representation rather than accepting an invented measurement.

If a perturbation changes a prediction, first decide whether the correct label should change too. If one severe failure disappears inside a high pass percentage, restore the predeclared severity gate. If a card claims privacy, locate the actual mechanism, unit and accounting evidence. Synthetic data, redaction and a finite attack set should not be substituted for a guarantee they did not establish.

## Progressive hints

Hint 1: Example B (Expose repeated identities) alters one assumption of Example A (Count group errors). Hint 2: exercise 4, Keep severe failures visible, should end at overall pass rate 0.9; severe failure count 1. Work backward from it. Hint 3: exercise 5, Represent an untested group, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Trace a controlled perturbation, from its inputs alone. Predict whether exercise 3, Trace a new perturbation, survives one changed input. Then explain Subgroup denominator, Robustness condition, Finite safety evidence in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Count group errors) cannot be rebuilt without help, revisit `torch-033` first. `torch-035` (Paired model comparisons and uncertainty) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22 for the Subgroup denominator, Robustness condition, Finite safety evidence behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

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
