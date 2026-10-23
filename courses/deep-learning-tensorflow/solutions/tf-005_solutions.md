# tf-005: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/tf-005.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](tf-005_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Label slope and state

At zero the loss is (0-2)^2=4 and the derivative is 2*(0-2)=-4. The rate-0.1 subtraction gives 0.4, then recomputing the function gives 2.56. The derivative is evaluated at the old state; it is not the updated state or the post-update loss. Keep each number labeled. This example supports the arithmetic of one small update and does not promise that every finite gradient step improves every objective.

**Expected:** Loss 4, derivative -4, new w 0.4 and new loss 2.56.

**Verify:** Assert each named quantity separately; do not label -4 as the updated parameter.

## Exercise 2: Construct central probes

The central formula uses both sides and divides by 2*h. At zero for a quadratic, the h-squared terms cancel symmetrically, leaving -4 apart from binary rounding. All three supplied sizes meet the stated absolute tolerance. Retain the scale/value table rather than merely printing one number that happened to match. For a nonquadratic function the approximation generally has truncation error, so agreement at every h is not a universal property of the method.

**Expected:** Every central approximation matches -4 within 1e-10.

**Verify:** Keep the three h/value pairs and compare them with the analytic derivative using an explicit absolute tolerance.

## Exercise 3: Expose a one-sided bias

Expanding f(h)-f(0) gives -4*h+h*h. Division by h produces -4+h, yielding the three stated forward differences. Their errors are exactly h in real arithmetic, which demonstrates finite-step bias without a framework. Smaller h reduces that bias until rounding and cancellation become relevant. The symmetric quadratic check avoids this term, but the lesson is about knowing the approximation contract, not declaring forward differences invalid for every use.

**Expected:** Values are -3.9, -3.99 and -3.999, differing from -4 by h.

**Verify:** Assert the three errors against their h values and compare with the central-probe table.

## Exercise 4: Move from the other side

At w=3, the derivative is 2. Subtracting one tenth of it changes the parameter to 2.8. Its distance from the optimum is 0.8, so the new squared loss is 0.64. The update decreases the parameter because the derivative is positive on this side of the optimum. Recompute the loss at the new point instead of reusing the old value 1; a correct update followed by a stale printed loss would be misleading evidence.

**Expected:** Derivative 2, new w 2.8 and new loss 0.64.

**Verify:** Assert all three values within 1e-12 and explain why the update now decreases the parameter.

## Exercise 5: Diagnose an invalid derivative claim

For absolute value at zero, a left slope of -1 and a right slope of +1 show that no ordinary two-sided derivative exists. The symmetric calculation returns 0 because its numerator cancels, not because the kink disappeared. Reject h=0 to avoid division by zero and reject NaN because nearby comparisons would be uninterpretable. A framework may choose a subgradient convention at the kink; label that separately from a unique classical derivative.

**Expected:** One-sided slopes -1 and +1 contradict differentiability; central is 0. Invalid h/point cases raise ValueError.

**Verify:** Record the three slopes and capture both input-validation exceptions; do not call central zero a unique derivative.

## Exercise 6: Transfer to a scaled objective

The derivative of 3*(w-1)^2 is 6*(w-1), giving 6 at w=2. A rate-0.1 step reaches 1.4 and its loss is 3*0.4^2=0.48. This fresh objective confirms that the learner can transfer the mechanism rather than memorize -4. A direct symbolic derivative and a central finite difference are complementary checks. Neither removes the need to inspect which actual computation a later automatic-differentiation tape records.

**Expected:** Gradient 6, new w 1.4 and new loss 0.48.

**Verify:** Compare a fresh central probe with 6, then assert the new parameter and recomputed loss.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import math


def central_difference(function, point, h):
    point, h = float(point), float(h)
    if not math.isfinite(point) or not math.isfinite(h) or h <= 0:
        raise ValueError("finite point and positive finite h required")
    high, low = float(function(point + h)), float(function(point - h))
    if not math.isfinite(high) or not math.isfinite(low):
        raise ValueError("finite probe values required")
    return (high - low) / (2 * h)
```

## Retrieval and alternatives

Derive the slope of (w+1)^2 at zero without a framework. Then explain why h and a learning rate play different roles even though both may be written as small decimal numbers.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
