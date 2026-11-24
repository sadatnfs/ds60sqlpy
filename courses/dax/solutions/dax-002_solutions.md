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

**Why it fits this model:** DISTINCTCOUNT(Sales[CustomerKey]) counts keys that actually appear on fact rows. Sales carries keys 10, 20 and 30, so three customers bought something even though the dimension holds four.

**Tempting mistake:** COUNTROWS(Customer) returns 4 because it counts Di (key 40), who has no sales. It answers how many customers exist, not how many purchased.

**How to confirm:** `EVALUATE ROW ( "Buyers", DISTINCTCOUNT ( Sales[CustomerKey] ), "Customers", COUNTROWS ( Customer ) )` should return 3 and 4.

### Exercise 2

Explain the result if S2 is duplicated with the same SaleID.

The row count and revenue rise incorrectly; the unique SaleID contract fails. DISTINCTCOUNT(OrderID) alone would conceal the duplicate.

**Why it fits this model:** SaleID is the row identity for this grain. A second S2 adds one line and its NetAmount of 4, so lines become 9 and revenue 191, while order 101 still counts once.

**Tempting mistake:** Using DISTINCTCOUNT(Sales[OrderID]) as the health check. It still returns 7 after the duplicate, so the test passes while revenue is overstated by 4.

**How to confirm:** Compare COUNTROWS(Sales) with DISTINCTCOUNT(Sales[SaleID]); 9 against 8 exposes the duplicate, and clean data gives 8 and 8.

### Exercise 3

Write the average revenue per order measure.

DIVIDE ( [NetRevenue], [OrderCount] ) is 187 / 7 for the whole model and 24 for order 101.

**Why it fits this model:** Revenue per order is a ratio of two totals computed in the same context: 187 / 7 is about 26.71 for the whole model, and 24 / 1 = 24 for order 101. DIVIDE returns BLANK instead of an error when no order is visible.

**Tempting mistake:** AVERAGE(Sales[NetAmount]) gives 187 / 8 = 23.375, the average line, because it divides by eight sale lines rather than seven orders.

**How to confirm:** AVERAGEX ( VALUES ( Sales[OrderID] ), [NetRevenue] ) also returns about 26.71 overall, a useful cross-check that both forms average at order grain.

### Exercise 4

Diagnose summing per-product order counts.

The per-product counts are 3, 2 and 3, summing to 8, while overall distinct orders are 7.

**Why it fits this model:** Notebook appears in orders 101, 201 and 204, Pen in 101 and 202, and Mug in 102, 203 and 205. Order 101 holds both a Notebook and a Pen line, so it belongs to two product rows.

**Tempting mistake:** Adding the product rows with SUMX ( VALUES ( Product[Product] ), [OrderCount] ) returns 8 and counts order 101 twice.

**How to confirm:** The matrix total row should still read 7, because DISTINCTCOUNT is evaluated again in the total context instead of summing 3 + 2 + 3.

### Exercise 5

State a policy for a missing order identifier.

Decide whether to reject the row, show an unknown-order bucket or use DISTINCTCOUNTNOBLANK with an explicit exclusion. Do not call a blank identifier a known order.

**Why it fits this model:** DISTINCTCOUNT treats BLANK as one more distinct value. A ninth line with an empty OrderID would raise the order count from 7 to 8 even though no new known order exists.

**Tempting mistake:** Assuming DISTINCTCOUNT skips blanks the way COUNT skips empty cells. That inflates the order count by one and quietly lowers revenue per order.

**How to confirm:** Report COUNTBLANK(Sales[OrderID]) beside both DISTINCTCOUNT and DISTINCTCOUNTNOBLANK; with one blank line they should read 1, 8 and 7, making the policy visible.

### Exercise 6

Transfer the grain question to a hospital visit table with several charge lines.

Count distinct visit IDs for visits, sum charge amounts for billed charges and preserve a separate unique line key.

**Why it fits this model:** A visit with several charge lines has the same shape as order 101 with two sale lines. Visits are counted by distinct visit ID, money is summed at charge-line grain, and each line keeps its own key.

**Tempting mistake:** Using COUNTROWS(Charges) as the visit count, which turns a visit with three charges into three visits, just as COUNTROWS(Sales) gives 8 instead of 7 orders.

**How to confirm:** Check that the distinct visit count never exceeds the charge-line count and that COUNTROWS(Charges) equals DISTINCTCOUNT(Charges[LineID]).

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
