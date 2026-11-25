# dax-035: explained reference and practice reasoning

Check that the reference reads 'Date'[FiscalYear] rather than deriving the label from Year, and that the to-date case caps dates at February 28, 2025. Your draft should explain why 123 matches the calendar total here only by coincidence. Read it beside the [reference source](dax-035_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Two neighboring fiscal labels

The declared fiscal year starts July 1 and is named by its ending year.

| Day | FiscalYear |
| --- | --- |
| 2024-06-30 | 2024 |
| 2024-07-01 | 2025 |

Using Gregorian Year for both rows would miss the fiscal transition. A label convention belongs in the model specification.

- June 30 belongs to the fiscal year ending in 2024.
- The next day starts the fiscal year ending in 2025.
- A one-day boundary changes the fiscal label without changing the Gregorian year.

### Case B: Available fiscal-year-to-date revenue

FY 2025 under the July-start convention, observed only through 2025-02-28; active OrderDate.

| FiscalYTDRevenue |
| --- |
| 123 |

There happen to be no second-half 2024 sales in this fixture. That does not make Gregorian and fiscal-year measures generally equivalent.

- The fiscal interval starts July 1, 2024.
- The as-of boundary stops at February 28, 2025, not June 30.
- The available matching sales are S4..S8, totaling 123.

## Explained practice answers

### Exercise 1

Predict FiscalYear for January 3, 2025.

The fiscal label is 2025.

**Why it fits this model:** FiscalYear is Year plus 1 from July onward. January 3, 2025 is in the July 2024 to June 2025 year, labeled by its ending year, 2025.

**Tempting mistake:** Reading the label from Year coincides in January but fails from July: July 1, 2024 has Year 2024 and FiscalYear 2025.

**How to confirm:** SELECTCOLUMNS for 2025-01-03 returns FiscalYear 2025; case A shows 2024-07-01 as 2025.

### Exercise 2

Change the naming convention to the starting year.

July 1, 2024 would be labeled FY 2024. Update labels and documentation without pretending the population changed.

**Why it fits this model:** A starting-year label renames the same date set. July 2024 to June 2025 becomes FY 2024, and fiscal-to-date revenue through February 28, 2025 is still 123.

**Tempting mistake:** Changing the label but keeping the filter 'Date'[FiscalYear] = 2025 now selects July 2025 onward, past the watermark, and returns BLANK.

**How to confirm:** Under the new labels, FiscalYear = 2024 and dates <= 2025-02-28 return 123, the same population as case B.

### Exercise 3

Write a fiscal-to-date metric caption.

For example: FY 2025 order revenue through February 28, 2025, fiscal year ending June 30.

**Why it fits this model:** The caption must say three things: which fiscal year, its end month, and the as-of date. 123 covers July 1, 2024 to February 28, 2025, and its sales are S4 to S8.

**Tempting mistake:** A caption of only "FY 2025 revenue: 123" reads as the full year to June 2025, of which four months are still unobserved.

**How to confirm:** The caption matches case B's filters, and S4 to S8 add to 123.

### Exercise 4

Diagnose comparing this 123 with a complete prior fiscal year as if coverage matched.

A partial-versus-full comparison mixes period completeness and performance. Construct a comparable prior as-of period.

**Why it fits this model:** A comparable prior uses the same span. The Date table starts on January 1, 2024, so FY 2024 has only its last six months here, and its 64 USD all comes from January 2024.

**Tempting mistake:** Calling 123 against 64 growth of about 92 percent compares 8 months of a year with an incomplete 6. A single March 2024 sale would push the full-year figure above the as-of value.

**How to confirm:** FY 2024 through 2024-02-29 returns 64, and the caption should note that the calendar starts on January 1, 2024.

### Exercise 5

Explain why a fiscal label alone cannot define a 4-4-5 retail calendar.

Month shifting is insufficient for irregular week-based periods; provide and validate the intended calendar metadata.

**Why it fits this model:** A 4-4-5 calendar groups whole weeks: 28, 28 and 35 days per quarter. RetailYear here is only a month shift that starts on February 1.

**Tempting mistake:** Treating RetailYear as week-based works for February 2025, which has exactly 28 days, but March has 31 days where a 4-4-5 period has 28.

**How to confirm:** A 4-4-5 quarter has 91 days, while February to April 2025 has 89; the calendar needs week-level metadata, not a label.

### Exercise 6

Transfer the boundary review to an accounting close.

Model the chosen accounting period explicitly and retain reconciliation to transaction dates rather than silently substituting one for the other.

**Why it fits this model:** Keep both dates. S6 was ordered on January 5 and shipped on February 1, so the January close differs by role: 67 by order date, 47 by ship date.

**Tempting mistake:** Overwriting transaction dates with the accounting period loses the trace, and nobody can then explain the 20 USD gap between the two January figures.

**How to confirm:** January order revenue 67 equals January ship revenue 47 plus S6's 20, which ships in February.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
