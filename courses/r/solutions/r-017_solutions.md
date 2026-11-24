# r-017: reference reasoning

Use the [complete reference](r-017_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The intermediate character conversion retrieves the labels before numeric parsing. It is appropriate only if those labels genuinely represent measurements.

Subsetting retains the declared levels. Zero counts for B and C can be useful evidence rather than categories that should automatically disappear.

## Explained practice

### Exercise 1

Predict as.numeric(factor(c("5","9"))).

The values are 1,2 under the default sorted levels.

**Approach:** Build `factor(c("5", "9"))` and apply `as.numeric()` to it.

**Why it holds here:** The default levels are the sorted labels "5" and "9", and as.numeric returns each value's level position, so the result is 1, 2.

**Tempting mistake:** Expecting 5 and 9. Those are the labels; recovering them needs `as.numeric(as.character(x))`, as Example 1 shows.

**Verify:** `identical(as.numeric(factor(c("5", "9"))), c(1, 2))` returns TRUE.

### Exercise 2

Choose B as a reference level.

relevel(..., ref="B") puts B first for the relevant contrast convention.

**Approach:** Call `relevel(group, ref = "B")` with the exact declared label.

**Why it holds here:** B is one of the declared levels, so relevel moves it to the front and keeps A and C. Models then compare other groups with B.

**Tempting mistake:** Rebuilding with `factor(group, levels = "B")`. B moves first, but A and C are no longer levels, so both A rows become NA.

**Verify:** `levels(relevel(group, ref = "B"))` returns "B", "A", "C".

### Exercise 3

Retain an unused C level in a table.

The table includes C with count zero.

**Approach:** Declare C in `levels` when the factor is created, then call `table(group)`.

**Why it holds here:** The starter holds A twice and B once. Because C is declared, the table lists it with 0, showing that C was considered and had no rows.

**Tempting mistake:** Creating the factor without a levels argument. The table shows only A and B, so a reader cannot tell whether C was absent or never part of the design.

**Verify:** `unname(table(group)["C"])` returns 0.

### Exercise 4

Diagnose treating ordered low/medium/high as equally spaced numbers.

Choose a model encoding justified by the measurement assumptions.

**Approach:** Keep low, medium and high as an ordered factor and choose an encoding that matches what is known about the gaps.

**Why it holds here:** The order is known, but nothing says medium sits halfway between low and high. `as.integer()` on the reference values gives 1 and 3, which are positions, not distances.

**Tempting mistake:** Feeding the codes into a model as a number. That assumes the step from low to medium equals the step from medium to high; default polynomial contrasts for ordered factors make the same equal-spacing assumption.

**Verify:** `as.integer(ordered_group)` returns 1 and 3, and `is.ordered(ordered_group)` returns TRUE.

### Exercise 5

Handle a label outside declared levels.

It becomes NA and should be audited rather than silently accepted.

**Approach:** Detect labels that turned into NA by comparing the raw text with the factor, and report them before analysis.

**Why it holds here:** "D" is not among A, B and C, so the factor value is NA and no warning appears. Example 3 shows how lowercase b fails the same way.

**Tempting mistake:** Counting with a plain `table()`. NA rows are left out, so the totals shrink and nobody sees why.

**Verify:** `is.na(unknown)` returns TRUE, and `table(..., useNA = "ifany")` shows the NA count.

### Exercise 6

Inspect a categorical design matrix.

Check column names and baseline interpretation before explaining fitted coefficients.

**Approach:** Print `colnames(model.matrix(~group))` and the column sums before describing any coefficient.

**Why it holds here:** The columns are the intercept, groupB and groupC, so A is the baseline. groupC sums to 0 because no row has C.

**Tempting mistake:** Describing the groupB coefficient as the average for B. It is B minus A, and the groupC estimate cannot be computed at all.

**Verify:** `colnames(design)` returns "(Intercept)", "groupB", "groupC", and `colSums(design)` shows 3, 1 and 0.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
