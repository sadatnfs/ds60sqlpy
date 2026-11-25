# dax-031: explained reference and practice reasoning

Confirm that the reference counts 'Date' rows and DISTINCTCOUNT of Sales[OrderDate] under the same month filter, giving 31 and 3. For 2025-01-04, both Sales rows and revenue should be BLANK while the calendar count is 1. Read it beside the [reference source](dax-031_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: January calendar versus event dates

January 2025, active OrderDate relationship; observed coverage includes the full month.

| CalendarDates | OrderDatesWithSales |
| --- | --- |
| 31 | 3 |

A sales-day average and a calendar-day average use different denominators. Neither should be called a generic daily average without that qualification.

- The complete Date table contains January 1 through 31.
- Sales occur on January 2, 3 and 5.
- The calendar count is 31 while observed event-date count is 3.

### Case B: A date exists without a sale

2025-01-04 is inside declared observation coverage but has no OrderDate fact.

| CalendarDates | SalesRows | Revenue |
| --- | --- | --- |
| 1 | BLANK | BLANK |

If this were beyond observation coverage, the same blank visual appearance would need a different interpretation. Availability metadata prevents that ambiguity.

- The Date selection contains one valid date.
- No Sales row has OrderDate 2025-01-04.
- The fact count and revenue are BLANK; the calendar row is not missing.

## Explained practice answers

### Exercise 1

Predict the number of Date rows in February 2024.

There are 29 unique calendar dates.

**Why it fits this model:** The Date table holds one row per calendar day from 2024-01-01 to 2025-12-31, and 2024 is a leap year, so February 2024 has 29 rows whether or not anything sold.

**Tempting mistake:** Counting sale dates instead: DISTINCTCOUNT(Sales[OrderDate]) under February 2024 is BLANK, because the first sales are in January of each year.

**How to confirm:** Under Year 2024 and MonthNumber 2, COUNTROWS('Date') returns 29.

### Exercise 2

Change case B to January 2, 2025.

CalendarDates is 1, SalesRows is 1 and Revenue is 27.

**Why it fits this model:** The filter names one full date, 2025-01-02, so the calendar contributes one row and the order relationship brings in S4 alone, 27 USD.

**Tempting mistake:** Filtering DayOfMonth = 2 and MonthNumber = 1 without the year also selects 2024-01-02, which adds S1 and S2 and gives 3 rows and 51.

**How to confirm:** CalendarDates 1, SalesRows 1 and Revenue 27.

### Exercise 3

Write a date-table quality checklist.

Check one row per date, no blanks or gaps in the required classic calendar, correct date type, explicit coverage and the intended active fact relationship.

**Why it fits this model:** Each check has a number here: 731 rows for 731 distinct dates, no blanks, MAX minus MIN plus 1 equal to the row count, and 31 rows in January 2025 against 3 sale dates.

**Tempting mistake:** Building the calendar from DISTINCT(Sales[OrderDate]) leaves 7 dates. January 2025 would then have 3 days, and every per-day or window measure would skip the gaps.

**How to confirm:** `INT ( MAX ( 'Date'[Date] ) - MIN ( 'Date'[Date] ) ) + 1` equals COUNTROWS('Date') and DISTINCTCOUNT('Date'[Date]), all 731.

### Exercise 4

Diagnose using MAX(Date[Date]) as the latest observed sales date.

It is a calendar extent, not an observation watermark. Use a declared availability boundary or the appropriate fact-date contract.

**Why it fits this model:** The calendar runs to 2025-12-31 so that future dates exist, but the data is declared observed only through 2025-02-28 and the last order date is 2025-02-03.

**Tempting mistake:** Using MAX('Date'[Date]) as the latest data date returns December 31, 2025, so a freshness label would claim ten months of coverage that do not exist.

**How to confirm:** Unfiltered, MAX('Date'[Date]) is 2025-12-31 and MAX(Sales[OrderDate]) is 2025-02-03; neither replaces the declared watermark, 2025-02-28.

### Exercise 5

Explain why filling every future blank with zero can distort a forecast baseline.

It inserts invented zero-demand observations after the availability boundary.

**Why it fits this model:** Observed days without sales are true zeros. Days after the watermark are unknown. January and February 2025 are 59 observed days with 123 USD, about 2.08 per day.

**Tempting mistake:** Coalescing every future day to 0 adds March as 31 days of zero demand and drops the baseline to 123 / 90, about 1.37, as if sales had collapsed.

**How to confirm:** The observed-window average is about 2.08, and any day after 2025-02-28 should return BLANK rather than 0.

### Exercise 6

Transfer the distinction to working days.

Define working-day membership explicitly and reconcile the denominator, rather than deleting dates with no transactions.

**Why it fits this model:** A working-day denominator needs its own rule. January 2025 has 23 weekdays, and S6 was ordered on Sunday, January 5, so the policy must also say where weekend sales belong.

**Tempting mistake:** Dropping dates without transactions leaves three sale dates and reports 67 / 3, about 22.33 per working day, which counts a Sunday as a working day too.

**How to confirm:** With a weekday flag such as WEEKDAY('Date'[Date], 2) <= 5, January 2025 has 23 working days and 47 USD sold on them (S4 and S5).

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
