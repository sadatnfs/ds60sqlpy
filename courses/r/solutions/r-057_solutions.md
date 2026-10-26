# r-057: reference reasoning

Use the [complete reference](r-057_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference inspects resolved traces rather than only checking an object class. Observed data and a comparison rule have separate names, and the bar example preserves category identity with precomputed heights. A row-order control shows why line connections need an explicit sequence.

Exactly two Plotly figures are printed. The prepared worker can capture their JSON specifications offline; browser delivery, zoom, hover and accessibility remain separate visual/interaction checks.

## Explained practice

### Exercise 1

Construct one marker trace from the three observed pairs.

The trace contains the three source coordinates without an implied connecting trajectory.

**Expected evidence:** Three markers with exact values.

### Exercise 2

Add and name the rule y=2x as a line trace.

The second trace has values 2,4,6 and a distinct explanatory name.

**Expected evidence:** Two identifiable traces.

### Exercise 3

Set axis titles through layout.

The layout identifies the x and y quantities while trace coordinates remain unchanged.

**Expected evidence:** Correct labels and unchanged data.

### Exercise 4

Diagnose an unsorted line trace.

A line follows supplied order; sort or group under a declared trajectory contract before connecting observations.

**Expected evidence:** Ordering repair identified.

### Exercise 5

Build a bar figure from the supplied count table and inspect its values.

Trace coordinates preserve category names and 2,1,3 heights.

**Expected evidence:** Exact bar data.

### Exercise 6

Explain what explicit printing and figure-specification checks establish.

Printing requests capture; data checks validate the specification. Actual browser rendering and interactions need separate observation.

**Expected evidence:** Evidence boundaries retained.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
