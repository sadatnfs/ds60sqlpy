# torch-034: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A reliability report should preserve the conditions and denominators behind a score. Group A with zero errors in one case does not provide the same evidence as zero errors in hundreds of independent cases. Duplicate records can improve an apparent rate without testing new conditions. Perturbation tests need a label policy: crossing a legitimate decision boundary may change the correct target rather than reveal a robustness failure.

Privacy and safety claims require their own mechanisms and evidence. A synthetic fixture containing no personal data does not establish differential privacy. A finite set of successful adversarial checks does not prove all future inputs are safe. This chapter uses Torch tensors for error accounting and controlled perturbations, then writes a bounded model-card record with untested conditions and failure severity.

**Subgroup denominator:** The observation count supporting a group metric.

**Robustness condition:** A specified input change under a declared label policy.

**Finite safety evidence:** Observed results on bounded cases without a universal guarantee.

**Model card:** A record of intended use, evidence and limitations.

## Reading the implementation

Compute boolean error vectors before aggregation. Groupby declared labels and retain integer error/count pairs. Compare row count with unique ID count to expose duplicates. Use None for an untested group rather than a rate of zero. Keep severity categories separate from overall pass rate, and make the decision gate explicit before inspecting results.

## Keep population, perturbation and mechanism claims separate

The original three records contain one error: group A has \(\frac{1}{2}\) and group B has 0/1. Overall error is \(\frac{1}{3}\). Repeating the correct record c five additional times creates eight rows but only three unique IDs. A naive row-weighted error becomes \(\frac{1}{8}\) even though no new case was tested. The apparent improvement comes entirely from changing the weight of one existing success.

This counterexample does not imply that every repeated identity should be removed. A longitudinal task may legitimately contain several observations from one person or device. The question is which unit the reported quantity is intended to average over, and whether dependence is modeled. Exact duplicate detection, source-family grouping and a weighting policy are related but different controls. A set of three IDs alone also does not prove those units are statistically independent.

Zero errors among one observation is weak evidence about an unknown error probability. Under a deliberately stated independent Bernoulli sampling model, the chance of observing zero errors in n cases is \((1-p)^n\). Solving \((1-p)^n=0.05\) gives a one-sided 95% upper bound \(1-{0.05}^{\frac{1}{n}}\):0.95 at \(n=1\) and approximately 0.0295 at \(n=100\). This arithmetic illustrates why denominators matter. The hand-selected synthetic cases do not automatically satisfy the random-sampling assumptions needed to interpret that bound as a population claim.

An empty group has no measured rate. Returning None preserves that absence; returning zero invents a successful observation. A report or chart should not replace missing rates with zero merely to fill a display. Likewise, a confidence calculation cannot create coverage for a group or condition that never appeared in the data. Keep coverage counts and the intended target population beside every aggregate.

The perturbation rule here is f(x)=1 when \(x\ge 0\). Starting at one, the shifts -0.1, -0.9, -1.1 produce 0.9, 0.1, -0.1 and therefore labels 1, 1, 0. If the target itself is defined by the observed sign, the final change is correct behavior after crossing the decision boundary. Calling it a robustness failure would assume an invariant label that the task definition does not support.

A different application might model these shifts as measurement noise while the latent class remains fixed. That is a different target policy and needs its own oracle. For this simple sign rule, perturbations with magnitude strictly below one cannot cross from the starting point to the negative side. That analytic statement is local to this scalar rule and declared perturbation set; it is not evidence that an arbitrary neural classifier is robust to all small changes.

Severity is another independent axis. Nine minor passes and one severe failure yield a90% overall pass rate. If the predeclared release rule blocks on any severe failure, the correct decision remains no-go. Choosing a favorable aggregate after observing the severe failure changes the decision policy. Preserve case-level identity, severity and the actual failed condition so a summary cannot erase it.

Privacy is not established by removing names from an example or by obtaining a good accuracy score. Differential privacy describes a randomized mechanism's output behavior under a defined change to a dataset. Its guarantee depends on the neighboring-dataset unit, privacy parameters and the mechanism/accounting assumptions. Record-level adjacency and person-level adjacency are different promises when a person contributes multiple rows. Clipping, noise, sampling and repeated releases require a coherent analysis; this chapter implements none of them. [NIST SP 800-226](https://csrc.nist.gov/pubs/sp/800/226/final) discusses evaluation of such guarantees and implementation hazards.

An empirical privacy attack test and a mathematical privacy guarantee answer different questions. Failing to observe leakage in a few attempts does not prove a bound over all neighboring datasets and outputs. Conversely, a claimed formal bound does not remove the need to inspect the actual implementation, access controls and intended release. The lesson's model card therefore records synthetic teaching use and no privacy guarantee rather than promoting absence of personal data into a property of the training algorithm.

