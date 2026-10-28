# eval-021: explained reference

The full reference is `eval-021_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Remove the trace

This isolates the one-step residual calculation and its terminal mask.

**Expected observation:** Advantages reduce to residuals 0.86 and 1.6.

## 2. Terminate the first step

The array illustrates boundary behavior; separate episodes should otherwise be processed with explicit episode structure.

**Expected observation:** The first result is 0.5 and does not inherit the second residual.

## 3. Positive advantage outside the interval

The surrogate stops rewarding that favorable increase beyond the upper boundary.

**Expected observation:** The clipped term is 1.2.

## 4. Negative advantage outside the interval

The bad-direction probability increase still receives its larger penalty.

**Expected observation:** The term is -1.5, not-1.2.

## 5. Check an unobserved action

Clipping a finite sampled objective cannot by itself bound every unobserved action probability or full-distribution divergence.

**Expected observation:** Their sampled terms agree while global KL differs.

## 6. Freeze rollout quantities

Gradients through old probabilities or an unintended baseline optimize another objective and can destroy the interpretation of the ratio estimator.

**Expected observation:** Stored old log probabilities and computed advantages are fixed.
