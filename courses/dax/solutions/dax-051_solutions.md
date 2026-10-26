# dax-051: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-051_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: An unfiltered agreement case

No existing Quantity filter; all three forms select quantity at least two.

| TableFilter | ColumnFilter | IntersectingColumn |
| --- | --- | --- |
| 163 | 163 | 163 |

Agreement on an unfiltered example does not establish interchangeability under interactive selections.

- S2 and S 6 have quantity 1 and contribute 4 +20 =24.
- Removing those lines from 187 leaves 163.
- The three forms agree in this incoming context.

### Case B: The same-column selection exposes a difference

Incoming Sales.Quantity=1; compare filtering current rows with replacing or intersecting that column selection.

| TableFilter | ColumnFilter | IntersectingColumn |
| --- | --- | --- |
| BLANK | 163 | BLANK |

A rewrite that changes BLANK to 163 is not an optimization of the same calculation. It is a change in the question.

- The incoming visible fact rows are S2 and S 6, both quantity 1.
- FILTER over those rows finds no quantity>=2 line, while the plain Boolean predicate replaces the original selection.
- KEEPFILTERS intersects incompatible quantity conditions and also yields BLANK.

## Explained practice answers

### Exercise 1

Predict the three results under an incoming Quantity>=2 selection.

All three return 163 in this fixture, another agreement case that does not replace the counterexample.

### Exercise 2

Change the predicate to Quantity>=3.

Without other filters the retained revenue is 27 +20 =47.

### Exercise 3

Write a minimum semantic regression grid.

Check unfiltered, same-column disjoint/overlapping filters, unrelated dimensions, blanks, totals and missing members before comparing timings.

### Exercise 4

Diagnose choosing a rewrite because it returns a larger nonblank number.

Validate the metric definition and incoming context first; retain the counterexample as a regression.

### Exercise 5

Explain why KEEP FILTERS is not an automatic proof for arbitrary table filters.

Prove the intended equivalence for the actual expression/model; do not generalize this one-column example beyond its assumptions.

### Exercise 6

Transfer the review to a SQL query optimization.

A faster query that drops duplicate events or changes missing-value policy is not a semantics-preserving optimization.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
