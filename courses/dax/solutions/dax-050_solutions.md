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

- The full dimension product is 4 times 4 =16 pairs.
- Observed pairs are(1,10),(2,10),(3,20),(2,30),(1,20),(3,30).
- Repeated purchases of the same pair do not add a new pair, leaving six observed groups.

### Case B: Adding a complete calendar dimension

Whole two-year Date dimension has 731 days; compare possible versus observed product/customer/date cells.

| CandidateCells | ObservedCells |
| --- | --- |
| 11696 | 8 |

These are logical table sizes. Engine optimizations may avoid constructing the full product, and a source-only exercise cannot establish the physical materialization or elapsed time.

- The possible-cell count is 4 *4 *731 =11696.
- Each of the eight sales lines has a distinct product/customer/order-date combination in this fixture.
- The observed grouping therefore has eight cells.

## Explained practice answers

### Exercise 1

Predict candidate pairs after adding one unsold product.

The full candidate grid becomes 5 *4 =20; observed pairs can remain six.

### Exercise 2

Restrict the calendar to January 2025.

The candidate grid becomes 4 *4 *31 =496; the observed fact combinations in that month must be counted separately.

### Exercise 3

Choose a population for a complete customer/product coverage matrix.

Use a deliberate full scaffold with explicit missing/zero semantics if coverage requires it; an observed-only grouping would omit requested cells.

### Exercise 4

Diagnose claiming a 11696-row physical scan from this result alone.

A real engine can prune or combine work. Obtain qualified plan/timing evidence before making a physical-performance claim.

### Exercise 5

Explain whether observed combinations always preserve zero-activity denominators.

No. Denominators for eligibility or coverage may require dimension members that never produced facts.

### Exercise 6

Transfer the analysis to a product-by-store-by-day model.

Estimate potential combinations, identify which are meaningful and preserve the required zero/missing populations while measuring actual implementation cost separately.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
