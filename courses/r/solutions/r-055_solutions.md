# r-055: reference reasoning

Use the [complete reference](r-055_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The fitted-line comparison verifies a real change in the statistic's input data, not only a cosmetic zoom. Its expected removal warning should be interpreted as part of that mechanism. Facet metadata and transformed coordinates supply separate checks for scale behavior.

The reference prints only two plots. Correct layer metadata does not guarantee that the delivered visual comparison is clear, so captions, scales and missing-category policies remain part of the graphical review.

## Explained practice

### Exercise 1

Build the coordinate-zoom and scale-limited fitted-line comparison.

The coordinate zoom retains all four observations in the fit, while the scale limit removes the extreme y value before fitting.

**Expected evidence:** Different fitted numerical layers.

### Exercise 2

Choose a zoom that preserves the model-fitting data.

Use coord_cartesian and retain the full-data fit; document any points outside the displayed window.

**Expected evidence:** Model inputs preserved.

### Exercise 3

Compare fixed and free-y facet scale assignments.

Fixed panels share one y-scale assignment; free_y gives one per panel in this fixture.

**Expected evidence:** One versus two scale assignments.

### Exercise 4

Transform positive values 1,10,100 with a log10 x scale.

The built x coordinates are 0,1,2, representing equal ratios as equal spacing.

**Expected evidence:** Expected transformed positions.

### Exercise 5

Diagnose a new category missing from a named palette contract.

Admit the category with an explicit mapping or reject it under the application contract; do not silently change existing identities.

**Expected evidence:** Unmapped category detected.

### Exercise 6

Explain when free scales can mislead a magnitude comparison.

Free scales can make a small and a large range occupy similar panel heights; shared scales or explicit annotation are needed for direct magnitude comparison.

**Expected evidence:** Comparison limit stated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
