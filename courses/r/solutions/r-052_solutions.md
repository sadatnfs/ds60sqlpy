# r-052: reference reasoning

Use the [complete reference](r-052_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The summary is calculated from the same raw group observations shown in the graphic. The reference distinguishes a standard error from its t-based interval multiplier, and it includes interval endpoints when selecting shared panel limits.

The plot helper restores layout state without taking ownership of the surrounding device. Numerical and file checks can establish the calculations and drawing path, while the final classroom image still needs visual inspection for labels, overlap and accessibility.

## Explained practice

### Exercise 1

Calculate both group means and standard errors from the raw observations.

Means are 2.5 and 4.5; squared SEs are 5/12 and 17/12 respectively.

**Expected evidence:** Correct means and SE denominators.

**Approach:** Compute each group's mean and sd with the n minus 1 divisor, then divide sd by the square root of its own count, 4.

**Why it holds here:** A = 1, 2, 3, 4 has mean 2.5 and squared deviations summing to 5, so the variance is 5/3 and SE squared is 5/12. B = 2, 3, 6, 7 has mean 4.5 and squared deviations summing to 17, so SE squared is 17/12.

**Tempting mistake:** Dividing the squared deviations by n instead of n minus 1. A would then get SE squared 5/16 instead of 5/12, a quarter smaller in variance and too narrow in every interval built from it.

**Verify:** `se^2` returns 5/12 and 17/12 within 1e-12.

### Exercise 2

Construct the stated 95 percent t intervals for the means.

Each interval is mean plus/minus qt(0.975,3) times its SE, under the stated sampling/model assumptions.

**Expected evidence:** Correctly labeled mean intervals.

**Approach:** Multiply each SE by qt(0.975, 3), about 3.18, and add and subtract that half width from each mean.

**Why it holds here:** Each group has 4 values and so 3 degrees of freedom. A's half width is about 2.05, giving 0.45 to 4.55, and B's is about 3.79, giving 0.71 to 8.29.

**Tempting mistake:** Using the normal value 1.96. With 3 degrees of freedom the half widths shrink by about 38 percent, to about 1.27 and 2.33, and the intervals claim more precision than four values support.

**Verify:** `all(half > se)` returns TRUE, and `half` returns about 2.05 and 3.79.

### Exercise 3

Draw raw observations and summaries with shared y limits.

The two panels use one numerical y mapping, supporting direct magnitude comparison.

**Expected evidence:** One two-panel page with shared limits.

**Approach:** Compute one ylim from the raw values together with every interval endpoint and pass it to both panels.

**Why it holds here:** The raw values span 1 to 7 but the intervals reach about 0.45 and 8.29, so the shared range is 0.45 to 8.29. A unit of height then means the same amount in both panels.

**Tempting mistake:** Taking limits from the raw values alone. B's upper end and A's lower end then fall outside 1 to 7, so their arrows are clipped and look shorter than they are.

**Verify:** `range(c(unlist(groups), means - half, means + half))` returns about 0.45 and 8.29.

### Exercise 4

Diagnose labeling mean plus/minus one SE as a 95 percent confidence interval.

One SE is not the same procedure as the stated t interval; relabel or calculate the intended interval.

**Expected evidence:** Interval target/construction repaired.

**Approach:** Label the bars by what they are: draw the t interval and call it a 95 percent interval, or draw plus or minus one SE and call it that.

**Why it holds here:** For these groups the t interval is qt(0.975, 3), about 3.18 times, wider than one SE. A's one SE bar would run 1.85 to 3.15, while its stated interval runs 0.45 to 4.55.

**Tempting mistake:** Drawing mean plus or minus SE and titling it 95 percent intervals. The bars are about a third of the stated width, so A and B look more clearly separated than the intervals allow.

**Verify:** `half / se` returns about 3.18 for both groups.

### Exercise 5

Explain why zero cannot be placed on an ordinary logarithmic axis.

The logarithm is not finite at zero; choose a justified alternate representation or admission policy rather than silently dropping the observation.

**Expected evidence:** Domain issue explicitly handled.

**Approach:** Check the values before plotting on a log axis, and decide openly how a zero or negative value will be handled.

**Why it holds here:** log(0) is minus infinity, so zero has no position on the axis. For 1, 10 and 100 the log10 gaps are both 1, which is why those points sit equally spaced even though their raw differences are 9 and 90.

**Tempting mistake:** Letting plot drop the zero with only a warning, or adding 1 to every value. The shift turns 1, 10 and 100 into 2, 11 and 101, whose ratios are no longer equal, so the spacing changes meaning.

**Verify:** `is.finite(log(0))` returns FALSE, and the log10 differences of `c(1, 10, 100)` return 1 and 1.

### Exercise 6

Restore a caller's layout after a plotting helper.

The helper restores mfrow/margins and does not close an unrelated device.

**Expected evidence:** Caller layout preserved.

**Approach:** Inside draw, save the result of par(mfrow = c(1, 2), mar = ...) and register `par(old)` with on.exit.

**Why it holds here:** par returns the previous values of the settings it changes, so on.exit restores the caller's layout and margins when draw returns, even after an error. draw never closes the device, which belongs to the caller.

**Tempting mistake:** Ending the helper with dev.off to tidy up, which closes the caller's device, or never restoring mfrow, so the caller's next plot lands in half of the page.

**Verify:** `identical(par("mfrow"), before)` returns TRUE after draw.

## What the checks establish

The reference makes 4 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
