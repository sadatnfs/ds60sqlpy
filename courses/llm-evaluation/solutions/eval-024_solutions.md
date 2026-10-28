# eval-024: explained reference

The full reference is `eval-024_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Recover behavior value

This is a basic estimator invariant under the constructed log.

**Expected observation:** All weights are 1 and the mean observed reward is 0.75.

## 2. Evaluate a useful target

Known counterfactual outcomes make this value inspectable only in the authored environment; real evaluations need data and assumptions.

**Expected observation:** The target value is 0.9.

## 3. Remove behavior support

A value model may extrapolate there, but that is a different identifying assumption and not justified by overlap-based evaluation alone.

**Expected observation:** The helper rejects the target.

## 4. Use a zero outcome model

This algebraic check separates the correction structure from a claim that the supplied model is correct.

**Expected observation:** The doubly robust expression reduces to ordinary importance sampling.

## 5. Interpret self-normalization

Self-normalization changes the estimator. A useful variance tradeoff should not be described as exact finite-sample unbiasedness.

**Expected observation:** Their finite-sample values differ.

## 6. Audit the final claim

A complete alignment decision needs independent task utility, support, uncertainty and critical-condition evidence, not only a favorable training reward or off-policy point estimate.

**Expected observation:** Treat that log as selection evidence and obtain a protected final assessment.
