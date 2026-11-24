# dax-039: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-039_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Two states are not one closing balance

Analytics model; January and February 2025; all products; complete snapshots on January 31 and February 28.

| SummedSnapshots | ClosingUnits |
| --- | --- |
| 65 | 30 |

The incorrect sum can still be useful as an intermediate check, but it must not be labeled inventory on hand at period end.

- January 31 has 10 + 20 + 5 = 35 units.
- February 28 has 8 + 15 + 7 = 30 units.
- All snapshot rows sum to 65; the closing selected-date balance is 30.

### Case B: An explicitly carried-forward subset

Notebook and Mug only; as-of February 15; carry the last eligible snapshot under an explicit policy.

| CarriedUnits |
| --- |
| 15 |

This is a model-based as-of estimate, not a measured February 15 snapshot. Real systems may require stricter freshness or complete change-event accounting.

- For each selected product, the last snapshot not after February 15 is January 31.
- Notebook has 10 and Mug has 5 at that snapshot.
- The policy-derived carried total is 15, with 15 days of staleness.

## Explained practice answers

### Exercise 1

Predict the closing balance for Notebook and Mug at February 28.

It is 8 + 7 = 15, coincidentally equal to the earlier carried subset for different reasons.

**Why it fits this model:** Inventory is a state. At February 28 the closing balance for Notebook and Mug is that date's snapshot: 8 + 7 = 15.

**Tempting mistake:** Summing both month-end snapshots for the two products gives 10 + 5 + 8 + 7 = 30, which counts each product twice.

**How to confirm:** Under 'Date'[Date] = DATE(2025, 2, 28) and ProductKey IN {1, 3}, SUM(Inventory[Units]) returns 15; case B's 15 comes from the January 31 values 10 + 5.

### Exercise 2

Remove Mug's February snapshot conceptually.

A shared February 28 date can omit Mug, while per-product carry-forward would use January 31's5. The policies must be named separately.

**Why it fits this model:** Without Mug's February row, the two policies differ. A shared last date (February 28) has only Notebook, while per-product carry-forward takes Mug's last known 5 from January 31.

**Tempting mistake:** Using LASTDATE('Date'[Date]) or the latest snapshot across all products and calling it per-product last known. Mug silently drops out.

**How to confirm:** The shared-date policy gives 8; per-product carry-forward gives 8 + 5 = 13. Label which one the measure implements.

### Exercise 3

Write a staleness acceptance rule for carried balances.

For example, retain a balance only if its age is at most a declared number of days; otherwise return BLANK and a missing/stale indicator.

**Why it fits this model:** A carried balance has an age: cutoff minus the snapshot used. At the February 15 cutoff, the January 31 snapshots are 15 days old.

**Tempting mistake:** Carrying the last known value with no age limit, so a snapshot that is months old still shows as current stock.

**How to confirm:** With a 31-day limit, February 15 returns 15; with a 7-day limit it returns BLANK plus a stale flag for both products.

### Exercise 4

Diagnose dividing 65 by six rows and calling it average inventory over two months.

The result mixes product and temporal weighting. Define whether the desired average is across products, observation dates or time intervals.

**Why it fits this model:** The six rows are three products at two dates. Daily totals are 35 on January 31 and 30 on February 28.

**Tempting mistake:** 65 / 6, about 10.83, mixes products and dates: it is the mean per product-snapshot, not the average stock held.

**How to confirm:** AVERAGEX(VALUES(Inventory[SnapshotDate]), CALCULATE(SUM(Inventory[Units]))) returns 32.5 units averaged over the two snapshot dates.

### Exercise 5

Explain a product with no snapshot before the cutoff.

Return an explicit unavailable result; do not invent a zero or use a later snapshot that leaks future information.

**Why it fits this model:** If the cutoff is January 15, 2025, no snapshot is on or before it, so LastKnown is BLANK and no rows match. Bag (ProductKey 4) has no snapshots at all.

**Tempting mistake:** Returning 0 for these products, or using the February 28 snapshot, which reports stock not yet known on January 15.

**How to confirm:** Case B with Cutoff set to DATE(2025, 1, 15) returns BLANK, and the report should flag the products with no available balance.

### Exercise 6

Transfer semi-additivity to account balances.

Sum compatible accounts at a date, but use closing/average-balance rules over time rather than summing repeated states.

**Why it fits this model:** Account balances behave like inventory. If an account shows 100 on January 31 and 120 on February 28, the two-month closing balance is 120.

**Tempting mistake:** Summing the two month-end balances to 220, while the 20 of net transactions across February is the flow that explains the change.

**How to confirm:** The closing balance (120) equals the opening balance (100) plus February transactions (20); balances add across accounts on one date, not across dates.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
