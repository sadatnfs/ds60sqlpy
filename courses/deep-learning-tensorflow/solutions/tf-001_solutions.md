# tf-001: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/tf-001.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](tf-001_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Name the units and roles

The three t-prefixed records are training examples and the four h-prefixed records are demonstration evaluation examples. The feature and target in one record belong together; treating every scalar as an independent sample would inflate the count. Label the group IDs explicitly. Their disjointness is part of the intended new-group claim, whereas the visible synthetic arithmetic is not an independent exam. An alternative table layout is acceptable when all seven identities and their roles remain inspectable.

**Expected:** Three training rows and four holdout rows; the row-ID and group-ID intersections are empty.

**Verify:** Inspect the row-count table and assert the two ID-set intersections are empty.

## Exercise 2: Compare a fixed baseline

Fit the mean on [2,4,6], obtaining 4. Training residuals are [2,0,-2], so squared sum 8 divided by 3 is 8/3. Evaluation residuals are [-4,-6,-8,-10], whose squares sum to 216; divide by 4 to obtain 54. The evaluation-target mean 11 must not replace 4. That would use information from the set reserved for inspection and answer a different question. Keep both labeled metrics, even when the evaluation result is worse.

**Expected:** The constant is 4, training MSE is 8/3 and holdout MSE is 54.

**Verify:** Record all seven residuals and compare their two separately labeled sums and denominators.

## Exercise 3: Separate a sum from a mean

Subtract target from prediction for each pair, giving -1 and +1. Squaring removes the sign and produces two ones. Their sum is 2 and their mean is 1. The exact difference between these reductions is the denominator, not rounding. If the target were measured in meters, this squared quantity would be square meters. Comparing a sum from two rows with a mean from four rows obscures both the unit and the sample-size dependence.

**Expected:** Residuals [-1,1], squared-error sum 2 and MSE 1; squared target units.

**Verify:** Assert the sum equals twice the mean for these two records; do not compare 2 with another dataset mean.

## Exercise 4: Find a grouped leak

After h1 is assigned t1's source group, the row-ID intersection can still be empty while the group intersection contains that source. For an evaluation about new accounts, measurements from the same account can share information, so the split no longer supports that claim. Rename neither record to hide the overlap. The repair is a grouped partition created before fitting, followed by fresh selection under that partition. A different intended unit requires a separately stated policy.

**Expected:** Row IDs remain disjoint but one source group overlaps; a new-source-group claim is rejected.

**Verify:** Inspect both intersections separately and retain the named overlapping group in the report.

## Exercise 5: Refuse an empty score

No arithmetic mean exists for an empty collection because its denominator is zero. Returning zero would confuse absence of evidence with perfect prediction. Raise ValueError with an empty-evaluation explanation before computing any score. The reference also rejects mismatched prediction/target lengths so accidental truncation by zip cannot conceal missing records. After the rejected call, recompute the valid four-row case: the expected 54 confirms that failure handling did not mutate the original fixture.

**Expected:** An empty evaluation set has no mean; the reference raises ValueError instead of reporting zero.

**Verify:** Capture the empty-input exception and confirm the original four-row evaluation still yields 54 afterward.

## Exercise 6: Bound the conclusion

Zero error shows that y=2*x matches these seven published feature/target pairs. The rule and labels are already visible, so this is an arithmetic demonstration and cannot establish unseen-population performance. A statement such as every future input is correct is unsupported. Choose new source groups or a later time period under a frozen protocol and state the intended use first. Report any revision made after inspecting those results as selection work rather than untouched testing.

**Expected:** The supported statement concerns those seven published points only; all-future accuracy or production-safety claims remain unsupported.

**Verify:** The evidence note names seven observations, the already visible rule, and a new source/time fixture that has not influenced selection.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import math

TRAIN = [{"id": f"t{i}", "group": f"train-{i}", "x": i, "y": 2 * i} for i in range(1, 4)]
HOLDOUT = [
    {"id": f"h{i}", "group": f"holdout-{i}", "x": i + 3, "y": 2 * (i + 3)} for i in range(1, 5)
]


def mse(predictions, targets):
    predictions, targets = list(predictions), list(targets)
    if not predictions or len(predictions) != len(targets):
        raise ValueError("nonempty equal-length evaluation pairs required")
    pairs = [(float(a), float(b)) for a, b in zip(predictions, targets)]
    if not all(math.isfinite(a) and math.isfinite(b) for a, b in pairs):
        raise ValueError("finite evaluation pairs required")
    return sum((a - b) ** 2 for a, b in pairs) / len(pairs)


def validate_split(train, holdout):
    if not train or not holdout:
        raise ValueError("nonempty train and holdout required")
    ids = [{row["id"] for row in part} for part in (train, holdout)]
    groups = [{row["group"] for row in part} for part in (train, holdout)]
    if any(len(keys) != len(part) for keys, part in zip(ids, (train, holdout))):
        raise ValueError("duplicate row IDs")
    if ids[0] & ids[1]:
        raise ValueError("row ID overlap")
    if groups[0] & groups[1]:
        raise ValueError("source group overlap")
    return True
```

## Retrieval and alternatives

Close the table and explain why a holdout is a decision policy. Then change the training targets to [1,3] and the evaluation target to [5]. Derive the fixed training-mean prediction and its single squared error without looking at the reference.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
