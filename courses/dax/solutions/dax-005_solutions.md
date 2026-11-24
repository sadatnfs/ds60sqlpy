# dax-005: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-005_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A scalar wrapped as a table

No filters; one named scalar in a one-row query result.

| RevenueUSD |
| --- |
| 187 |

Output aliases belong to this query. Renaming RevenueUSD does not rename the NetRevenue measure or change its arithmetic.

- SUM produces one scalar in the current context.
- ROW assigns that scalar the output name RevenueUSD.
- EVALUATE returns the one-row table, not a stored model column.

### Case B: A projected two-row result

No filters; smallest two unique SaleID values, then explicit output ordering.

| Line | Amount |
| --- | --- |
| S1 | 20 |
| S2 | 4 |

The result is two rows because the input selection has two rows. It is not a sum and not a measure definition. The amount column retains each line's value.

- SaleID is unique, so the two smallest keys select exactly S1 and S2.
- SELECTCOLUMNS evaluates each projected expression for its input row.
- The outer ORDER BY makes the displayed sequence S1 then S2.

## Explained practice answers

### Exercise 1

Repair EVALUATE SUM(Sales[NetAmount]).

Wrap the scalar: EVALUATE ROW("Revenue",SUM(Sales[NetAmount])).

**Why it fits this model:** EVALUATE accepts a table expression, while SUM returns a scalar. ROW builds a one-row table with a named column, so the corrected query returns Revenue = 187.

**Tempting mistake:** Wrapping the scalar in CALCULATE instead, as in EVALUATE CALCULATE ( SUM ( Sales[NetAmount] ) ). The expression is still a scalar, so the query fails the same way.

**How to confirm:** The repaired result has exactly one row and one column, Revenue, with the value 187.

### Exercise 2

Change the projection to include Quantity.

The first two rows have quantities 2 and 1; keep Amount rather than replacing it silently.

**Why it fits this model:** SELECTCOLUMNS takes name and expression pairs, so adding "Quantity", Sales[Quantity] extends the projection without changing which two rows TOPN selected.

**Tempting mistake:** Replacing the Amount pair with Quantity, or writing "Amount", Sales[Quantity]. The second form keeps a revenue label on a unit column.

**How to confirm:** The result should show three columns: S1 with 20 and 2, then S2 with 4 and 1.

### Exercise 3

Write a query returning three rows in descending SaleID order.

TOPN(3,Sales,Sales[SaleID],DESC) chooses S8, S7, S6; an outer ORDER BY makes that display order explicit.

**Why it fits this model:** TOPN with DESC chooses the set S8, S7 and S6, but TOPN does not promise an output order. The outer ORDER BY [Line] DESC states the display order explicitly.

**Tempting mistake:** Keeping TOPN on ASC and only changing ORDER BY to DESC. That shows S3, S2 and S1 in descending order, which is the wrong set displayed backward.

**How to confirm:** The rows should read S8 with 36, S7 with 20 and S6 with 20, in that order.

### Exercise 4

Diagnose the name RevenueUSD being used as a measure in a later separate query.

Define a measure or reconstruct the query. An alias in one returned table does not install model metadata.

**Why it fits this model:** The name RevenueUSD lives only in that one result table. A later query sees only the model's measures, so it must define its own measure or reuse [NetRevenue].

**Tempting mistake:** Referencing [RevenueUSD] in a second EVALUATE as if it were a measure. The query fails because no model object has that name.

**How to confirm:** Starting the second query with DEFINE MEASURE Sales[RevenueUSD] = [NetRevenue] and evaluating ROW ( "RevenueUSD", [RevenueUSD] ) returns 187.

### Exercise 5

Predict what changes if TOPN orders only by a tied amount.

More than N rows can be returned at a tie; add a unique key if an exact-sized selection is the intended contract.

**Why it fits this model:** TOPN keeps every row tied with the last value it accepts. Ranked by NetAmount, the top values are 40, 36 and 27, and then four lines (S1, S5, S6 and S7) all share 20.

**Tempting mistake:** Expecting TOPN ( 4, Sales, Sales[NetAmount], DESC ) to return four rows. It returns seven because all four tied lines at 20 enter together.

**How to confirm:** COUNTROWS on that TOPN returns 7; adding Sales[SaleID], ASC as a second ordering key returns exactly S3, S8, S4 and S1.

### Exercise 6

Explain how a query differs from a calculated table.

A query returns a requested table now; a calculated table is model content computed during processing and used later.

**Why it fits this model:** A query is evaluated when it is submitted, under the filters it states. A calculated table is computed during model refresh and stored, so its values do not respond to report filters.

**Tempting mistake:** Building a calculated table of category revenue to feed a region slicer. Its stored Paper 91 and Home 96 stay fixed when North is chosen.

**How to confirm:** The query evaluated with Customer[Region] = "North" returns Paper 71 and Home 36, while the stored calculated table still shows 91 and 96.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
