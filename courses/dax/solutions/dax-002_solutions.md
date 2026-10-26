# dax-002: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-002_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Whole model counts

All Sales rows; one row per SaleID.

| Lines | Orders | Revenue |
| --- | --- | --- |
| 8 | 7 | 187 |

Deduplicating entire orders before summing their lines would lose a product, while counting every line as an order overstates order count. The aggregation must match the question rather than flatten every metric to one grain.

- S1 and S2 share OrderID 101.
- Seven distinct order identifiers remain after counting 101 once.
- Revenue still includes both legitimate lines of that order.

### Case B: One multi-line order

OrderID 101 only; both matching fact rows retained.

| Lines | Orders | Revenue |
| --- | --- | --- |
| 2 | 1 | 24 |

This small order is a counterexample to the claim that line count equals order count. Keep it as a fixture when a later model refactor changes joins or grouping.

- S1 contributes Notebook quantity 2 and amount 20.
- S2 contributes Pen quantity 1 and amount 4.
- The order has two lines, one identity and revenue 24.

## Explained practice answers

### Exercise 1

Predict distinct customers with sales.

The keys are 10, 20 and 30: three customers with sales, although the Customer table has four rows.

### Exercise 2

Explain the result if S2 is duplicated with the same SaleID.

The row count and revenue rise incorrectly; the unique SaleID contract fails. DISTINCTCOUNT(OrderID) alone would conceal the duplicate.

### Exercise 3

Write the average revenue per order measure.

DIVIDE ( [NetRevenue], [OrderCount] ) is 187 / 7 for the whole model and 24 for order 101.

### Exercise 4

Diagnose summing per-product order counts.

The per-product counts are 3, 2 and 3, summing to 8, while overall distinct orders are 7.

### Exercise 5

State a policy for a missing order identifier.

Decide whether to reject the row, show an unknown-order bucket or use DISTINCTCOUNTNOBLANK with an explicit exclusion. Do not call a blank identifier a known order.

### Exercise 6

Transfer the grain question to a hospital visit table with several charge lines.

Count distinct visit IDs for visits, sum charge amounts for billed charges and preserve a separate unique line key.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
