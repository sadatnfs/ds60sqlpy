# eval-019: explained reference

The full reference is `eval-019_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Add a reward constant

Only relative action rewards influence the finite-policy optimum under a fixed reference.

**Expected observation:** The optimal distribution is unchanged.

## 2. Rescale reward and beta

The objective scale changes but the reward-to-regularization tradeoff does not.

**Expected observation:** The optimal distribution is unchanged.

## 3. Inspect the gradient sum

This invariance checks the centered gradient through the probability parameterization.

**Expected observation:** The sum is approximately zero.

## 4. Handle large rewards

The subtraction preserves normalized ratios while avoiding unnecessary overflow.

**Expected observation:** Stable normalization returns finite probabilities.

## 5. Identify missing support

Adding a probability floor creates another reference distribution and must be treated as a modeling change.

**Expected observation:** The bounded helper rejects the unsupported objective.

## 6. Test independent utility

KL regularization can limit distribution change, but it cannot validate the reward model or rule out exploitation of a proxy.

**Expected observation:** Proxy reward rises while independent task utility falls.
