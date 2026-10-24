# tf-003: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/tf-003.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](tf-003_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace the product

The original feature matrix has two observations and three input features. W has three feature rows and one output column, so the contracted feature dimension is valid. The first output is \(1-3+2=0\) and the second is \(0+2=2\). Preserve the (2,1) result shape because this helper represents an explicit output axis. A rank-one residual helper may choose a different layout later, but that conversion must be deliberate.

**Expected:** Result [[0],[2]] with shape (2,1).

**Verify:** Assert both output values and recover the first zero from four written terms.

## Exercise 2: Add an observation

A batch row changes the number of observations, not the feature width or the parameter count. Appending [3,0,0] adds prediction \(3\cdot 1\) + \(0\cdot 0\) + \(0\cdot (-1)\) + 2 = 5. The original rows remain 0 and 2. Comparing that unchanged prefix is useful evidence that a batching operation did not accidentally normalize across records or change a parameter. It does not imply an arbitrary future training pipeline has the same invariant.

**Expected:** The result is [[0],[2],[5]] with shape (3,1).

**Verify:** Compare the original two output rows unchanged and assert the new scalar is 5.

## Exercise 3: Reject incompatible features

Require X and W to be rank-two arrays, nonempty on their declared axes, and X.shape[1] equal to W.shape[0]. The supplied (2,3) and (2,1) operands disagree on three versus two input features, so raise ValueError with that mismatch before computing @. Do not transpose X merely to suppress the error. The observation and feature roles would change, and the resulting arithmetic would answer a different question.

**Expected:** A ValueError explains the input-feature mismatch before a matrix product is attempted.

**Verify:** Capture the mismatch exception and inspect the accepted (2,3) @ (3,1) result afterward.

## Exercise 4: Guard the bias axis

For one output, a scalar bias and a length-one output vector both add 2 to each result and produce [[0],[2]]. Bias [2,3,4] instead has one entry per input feature. Plain NumPy broadcasts it into a (2,3) result, but that violates the declared output contract. Validate bias rank and length explicitly. A per-observation bias would also be a different model and should not be accepted as an accidental broadcast.

**Expected:** Scalar and length-one vector biases give the same [[0],[2]]; feature-length bias raises ValueError.

**Verify:** Assert equality of the two accepted outputs and capture the rejected bias case independently.

## Exercise 5: Extend to two outputs

The two-output weight maps each input row to two sums. First output weights [1,0,-1] with bias 2 reproduce [0,2]. Second output weights [0,1,1] with bias -1 give \(2+3-1=4\) for the first record and \(1-1=0\) for the second. Assemble these as [[0,4],[2,0]]. Looking only at the (2,2) shape could miss an incorrect column order, sign or bias, so inspect values as well.

**Expected:** The result is [[0,4],[2,0]] with shape (2,2).

**Verify:** Check each output column by hand and assert the complete matrix, not just its shape.

## Exercise 6: Preserve a prediction under unit conversion

The centimeter inputs are 100 times the meter values. To preserve the same weighted contribution when inputs are divided by 100, multiply the corresponding weight by 100: 0.02 becomes 2. The shared bias remains 1. Both models therefore produce 3 and 5. Retaining weight 0.02 on the meter inputs would yield 1.02 and 1.04, a valid-shaped but different computation. Feature-unit metadata must travel with model preprocessing and inference contracts.

**Expected:** The centimeter model and meter model with \(W=[[2]]\) both predict [[3],[5]].

**Verify:** Assert both predictions agree and explain why changing X alone while retaining 0.02 would alter the model.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import numpy as np


def affine(x, weight, bias):
    x, weight, bias = (np.asarray(v, dtype=np.float64) for v in (x, weight, bias))
    if x.ndim != 2 or weight.ndim != 2 or not all(x.shape) or not all(weight.shape):
        raise ValueError("nonempty feature and weight matrices required")
    if x.shape[1] != weight.shape[0]:
        raise ValueError("input-feature dimensions do not match")
    if bias.ndim > 1 or (bias.ndim == 1 and bias.shape != (weight.shape[1],)):
        raise ValueError("bias must be scalar or output-length vector")
    if not all(np.isfinite(v).all() for v in (x, weight, bias)):
        raise ValueError("finite affine inputs required")
    return x @ weight + bias
```

## Retrieval and alternatives

Close the code and state the three matrix dimensions in words. Then choose a two-feature, two-output fixture of your own and derive its first row. Explain why a correctly shaped matrix can still use the wrong feature order.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
