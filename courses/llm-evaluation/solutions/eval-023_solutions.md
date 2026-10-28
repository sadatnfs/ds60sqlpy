# eval-023: explained reference

The full reference is `eval-023_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Shift all rewards

Relative normalization removes a common level; it does not preserve information about absolute task success.

**Expected observation:** The normalized advantages stay unchanged.

## 2. Inspect a constant group

These groups represent different absolute outcomes despite the same lack of within-group ranking signal.

**Expected observation:** Both produce zero relative advantages under the declared rule.

## 3. Change length weighting

A token average weights longer responses more heavily and defines a different objective from equal-response weighting.

**Expected observation:** Response average 0; token average 1/3.

## 4. Check the sampling law

Importance correction can recover the value expectation with adequate support, but has variance costs and does not by itself prove a gradient estimator is correct.

**Expected observation:** The value differs from current-policy KL.

## 5. Separate value from derivative

A zero average advantage or initial objective value does not imply absence of a learning signal.

**Expected observation:** Its value is 0 while its derivative is 0.5.

## 6. Declare algorithm variants

A shared acronym is insufficient to establish that two implementations optimize the same objective.

**Expected observation:** Record the change as part of the training algorithm.
