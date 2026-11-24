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

- S2 and S6 have quantity 1 and contribute 4 + 20 = 24.
- Removing those lines from 187 leaves 163.
- The three forms agree in this incoming context.

### Case B: The same-column selection exposes a difference

Incoming Sales.Quantity=1; compare filtering current rows with replacing or intersecting that column selection.

| TableFilter | ColumnFilter | IntersectingColumn |
| --- | --- | --- |
| BLANK | 163 | BLANK |

A rewrite that changes BLANK to 163 is not an optimization of the same calculation. It is a change in the question.

- The incoming visible fact rows are S2 and S6, both quantity 1.
- FILTER over those rows finds no quantity>=2 line, while the plain Boolean predicate replaces the original selection.
- KEEPFILTERS intersects incompatible quantity conditions and also yields BLANK.

## Explained practice answers

### Exercise 1

Predict the three results under an incoming Quantity>=2 selection.

All three return 163 in this fixture, another agreement case that does not replace the counterexample.

**Why it fits this model:** Every row under an incoming Quantity >= 2 filter already meets the predicate. Replacing, intersecting or filtering the visible rows keeps the same 6 lines.

**Tempting mistake:** Treating this second agreement as proof that the rewrites are equivalent. Case B's Quantity = 1 input still separates them.

**How to confirm:** Under Sales[Quantity] >= 2, all three columns return 163.

### Exercise 2

Change the predicate to Quantity>=3.

Without other filters the retained revenue is 27 + 20 = 47.

**Why it fits this model:** Quantity >= 3 keeps S4 (3 units, 27) and S5 (4 units, 20). Without other filters, all three forms keep the same two lines.

**Tempting mistake:** Expecting the case B pattern to change with the new threshold. Under Quantity = 1, the table and KEEPFILTERS forms still return BLANK and only the column filter returns 47.

**How to confirm:** Unfiltered, each form returns 47; under Quantity = 1 the results are BLANK, 47 and BLANK.

### Exercise 3

Write a minimum semantic regression grid.

Check unfiltered, same-column disjoint/overlapping filters, unrelated dimensions, blanks, totals and missing members before comparing timings.

**Why it fits this model:** The grid needs inputs that agree, overlap and conflict. An overlapping Quantity IN {1, 2} filter and an unrelated Blue filter separate cases A and B.

**Tempting mistake:** Testing only the unfiltered case, where all three return 163 and no rewrite can be wrong.

**How to confirm:** Under Quantity IN {1, 2}: TableFilter 116, ColumnFilter 163, KEEPFILTERS 116. Under Blue: all three 143.

### Exercise 4

Diagnose choosing a rewrite because it returns a larger nonblank number.

Validate the metric definition and incoming context first; retain the counterexample as a regression.

**Why it fits this model:** Under Quantity = 1, the column filter replaces the selection and returns 163, while the others return BLANK. A bigger number is not a better one.

**Tempting mistake:** Choosing the column filter because it fills cells the original left blank. It changes the metric for any visual filtered on Quantity.

**How to confirm:** Decide whether the business rule should respect the incoming Quantity selection; if so, keep case B's BLANK as the expected regression value.

### Exercise 5

Explain why KEEP FILTERS is not an automatic proof for arbitrary table filters.

Prove the intended equivalence for the actual expression/model; do not generalize this one-column example beyond its assumptions.

**Why it fits this model:** The KEEPFILTERS column form matches the FILTER(Sales, ...) form here because only one column is involved and FILTER iterates the visible rows.

**Tempting mistake:** Generalizing to a table filter built on ALL(Sales). That table carries every Sales column, and through the expanded table its reach extends to Product, Customer and Date, so its interaction with incoming dimension filters is different and must be tested.

**How to confirm:** Under Product[Color] = "Red", KEEPFILTERS(Sales[Quantity] >= 2) returns 20 (S5 only). Run any whole-table form under the same Red filter and compare before calling it equivalent.

### Exercise 6

Transfer the review to a SQL query optimization.

A faster query that drops duplicate events or changes missing-value policy is not a semantics-preserving optimization.

**Why it fits this model:** A SQL rewrite needs the same parity checks: duplicate rows, NULL handling and boundaries, before timings matter.

**Tempting mistake:** Summing over SELECT DISTINCT NetAmount to cut rows. S1, S5, S6 and S7 all have 20, so the total falls from 187 to 127.

**How to confirm:** Compare row counts and totals between original and rewritten queries (8 lines and 187) before reading any timing.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
