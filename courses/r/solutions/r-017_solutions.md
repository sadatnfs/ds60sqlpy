# r-017: reference reasoning

Use the [complete reference](r-017_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The intermediate character conversion retrieves the labels before numeric parsing. It is appropriate only if those labels genuinely represent measurements.

Subsetting retains the declared levels. Zero counts for B and C can be useful evidence rather than categories that should automatically disappear.

## Explained practice

### Exercise 1

Predict as.numeric(factor(c("5","9"))).

The values are 1,2 under the default sorted levels.

**Expected evidence:** The values are 1,2 under the default sorted levels.

### Exercise 2

Choose B as a reference level.

relevel(..., ref="B") puts B first for the relevant contrast convention.

**Expected evidence:** relevel(..., ref="B") puts B first for the relevant contrast convention.

### Exercise 3

Retain an unused C level in a table.

The table includes C with count zero.

**Expected evidence:** The table includes C with count zero.

### Exercise 4

Diagnose treating ordered low/medium/high as equally spaced numbers.

Choose a model encoding justified by the measurement assumptions.

**Expected evidence:** Choose a model encoding justified by the measurement assumptions.

### Exercise 5

Handle a label outside declared levels.

It becomes NA and should be audited rather than silently accepted.

**Expected evidence:** It becomes NA and should be audited rather than silently accepted.

### Exercise 6

Inspect a categorical design matrix.

Check column names and baseline interpretation before explaining fitted coefficients.

**Expected evidence:** Check column names and baseline interpretation before explaining fitted coefficients.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
