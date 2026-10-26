# r-060: reference reasoning

Use the [complete reference](r-060_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference calculates one eligibility/summary table and uses it consistently across the static and interactive views. It checks raw IDs, layer counts, trace counts and uncertainty coordinates, preventing duplicated summary marks from being mistaken for additional observations.

The two printed figures share a numerical contract while retaining different rendering systems. The source and worker capture can establish actual PNG/Plotly payload production, but final browser usability remains a separate observation. The group difference is explicitly descriptive because the fixture supplies no causal assignment design.

## Explained practice

### Exercise 1

Build the eligibility ledger from the ten raw records.

There are eight observed values and two missing measurements, with four observed values per group.

**Expected evidence:** Counts 10/8/2 and group counts 4/4.

### Exercise 2

Derive means, SEs and t-interval endpoints.

Means are 2.5 and 4.5; squared SEs 5/12 and 17/12; half-widths are qt(0.975,3) times SE.

**Expected evidence:** Independent numerical oracle.

### Exercise 3

Construct a static raw-point and interval display from those tables.

Eight raw marks and two mean intervals correspond to distinct statistical objects.

**Expected evidence:** Correct layer counts and interval coordinates.

### Exercise 4

Construct an interactive figure retaining raw IDs and a separate summary trace.

The raw trace has eight keyed observations; the summary trace has two means and supplied error bars.

**Expected evidence:** Trace counts 8 and 2 with retained identity.

### Exercise 5

Diagnose interpreting the mean difference as a causal effect.

The difference of two is descriptive for this fixture. A causal interpretation requires additional design assumptions and evidence.

**Expected evidence:** No unsupported causal claim.

### Exercise 6

Produce a factual report of what execution and capture established.

Report calculation and layer/trace checks, actual printed/captured figures, and any unperformed readability, hover or accessibility checks.

**Expected evidence:** A complete bounded evidence record.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
