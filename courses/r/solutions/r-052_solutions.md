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

### Exercise 2

Construct the stated 95 percent t intervals for the means.

Each interval is mean plus/minus qt(0.975,3) times its SE, under the stated sampling/model assumptions.

**Expected evidence:** Correctly labeled mean intervals.

### Exercise 3

Draw raw observations and summaries with shared y limits.

The two panels use one numerical y mapping, supporting direct magnitude comparison.

**Expected evidence:** One two-panel page with shared limits.

### Exercise 4

Diagnose labeling mean plus/minus one SE as a 95 percent confidence interval.

One SE is not the same procedure as the stated t interval; relabel or calculate the intended interval.

**Expected evidence:** Interval target/construction repaired.

### Exercise 5

Explain why zero cannot be placed on an ordinary logarithmic axis.

The logarithm is not finite at zero; choose a justified alternate representation or admission policy rather than silently dropping the observation.

**Expected evidence:** Domain issue explicitly handled.

### Exercise 6

Restore a caller's layout after a plotting helper.

The helper restores mfrow/margins and does not close an unrelated device.

**Expected evidence:** Caller layout preserved.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
