# dax-034: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-034_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A three-calendar-day denominator

Anchor February 3, 2025; included calendar days February 1, 2 and 3; all observed.

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

- The unfilled values are BLANK, 20, 36.
- The blank-excluding average is 56/2 = 28.
- The zero-filled observed-calendar values 0, 20, 36 average 56/3.

## Explained practice answers

### Exercise 1

Predict the two-day window ending February 3.

Revenue is 56 and both dates have sales, so both daily-average definitions give 28.

**Why it fits this model:** DATESINPERIOD with -2 days ending February 3 gives February 2 and 3. Both have sales, S7 20 and S8 36, so both averages are 56 / 2 = 28.

**Tempting mistake:** Concluding from this window that the two averages are equivalent. They agree only because every date in it had sales; case B's three days split them into 28 and about 18.67.

**How to confirm:** Days 2, Revenue 56, and both averages 28.

### Exercise 2

Move the three-day anchor to January 4, 2025.

Revenue is 47; the calendar-day average is 47/3, while the sale-day average is 47/2.

**Why it fits this model:** Ending at January 4 gives January 2 to 4: S4 27 on the 2nd and S5 20 on the 3rd, none on the 4th. The calendar average is 47 / 3, about 15.67, and the sale-day average 47 / 2 = 23.5.

**Tempting mistake:** Anchoring with a month filter makes MAX('Date'[Date]) return January 31, so the window becomes January 29 to 31 and the revenue BLANK.

**How to confirm:** Under 'Date'[Date] = DATE(2025, 1, 4), expect Days 3, Revenue 47 and averages of about 15.67 and 23.5.

### Exercise 3

Write a complete rolling-window contract.

For this case: OrderDate, three calendar days ending February 3 inclusive, complete available data, USD per calendar day.

**Why it fits this model:** The contract names the role, the length, the inclusive end, coverage and units. With OrderDate, February 1 to 3 holds 56 USD over 3 days, about 18.67 per calendar day.

**Tempting mistake:** Leaving the role unstated invites a ShipDate version: S6 ships February 1 and S7 February 3, so it gives 40 USD and about 13.33 per day.

**How to confirm:** The order-role window returns 3 days, 56 and about 18.67, matching case A.

### Exercise 4

Diagnose averaging only returned visual rows when zero-sale dates were suppressed.

Use an explicit calendar set rather than assuming visible event dates represent every eligible day.

**Why it fits this model:** The calendar set includes February 1, which is observed with no sales. AVERAGEX over the window with COALESCE keeps that day as 0.

**Tempting mistake:** Averaging the visible rows of a visual that hides empty dates uses only February 2 and 3 and reports 28 per day instead of about 18.67.

**How to confirm:** Over the window, AVERAGEX of COALESCE([NetRevenue], 0) returns about 18.67, while the visible-row average is 28.

### Exercise 5

Explain why a window ending after February 28 needs another check.

Later blanks can be unavailable outcomes; do not coalesce them to observed zero without a coverage policy.

**Why it fits this model:** Observation ends on 2025-02-28. A window ending March 2 holds one observed zero day (February 28) and two unobserved days.

**Tempting mistake:** Coalescing every blank to 0 reports 0 / 3 = 0 per day, as if March 1 and 2 were observed with no sales.

**How to confirm:** Flag March days as unavailable. The window should show one observed day with 0 USD and two unknown days, not a complete average.

### Exercise 6

Transfer the denominator to an availability percentage.

A missing telemetry interval may be unknown rather than available or unavailable; define its treatment before aggregating.

**Why it fits this model:** Availability needs three states: up, down and unknown. Of 24 hourly intervals with 20 up, 2 down and 2 missing, the known-only rate is 20 / 22, about 90.9 percent.

**Tempting mistake:** Treating the 2 missing intervals as down gives 20 / 24, about 83.3 percent; treating them as up gives 22 / 24, about 91.7 percent. Either way the unknown is hidden.

**How to confirm:** Report 20 / 22 with "2 of 24 intervals unknown" beside it, just as the window above separates observed zero days from blanks.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
