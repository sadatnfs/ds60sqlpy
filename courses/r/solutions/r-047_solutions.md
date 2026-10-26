# r-047: reference reasoning

Use the [complete reference](r-047_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference validates the fitted partition and the response identities in probability output. It intentionally uses an easy separable fixture so the model mechanics are independently inspectable. The pruning case changes the actual model object and retains a separate leaf count.

The complete-input policy belongs to the wrapper, not to a false assertion about rpart's native capabilities. Prediction outside the training range is labeled as a model extrapolation. Real complexity selection, calibration and group-aware validation require a separate study.

## Explained practice

### Exercise 1

Fit the declared depth-one classifier and predict x = 2 and x = 7.

The predictions are low and high, matching the two learned regions.

**Expected evidence:** low/high.

### Exercise 2

Inspect the probability matrix and its column identities.

Rows sum toone and columns identify the factor levels.

**Expected evidence:** Named low/high probabilities.

### Exercise 3

Prune with cp 1 and count terminal leaves.

The simplified model has one terminal root.

**Expected evidence:** One leaf.

### Exercise 4

Diagnose using perfect training accuracy to choose a complex tree.

A tree can fit authored or noisy training patterns without generalizing. Complexity selection belongs on development resamples, followed by a distinct final assessment.

**Expected evidence:** No unsupported generalization claim.

### Exercise 5

Implement a complete-finite-predictor admission policy for this application.

Reject NA or infinite x values explicitly while acknowledging that rpart has its own different native missingness mechanisms.

**Expected evidence:** Invalid input rejected by the wrapper.

### Exercise 6

Predict at x = 1000 and explain the extrapolation limit.

The tree returns the high region rather than extending a numerical trend. This is a model output outside observed support, not proof of the real-world label.

**Expected evidence:** high with a bounded interpretation.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
