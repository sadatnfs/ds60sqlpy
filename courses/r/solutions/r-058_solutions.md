# r-058: reference reasoning

Use the [complete reference](r-058_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference validates the identity metadata and the exact visibility vectors used by the controls. It also compares the full-data and selected-group means to demonstrate why a view change cannot silently inherit a full-data statistical label.

A static table accompanies the figure. The R and worker-capture checks can establish that these structures were emitted, but they cannot prove accessibility or interaction behavior in a browser. Those observations remain part of the separate classroom delivery qualification.

## Explained practice

### Exercise 1

Attach stable observation IDs independently of x/y coordinates.

Each trace retains the IDs belonging to its points even when the data is grouped.

**Expected evidence:** Correct point-associated IDs.

### Exercise 2

Define a hover template with labels and units.

The template identifies ID, input and measured value rather than presenting anonymous numbers.

**Expected evidence:** Readable field contract.

### Exercise 3

Encode All and Group A visibility buttons for two known traces.

All uses TRUE/TRUE and Group A uses TRUE/FALSE.

**Expected evidence:** Correct button argument vectors.

### Exercise 4

Diagnose a global mean label that remains unchanged when a view hides one group.

A visibility toggle does not automatically recompute the mean. Label it as the full-data mean or implement an explicit selection-dependent calculation.

**Expected evidence:** Denominator/selection semantics clarified.

### Exercise 5

Provide a non-hover-dependent table or summary.

A small printed table preserves the core information without requiring pointer interaction.

**Expected evidence:** Static alternative supplied.

### Exercise 6

Explain what remains unverified after inspecting the figure specification in R.

Clicking, keyboard use, hover readability, resizing and assistive-technology behavior require actual browser checks.

**Expected evidence:** No unsupported interaction-success claim.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
