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

- January 31 has 10 +20 +5 =35 units.
- February 28 has 8 +15 +7 =30 units.
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

It is 8 +7 =15, coincidentally equal to the earlier carried subset for different reasons.

### Exercise 2

Remove Mug's February snapshot conceptually.

A shared February 28 date can omit Mug, while per-product carry-forward would use January 31's5. The policies must be named separately.

### Exercise 3

Write a staleness acceptance rule for carried balances.

For example, retain a balance only if its age is at most a declared number of days; otherwise return BLANK and a missing/stale indicator.

### Exercise 4

Diagnose dividing 65 by six rows and calling it average inventory over two months.

The result mixes product and temporal weighting. Define whether the desired average is across products, observation dates or time intervals.

### Exercise 5

Explain a product with no snapshot before the cutoff.

Return an explicit unavailable result; do not invent a zero or use a later snapshot that leaks future information.

### Exercise 6

Transfer semi-additivity to account balances.

Sum compatible accounts at a date, but use closing/average-balance rules over time rather than summing repeated states.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
