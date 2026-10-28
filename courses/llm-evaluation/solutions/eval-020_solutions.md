# eval-020: explained reference

The full reference is `eval-020_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Evaluate the reference

The initial classifier is indifferent under the pairwise parameterization.

**Expected observation:** The loss for a positive preference is log 2.

## 2. Differentiate the two-action loss

The result includes the beta scale and the logistic residual; it should agree with finite differences.

**Expected observation:** The derivative is -1.

## 3. Compare beta optima

Initial gradient magnitude and final optimum displacement are different properties of the objective.

**Expected observation:** Preferred-action probabilities are 0.9,0.75 and approximately 0.634.

## 4. Change length normalization

Normalizing each sequence by its own length changes its relative contribution and therefore the objective.

**Expected observation:** The sequence-sum margin is negative while the mean-token margin is positive.

## 5. Protect the reference

Reference refresh can be a deliberate algorithmic choice, but it is not the same fixed-reference DPO problem.

**Expected observation:** The objective has changed.

## 6. Bound the claim

Task utility, robustness, calibration and critical constraints still need their own held-out evaluation.

**Expected observation:** Conclude improved fit to the declared preference objective only.
