# r-059: reference reasoning

Use the [complete reference](r-059_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference strengthens coordinate-set checks by comparing paired x/y keys, so a permutation of y values cannot pass merely because the marginal coordinate sets match. It separately counts marker observations and auxiliary line geometry.

Only the static baseline and one converted widget are printed. Their payload checks establish the stated supported conversion, while the final visual and interaction contract still requires browser inspection. This is not a blanket compatibility claim for every ggplot extension.

## Explained practice

### Exercise 1

Translate the supported scatterplot and inspect marker traces.

The marker payload retains the source coordinates; do not count line or auxiliary traces as additional observations.

**Expected evidence:** Four retained markers.

### Exercise 2

Compare paired coordinates rather than only independent sorted x and y values.

Matching paired coordinate keys detects a permutation that separately matching coordinate sets could miss.

**Expected evidence:** Pair identity preserved.

### Exercise 3

Add a mean reference line and inspect the translated structure.

The result contains extra trace geometry without adding source observations.

**Expected evidence:** Four markers and at least one additional trace.

### Exercise 4

Choose a bounded tooltip field set.

Avoid exposing unrelated implementation fields; test actual tooltip readability in the browser.

**Expected evidence:** An explicit tooltip contract.

### Exercise 5

Diagnose claiming complete visual equivalence from a successful conversion call.

Legend ordering, clipping, facets, themes, hover, keyboard interaction and final size still require visual/interaction checks.

**Expected evidence:** No unsupported parity claim.

### Exercise 6

Choose direct Plotly construction when translation obscures the intended interaction.

A direct trace specification can make IDs, controls and payloads easier to validate when automatic translation does not preserve the required contract clearly.

**Expected evidence:** A justified implementation choice.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
