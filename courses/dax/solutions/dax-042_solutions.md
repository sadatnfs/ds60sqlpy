# dax-042: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-042_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Convert each transaction before adding

Analytics model; three ForeignSales rows; each date/currency rate key exists exactly once.

| ConvertedUSD |
| --- |
| 270 |

The raw local sum 250 mixes USD and EUR and is not itself a legitimate currency total.

- F1 is 100 USD at rate 1, contributing 100 USD.
- F2 is 100 EUR at 1.1, contributing 110 USD; F3 is 50 EUR at 1.2, contributing 60 USD.
- The compatible converted amounts sum to 270 USD.

### Case B: A latest-rate shortcut changes the policy

EUR-only transactions; contrast transaction-date rates with one selected maximum rate in this tiny increasing-rate fixture.

| LocalEUR | CorrectUSD | NaiveLatestRateUSD |
| --- | --- | --- |
| 150 | 170 | 180 |

MAX rate happens to equal the latest rate in this fixture. A real latest-date policy must select by date, not assume rates increase monotonically.

- The local EUR amounts sum to 150.
- Transaction-date conversion gives 110 +60 =170 USD.
- Multiplying 150 by 1.2 gives 180 USD, ten more than the stated policy.

## Explained practice answers

### Exercise 1

Predict the converted amount for F 3 alone.

50 times 1.2 gives 60 USD.

### Exercise 2

Change the FebruaryEUR rate to 1.0.

Correct EUR conversion becomes 110 +50 =160 USD. A MAX-rate shortcut would use 1.1 and still be wrong.

### Exercise 3

Write a rate-coverage quality rule.

Reject or flag missing and duplicate date/currency matches before conversion; publish no apparently complete total while transactions are unconverted.

### Exercise 4

Diagnose substituting zero when a rate is missing.

It understates the total and hides missing data. Keep an unavailable result and an explicit count of affected transactions.

### Exercise 5

Explain whether dividing by the rate would be correct.

For EUR to USD multiply by USD/EUR; dividing implements a different direction. Reciprocal conventions must be labeled.

### Exercise 6

Transfer the grain rule to tax rates or indexed prices.

Match the complete rate key and effective interval before aggregation, and test missing or overlapping validity periods.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
