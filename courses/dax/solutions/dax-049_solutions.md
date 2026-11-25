# dax-049: explained reference and practice reasoning

Confirm that the reference counts Sales and Product cardinalities in separate rows, returning 8, 3, 7, 8 and 4, 3, 3. Your draft should explain why ProductKeys is 3 in Sales but Product has 4 rows. Read it beside the [reference source](dax-049_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Fact-column cardinalities

Clean retail fact; no filters; counts describe source cardinality, not physical scan metrics.

| SalesRows | ProductKeys | OrderDates | SaleIDs |
| --- | --- | --- | --- |
| 8 | 3 | 7 | 8 |

A unique identifier has high cardinality here because it preserves necessary line identity. Its cost must be weighed against correctness and lineage requirements.

- There are eight unique sale lines.
- Three product keys repeat across them, and S1/S2 share one order date.
- Distinct counts are 3 products,7 order dates and 8 SaleIDs.

### Case B: Dimension attributes have another grain

Product dimension, including the unsold Bag member.

| ProductRows | Categories | Colors |
| --- | --- | --- |
| 4 | 3 | 3 |

A dimension count is not inferred from fact activity. Removing unsold members to shrink a model can change the intended reporting population.

- Four product rows describe four catalog keys.
- Categories are Paper, Home, Travel and colors are Blue, Red, Green.
- The dimension's domain includes valid attributes absent from current sales.

## Explained practice answers

### Exercise 1

Predict SaleID cardinality after adding one valid new line.

Row count and distinct SaleID count both increase by one; other column cardinalities depend on the new values.

**Why it fits this model:** SaleID is the line key. A valid new line, S9, adds one row and one distinct SaleID, so both counts go from 8 to 9.

**Tempting mistake:** Reusing an existing key such as "S8" for the new line gives 9 rows but still 8 distinct SaleIDs. The key no longer identifies one line.

**How to confirm:** After adding S9, COUNTROWS(Sales) and DISTINCTCOUNT(Sales[SaleID]) both return 9; ProductKeys stays 3 unless S9 sells Bag.

### Exercise 2

Replace a long descriptive fact label with a dimension key conceptually.

The logical model can avoid repeated descriptive values, but actual storage savings require measurement rather than a fixed claimed ratio.

**Why it fits this model:** The fact table already stores ProductKey (3 distinct values over 8 rows) and gets names and categories from the 4-row Product dimension.

**Tempting mistake:** Promising that replacing a label column with a key saves a fixed percentage of storage. Compression depends on the data and the engine, and nothing here was measured.

**How to confirm:** The logical check is that every Sales[ProductKey] matches one Product row and that revenue by ProductName is still Notebook 67, Pen 24 and Mug 96.

### Exercise 3

Write a performance-claim checklist.

Record model/source identity, storage mode, representative filters, result parity, engine/version, hardware, cache state and repeated observed timings.

**Why it fits this model:** A performance claim needs evidence of the same answer, the same workload and a measurement, in that order.

**Tempting mistake:** Timing a rewrite on this 8-row fixture and treating the result as evidence. At this size there is nothing to separate from noise.

**How to confirm:** The checklist starts with result parity (for example NetRevenue 187 and GrossRevenue 195), then records model, storage mode, filters, engine version, hardware, cache state and repeated timings.

### Exercise 4

Diagnose saying SUMX is always slow and SUM is always fast.

Use the simplest correct expression, inspect actual engine work and measure the intended workload; do not infer universal speed from a function name.

**Why it fits this model:** Function names do not decide speed. SUM(Sales[NetAmount]) and SUMX(Sales, Sales[NetAmount]) express the same calculation, 187. GrossRevenue needs the row-level product.

**Tempting mistake:** Replacing SUMX(Sales, Quantity x UnitPrice) with SUM(Quantity) x SUM(UnitPrice) to avoid an iterator gives 17 x 100 = 1700 instead of 195.

**How to confirm:** Keep the correct expression (195), and compare engine timings only between expressions that return the same value.

### Exercise 5

Explain why deleting SaleID can be a correctness regression.

A storage change must preserve the business grain and required diagnostics, not merely reduce a distinct-count statistic.

**Why it fits this model:** SaleID is the only column here that is unique per line. OrderID has 7 distinct values for 8 rows because order 101 has S1 and S2.

**Tempting mistake:** Dropping SaleID because its cardinality equals the row count. Without it, two identical lines could not be told apart or checked for duplicates.

**How to confirm:** DISTINCTCOUNT(Sales[SaleID]) = COUNTROWS(Sales) = 8 is the duplicate check, and it only works while the key exists.

### Exercise 6

Transfer cardinality reasoning to timestamps.

Choose the temporal grain from the measurement requirement, then consider model design and encoding rather than arbitrarily truncating events.

**Why it fits this model:** OrderDate has 7 distinct days. Truncating dates to months leaves 3 values (January 2024, January 2025 and February 2025).

**Tempting mistake:** Truncating to month to save space breaks the daily windows from earlier lessons, such as the three days ending February 3, 2025 (56 USD).

**How to confirm:** Choose the grain from the questions to be answered: day-level windows need dates. Then measure the storage of that choice.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
