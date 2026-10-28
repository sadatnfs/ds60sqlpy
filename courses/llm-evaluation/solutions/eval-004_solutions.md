# eval-004: explained reference

The full reference is `eval-004_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Reconstruct the confusion table

Two negative-negative pairs, one positive-negative pair and one positive-positive pair determine both marginals and agreement.

**Expected observation:** Rows A and columns B give [[2,0],[1,1]].

## 2. Perfect variation

There is perfect observed agreement with nondegenerate marginals, so the corrected coefficient is defined and equals 1.

**Expected observation:** Kappa equals 1.

## 3. Complete disagreement

A negative coefficient means less agreement than the marginal reference, not a negative count of labels.

**Expected observation:** Kappa equals -1.

## 4. Single-category degeneracy

Both raw and reference agreement are 1. The coefficient becomes 0/0, so preserve the degeneracy instead of replacing it with an attractive score.

**Expected observation:** Kappa is undefined and rejected.

## 5. Distinguish weighted quantities

Observed squared-distance disagreement is useful descriptively, but weighted kappa would normalize it by expected disagreement under marginals.

**Expected observation:** The implemented quantity lacks an expected-disagreement correction.

## 6. Change the dependence unit

Additional paraphrases may reveal within-family variation, but family-level uncertainty cannot treat twenty rows as twenty independent sampled families.

**Expected observation:** The evaluation still has two sampled families.
