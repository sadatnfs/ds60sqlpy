# dax-050: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-050_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Possible customer/product pairs

No filters; dimension population 4 products by 4 customers; observed pair grain from Sales.

| CandidatePairs | ObservedPairs |
| --- | --- |
| 16 | 6 |

The ten unobserved pairs may matter for a coverage report even though they contribute no current revenue. Their inclusion is a question of semantics.

- The full dimension product is 4 times 4 = 16 pairs.
- Observed pairs are (1, 10), (2, 10), (3, 20), (2, 30), (1, 20), (3, 30).
- Repeated purchases of the same pair do not add a new pair, leaving six observed groups.

### Case B: Adding a complete calendar dimension

Whole two-year Date dimension has 731 days; compare possible versus observed product/customer/date cells.

| CandidateCells | ObservedCells |
| --- | --- |
| 11696 | 8 |

These are logical table sizes. Engine optimizations may avoid constructing the full product, and a source-only exercise cannot establish the physical materialization or elapsed time.

- The possible-cell count is 4 * 4 * 731 = 11696.
- Each of the eight sales lines has a distinct product/customer/order-date combination in this fixture.
- The observed grouping therefore has eight cells.

## Explained practice answers

### Exercise 1

Predict candidate pairs after adding one unsold product.

The full candidate grid becomes 5 * 4 = 20; observed pairs can remain six.

**Why it fits this model:** The candidate grid multiplies the dimension sizes. With 5 products and 4 customers it has 20 cells, but no new sale means no new observed pair.

**Tempting mistake:** Expecting ObservedPairs to rise to 7 with the new product. SUMMARIZE over Sales only sees combinations that sold.

**How to confirm:** CandidatePairs returns 20 and ObservedPairs stays 6.

### Exercise 2

Restrict the calendar to January 2025.

The candidate grid becomes 4 * 4 * 31 = 496; the observed fact combinations in that month must be counted separately.

**Why it fits this model:** Filtering the calendar to January 2025 leaves 31 dates in VALUES('Date'[Date]), so the grid is 4 x 4 x 31. Observed cells come from S4, S5 and S6.

**Tempting mistake:** Filtering only Sales to January and expecting the grid to shrink. CROSSJOIN of VALUES still reads all 731 dates unless the Date table is filtered.

**How to confirm:** Under Year 2025 and MonthNumber 1, CandidateCells is 496 and ObservedCells is 3.

### Exercise 3

Choose a population for a complete customer/product coverage matrix.

Use a deliberate full scaffold with explicit missing/zero semantics if coverage requires it; an observed-only grouping would omit requested cells.

**Why it fits this model:** A coverage matrix needs every requested cell: 4 products by 4 customers, 16 cells, of which 6 have sales. Bag's row and Di's column are empty.

**Tempting mistake:** Using SUMMARIZECOLUMNS(Product[ProductName], Customer[CustomerName], "Revenue", [NetRevenue]) drops cells with blank revenue and returns 6 rows.

**How to confirm:** ADDCOLUMNS over CROSSJOIN(VALUES(Product[ProductName]), VALUES(Customer[CustomerName])) with a missing marker returns 16 rows, 10 of them without sales.

### Exercise 4

Diagnose claiming a 11696-row physical scan from this result alone.

A real engine can prune or combine work. Obtain qualified plan/timing evidence before making a physical-performance claim.

**Why it fits this model:** 11696 is 4 x 4 x 731, the size of a logical expression. The engine may never build that table.

**Tempting mistake:** Reporting that the query scanned 11696 rows. No query plan or server timing was captured, so that is a guess presented as a measurement.

**How to confirm:** Describe 11696 as the logical size of the CROSSJOIN, and back any claim about physical work with a captured plan.

### Exercise 5

Explain whether observed combinations always preserve zero-activity denominators.

No. Denominators for eligibility or coverage may require dimension members that never produced facts.

**Why it fits this model:** Eligibility comes from the dimension. Di (customer 40) has no sales, so she appears in Customer but not in any Sales grouping.

**Tempting mistake:** Taking the denominator from SUMMARIZE(Sales, Sales[CustomerKey]) gives 3 active out of 3 customers, a 100 percent rate.

**How to confirm:** Over the Customer dimension, 3 of 4 customers have sales, a rate of 0.75.

### Exercise 6

Transfer the analysis to a product-by-store-by-day model.

Estimate potential combinations, identify which are meaningful and preserve the required zero/missing populations while measuring actual implementation cost separately.

**Why it fits this model:** A product-by-store-by-day model multiplies the same way. 1,000 products, 50 stores and 365 days give 18,250,000 candidate cells.

**Tempting mistake:** Building that full scaffold in an iterator when only store-days with sales matter, or using only observed cells when zero-sale days count.

**How to confirm:** Estimate the grid size first, decide which empty cells the question needs, and measure the cost of the chosen scaffold.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
