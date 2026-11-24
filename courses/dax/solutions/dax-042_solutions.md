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
- Transaction-date conversion gives 110 + 60 = 170 USD.
- Multiplying 150 by 1.2 gives 180 USD, ten more than the stated policy.

## Explained practice answers

### Exercise 1

Predict the converted amount for F 3 alone.

50 times 1.2 gives 60 USD.

**Why it fits this model:** F3 is 50 EUR on 2025-02-03, and the rate key (2025-02-03, EUR) gives 1.2 USD per EUR. 50 x 1.2 = 60.

**Tempting mistake:** Using the latest January rate, 1.1, because the rate is looked up by currency only. That gives 55.

**How to confirm:** Filtering ForeignSales[ForeignID] = "F3" in case A's measure returns 60.

### Exercise 2

Change the FebruaryEUR rate to 1.0.

Correct EUR conversion becomes 110 + 50 = 160 USD. A MAX-rate shortcut would use 1.1 and still be wrong.

**Why it fits this model:** Converting each row at its own date's rate gives F2 at 100 x 1.1 = 110 and F3 at 50 x 1.0 = 50, so EUR converts to 160.

**Tempting mistake:** The MAX-rate shortcut now takes 1.1 for all 150 EUR, giving 165, which is wrong because it ignores dates.

**How to confirm:** After the change, CorrectUSD reads 160 and NaiveLatestRateUSD reads 165; overall ConvertedUSD becomes 100 + 160 = 260.

### Exercise 3

Write a rate-coverage quality rule.

Reject or flag missing and duplicate date/currency matches before conversion; publish no apparently complete total while transactions are unconverted.

**Why it fits this model:** Every ForeignSales row needs exactly one rate for its (SaleDate, Currency). Here all three rows match one rate each.

**Tempting mistake:** Checking only that the rate table has no blanks. A transaction on a date with no rate is a missing join, not a blank rate value.

**How to confirm:** COUNTROWS(FILTER(ForeignSales, ISBLANK(LOOKUPVALUE(ExchangeRate[USDPerUnit], ...)))) returns 0, and the rate table's (RateDate, Currency) key stays unique.

### Exercise 4

Diagnose substituting zero when a rate is missing.

It understates the total and hides missing data. Keep an unavailable result and an explicit count of affected transactions.

**Why it fits this model:** A missing rate means the USD value is unknown. If the 2025-02-03 EUR rate were absent, F3's 50 EUR would have no conversion.

**Tempting mistake:** Coalescing the missing rate to 0 makes F3 contribute nothing, so the total drops to 210 without warning.

**How to confirm:** Return BLANK for the total, or show 210 with "1 transaction unconverted" beside it, instead of a 210 that looks complete.

### Exercise 5

Explain whether dividing by the rate would be correct.

For EUR to USD multiply by USD/EUR; dividing implements a different direction. Reciprocal conventions must be labeled.

**Why it fits this model:** USDPerUnit is USD per one unit of local currency, so EUR times USD/EUR gives USD.

**Tempting mistake:** Dividing instead gives 100 / 1.1 + 50 / 1.2, about 132.58 USD for the EUR rows, which treats the rate as EUR per USD.

**How to confirm:** Unit check: EUR x (USD / EUR) = USD. Converted EUR should be 170, above 150 local, while each rate is above 1.

### Exercise 6

Transfer the grain rule to tax rates or indexed prices.

Match the complete rate key and effective interval before aggregation, and test missing or overlapping validity periods.

**Why it fits this model:** Tax rates and price indexes also have full keys: jurisdiction, product class and effective date range, like (RateDate, Currency) here.

**Tempting mistake:** Joining by jurisdiction only and taking the latest rate repeats the MAX-rate mistake.

**How to confirm:** For each transaction, count the matching rates: zero means missing and two means overlapping validity, and both should fail before aggregation.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
