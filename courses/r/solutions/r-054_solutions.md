# r-054: reference reasoning

Use the [complete reference](r-054_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference verifies the statistic applied by each geometry and includes a deliberate invalid count-layer specification. It keeps raw records and precomputed counts separate even when their final heights match.

The line-group and histogram checks inspect transformed layer data, not just object classes. Exactly two plots are printed in the reference. Interpretation of patterns and visual accessibility still require the delivered figure to be reviewed.

## Explained practice

### Exercise 1

Count six raw category records with geom_bar.

The three category heights are 2,1,3.

**Expected evidence:** Correct count heights.

### Exercise 2

Draw an existing count table with geom_col.

The supplied counts are drawn directly rather than counting the three summary rows.

**Expected evidence:** Correct identity heights.

### Exercise 3

Diagnose geom_bar(aes(category,n)) with the default statistic.

The count statistic does not accept both x and y this way; use geom_col for supplied heights or remove y for raw counting.

**Expected evidence:** A specific contract error and repair.

### Exercise 4

Construct two person-specific lines over shared times.

The built line layer contains two groups and six observations.

**Expected evidence:** Two trajectories.

### Exercise 5

Build a histogram with explicit binwidth and boundary and verify total count.

The bin policy is recorded and the bin counts sum to the number of admitted observations.

**Expected evidence:** Histogram count conservation.

### Exercise 6

Explain why changing bins can change a visual conclusion without changing observations.

Different boundaries aggregate observations differently; use a documented policy and sensitivity checks before interpreting a pattern.

**Expected evidence:** Binning sensitivity identified.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
