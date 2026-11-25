# r-041: reference reasoning

Run the [complete reference](r-041_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference preserves the observed set explicitly. Selecting x[valid] avoids performing arithmetic on missing entries and makes the denominator count inspectable. The zero in the first fixture is a valid measurement, so removing it would create another selection error.

The grouped calculation retains enough information to reconstruct the observation-weighted mean. Averages of group averages change the weighting unless group counts are equal or equal group weighting is the intended question. The all-missing branch returns missing output deliberately; it does not turn absent evidence into a zero estimate.

The tail comparison uses the same five authored values for both summaries. Its conclusion is about their arithmetic sensitivity. Decisions about measurement error, eligibility or population inference require evidence not present in this small fixture.

## Explained practice

### Exercise 1

Predict the row, observed and missing counts for c(0, NA, 2, NA).

There are four rows, two observed values and two missing values; the observed mean is one.

**Expected evidence:** Counts 4,2,2; mean 1.

**Approach:** Build the missingness mask with is.na and count both sides of it before computing any summary.

**Why it holds here:** In c(0, NA, 2, NA), the 0 is a measurement, so 2 values are observed, 2 are missing and the observed mean is (0 + 2) / 2 = 1.

**Tempting mistake:** Treating zero as empty, for example with `x[!is.na(x) & x != 0]`. The observed count drops to 1 and the mean rises to 2, so a real zero reading vanishes from the denominator.

**Verify:** `describe(c(0, NA_real_, 2, NA_real_))` returns rows 4, observed 2, missing 2 and mean 1.

### Exercise 2

Add an observed value eight to c(1, NA, 4, 6, NA) and update the mean.

The observed sum becomes 19 and the observed count four, so the mean is 19/4.

**Expected evidence:** Observed count 4, mean 4.75.

**Approach:** Add the new value to the observed sum and to the observed count, then divide once.

**Why it holds here:** The observed values become 1, 4, 6 and 8, so the sum moves from 11 to 19 and the count from 3 to 4, giving 19/4 = 4.75.

**Tempting mistake:** Averaging the old mean with the new value, (11/3 + 8) / 2, which is about 5.83. That gives the single new value the same weight as the three earlier ones.

**Verify:** `b[["observed"]]` returns 4 and `b[["mean"]] == 19 / 4` returns TRUE.

### Exercise 3

Construct group summaries for A=c(1,NA) and B=c(4,6,NA), retaining observed counts.

A has one observed value and mean one; B has two and mean five. The overall observed mean is the count-weighted 11/3, not the equal-group mean three.

**Expected evidence:** A: count 1 / mean 1; B: count 2 / mean 5; overall 11/3.

**Approach:** Call describe on each group, keep each observed count, and weight the group means by those counts for the overall figure.

**Why it holds here:** A has one observed value, 1, and B has two, 4 and 6, with mean 5. Weighting gives (1 times 1 + 5 times 2) / 3 = 11/3, the same as averaging the three observed values directly.

**Tempting mistake:** Averaging the two group means to get 3. That treats A's single value as half the evidence when it is a third of the observed values.

**Verify:** `summaries$A[["observed"]]` and `summaries$B[["observed"]]` return 1 and 2, and the weighted result returns 11/3 within all.equal.

### Exercise 4

Diagnose replacing every missing measurement with zero before averaging.

The replacement changes the data and denominator. For the five-row fixture it produces 11/5 rather than the observed-value mean 11/3. Neither is a justified population estimate without a missingness model.

**Expected evidence:** The two descriptive quantities differ and the assumption is stated.

**Approach:** Report the observed value mean with its count, and state that it describes the 3 observed rows, not all 5.

**Why it holds here:** Filling both gaps with 0 turns the sum of 11 over 3 values into 11 over 5, so the mean drops from about 3.67 to 2.2, a 40 percent cut caused only by the fill rule.

**Tempting mistake:** Using `replace(x, is.na(x), 0)` because it keeps all five rows. The two missing records never supplied a measured zero, so both the data and the denominator change.

**Verify:** `mean(filled) == 11 / 5` returns TRUE, and comparing it with the weighted 11/3 returns FALSE under all.equal.

### Exercise 5

Define and test the summary of c(NA_real_, NA_real_).

Return counts two/zero/two and an explicit NA_real_ mean; do not report zero as an observed average.

**Expected evidence:** Observed count 0; mean NA.

**Approach:** Check `any(valid)` before calling mean or median, and return NA_real_ for both when nothing was observed.

**Why it holds here:** For c(NA_real_, NA_real_) the observed count is 0. Without the guard, `mean(x[valid])` averages an empty vector and returns NaN, which is not the explicit missing result the summary should state.

**Tempting mistake:** Using `mean(x, na.rm = TRUE)` and printing the result as an average. It also returns NaN here, and a later `ifelse(is.nan(m), 0, m)` would report 0 for a column with no data.

**Verify:** `empty[["observed"]] == 0` returns TRUE and `is.na(empty[["mean"]])` returns TRUE.

### Exercise 6

Compare mean and median after adding 100 to c(1,2,2,3), and explain the inferential limit.

Mean becomes 21.6 and median 2. The difference describes sensitivity to the tail; it does not establish that 100 is erroneous or that the sample represents a population.

**Expected evidence:** Correct summaries and a bounded interpretation.

**Approach:** Print the mean and median side by side on the full five values and describe their difference as sensitivity to one large value.

**Why it holds here:** `c(1, 2, 2, 3, 100)` sums to 108, so the mean is 21.6, while the middle value stays 2. Without 100 both summaries are 2, so a single value moves the mean by 19.6.

**Tempting mistake:** Deleting 100 as an outlier because it moves the mean. Nothing in these five numbers says whether 100 is an error or a real large observation.

**Verify:** `all.equal(mean(tail), 21.6)` returns TRUE and `median(tail)` returns 2.

## What the checks establish

The assertions confirm summaries that keep rows, observed and missing counts beside the mean, group summaries where A has one observed value with mean 1 and B has two with mean 5, a pooled mean of 11/3 that differs from the 11/5 produced by filling missing values with zero, an empty summary with an NA mean, and a skewed tail whose mean of 21.6 sits far from its median of 2. They do not decide whether missingness is random.

The reference makes 8 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
