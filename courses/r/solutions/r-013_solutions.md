# r-013: reference reasoning

Use the [complete reference](r-013_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Each returned function retains its own configured factor. No global factor is needed at call time.

The unforced promise looks up rate on first use after the change. The forced closure retained the value two during construction.

## Explained practice

### Exercise 1

Predict make_multiplier(4)(2).

The result is eight.

**Expected evidence:** The result is eight.

### Exercise 2

Create two factories with different factors.

Their outputs remain independently configured.

**Expected evidence:** Their outputs remain independently configured.

### Exercise 3

Capture a threshold at construction time.

Later caller rebinding does not change the captured threshold.

**Expected evidence:** Later caller rebinding does not change the captured threshold.

### Exercise 4

Diagnose a lazy factory changing after caller configuration changes.

Force the argument when fixed configuration is intended.

**Expected evidence:** Force the argument when fixed configuration is intended.

### Exercise 5

Reject an invalid scalar configuration before returning a closure.

No partially configured function is returned for missing or nonfinite input.

**Expected evidence:** No partially configured function is returned for missing or nonfinite input.

### Exercise 6

Explain why hidden global mutation complicates a model pipeline.

Prefer explicit inputs or documented captured state with reset and reproducibility rules.

**Expected evidence:** Prefer explicit inputs or documented captured state with reset and reproducibility rules.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
