# eval-013: explained reference

The full reference is `eval-013_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Two noisy candidates

Three combinations select+0.1 and one selects-0.1, giving(0.3-0.1)/4.

**Expected observation:** The mean maximum is 0.05.

## 2. Change only final outcomes

This invariant distinguishes assessment from a hidden second round of tuning.

**Expected observation:** The selected candidate IDs do not change.

## 3. Specify a tie rule

Tie handling is part of a reproducible procedure; it should not depend on which final outcome is better.

**Expected observation:** The reference chooses the first candidate deterministically.

## 4. Find the optimistic procedure

The larger score is explained by using outcome information twice, not by evidence that the original procedure improved.

**Expected observation:** Its same-table average is 0.85, but it is no longer protected assessment.

## 5. Place preprocessing

An outer holdout can leak through a transform even when the final estimator receives only training rows.

**Expected observation:** Inside the corresponding training/development partition.

## 6. Reclassify a reused holdout

Acquire a new protected assessment for the changed procedure rather than claiming the original untouched-test interpretation.

**Expected observation:** The set becomes development or regression evidence for that revision.
