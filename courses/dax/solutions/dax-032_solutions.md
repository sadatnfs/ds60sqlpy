# dax-032: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-032_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: An early January anchor

Anchor 2025-01-03; classic Gregorian year; active OrderDate; coverage is available.

| CurrentDay | YTD |
| --- | --- |
| 20 | 47 |

An empty January 1 date does not disappear from the calendar set. It simply contributes no fact amount.

- The current date contains S5 and revenue 20.
- The YTD set begins January 1 and ends January 3.
- S4 and S 5 contribute 27 +20 =47.

### Case B: An anchor in February

Anchor 2025-02-03; same calendar and date role.

| CurrentDay | YTD |
| --- | --- |
| 36 | 123 |

The measure reevaluates over an expanded set, not over the text currently visible in one table cell.

- S8 contributes 36 on the current day.
- The YTD set includes January plus February 1 through 3.
- S4..S8 sum 27 +20 +20 +20 +36 =123.

## Explained practice answers

### Exercise 1

Predict YTD at January 2,2025.

YTD is 27.

### Exercise 2

Change the February anchor to February 2.

YTD falls from 123 to 87.

### Exercise 3

Write a YTD audit ledger.

For February 3: Gregorian January 1 through February 3, OrderDate role, S4..S8, amount 123.

### Exercise 4

Diagnose current-day revenue multiplied by elapsed days.

It estimates a different quantity and does not reproduce the observed sum over the actual YTD date set.

### Exercise 5

Explain a YTD result after the declared data watermark.

Label the result as based on data available through the watermark; do not imply full coverage through a later requested anchor.

### Exercise 6

Transfer the pattern to shipped revenue.

Use an explicitly selected shipment relationship and reconcile shipment dates within the same YTD interval.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
