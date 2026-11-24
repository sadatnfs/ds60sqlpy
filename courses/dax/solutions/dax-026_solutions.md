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

- VALUES supplies keys 1, 2, 3, 4.
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
- That all-blank group is omitted; keys 1, 2, 3 remain.

## Explained practice answers

### Exercise 1

Predict the summary if Revenue uses COALESCE([NetRevenue],0).

Key 4 appears with zero, creating four result rows.

**Why it fits this model:** SUMMARIZECOLUMNS drops a group only when every expression is blank. COALESCE makes Bag's value 0, a nonblank result, so key 4 returns with 0 and the table has four rows.

**Tempting mistake:** Treating COALESCE as a display tweak hides that it changes row presence. An AVERAGEX over the new rows drops from 187 / 3, about 62.33, to 187 / 4 = 46.75.

**How to confirm:** The summary returns keys 1 to 4 with revenues 67, 24, 96 and 0.

### Exercise 2

Project only product names from the first result.

The row count remains four if the input table is unchanged; naming only a column does not imply DISTINCT.

**Why it fits this model:** SELECTCOLUMNS projects every input row and never groups. With the four-row first result, projecting product names gives Notebook, Pen, Mug and Bag.

**Tempting mistake:** Assuming a projection deduplicates is the trap. Projecting Category instead returns Paper, Paper, Home and Travel, four rows, not three.

**How to confirm:** COUNTROWS of the projection is 4, and DISTINCT over the Category projection is 3.

### Exercise 3

Write an intermediate-table ledger for a revenue-threshold calculation.

Record keys 1..4, revenues 67/24/96/BLANK, then the qualifying key set for the threshold before applying it as a filter.

**Why it fits this model:** Record each stage. Candidates are keys 1 to 4; extended revenues are 67, 24, 96 and BLANK; a rule of revenue above 50 keeps keys 1 and 3; applying them as a filter gives 163.

**Tempting mistake:** Testing the threshold on Sales lines with `FILTER ( Sales, Sales[NetAmount] > 50 )` keeps nothing, since the largest line is S3 at 40, so the result is BLANK instead of 163.

**How to confirm:** `CALCULATE ( [NetRevenue], FILTER ( VALUES ( Product[ProductKey] ), [NetRevenue] > 50 ) )` returns 163.

### Exercise 4

Diagnose treating a virtual RevenueForKey column as a persisted model attribute.

It does not become a reusable Product column outside the table expression; define an appropriate model object or reconstruct it.

**Why it fits this model:** RevenueForKey is a column of the ADDCOLUMNS result and exists only inside that query. The outer SELECTCOLUMNS can read it because it is iterating that table.

**Tempting mistake:** Writing a later measure that refers to Product[RevenueForKey] fails, because the Product table has no such column, and copying the virtual name into a visual does nothing.

**How to confirm:** Case A returns 67, 24, 96 and BLANK. For reuse, define a model measure such as [NetRevenue] and evaluate it per product.

### Exercise 5

Explain why adding a constant 1 to a summary can change row presence.

The all-blank suppression condition no longer holds for that group.

**Why it fits this model:** A constant column is never blank. Adding "One", 1 to the SUMMARIZECOLUMNS call means Bag's group has one nonblank expression, so its row returns with Revenue BLANK.

**Tempting mistake:** Adding a helper constant for convenience and expecting three rows. The table now lists Bag, and any COUNTROWS of the result reads 4.

**How to confirm:** `SUMMARIZECOLUMNS ( Product[ProductKey], "Revenue", [NetRevenue], "One", 1 )` returns four rows, one of them key 4 with a BLANK revenue.

### Exercise 6

Transfer the distinction to a customer coverage report.

Start from the intended customer population and preserve absent outcomes explicitly rather than allowing a nonempty rule to redefine the denominator.

**Why it fits this model:** Coverage needs every eligible customer as the denominator. Starting from all four customers, three have sales (Ada 51, Bo 80, Cy 56), so coverage is 3 / 4 = 0.75.

**Tempting mistake:** Counting the rows of `SUMMARIZECOLUMNS ( Customer[Customer], "Revenue", [NetRevenue] )` drops Di and reports 3 / 3 = 1.0, full coverage that does not exist.

**How to confirm:** ADDCOLUMNS over VALUES(Customer[Customer]) returns four rows with Di BLANK, and the coverage measure returns 0.75.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
