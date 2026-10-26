# r-004: reference reasoning

Use the [complete reference](r-004_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The mask explicitly excludes missing amounts and separately tests the threshold. Unknown values are counted, not interpreted as measured failures.

The first condition prevents an invalid extraction from an empty vector. The truth-table checks explain when uncertainty does and does not affect the combined answer.

## Explained practice

### Exercise 1

Predict TRUE & NA and FALSE & NA.

The first is NA; the second is FALSE.

**Expected evidence:** The first is NA; the second is FALSE.

### Exercise 2

Change the threshold from ten to fifteen.

Only the amount twenty remains.

**Expected evidence:** Only the amount twenty remains.

### Exercise 3

Construct a mask for known amounts from ten through twenty inclusive.

Use !is.na(x) & x >= 10 & x <= 20.

**Expected evidence:** Use !is.na(x) & x >= 10 & x <= 20.

### Exercise 4

Diagnose x == NA.

Use is.na(x) to test missingness.

**Expected evidence:** Use is.na(x) to test missingness.

### Exercise 5

Guard an empty vector before extracting its first element.

length(x) > 0 && x[[1]] > 0 safely returns FALSE for an empty vector.

**Expected evidence:** length(x) > 0 && x[[1]] > 0 safely returns FALSE for an empty vector.

### Exercise 6

Separate an all-known claim from all(..., na.rm=TRUE).

Report missingness and state that the reduced claim concerns observed predicates only.

**Expected evidence:** Report missingness and state that the reduced claim concerns observed predicates only.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
