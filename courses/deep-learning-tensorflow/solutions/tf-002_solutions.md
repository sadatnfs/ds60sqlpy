# tf-002: worked solutions

Compare after an attempt with the [learner guide](../guides/tf-002.md) ([comparison steps](../STUDY-GUIDE.md#after-the-solutions)).

## Exercise 1: Trace compatible axes

Two vectors of shape (3,) align their single observation axes, so each input is subtracted from its paired target. The result is [-1,-2,-3]. A column target has shape (3,1); aligning it with a vector creates a (3,3) grid. Its rows are [-1,0,1], [-3,-2,-1], [-5,-4,-3]. This operation is legal broadcasting. The failure is the changed pairing meaning, which a later aggregate cannot infer or undo.

**Expected:** Vector residual shape (3,) with [-1,-2,-3]; column broadcast shape (3,3) with the displayed nine values.

**Verify:** Assert both shapes and compare the two residual arrays entry by entry.

## Exercise 2: Construct a paired subtraction guard

A suitable helper converts values explicitly to float64, then checks rank, nonempty length and equal shape before subtraction. Reject the column with ValueError instead of automatically flattening it. Flattening can conceal a mistaken feature or time axis. The accepted vector result must still have shape (3,) and dtype float64. If another application genuinely permits matrices, it needs a different declared contract rather than weakening this paired-record function silently.

**Expected:** Valid vectors return [-1,-2,-3]; the (3,) versus (3,1) call raises ValueError.

**Verify:** Capture the shape exception before any subtraction, then rerun the valid fixture and inspect float64 dtype.

## Exercise 3: Diagnose an integer update

The integer array cannot store half-unit changes under an in-place update, so NumPy raises a casting TypeError. Create values.astype(np.float64) or a new float64 array, then perform the subtraction on that copy. The new values are [0.5,1.5,2.5]. Retain the integer input to prove the repair does not mutate it. Casting results back to integers would discard the fractional update and introduce a different calculation, not solve the representation problem.

**Expected:** The integer in-place operation raises a casting TypeError; the float64 copy becomes [0.5,1.5,2.5], and the original stays [1,2,3].

**Verify:** Inspect the two dtypes and assert original values remain unchanged after the successful floating update.

## Exercise 4: Reject absence and nonfinite data

Reject empty input before taking a mean or returning an apparently meaningful residual. Reject NaN and infinities with np.isfinite because later arithmetic can otherwise propagate an invalid value into every update. Catch each deliberate invalid case separately so a broken implementation cannot pass by returning a default array. The original valid fixture should still succeed afterward, which also checks that validation did not alter shared inputs or leave hidden mutable state.

**Expected:** Both calls raise ValueError, with empty/finite diagnostics; the valid example remains finite.

**Verify:** Capture each named exception separately and assert np.isfinite on the subsequent valid residual.

## Exercise 5: Compare tolerance with exact text

Decimal fractions such as 0.1 generally have no exact finite binary floating representation. The exact string printed for their sum is therefore not the right acceptance condition. Compare the absolute error with a stated tolerance, here 1e-12 with relative tolerance zero. That small scalar check does not justify the same threshold for every dtype or a long unstable calculation. In particular, accepting a whole wrong matrix because some average is close would misuse tolerance.

**Expected:** The printed representation may differ from 0.3 in its last digits; np.isclose with rtol=0 and atol=1e-12 passes.

**Verify:** Record the actual absolute difference and assert it is no greater than 1e-12 rather than matching output text.

## Exercise 6: Transfer the unit contract

Convert [100,200] centimeters to [1,2] meters by dividing by 100. Only then compare with the meter targets, yielding [0,0]. The unconverted residual [99,198] comes from subtracting incompatible meanings. Dtype conversion alone cannot repair it: both arrays could already be float64 and still represent different units. Keep the conversion policy with the feature schema so a later inference caller does not accidentally feed centimeters to a model expecting meters.

**Expected:** After dividing centimeters by 100, residuals are [0,0] meters; unconverted subtraction gives [99,198] and is semantically wrong.

**Verify:** Assert the converted result and name the meter unit explicitly in a comment or evidence note.

## Inspectable reference functions

`paired_difference` refuses unequal shapes, empty vectors and nonfinite values instead of broadcasting a column against a vector. [tf-002_solution.py](tf-002_solution.py) also asserts the (3,3) grid and the centimeter-to-meter transfer.

```python
from __future__ import annotations
import numpy as np


def paired_difference(left, right):
    left, right = (np.asarray(value, dtype=np.float64) for value in (left, right))
    if left.ndim != 1 or right.ndim != 1 or left.shape != right.shape:
        raise ValueError("equal vector shapes required")
    if left.size == 0:
        raise ValueError("nonempty vectors required")
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError("finite vectors required")
    return left - right
```

## Retrieval and alternatives

Without executing, predict the shape of a (2,) vector minus a (2,1) column. Explain why a pair guard should reject it even though NumPy can compute it. Then create a new paired centimeter/meter fixture and justify its conversion.

Then follow the [after-solutions routine](../STUDY-GUIDE.md#after-the-solutions).
