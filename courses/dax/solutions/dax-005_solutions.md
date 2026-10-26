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

### Exercise 2

Change the projection to include Quantity.

The first two rows have quantities 2 and 1; keep Amount rather than replacing it silently.

### Exercise 3

Write a query returning three rows in descending SaleID order.

TOPN(3,Sales,Sales[SaleID],DESC) chooses S8,S7,S6; an outer ORDER BY makes that display order explicit.

### Exercise 4

Diagnose the name RevenueUSD being used as a measure in a later separate query.

Define a measure or reconstruct the query. An alias in one returned table does not install model metadata.

### Exercise 5

Predict what changes if TOPN orders only by a tied amount.

More than N rows can be returned at a tie; add a unique key if an exact-sized selection is the intended contract.

### Exercise 6

Explain how a query differs from a calculated table.

A query returns a requested table now; a calculated table is model content computed during processing and used later.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
