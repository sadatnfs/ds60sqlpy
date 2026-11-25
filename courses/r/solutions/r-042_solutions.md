# r-042: reference reasoning

Run the [complete reference](r-042_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference uses different variance conventions for different objects. sd(x) estimates population spread from a sample, whereas the enumeration treats all bootstrap means as the complete conditional distribution. Neither result should be silently substituted for the other.

The shift test checks an invariant of centered spread. The count guard prevents an undefined sample-variance calculation from being interpreted as a usable estimate. Interval construction is shown explicitly, with its target and assumptions retained; no coverage claim is inferred from one synthetic realization.

## Explained practice

### Exercise 1

Derive the sample mean and estimated SE for c(2,4,6,8).

The mean is 5; sample variance 20/3; estimated SE is sqrt(5/3).

**Expected evidence:** Mean 5, SE squared 5/3.

**Approach:** Compute the sample variance with the n minus 1 divisor, divide it by n for the variance of the mean, and take the square root.

**Why it holds here:** The deviations from 5 are -3, -1, 1 and 3, whose squares sum to 20. Dividing by 3 gives 20/3, dividing again by 4 gives 5/3, so the standard error is about 1.29.

**Tempting mistake:** Dividing the squared deviations by n, which gives 5 and an SE squared of 5/4. That is the bootstrap's plug-in variance, not the sample estimate this lesson asks for.

**Verify:** `isTRUE(all.equal(mean_se(x)^2, 5 / 3))` returns TRUE.

### Exercise 2

Add three to every observation and compare the estimate and SE.

The mean becomes 8 while the standard error is unchanged.

**Expected evidence:** Mean 8; same SE.

**Approach:** Shift every value by 3 and recompute both the mean and the standard error.

**Why it holds here:** x + 3 is 5, 7, 9 and 11. The mean moves to 8, but each deviation from the mean is still -3, -1, 1 or 3, so sd, and therefore the SE, are unchanged.

**Tempting mistake:** Expecting the SE to grow because the mean grew, as if uncertainty were a fixed share of the estimate. Multiplying by 3, not adding 3, is what would triple the SE.

**Verify:** `mean(x + 3) == 8` returns TRUE and `isTRUE(all.equal(mean_se(x + 3), mean_se(x)))` returns TRUE.

### Exercise 3

Enumerate all four-draw bootstrap samples and verify their conditional variance.

The empirical variance is 5 and four independent draws produce mean variance 5/4.

**Expected evidence:** 256 means; conditional variance 1.25.

**Approach:** Enumerate all 4^4 = 256 ordered index tuples with expand.grid, weight each one equally, and divide the squared deviations of their means by 256.

**Why it holds here:** Every ordered draw is equally likely, so these 256 means are the complete bootstrap distribution. Its center is 5 and its variance is the plug-in variance 5 divided by 4 draws, which is 1.25.

**Tempting mistake:** Calling `var(means)`, which divides by 255 and returns about 1.255, as if the 256 values were a sample. Listing only the 35 unordered multisets with equal weight is also wrong, because 2, 2, 2, 2 arises once while a mix of four different values arises 24 times.

**Verify:** `length(means)` returns 256, and `mean((means - 5)^2)` returns 1.25 within all.equal.

### Exercise 4

Diagnose dividing the observation standard deviation by n instead of sqrt(n).

The wrong formula shrinks uncertainty too quickly. For n4 it is half the correct SE.

**Expected evidence:** Wrong SE equals correct SE/2.

**Approach:** Divide the standard deviation by the square root of n.

**Why it holds here:** With n = 4 the square root is 2, so the correct SE is sd/2, about 1.29, while sd/4 is about 0.65. The variance of a mean shrinks with n, so its standard deviation shrinks with the square root of n.

**Tempting mistake:** Using `sd(x) / length(x)`. Here it halves the SE, and with 100 observations it would be ten times too small, giving intervals far narrower than the data support.

**Verify:** `isTRUE(all.equal(sd(x) / length(x), mean_se(x) / 2))` returns TRUE.

### Exercise 5

State a policy for estimating this SE from zero or one observation.

Reject the request explicitly instead of presenting NA as a successful uncertainty estimate.

**Expected evidence:** A defined error for count below 2.

**Approach:** Stop with a clear message when fewer than two finite values are supplied.

**Why it holds here:** The sample variance divides by n minus 1, which is 0 for one value, so `sd(1)` returns NA. One observation carries no information about spread.

**Tempting mistake:** Returning NA or 0 so the code keeps running. An NA SE turns the interval into NA, NA without saying why, and 0 claims perfect certainty from a single reading.

**Verify:** `inherits(try(mean_se(1), silent = TRUE), "try-error")` returns TRUE.

### Exercise 6

Compare a Student t mean interval with a percentile interval from the exact bootstrap distribution.

Both describe uncertainty of a mean under different procedures; their agreement or disagreement on this fixture does not establish population coverage or a future-observation prediction interval.

**Expected evidence:** Correctly labeled intervals with declared quantile convention.

**Approach:** Label each interval by its procedure and target before comparing endpoints: a t interval for the mean, and percentile limits of the exact bootstrap distribution.

**Why it holds here:** The t interval is 5 plus or minus qt(0.975, 3) times about 1.29, roughly 0.89 to 9.11. The bootstrap limits are 3 and 7, because the 7th and 8th smallest of the 256 means are both 3. The bootstrap uses the smaller plug-in variance and no t correction for 3 degrees of freedom.

**Tempting mistake:** Preferring the bootstrap interval because it is narrower, or claiming either has 95 percent coverage. With 4 values, the percentile method is known to be too narrow, and one fixture cannot check coverage.

**Verify:** The printed list shows `t_mean_interval` near 0.89 and 9.11 and `exact_empirical_percentile` at 3 and 7.

## What the checks establish

The checks confirm a mean of 5 with squared standard error 5/3, a shift by 3 that moves the mean but not the standard error, all 256 bootstrap resamples averaging exactly 5 with variance 5/4, the relationship between the standard deviation and the standard error, rejection of a single observation, and t and percentile intervals that both contain 5. They do not show that either interval has its nominal coverage for such a small sample.

The reference makes 7 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
