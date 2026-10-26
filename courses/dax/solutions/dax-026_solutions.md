# dax-026: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-026_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Extend every candidate key

All four clean-model Product keys; retain every input row while adding revenue.

| ProductKey | Revenue |
| --- | --- |
| 1 | 67 |
| 2 | 24 |
| 3 | 96 |
| 4 | BLANK |

An extension column is addressed by its name in the virtual table expression. It is not automatically installed as a persistent Product column.

- VALUES supplies keys 1,2,3,4.
- ADDCOLUMNS computes one revenue result per input key.
- Bag's blank measure does not remove key 4 from this projected table.

### Case B: A grouped summary omits an all-blank group

Same clean model; grouped summary with one measure expression.

| ProductKey | Revenue |
| --- | --- |
| 1 | 67 |
| 2 | 24 |
| 3 | 96 |

Adding a nonblank expression or deliberately coalescing revenue can alter which groups appear. Do not assume that all table-producing functions have the same row-retention policy.

- The four candidate keys form groups.
- Key 4 has BLANK for every supplied expression.
- That all-blank group is omitted; keys 1,2,3 remain.

## Explained practice answers

### Exercise 1

Predict the summary if Revenue uses COALESCE([NetRevenue],0).

Key 4 appears with zero, creating four result rows.

### Exercise 2

Project only product names from the first result.

The row count remains four if the input table is unchanged; naming only a column does not imply DISTINCT.

### Exercise 3

Write an intermediate-table ledger for a revenue-threshold calculation.

Record keys 1..4, revenues 67/24/96/BLANK, then the qualifying key set for the threshold before applying it as a filter.

### Exercise 4

Diagnose treating a virtual RevenueForKey column as a persisted model attribute.

It does not become a reusable Product column outside the table expression; define an appropriate model object or reconstruct it.

### Exercise 5

Explain why adding a constant 1 to a summary can change row presence.

The all-blank suppression condition no longer holds for that group.

### Exercise 6

Transfer the distinction to a customer coverage report.

Start from the intended customer population and preserve absent outcomes explicitly rather than allowing a nonempty rule to redefine the denominator.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