A useful card joins intended use, data/version identity, evaluation units, group counts, perturbation policy, severity results and untested conditions. It can summarize existing evidence but does not create it. The paired TensorFlow route uses the same reasoning fixtures, so framework choice does not change the denominator, independence or privacy interpretation.

## Exercise 1: Count errors for three groups

The question is: Use groups A, B, B, C with truth 0, 1, 1, 0 and predictions 0, 0, 1, 1.

Group C's single record makes its error rate 1, a reason to report counts with every rate.

```python
truth_t = torch.tensor([0, 1, 1, 0])
pred_t = torch.tensor([0, 0, 1, 1])
groups_t = ["A", "B", "B", "C"]
wrong = pred_t != truth_t
summary = {
    g: (int(wrong[torch.tensor([x == g for x in groups_t])].sum()), groups_t.count(g))
    for g in ["A", "B", "C"]
}
assert summary == {"A": (0, 1), "B": (1, 2), "C": (1, 1)}
```

**Expected:** A: 0 of 1 wrong; B: 1 of 2; C: 1 of 1.

**Verify:** In a fresh process, the exercise checks confirm `summary == {'A': (0, 1), 'B': (1, 2), 'C': (1, 1)}`.

## Exercise 2: Deduplicate repeated identities

The question is: Use row identities p, q, q, r, r, r and count rows, unique identities and the largest repeat.

Identity r would carry half of a row-weighted score.

```python
rows_t = ["p", "q", "q", "r", "r", "r"]
assert len(rows_t) == 6 and len(set(rows_t)) == 3 and max(rows_t.count(i) for i in set(rows_t)) == 3
```

**Expected:** 6 rows, 3 unique identities, largest repeat 3.

**Verify:** In a fresh process, the exercise checks confirm `len(rows_t) == 6`, `len(set(rows_t)) == 3` and `max((rows_t.count(i) for i in set(rows_t))) == 3`.

## Exercise 3: Trace a new perturbation

The question is: Classify \(x\ge 0\) at base 0.5 after shifts -0.4, -0.5 and -0.6.

The boundary case shows why the tie rule must be stated with a perturbation test.

```python
start = torch.tensor(0.5)
moves = torch.tensor([-0.4, -0.5, -0.6])
assert ((start + moves) >= 0).long().tolist() == [1, 1, 0]
```

**Expected:** labels 1, 1, 0; the shift of -0.5 lands exactly on the boundary.

**Verify:** In a fresh process, the exercise checks confirm `(start + moves >= 0).long().tolist() == [1, 1, 0]`.

## Exercise 4: Keep severe failures visible

The question is: Use 9 minor passes and 1 severe failure.

A high aggregate cannot override a predeclared critical-failure gate. Report both frequency and consequence.

```python
passed = torch.tensor([True] * 9 + [False])
severe = torch.tensor([False] * 9 + [True])
np.testing.assert_allclose(passed.float().mean().item(), 0.9, atol=1e-6, rtol=0)
assert int((~passed & severe).sum()) == 1
```

**Expected:** overall pass rate 0.9; severe failure count 1.

**Verify:** In a fresh process, the exercise checks confirm `passed.float().mean().item()` matches `0.9` within 1e-06 and `int((~passed & severe).sum()) == 1`.

## Exercise 5: Represent an untested group

The question is: Define a rate helper with count 0.

Absence of observations is not a perfect score. Keeping None visible prevents an untested group from looking validated.

```python
def rate(errors, count):
    return None if count == 0 else errors / count


assert rate(0, 0) is None and rate(0, 1) == 0
```

**Expected:** None for untested; 0 for zero errors in one case.

**Verify:** In a fresh process, the exercise checks confirm `rate(0, 0) is None` and `rate(0, 1) == 0`.

## Exercise 6: Write a bounded card

The question is: Record 3 unique units, synthetic teaching use and untested future conditions.

The card organizes evidence and limits; it does not create evidence merely by being complete. A production decision needs representative tests and appropriate privacy analysis.

```python
card = {
    "unique_units": 3,
    "use": "synthetic teaching",
    "untested": ["future population", "private-data behavior"],
    "differential_privacy_established": False,
}
assert card["unique_units"] == 3 and not card["differential_privacy_established"]
```

**Expected:** card explicitly has no privacy guarantee.

**Verify:** In a fresh process, the exercise checks confirm `card['unique_units'] == 3` and `not card['differential_privacy_established']`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
