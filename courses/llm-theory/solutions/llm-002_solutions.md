# llm-002: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-002.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-002_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Explain the shift

For [0,0], shifted scores are [0,0], exponential masses are [1,1] and their sum is 2. The normalized values are one half each. For [1000,1000], subtracting the maximum yields the same [0,0], so the actual exponentials remain [1,1]. Algebraically, the common factor exp(offset) cancels in the ratio. Avoid computing that factor merely to cancel it afterward, because it may overflow before the mathematical simplification can help.

**Expected:** Both outputs are [0.5,0.5] and every row sum is 1.

**Verify:** Assert the output vectors with rtol=0, atol=1e-12 and record the two exponentials actually formed after shifting.

## Exercise 2: Construct a stable helper

The masses for [0,log(3)] are proportional to [1,3], giving [1/4,3/4]. The same vector plus 1000 should yield the same result. A stable implementation subtracts the maximum, producing masses [1/3,1], whose normalization is still [1/4,3/4]. The reference accepts one finite nonempty vector, validates an optional boolean mask and rejects unsupported shapes. That narrow interface avoids accidentally treating a whole matrix as one categorical distribution.

**Expected:** Both yield [0.25,0.75] within 1e-12.

**Verify:** Assert each vector and their difference separately; no direct exp(1000) is needed.

## Exercise 3: Preserve the legal candidate set

Remove the forbidden middle score before the maximum and denominator are formed. The remaining two zeros give [1/2,0,1/2]. If you first normalize [0,100,0], almost all mass goes to the middle choice; deleting it afterward leaves a row sum near zero. The triangle or zero at that position may look convincing while the legal row is no longer normalized. Renormalization can repair ordinary cases, but the pre-normalization mask avoids needless extreme exponentials.

**Expected:** Legal distribution [0.5,0,0.5]; the post-normalization deletion loses probability mass.

**Verify:** Assert the legal row sum is 1 and compare it with the tiny remaining mass from the broken order.

## Exercise 4: Find a wrong reduction axis

A 2x2 zero matrix has four equal masses if normalized globally, so each entry becomes 1/4 and each row sums to 1/2. With one categorical decision per row, each row instead contains two equal masses, each normalized to 1/2, so its sum is 1. Both computations can be implemented without an exception. The domain meaning selects the axis, and row-sum assertions reveal the mismatch that nonnegative-value checks would miss.

**Expected:** A global normalizer gives every entry 0.25 and row sums 0.5; row-wise normalization gives entries 0.5 and row sums 1.

**Verify:** Inspect the two row-sum arrays, not just whether all four values are nonnegative.

## Exercise 5: Reject invalid distributions

An empty vector and an all-false mask have no legal probability distribution. NaN prevents meaningful finite score comparisons. Reject those cases with ValueError and reject integer masks with TypeError to preserve an explicit inclusion convention. Validate independently rather than catching every error and returning zeros. The valid equal-score fixture must succeed afterward. This also proves that invalid input did not mutate a mask or leave cached state affecting subsequent calls.

**Expected:** Empty, NaN and all-false cases raise ValueError; integer mask raises TypeError.

**Verify:** Capture all four exceptions independently and verify the original equal-score case still returns [0.5,0.5].

## Exercise 6: Transfer to temperature

Dividing [0,log(3)] by 2 makes the relative exponential masses [1,sqrt(3)], producing the stated normalized values. Both are closer to one half than before, but the second remains larger. Positive temperature changes concentration while preserving the ordering of unequal scores. It neither adds evidence nor makes the highest-scoring answer true. A separate decoder policy will decide how to sample or choose from the distribution; softmax alone does not select a token.

**Expected:** At temperature 2, probabilities are [1/(1+sqrt(3)),sqrt(3)/(1+sqrt(3))]; index 1 remains the largest.

**Verify:** Assert the new values within 1e-12, the sum 1 and the unchanged argmax; do not interpret the winner as guaranteed truth.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import numpy as np


def softmax(scores, allowed=None):
    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 1 or scores.size == 0 or not np.isfinite(scores).all():
        raise ValueError("finite nonempty score vector required")
    if allowed is None:
        allowed = np.ones(scores.shape, dtype=bool)
    allowed = np.asarray(allowed)
    if allowed.dtype != np.bool_:
        raise TypeError("allowed must be boolean")
    if allowed.shape != scores.shape or not allowed.any():
        raise ValueError("same-shaped mask with at least one allowed choice required")
    masked = np.where(allowed, scores, -np.inf)
    mass = np.exp(masked - masked.max())
    return mass / mass.sum()
```

## Retrieval and alternatives

Close the helper and explain why a common score offset cancels but a positive temperature can change probabilities. Use a three-choice fixture with one forbidden option and state the denominator before calculating it.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
