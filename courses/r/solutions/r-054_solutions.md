# r-054: reference reasoning

Run the [complete reference](r-054_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference verifies the statistic applied by each geometry and includes a deliberate invalid count-layer specification. It keeps raw records and precomputed counts separate even when their final heights match.

The line-group and histogram checks inspect transformed layer data, not just object classes. Exactly two plots are printed in the reference. Interpretation of patterns and visual accessibility still require the delivered figure to be reviewed.

## Explained practice

### Exercise 1

Count six raw category records with geom_bar.

The three category heights are 2,1,3.

**Expected evidence:** Correct count heights.

**Approach:** Map only category in aes and add geom_bar, letting its default count statistic tally the six raw rows.

**Why it holds here:** d has two A rows, one B row and three C rows, and the factor levels fix the order A, B, C. stat_count therefore produces heights 2, 1 and 3 in that order.

**Tempting mistake:** Reaching for geom_histogram because the plot shows counts. The bin statistic needs a continuous x, so a factor such as category is rejected instead of being counted.

**Verify:** `as.numeric(ggplot2::ggplot_build(p)$data[[1]]$y)` returns 2, 1, 3.

### Exercise 2

Draw an existing count table with geom_col.

The supplied counts are drawn directly rather than counting the three summary rows.

**Expected evidence:** Correct identity heights.

**Approach:** Map category to x and n to y on the counts table and draw geom_col, which uses the identity statistic.

**Why it holds here:** counts already holds one row per category with n = 2, 1 and 3, so the bar heights must be read straight from n. Counting those rows again would add nothing true.

**Tempting mistake:** Expanding the table back into rows with rep(counts$category, counts$n) and calling geom_bar. It happens to match here, but rep truncates a weighted count such as 2.5 to 2, so the bar height changes without warning.

**Verify:** `as.numeric(ggplot2::ggplot_build(identity)$data[[1]]$y)` returns 2, 1, 3.

### Exercise 3

Diagnose geom_bar(aes(category,n)) with the default statistic.

The count statistic does not accept both x and y this way; use geom_col for supplied heights or remove y for raw counting.

**Expected evidence:** A specific contract error and repair.

**Approach:** Read the failure of geom_bar(aes(category, n)) as a contract violation: stat_count accepts one positional aesthetic. Repair it with geom_col, or with geom_bar(stat = "identity").

**Why it holds here:** The counts table has already been summarized, so the y value must be drawn as given. The count statistic was built for raw records and refuses to choose between counting rows and using n.

**Tempting mistake:** Deleting n from aes and keeping geom_bar on the counts table. The plot now builds, but each category appears in one row, so all three bars have height 1 instead of 2, 1 and 3.

**Verify:** `inherits(try(ggplot2::ggplot_build(bad), silent = TRUE), "try-error")` returns TRUE.

### Exercise 4

Construct two person-specific lines over shared times.

The built line layer contains two groups and six observations.

**Expected evidence:** Two trajectories.

**Approach:** Map group = person, and colour = person for the legend, before adding geom_line and geom_point.

**Why it holds here:** Person A rises 1, 2, 3 and person B falls 3, 2, 1 over times 1 to 3. The two paths cross at time 2, where both values are 2, so separate groups are what show that they cross rather than bounce off each other.

**Tempting mistake:** Dropping both group and colour. All six rows become one group, and the single line jumps vertically at each time between the A and B values, which does not represent either person.

**Verify:** `length(unique(ggplot2::ggplot_build(lines)$data[[1]]$group))` returns 2.

### Exercise 5

Build a histogram with explicit binwidth and boundary and verify total count.

The bin policy is recorded and the bin counts sum to the number of admitted observations.

**Expected evidence:** Histogram count conservation.

**Approach:** Set binwidth = 2, boundary = 0 and closed = "left" on geom_histogram for the values 1, 2, 3 and 4, then sum the built count column.

**Why it holds here:** With those settings 1 falls in the bin starting at 0, and 2 and 3 fall in the bin starting at 2. The value 4 sits exactly on a break, which is the case the closed argument and boundary must decide. Whatever happens to it, no value may be lost or counted twice.

**Tempting mistake:** Accepting the default of 30 bins and its message. Four values spread over 30 narrow bins leave most bins empty, so the plot looks like isolated spikes and the bin policy goes unrecorded.

**Verify:** `sum(ggplot2::ggplot_build(histogram)$data[[1]]$count)` returns 4.

### Exercise 6

Explain why changing bins can change a visual conclusion without changing observations.

Different boundaries aggregate observations differently; use a documented policy and sensitivity checks before interpreting a pattern.

**Expected evidence:** Binning sensitivity identified.

**Approach:** Rebuild the same histogram with boundary = 1 and compare the built counts with the boundary 0 version before describing a shape.

**Why it holds here:** With boundary 1 and width 2 the bins hold 1 and 2, then 3 and 4, so the heights are 2 and 2 and the data look flat. Boundary 0 isolates the value 1 in its own bin and makes the heights unequal, although the four observations never changed.

**Tempting mistake:** Trying several boundaries and keeping the one that shows the expected pattern. That treats the layer transformation as evidence about the data.

**Verify:** Rebuilding with boundary = 1 returns counts 2 and 2, and both versions return a count total of 4.

## What the checks establish

The checks confirm that counting raw records and drawing a precomputed table both give bar heights 2, 1 and 3, that `geom_bar()` with a y mapping fails to build, that two person-specific lines get two separate groups, and that the histogram's bins hold four observations in total. They do not show that a chosen bin width supports a particular conclusion.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
