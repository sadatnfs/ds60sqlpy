# tf-006: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/tf-006.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](tf-006_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Build a forward/backward table

At w=1, z=2, a=4 and L=9. The immediate sensitivities are 2 from w to z, 4 from z to a, and 6 from a to loss. Their product is 48. Expanding the loss as 16*w^4-8*w^2+1 gives derivative 64*w^3-16*w, also 48 at one. These two representations provide independent bookkeeping. A forward table alone cannot check the backward multiplication because the gradient is not used to produce the original loss.

**Expected:** Forward values [2,4,9], factors [2,4,6] in forward order, total gradient 48.

**Verify:** Assert the product of the three factors and compare it with the derivative of the expanded scalar polynomial.

## Exercise 2: Change one inner operation

With inner scale 3, z becomes 3, a becomes 9 and loss becomes 64. Local factors are 3, 6 and 16, whose product is 288. Only changing one occurrence of the old factor 2 would be wrong because the derivative is evaluated at changed intermediate values as well. Recompute the forward path first, then calculate all sensitivities at that same state. Retaining the old activation while changing the inner derivative defines an inconsistent backward trace.

**Expected:** z=3, a=9, loss=64 and gradient 288.

**Verify:** Inspect the changed forward trace and assert 16*6*3 equals the total gradient.

## Exercise 3: Construct an independent probe

The reference returns both forward fields and their connected gradient. The finite probe must call the scalar forward function at 1+h and 1-h, fully recomputing z and a. At h=1e-5, the polynomial approximation meets the stated 1e-7 absolute tolerance. It need not equal 48 bit-for-bit. Using an already stored activation in both probe calls would instead measure a constant function and would not independently check the original derivative.

**Expected:** Analytic gradient 48 and central estimate within 1e-7.

**Verify:** Recompute every intermediate in both perturbed calls and retain the numeric absolute error.

## Exercise 4: State the activation boundary

ReLU maps -1 to zero and +1 to one, with slopes zero and one on the corresponding open regions. At zero the one-sided slopes disagree, so there is no unique classical derivative. The central probe averages them and returns one half. A framework can select zero as a training convention without claiming that the classical derivative exists. The learner should state this boundary explicitly instead of treating every disagreement with finite differences as a framework bug.

**Expected:** Negative-side slope 0, positive-side slope 1; the zero kink has no unique ordinary derivative.

**Verify:** Inspect one-sided values and show a central probe at zero yields 0.5 rather than proving the chosen convention.

## Exercise 5: Diagnose a disconnected calculation

A function closing over frozen_a=4 returns loss 9 for every w. Its slope is therefore zero, despite matching the full path at w=1. The full composition still changes with w and has slope 48 there. This counterexample shows why dependency recording matters: equal forward numbers at one point do not imply equal functions or gradients. Restore the calculation from w through z and a inside each evaluation rather than patching the final derivative value.

**Expected:** Both losses are 9; frozen slope 0 and full slope 48.

**Verify:** Assert both equal forward values and the two different slopes instead of accepting the matching loss as a dependency check.

## Exercise 6: Find a missing factor

Omitting dz/dw leaves 6*4=24 in the scale-2 case and 16*6=96 in the scale-3 case. Multiplying by the missing scale restores 48 and 288. A single adjusted learning rate cannot generally repair this omission across different operations or model states. Keep the derivative factors with their named input/output relationships. This trace becomes a useful explanation when the next lesson reports a missing or incorrect gradient from an automatic recording scope.

**Expected:** The incorrect gradients are 24 and 96, versus correct 48 and 288.

**Verify:** Write the missing scale factor explicitly and assert the repaired products for both fixtures.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import math


def chain_trace(weight, scale=2):
    weight, scale = float(weight), float(scale)
    if not math.isfinite(weight) or not math.isfinite(scale):
        raise ValueError("finite weight and scale required")
    z = scale * weight
    activation = z * z
    loss = (activation - 1) ** 2
    gradient = 2 * (activation - 1) * 2 * z * scale
    return {"z": z, "activation": activation, "loss": loss, "gradient": gradient}
```

## Retrieval and alternatives

Without viewing the trace, replace the inner scale with 1 and derive the loss and gradient at w=2. Then explain why holding a fixed changes the function even when the original loss remains identical.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
