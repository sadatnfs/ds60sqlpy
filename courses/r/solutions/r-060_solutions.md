# r-060: reference reasoning

Run the [complete reference](r-060_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference calculates one eligibility/summary table and uses it consistently across the static and interactive views. It checks raw IDs, layer counts, trace counts and uncertainty coordinates, preventing duplicated summary marks from being mistaken for additional observations.

The two printed figures share a numerical contract while retaining different rendering systems. The source and worker capture can establish actual PNG/Plotly payload production, but final browser usability remains a separate observation. The group difference is explicitly descriptive because the fixture supplies no causal assignment design.

## Explained practice

### Exercise 1

Build the eligibility ledger from the ten raw records.

There are eight observed values and two missing measurements, with four observed values per group.

**Expected evidence:** Counts 10/8/2 and group counts 4/4.

**Approach:** Keep d with all ten records, form observed from the non missing rows, and record n and missing per group in summary.

**Why it holds here:** Each group has five records and one missing value, A5 and B5, so the ledger shows 10 records, 8 observed values and 2 missing ones, four observed per group. The figure can then say exactly what it excludes.

**Tempting mistake:** Calling na.omit(d) first and summarizing what remains. The counts of 4 look complete, and nothing in the output says two measurements were absent.

**Verify:** `nrow(observed)` returns 8, `summary$n` returns 4 and 4, and `summary$missing` returns 1 and 1.

### Exercise 2

Derive means, SEs and t-interval endpoints.

Means are 2.5 and 4.5; squared SEs 5/12 and 17/12; half-widths are qt(0.975,3) times SE.

**Expected evidence:** Independent numerical oracle.

**Approach:** Inside the split, compute n, sd, se and qt(0.975, n - 1) from the non missing values only, then store lower, upper and half.

**Why it holds here:** Group A's observed values 1, 2, 3, 4 give mean 2.5 and SE squared 5/12. Group B's 2, 3, 6, 7 give mean 4.5 and 17/12. With 3 degrees of freedom the half widths are about 2.05 and 3.79.

**Tempting mistake:** Taking n as length(values), which counts the missing entry. A would then use 5 and 4 degrees of freedom, and its half width would fall from about 2.05 to about 1.60, overstating precision from a value that was never measured.

**Verify:** `summary$se^2` returns 5/12 and 17/12, and `summary$half` returns about 2.05 and 3.79.

### Exercise 3

Construct a static raw-point and interval display from those tables.

Eight raw marks and two mean intervals correspond to distinct statistical objects.

**Expected evidence:** Correct layer counts and interval coordinates.

**Approach:** Plot observed as points, then add geom_errorbar and a cross geom_point using data = summary and inherit.aes = FALSE, with a caption naming the interval type.

**Why it holds here:** The global mapping uses value, which exists in observed but not in summary. Turning off inheritance lets the summary layers use lower, upper and mean, so the plot shows eight raw values and two intervals as different objects.

**Tempting mistake:** Omitting inherit.aes = FALSE on the summary layers. They then look for value in summary, and the build stops instead of drawing the intervals.

**Verify:** `nrow(layers[[1]])` returns 8, and `nrow(layers[[2]])` and `nrow(layers[[3]])` each return 2.

### Exercise 4

Construct an interactive figure retaining raw IDs and a separate summary trace.

The raw trace has eight keyed observations; the summary trace has two means and supplied error bars.

**Expected evidence:** Trace counts 8 and 2 with retained identity.

**Approach:** Add the observed trace with customdata = ~id and a hover template, then a separate summary trace with error_y set from summary$half.

**Why it holds here:** The two traces hold different things: eight measured values with IDs A1 to A4 and B1 to B4, and two means with their interval half widths. Keeping them apart means the observation count stays at 8.

**Tempting mistake:** Appending the two means to the observed rows and drawing one trace. It then has ten points, two of them with no ID, and anyone counting markers sees ten observations.

**Verify:** `length(traces[[1]]$x)` returns 8, `length(traces[[2]]$x)` returns 2, and the sorted customdata returns the eight observed IDs.

### Exercise 5

Diagnose interpreting the mean difference as a causal effect.

The difference of two is descriptive for this fixture. A causal interpretation requires additional design assumptions and evidence.

**Expected evidence:** No unsupported causal claim.

**Approach:** Describe the gap of 2 between the means as a difference in this sample, and name what would be required before calling it an effect.

**Why it holds here:** d contains only id, group and value. Nothing records how records came to be in A or B, and with intervals of about 0.45 to 4.55 and 0.71 to 8.29 the data are also compatible with a much smaller or larger gap.

**Tempting mistake:** Writing that being in group B raises the value by 2. That needs an assignment mechanism or an identification argument, and the fixture supplies neither.

**Verify:** `diff(summary$mean)` returns 2, and `names(d)` returns only id, group and value.

### Exercise 6

Produce a factual report of what execution and capture established.

Report calculation and layer/trace checks, actual printed/captured figures, and any unperformed readability, hover or accessibility checks.

**Expected evidence:** A complete bounded evidence record.

**Approach:** Write the evidence record in three parts: numerical checks, layer and trace checks with the figures actually printed, and the browser checks still outstanding.

**Why it holds here:** The reference establishes 10, 8 and 2 records, the means, SEs and half widths, layer counts 8, 2 and 2, trace counts 8 and 2, and the error array. It prints the summary table and both figures, but it does not observe hover, readability or screen reader output.

**Tempting mistake:** Writing that the figure was validated because the script finished. That merges payload checks with classroom observations that nobody made.

**Verify:** The reference prints r-060 reference checks passed after the three printed objects, and the record shows the browser checks marked as not yet performed.

## What the checks establish

The checks confirm ten records with eight unique observed ids and two missing, means of 2.5 and 4.5 with squared standard errors 5/12 and 17/12, a static display with eight raw points, two means and two intervals, an interactive figure with eight raw points carrying their ids and a summary trace whose error bars equal the half widths, and a mean difference of 2. They do not support a causal interpretation of that difference.

The reference makes 7 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
