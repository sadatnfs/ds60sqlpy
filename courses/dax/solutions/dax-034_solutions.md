# dax-034: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-034_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A three-calendar-day denominator

AnchorFebruary 3,2025; included calendar days February 1,2,3; all observed.

| Days | Revenue | RevenuePerCalendarDay |
| --- | --- | --- |
| 3 | 56 | 18.66666667 |

The denominator is independent of whether a sale happened on a given included date. That is what makes it a calendar-day rate.

- February 1 has no order, February 2 contributes 20 and February 3 contributes 36.
- Window revenue is 56 and the Date table supplies three eligible dates.
- The calendar-day ratio is 56/3.

### Case B: Two different averages over the same window

Same three observed calendar dates; contrast exclusion of BLANK with an explicit zero policy.

| SaleDayAverage | ObservedCalendarAverage |
| --- | --- |
| 28 | 18.66666667 |

Neither name should be shortened to average daily revenue without identifying the denominator. A small blank-handling change can alter the business meaning.

- The unfilled values are BLANK,20,36.
- The blank-excluding average is 56/2 =28.
- The zero-filled observed-calendar values 0,20,36 average 56/3.

## Explained practice answers

### Exercise 1

Predict the two-day window ending February 3.

Revenue is 56 and both dates have sales, so both daily-average definitions give 28.

### Exercise 2

Move the three-day anchor to January 4,2025.

Revenue is 47; the calendar-day average is 47/3, while the sale-day average is 47/2.

### Exercise 3

Write a complete rolling-window contract.

For this case: OrderDate, three calendar days ending February 3 inclusive, complete available data, USD per calendar day.

### Exercise 4

Diagnose averaging only returned visual rows when zero-sale dates were suppressed.

Use an explicit calendar set rather than assuming visible event dates represent every eligible day.

### Exercise 5

Explain why a window ending after February 28 needs another check.

Later blanks can be unavailable outcomes; do not coalesce them to observed zero without a coverage policy.

### Exercise 6

Transfer the denominator to an availability percentage.

A missing telemetry interval may be unknown rather than available or unavailable; define its treatment before aggregating.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
