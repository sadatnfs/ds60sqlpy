# tf-004: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/tf-004.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](tf-004_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace squared units

Squaring [1,-1,2] gives [1,1,4]. The sum is 6 and division by three gives MSE 2. Root mean squared error is sqrt(2), in target units rather than squared target units. These values all describe the same residual fixture under different reporting transformations. A negative residual does not subtract error from a positive one after squaring; using the mean raw residual could hide cancellation and is a different statistic.

**Expected:** Squares [1,1,4], sum 6, mean 2 and root mean square sqrt(2).

**Verify:** Assert both reductions and state squared target units versus original target units.

## Exercise 2: Duplicate the batch

The duplicated vector contains six residuals and squared sum 12. Dividing by six leaves mean 2. This is an invariant of duplicating the entire empirical distribution under equal observation weights. The summed objective doubles, which can also double an unnormalized gradient later. That does not make sum wrong; it means the reduction must be declared when comparing learning rates, batch sizes or reported objectives.

**Expected:** Sum 12 and mean 2 over six records.

**Verify:** Compare both outputs with the three-record fixture and record the changed denominator.

## Exercise 3: Construct a masked reduction

Index the accepted entries first, obtaining [1,-1]. Their squared sum is 2 and their mean is 1. A broken zero-fill approach retains three denominator positions, returning 2/3. The helper validates the boolean mask and its shape before selection, then rejects a selection with no entries. Keep a counterexample whose excluded residual is nonzero so the test checks a real mask/denominator mechanism rather than coincidentally matching values.

**Expected:** Masked sum 2 and masked mean 1; the zero-then-mean bug gives 2/3.

**Verify:** Assert the selected count is two and compare the three different scalar results.

## Exercise 4: Reject an absent objective

A missing residual set and an all-false selection have no mean objective. Reject them with ValueError. An integer mask is ambiguous under the explicit boolean inclusion contract and raises TypeError. The unsupported name median is not silently treated as mean or sum. After each rejected call, the original [1,-1,2] fixture must still return 2. A default zero would confuse no accepted data with genuinely zero accepted errors.

**Expected:** Empty/all-false/unknown-reduction cases raise ValueError; integer mask raises TypeError.

**Verify:** Capture the four named exceptions separately and retain the valid mean 2 afterward.

## Exercise 5: Compare objective preferences

A has squared sum 16 and MSE 16/3, while B has squared sum 12 and MSE 4, so squared error prefers B. Absolute sums are 4 and 6, yielding MAE 4/3 versus 2 and preferring A. The disagreement reflects how strongly the objective penalizes a single large error. Choose the metric from the intended use and cost of errors, not from whichever ranking flatters a preferred system.

**Expected:** MSE prefers B: 4 versus 16/3; MAE prefers A: 4/3 versus 2.

**Verify:** Write a two-model/two-metric table with the explicit denominator three; do not choose the metric after seeing the ranking.

## Exercise 6: Transfer to unequal groups

The four observed squared residuals are [4,0,0,0], whose mean is 1. The two group MSEs are 4 and 0; averaging these groups equally gives 2. Neither number is an arithmetic mistake, but their units of weighting differ. Weight group means by counts one and three to recover the all-record mean. A later distributed or grouped evaluation must preserve the chosen unit instead of assuming every shard has the same cardinality.

**Expected:** All-record MSE 1; equal-group average 2.

**Verify:** Inspect the one-versus-three group counts and assert the example-weighted mean matches 1.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import numpy as np


def reduce_squared(residuals, reduction="mean", mask=None):
    residuals = np.asarray(residuals, dtype=np.float64)
    if residuals.ndim != 1 or residuals.size == 0 or not np.isfinite(residuals).all():
        raise ValueError("finite nonempty residual vector required")
    if reduction not in {"mean", "sum"}:
        raise ValueError("reduction must be mean or sum")
    if mask is not None:
        mask = np.asarray(mask)
        if mask.dtype != np.bool_:
            raise TypeError("mask must be boolean")
        if mask.shape != residuals.shape or not mask.any():
            raise ValueError("same-shaped nonempty mask required")
        residuals = residuals[mask]
    squared = np.square(residuals)
    return float(squared.mean() if reduction == "mean" else squared.sum())
```

## Retrieval and alternatives

Without the helper, derive the mean squared loss of residuals [3,0] and its value after duplicating both records. Then explain how an all-false mask differs from two accepted zero residuals.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
