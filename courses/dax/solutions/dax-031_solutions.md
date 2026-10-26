# dax-031: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-031_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: January calendar versus event dates

January 2025, active OrderDate relationship; observed coverage includes the full month.

| CalendarDates | OrderDatesWithSales |
| --- | --- |
| 31 | 3 |

A sales-day average and a calendar-day average use different denominators. Neither should be called a generic daily average without that qualification.

- The complete Date table contains January 1 through 31.
- Sales occur on January 2,3 and 5.
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

### Exercise 2

Change case B to January 2,2025.

CalendarDates is 1, SalesRows is 1 and Revenue is 27.

### Exercise 3

Write a date-table quality checklist.

Check one row per date, no blanks or gaps in the required classic calendar, correct date type, explicit coverage and the intended active fact relationship.

### Exercise 4

Diagnose using MAX(Date[Date]) as the latest observed sales date.

It is a calendar extent, not an observation watermark. Use a declared availability boundary or the appropriate fact-date contract.

### Exercise 5

Explain why filling every future blank with zero can distort a forecast baseline.

It inserts invented zero-demand observations after the availability boundary.

### Exercise 6

Transfer the distinction to working days.

Define working-day membership explicitly and reconcile the denominator, rather than deleting dates with no transactions.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
