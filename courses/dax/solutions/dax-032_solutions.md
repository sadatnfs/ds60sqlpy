# dax-032: explained reference and practice reasoning

Check that the reference applies DATESYTD to 'Date'[Date] inside CALCULATE under each single-date anchor. Your draft should enumerate the admitted lines: S4 and S5 for 47, then S4 through S8 for 123. Read it beside the [reference source](dax-032_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: An early January anchor

Anchor 2025-01-03; classic Gregorian year; active OrderDate; coverage is available.

| CurrentDay | YTD |
| --- | --- |
| 20 | 47 |

An empty January 1 date does not disappear from the calendar set. It simply contributes no fact amount.

- The current date contains S5 and revenue 20.
- The YTD set begins January 1 and ends January 3.
- S4 and S5 contribute 27 + 20 = 47.

### Case B: An anchor in February

Anchor 2025-02-03; same calendar and date role.

| CurrentDay | YTD |
| --- | --- |
| 36 | 123 |

The measure reevaluates over an expanded set, not over the text currently visible in one table cell.

- S8 contributes 36 on the current day.
- The YTD set includes January plus February 1 through 3.
- S4..S8 sum 27 + 20 + 20 + 20 + 36 = 123.

## Explained practice answers

### Exercise 1

Predict YTD at January 2, 2025.

YTD is 27.

**Why it fits this model:** DATESYTD returns January 1 through the latest date in context. On 2025-01-02 that is two dates, and only S4 sold, so YTD is 27.

**Tempting mistake:** Accumulating from the first calendar date, 2024-01-01, counts all of 2024 as well and returns 64 + 27 = 91, a running total, not year to date.

**How to confirm:** Under 'Date'[Date] = DATE(2025, 1, 2), CurrentDay and YTD both return 27.

### Exercise 2

Change the February anchor to February 2.

YTD falls from 123 to 87.

**Why it fits this model:** Moving the anchor back one day drops S8's 36, ordered February 3, so YTD becomes 123 - 36 = 87, and CurrentDay becomes S7's 20.

**Tempting mistake:** Anchoring by month (Year 2025, MonthNumber 2) lets DATESYTD run to February 28 and return 123 for any February day, which hides the change.

**How to confirm:** Under DATE(2025, 2, 2), expect CurrentDay 20 and YTD 87.

### Exercise 3

Write a YTD audit ledger.

For February 3: Gregorian January 1 through February 3, OrderDate role, S4..S8, amount 123.

**Why it fits this model:** The ledger names the calendar, role, date span and lines: Gregorian year, OrderDate, 2025-01-01 through 2025-02-03, S4 27, S5 20, S6 20, S7 20 and S8 36, which add to 123.

**Tempting mistake:** Building the ledger from ShipDate drops S8, shipped February 4, and adds to 87, which no longer matches the measure it is supposed to audit.

**How to confirm:** The listed amounts add to case B's YTD of 123.

### Exercise 4

Diagnose current-day revenue multiplied by elapsed days.

It estimates a different quantity and does not reproduce the observed sum over the actual YTD date set.

**Why it fits this model:** YTD sums observed sales over its date set. February 3 is day 34 of 2025, and actual sales over those 34 days are 123.

**Tempting mistake:** Multiplying CurrentDay 36 by 34 elapsed days gives 1224, about ten times the real value, because it treats one day's sales as a daily rate.

**How to confirm:** 36 x 34 = 1224 against the observed 123; the two answer different questions.

### Exercise 5

Explain a YTD result after the declared data watermark.

Label the result as based on data available through the watermark; do not imply full coverage through a later requested anchor.

**Why it fits this model:** After 2025-02-28 nothing is observed. At an anchor of March 15, 2025 DATESYTD still returns 123, the same as at February 28, because March days have no data.

**Tempting mistake:** Labeling 123 as YTD through March 15 implies a March with zero sales, when March was never observed.

**How to confirm:** YTD at 2025-03-15 equals YTD at 2025-02-28 (123). The label should say data through February 28, 2025.

### Exercise 6

Transfer the pattern to shipped revenue.

Use an explicitly selected shipment relationship and reconcile shipment dates within the same YTD interval.

**Why it fits this model:** Shipped YTD keeps the same January 1 to February 3 interval but activates the ShipDate relationship. That keeps S4, S5, S6 and S7 and drops S8, shipped February 4: 87.

**Tempting mistake:** Leaving the order relationship active returns 123, which counts S8 as shipped one day early.

**How to confirm:** `CALCULATE ( [NetRevenue], DATESYTD ( 'Date'[Date] ), USERELATIONSHIP ( Sales[ShipDate], 'Date'[Date] ) )` returns 87 at February 3 and 123 at February 4.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
