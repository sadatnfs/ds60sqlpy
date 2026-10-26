# dax-038: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-038_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: First two positions

Whole clean-model Sales relation ordered by unique SaleID; absolute positions 1 through 2.

| Line | Amount |
| --- | --- |
| S1 | 20 |
| S2 | 4 |

A two-row average here would average order lines. It would not represent average revenue for two calendar days.

- The first two keys are S1 and S 2.
- Both rows belong to order 101 and date 2024-01-02.
- The window contains two lines, not two distinct dates; amounts are 20 and 4.

### Case B: Last two positions

Same explicit relation and ordering; last two absolute positions.

| Line | Amount |
| --- | --- |
| S7 | 20 |
| S8 | 36 |

The result happens to align with two successive sale dates. That coincidence does not make the operator a date-window function.

- Position-1 identifies S8; position-2 identifies S7.
- The inclusive window includes both rows.
- Their amounts total 56, but the relation contract remains line-based.

### Case C: INDEX chooses one absolute position

One unpartitioned relation ordered by the unique SaleID; no outer row required.

| SaleID | NetAmount |
| --- | --- |
| S1 | 20 |

INDEX selects a position in the declared order. Position zero or a position beyond this eight-row relation would return an empty table.

- ALL exposes all eight line identities and amounts.
- The declared unique order starts with S1.
- Absolute position one therefore returns S1 and amount 20.

### Case D: OFFSET identifies a previous row

The outer context identifies S4; the relation contains every SaleID in ascending unique order.

| SaleID |
| --- |
| S3 |

OFFSET needs an unambiguous current-row contract. Adding columns, partitions or ties can change matching requirements; specify MATCHBY where identity differs from sort columns.

- The outer filter supplies exactly one current SaleID: S4.
- The explicit ALL relation permits movement outside that current-row selection.
- Moving one position backward reaches S3; a backward move from S1 would be empty.

## Explained practice answers

### Exercise 1

Identify the first position that INDEX(1,...) would select in this relation.

It selects S1; a different order or partition can change the result.

### Exercise 2

Describe OFFSET(-1,...) from a current row matched to S4.

It would refer to S3 with amount 40, provided the current-row matching contract is explicit and valid.

### Exercise 3

Specify a per-customer chronological ordering.

Partition by CustomerKey and order by OrderDate plus a unique SaleID tie-breaker; define how the current row is matched.

### Exercise 4

Diagnose ordering only by NetAmount for a relative previous-row comparison.

Without a deliberate identity/tie policy, 'previous' is ambiguous for the business question even if an engine can extend the order.

### Exercise 5

Explain a boundary row with no previous member.

Treat the missing comparison explicitly rather than assuming a fabricated zero-valued previous row.

### Exercise 6

Transfer the distinction to the last three measurements of a sensor.

A three-row window is appropriate only if observation count is the intended unit; use a time interval for elapsed-time questions.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
