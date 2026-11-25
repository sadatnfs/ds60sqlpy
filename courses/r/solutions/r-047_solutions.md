# r-047: reference reasoning

Run the [complete reference](r-047_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference validates the fitted partition and the response identities in probability output. It intentionally uses an easy separable fixture so the model mechanics are independently inspectable. The pruning case changes the actual model object and retains a separate leaf count.

The complete-input policy belongs to the wrapper, not to a false assertion about rpart's native capabilities. Prediction outside the training range is labeled as a model extrapolation. Real complexity selection, calibration and group-aware validation require a separate study.

## Explained practice

### Exercise 1

Fit the declared depth-one classifier and predict x = 2 and x = 7.

The predictions are low and high, matching the two learned regions.

**Expected evidence:** low/high.

**Approach:** Call rpart with method = "class" and a control that allows splits on 8 rows: minsplit 2, minbucket 1, maxdepth 1, cp 0 and xval 0.

**Why it holds here:** The labels switch from low to high between x = 4 and x = 5, so a single cut there separates them perfectly. x = 2 falls on the low side and x = 7 on the high side.

**Tempting mistake:** Relying on the default control. rpart's default minsplit is 20, so with only 8 rows it never attempts a split, returns a lone root, and gives x = 2 and x = 7 the same class.

**Verify:** `as.character(predict(fit, new, type = "class"))` returns "low" and "high".

### Exercise 2

Inspect the probability matrix and its column identities.

Rows sum toone and columns identify the factor levels.

**Expected evidence:** Named low/high probabilities.

**Approach:** Request type = "prob", read its column names, and select columns by name rather than by position.

**Why it holds here:** The fixture sets levels = c("low", "high"), so the columns appear in that order. Each leaf is pure, so the rows for x = 2 and x = 7 are (1, 0) and (0, 1) and each sums to 1.

**Tempting mistake:** Taking `prob[, 2]` as the probability of high. In the pruning example the factor is built without explicit levels, so they sort alphabetically to high, low, and column 2 would be low.

**Verify:** `identical(colnames(prob), c("low", "high"))` returns TRUE and `max(abs(rowSums(prob) - 1))` returns a value below 1e-12.

### Exercise 3

Prune with cp 1 and count terminal leaves.

The simplified model has one terminal root.

**Expected evidence:** One leaf.

**Approach:** Store the result of prune(fit, cp = 1) in a new object and count leaves in that object's frame.

**Why it holds here:** The single split takes misclassifications from 4 of 8 to 0, a relative improvement of 1, and pruning at that complexity removes it. The frame keeps only the root, which is itself the one leaf.

**Tempting mistake:** Counting leaves on fit after calling prune. prune returns a new tree and leaves fit unchanged, so that count still shows 2.

**Verify:** `nrow(small$frame)` returns 1 and `sum(small$frame$var == "<leaf>")` returns 1.

### Exercise 4

Diagnose using perfect training accuracy to choose a complex tree.

A tree can fit authored or noisy training patterns without generalizing. Complexity selection belongs on development resamples, followed by a distinct final assessment.

**Expected evidence:** No unsupported generalization claim.

**Approach:** Report training accuracy as a fit statistic, and choose depth or cp on development folds before a separate final assessment.

**Why it holds here:** One cut already classifies all 8 training rows correctly. Any deeper tree would also score 8 of 8, so training accuracy cannot rank the candidates at all.

**Tempting mistake:** Selecting the deepest tree because it is also perfect on training data. With noisy labels, extra splits would isolate single rows, and only rows outside training show whether those splits help.

**Verify:** `all(as.character(predict(fit, d, type = "class")) == as.character(d$label))` returns TRUE, which shows fit on the 8 training rows only.

### Exercise 5

Implement a complete-finite-predictor admission policy for this application.

Reject NA or infinite x values explicitly while acknowledging that rpart has its own different native missingness mechanisms.

**Expected evidence:** Invalid input rejected by the wrapper.

**Approach:** Wrap predict in a function that stops on any NA or non-finite x before rpart sees it.

**Why it holds here:** This application declares that it scores only complete finite inputs. The check sits in the wrapper, so the rule is visible in code and does not depend on how rpart routes missing values internally.

**Tempting mistake:** Passing NA straight to predict. rpart has its own rules for missing predictors and still returns a class, so a row with no x value gets a confident looking label and nothing is logged.

**Verify:** `inherits(try(predict_complete(NA_real_), silent = TRUE), "try-error")` returns TRUE.

### Exercise 6

Predict at x = 1000 and explain the extrapolation limit.

The tree returns the high region rather than extending a numerical trend. This is a model output outside observed support, not proof of the real-world label.

**Expected evidence:** high with a bounded interpretation.

**Approach:** Score x = 1000 through the wrapper and report it as a value far outside the training range 1 to 8.

**Why it holds here:** Every x above the cut lands in the high leaf, so 1000 gets exactly the same class and probabilities as x = 5. A tree's leaves are constant regions, so there is no trend to extend.

**Tempting mistake:** Reading the result as stronger evidence for high because 1000 is far beyond the cut. The tree gives x = 5 and x = 1000 an identical output, and no training row says anything about values that large.

**Verify:** `as.character(predict_complete(1000)) == "high"` returns TRUE.

## What the checks establish

The assertions confirm that new points are classified low and high, that probability columns are named low and high and each row sums to 1, that pruning with cp 1 leaves one leaf, that a wrapper rejects a missing x, that an x of 1000 is still labeled high because the tree extends its last partition, and that the training rows are all classified correctly. Perfect training accuracy here is not evidence about held-out accuracy.

The reference makes 6 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
