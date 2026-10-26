# r-051: reference reasoning

Use the [complete reference](r-051_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference produces at most two graphics: one in the caller's active device and one in an owned temporary PNG device. It checks the underlying pairs and explicit coordinate range, then separately validates file structure and cleanup.

The row-order example is numerical so the cause of a misleading connected line is inspectable without relying on an image. Actual classroom delivery and readability still require the browser/figure acceptance workflow; a successful Rscript exit does not establish those observations.

## Explained practice

### Exercise 1

Draw the five paired observations with labeled axes.

A scatterplot establishes the coordinate system and identifies the measured quantities.

**Expected evidence:** One labeled base plot.

### Exercise 2

Overlay the rule y=2x without starting another plot.

The overlay shares the established axes and passes through the authored points.

**Expected evidence:** Correct shared-coordinate overlay.

### Exercise 3

Set and inspect exact limits 0:4 and 0:8.

With xaxs/yaxs set to i, par("usr") matches the four declared bounds.

**Expected evidence:** Expected coordinate limits.

### Exercise 4

Diagnose connecting unsorted rows in a time-series line.

lines follows supplied order. Sort by the declared time variable or use an appropriate grouping/order rule before implying a trajectory.

**Expected evidence:** Ordering defect and repair identified.

### Exercise 5

Create, close and validate an owned PNG tempfile.

The file has a valid PNG signature and is removed by scoped cleanup; unrelated devices remain owned by their callers.

**Expected evidence:** Actual file evidence and scoped cleanup.

### Exercise 6

Distinguish numerical, file and browser evidence for the graphic.

Data assertions check values, signature checks file structure, and a browser inspection checks delivery/readability. None automatically substitutes for the others.

**Expected evidence:** Three evidence layers stated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
