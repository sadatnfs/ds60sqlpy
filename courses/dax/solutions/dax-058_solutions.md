# dax-058: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-058_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Reconcile named monetary populations

Analytics model; complete supplied refund and rate fixtures; core and foreign populations are reported separately.

| CoreNetSales | RefundsAttributedToSales | AdjustedCoreRevenue | SeparateForeignUSD |
| --- | --- | --- | --- |
| 187 | 13 | 174 | 270 |

Showing components makes double subtraction and population mixing visible. The foreign number is not silently added to a core-only budget comparison.

- Core line discounts are already included in NetAmount, whose total is 187.
- Refunds 4 and 9 total 13; adjusted core revenue is 174.
- Foreign amounts convert to 100 + 110 + 60 = 270 USD under their separate policy.

### Case B: Compare an aligned two-month core population

FullJanuary/February 2025, Paper/Home core sales, refunds attributed to original sale dates; Budget covers exactly that month/category scope.

| CoreBeforeRefund | Refunds | AdjustedCore | Budget | Variance |
| --- | --- | --- | --- | --- |
| 123 | 9 | 114 | 165 | -51 |

A return-date report could differ, but this fixture does not contain ReturnDate. The correct conclusion is to state the limitation, not invent another temporal attribution.

- Core 2025 sales in these months total 123.
- Only the refund linked to S4 belongs to that sale-date population, subtracting 9.
- The four compatible budget rows total 165; 114 - 165 = -51.

## Explained practice answers

### Exercise 1

Reconcile adjusted core revenue by year.

2024 contributes 64 - 4 = 60; 2025 contributes 123 - 9 = 114; together they total 174.

**Why it fits this model:** Each refund is attributed through its SaleID, so it lands in the year of its sale: R1 (4) on S2 in 2024 and R2 (9) on S4 in 2025.

**Tempting mistake:** Including the 270 USD of foreign sales in the yearly totals. They are a separate population with their own currency rules.

**How to confirm:** 2024 gives 64 - 4 = 60 and 2025 gives 123 - 9 = 114; they add to 174, matching case A.

### Exercise 2

Request a report by actual refund-event month.

It cannot be derived from this fixture. Add a properly grained return-event date and explicit date role rather than reusing OrderDate without disclosure.

**Why it fits this model:** Returns has ReturnID, SaleID and Refund. It has no date, so a refund-event month cannot be derived.

**Tempting mistake:** Reporting refunds by the original order month without saying so. R2 would appear in January 2025 because S4 was ordered then, whenever the refund happened.

**How to confirm:** Check the Returns columns (ReturnID, SaleID, Refund). Until a ReturnDate is added with its own relationship, label any monthly refund view by sale date.

### Exercise 3

Write the capstone's metric and model specification.

Document core sales, linked refunds, separate foreign transactions/rates, monthly-category budget, observation coverage, unknown-key policy and context-result regression cases.

**Why it fits this model:** The specification states the grain, keys, currency and date role of each input so that core 187, refunds 13, adjusted core 174 and foreign 270 can be rebuilt.

**Tempting mistake:** Publishing one "revenue" figure of 444 (174 + 270) that mixes adjusted core sales with converted foreign sales.

**How to confirm:** The spec lists the regression rows: case A (core 187, refunds 13, adjusted 174, foreign 270) and case B (core 123, refunds 9, adjusted 114, budget 165, variance -51).

### Exercise 4

Diagnose subtracting the line Discount again from NetAmount.

It would double-count discounts and understate core revenue. Reconcile 195 gross -8 discount =187 net before applying refunds.

**Why it fits this model:** NetAmount is already net of line discounts: 195 gross minus 8 discount is 187.

**Tempting mistake:** Subtracting Discount again gives 179, and 166 after refunds, understating adjusted core revenue by 8.

**How to confirm:** SUMX of Quantity x UnitPrice returns 195, SUM of Discount returns 8, and NetRevenue returns 187 before the 13 in refunds.

### Exercise 5

Explain why 174 is not automatically accounting profit.

Costs, return-related inventory/COGS changes, tax and other expenses need explicit data and accounting policy.

**Why it fits this model:** 174 is revenue after refunds. Profit needs costs and a policy for what happens to returned goods.

**Tempting mistake:** Calling 174 profit. Even the simple product cost here is 44 for all lines, and the returned Pen (S2) and Notebook (S4) need a cost treatment.

**How to confirm:** List the missing inputs: cost of goods (44 before returns), returned-unit policy, tax and other expenses.

### Exercise 6

Design an external acceptance plan for the capstone.

Validate model loading, exact measures/context matrix, missing keys/rates, role restrictions, refresh behavior and qualified performance before any deployment claim.

**Why it fits this model:** Each acceptance gate needs its own evidence: model loading, measures in context, data quality, security, refresh and performance.

**Tempting mistake:** Treating the offline reference rows as deployment approval because they match the expected values.

**How to confirm:** In the target engine, run cases A and B and expect the spec's regression rows (case A from core 187 to foreign 270, case B from core 123 to variance -51); then add role, missing-rate and refresh tests.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
