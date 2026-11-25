# dax-038: explained reference and practice reasoning

Check that every reference case orders by the unique Sales[SaleID] and returns S1 and S2, S7 and S8, S1, then S3. Read it beside the [reference source](dax-038_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: First two positions

Whole clean-model Sales relation ordered by unique SaleID; absolute positions 1 through 2.

| Line | Amount |
| --- | --- |
| S1 | 20 |
| S2 | 4 |

A two-row average here would average order lines. It would not represent average revenue for two calendar days.

- The first two keys are S1 and S2.
- Both rows belong to order 101 and date 2024-01-02.
- The window contains two lines, not two distinct dates; amounts are 20 and 4.

### Case B: Last two positions

Same explicit relation and ordering; last two absolute positions.

| Line | Amount |
| --- | --- |
| S7 | 20 |
| S8 | 36 |

The result happens to align with two successive sale dates. That coincidence does not make the operator a date-window function.

- Position -1 identifies S8; position -2 identifies S7.
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

**Why it fits this model:** INDEX picks a position from the same ALL(Sales[SaleID], Sales[NetAmount]) relation and SaleID order as case A, so position 1 is S1, amount 20.

**Tempting mistake:** Changing the order to NetAmount ascending without noticing: position 1 then holds S2, amount 4, because the order defines the positions.

**How to confirm:** The case C query returns one row, S1 with 20, matching the first row of case A.

### Exercise 2

Describe OFFSET(-1,...) from a current row matched to S4.

It would refer to S3 with amount 40, provided the current-row matching contract is explicit and valid.

**Why it fits this model:** The outer filter identifies S4, and OFFSET looks one step back in the full ascending SaleID relation. That is S3, amount 40.

**Tempting mistake:** Passing the filtered table as the relation, so the relation holds only S4. There is then no row before it and OFFSET returns an empty table.

**How to confirm:** Case D returns S3; add Sales[NetAmount] to the ALL list and the row shows 40.

### Exercise 3

Specify a per-customer chronological ordering.

Partition by CustomerKey and order by OrderDate plus a unique SaleID tie-breaker; define how the current row is matched.

**Why it fits this model:** Partition by CustomerKey, then order by OrderDate with SaleID as the tie-breaker. Ada's lines are S1 and S2 on 2024-01-02, then S4.

**Tempting mistake:** Ordering by OrderDate without a partition or tie-breaker. S1 and S2 share a date, and S4's previous row becomes Bo's S3 rather than Ada's S2.

**How to confirm:** With PARTITIONBY(Sales[CustomerKey]) and ORDERBY(Sales[OrderDate], ASC, Sales[SaleID], ASC), OFFSET(-1) from S4 returns S2, amount 4.

### Exercise 4

Diagnose ordering only by NetAmount for a relative previous-row comparison.

Without a deliberate identity/tie policy, 'previous' is ambiguous for the business question even if an engine can extend the order.

**Why it fits this model:** NetAmount alone does not identify lines here: S1, S5, S6 and S7 all have 20, so their order relative to one another is unspecified.

**Tempting mistake:** Relying on the engine to extend the order with other columns and reading the result as a business answer. The previous row for S5 could be any of the 20s.

**How to confirm:** Ascending amounts are 4, 20, 20, 20, 20, 27, 36, 40. Adding SaleID as a tie-breaker gives S1, S5, S6, S7 for the 20s.

### Exercise 5

Explain a boundary row with no previous member.

Treat the missing comparison explicitly rather than assuming a fabricated zero-valued previous row.

**Why it fits this model:** Each partition's first row has no previous member. In the per-customer order, Ada's S1, Bo's S3 and Cy's S5 have nothing before them.

**Tempting mistake:** Coalescing the missing previous value to 0 reports S1 as a change of +20 from a sale that never existed.

**How to confirm:** For S1, OFFSET(-1) returns an empty table, and the change measure should return BLANK while S4 returns 27 - 4 = 23.

### Exercise 6

Transfer the distinction to the last three measurements of a sensor.

A three-row window is appropriate only if observation count is the intended unit; use a time interval for elapsed-time questions.

**Why it fits this model:** A window of three rows counts observations, not time. Readings at 09:00, 09:01 and 12:00 are three rows spanning three hours.

**Tempting mistake:** Calling WINDOW(-2, REL, 0, REL) "the last few minutes". Over sparse readings, three rows can cover minutes or days.

**How to confirm:** For elapsed-time questions, filter timestamps to an interval such as the last 15 minutes and count the readings inside it; the three-row window and the interval can disagree.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
