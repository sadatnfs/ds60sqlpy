# r-045: reference reasoning

Use the [complete reference](r-045_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference checks disjointness at the family level and refits inside each fold. Its perfect synthetic affine predictions test implementation mechanics, not the credibility of real-world validation. The training-only centering example isolates a preprocessing leak without mixing it with model error.

The final aggregation preserves both sums and counts, allowing the observation-weighted result to be reconstructed. Temporal ordering is checked independently. A complete applied study must also reserve model-selection decisions for development data and retain a final assessment that was not reused for tuning.

## Explained practice

### Exercise 1

Construct a group-disjoint split for four two-row families.

Assign A/B to training and C/D to assessment; assert no group intersection.

**Expected evidence:** Zero shared groups.

**Approach:** Choose whole families first, A and B for training and C and D for assessment, and only then select their rows.

**Why it holds here:** Each family holds two consecutive rows, so A and B cover ids 1 to 4 and C and D cover ids 5 to 8. No family can appear on both sides, which is the condition this fixture needs.

**Tempting mistake:** Drawing four row ids at random. With two rows per family, a random draw of four rows almost always takes one row from at least one family and leaves its sibling in assessment.

**Verify:** `length(intersect(d$group[train], d$group[!train]))` returns 0.

### Exercise 2

Demonstrate why an odd/even row split leaks the same families.

Every family appears in both partitions even though row IDs differ.

**Expected evidence:** Four shared families.

**Approach:** Put odd rows in one partition and even rows in the other, then intersect the family labels as well as the ids.

**Why it holds here:** Rows 1, 3, 5 and 7 carry A, B, C and D, and rows 2, 4, 6 and 8 carry the same four labels. The ids never overlap, yet every family is on both sides.

**Tempting mistake:** Checking only `intersect(d$id[row_train], d$id[row_test])`. It returns an empty vector and makes the split look clean while all four families leak.

**Verify:** `length(intersect(d$group[c(1, 3, 5, 7)], d$group[c(2, 4, 6, 8)]))` returns 4.

### Exercise 3

Perform leave-one-group-out prediction for the exact rule y=1+2x.

Each fold has disjoint families and recovers the exact authored affine relationship; retain fold counts and error sums.

**Expected evidence:** Near-zero error with explicit fold counts.

**Approach:** Loop over the four families, fit lm(y ~ x) on the other six rows, predict the two held out rows and store the fold count and squared error sum.

**Why it holds here:** y = 1 + 2x holds exactly for all eight rows, so every fold recovers intercept 1 and slope 2 from its six rows, and each held out pair has zero error. The folds hold 2 rows each, 8 in total.

**Tempting mistake:** Fitting once on all eight rows and then splitting the errors by family. On this exact fixture the errors are still zero, so the leak is invisible in the output; only the per fold intersection check exposes it.

**Verify:** `sum(folds$n)` returns 8 and `sum(folds$squared_error_sum) < 1e-20` returns TRUE.

### Exercise 4

Diagnose centering with the full dataset before splitting.

Held-out covariates have influenced the fitted transformation. Recompute the center within each training partition.

**Expected evidence:** Training-only center restored.

**Approach:** Estimate the center from the training values 0 and 2 only, then subtract that same center from the held out values.

**Why it holds here:** The training mean is 1, so 100 and 102 become 99 and 101. That transformation uses no held out information, so the assessment rows are treated as new data.

**Tempting mistake:** Centering all four values before splitting. The mean becomes 51 and the held out values become 49 and 51, so values the model should never have seen have shifted the center by 50.

**Verify:** `mean(c(0, 2)) == 1` returns TRUE and `mean(c(0, 2, 100, 102)) == 51` returns TRUE.

### Exercise 5

Define the temporal split at day 4 in days 1 through 6.

Train on 1:4 and evaluate on 5:6; no future row is used to fit the earlier predictor.

**Expected evidence:** max(train day)<min(test day).

**Approach:** Cut the six days at day 4: days 1 to 4 train and days 5 and 6 assess.

**Why it holds here:** The latest training day is 4 and the earliest assessment day is 5, so no later observation helps fit a predictor that is judged on later days.

**Tempting mistake:** Shuffling the six days before splitting. A shuffle can put day 6 in training and day 2 in assessment, so the model learns from the future it is meant to forecast.

**Verify:** `max(day[day <= 4]) < min(day[day > 4])` returns TRUE, comparing 4 with 5.

### Exercise 6

Aggregate folds with error sums 2 and 12 and counts 1 and 3.

The observation mean is 14/4=3.5; the equal-fold mean of 2 and 4 is 3.

**Expected evidence:** Both quantities labeled; observation mean 3.5.

**Approach:** Add the error sums and the counts separately and divide once, then report the equal fold mean as a second, labeled figure.

**Why it holds here:** The two folds hold 1 and 3 observations, so pooling gives (2 + 12) / 4 = 3.5. The per fold means are 2 and 4, and their plain average is 3.

**Tempting mistake:** Reporting the average of the fold means, 3, as the error per observation. It gives the single observation fold the same weight as the three observation fold and understates the pooled error by 0.5.

**Verify:** `(2 + 12) / (1 + 3) == 3.5` returns TRUE and `mean(c(2 / 1, 12 / 3)) == 3` returns TRUE.

## What the checks establish

The reference makes 7 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
