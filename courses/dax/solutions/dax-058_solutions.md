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
- Foreign amounts convert to 100 +110 +60 =270 USD under their separate policy.

### Case B: Compare an aligned two-month core population

FullJanuary/February 2025, Paper/Home core sales, refunds attributed to original sale dates; Budget covers exactly that month/category scope.

| CoreBeforeRefund | Refunds | AdjustedCore | Budget | Variance |
| --- | --- | --- | --- | --- |
| 123 | 9 | 114 | 165 | -51 |

A return-date report could differ, but this fixture does not contain ReturnDate. The correct conclusion is to state the limitation, not invent another temporal attribution.

- Core 2025 sales in these months total 123.
- Only the refund linked to S 4 belongs to that sale-date population, subtracting 9.
- The four compatible budget rows total 165;114 -165 =-51.

## Explained practice answers

### Exercise 1

Reconcile adjusted core revenue by year.

2024 contributes 64 -4 =60;2025 contributes 123 -9 =114; together they total 174.

### Exercise 2

Request a report by actual refund-event month.

It cannot be derived from this fixture. Add a properly grained return-event date and explicit date role rather than reusing OrderDate without disclosure.

### Exercise 3

Write the capstone's metric and model specification.

Document core sales, linked refunds, separate foreign transactions/rates, monthly-category budget, observation coverage, unknown-key policy and context-result regression cases.

### Exercise 4

Diagnose subtracting the line Discount again from NetAmount.

It would double-count discounts and understate core revenue. Reconcile 195 gross -8 discount =187 net before applying refunds.

### Exercise 5

Explain why 174 is not automatically accounting profit.

Costs, return-related inventory/COGS changes, tax and other expenses need explicit data and accounting policy.

### Exercise 6

Design an external acceptance plan for the capstone.

Validate model loading, exact measures/context matrix, missing keys/rates, role restrictions, refresh behavior and qualified performance before any deployment claim.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
