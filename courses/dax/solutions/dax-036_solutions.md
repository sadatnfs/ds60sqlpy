# dax-036: explained reference and practice reasoning

Confirm that the reference keeps the anchor and measure identical and changes only the TOTALYTD calendar argument. Your draft should derive 123 and 56 from the lines each year definition admits. Read it beside the [reference source](dax-036_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Classic Gregorian YTD

Classic marked Date column; Gregorian year; anchor 2025-02-03.

| GregorianYTD |
| --- |
| 123 |

This case requires only the already described classic date-table contract. It provides a stable baseline for comparing another calendar definition.

- The classic year begins January 1.
- January revenue 67 and February-to-date 56 are included.
- Gregorian YTD is 123.

### Case B: The declared February-start retail calendar

Assume the optional RetailCalendar metadata has been configured exactly as specified; RetailYear starts February 1.

| RetailYTD |
| --- |
| 56 |

This is a reference derivation under a declared metadata assumption, not observed preview-engine output. An undefined calendar name would not be a usable external query.

- The anchor belongs to RetailYear 2026 under the ending-year naming rule.
- Its year-to-date date set begins February 1, 2025.
- S7 and S8 contribute 20 + 36 = 56; January belongs to the prior retail year.

## Explained practice answers

### Exercise 1

Predict the retail-year label for January 31, 2025.

It is RetailYear 2025; February 1 begins RetailYear 2026.

**Why it fits this model:** RetailYear is Year plus 1 from February, so January 31, 2025 belongs to RetailYear 2025 and February 1, 2025 starts RetailYear 2026.

**Tempting mistake:** Assuming RetailYear equals the calendar year works on January 31 but gives 2025 for February 1, a year off for eleven months of each retail year.

**How to confirm:** SELECTCOLUMNS returns RetailYear 2025 for 2025-01-31 and 2026 for 2025-02-01.

### Exercise 2

Change the declared calendar to Gregorian year tags.

At the same anchor the intended calendar YTD population would match the Gregorian set and total 123.

**Why it fits this model:** With Gregorian tags the calendar's year begins January 1, so the YTD set at February 3 is January 1 to February 3, 2025, and the total is 123.

**Tempting mistake:** Keeping the name RetailCalendar after the tags change leads readers to expect the February-start 56, when the result is now the Gregorian 123.

**How to confirm:** After the change, the calendar version returns the same 123 as case A.

### Exercise 3

Write a review checklist for adding an external calendar object.

Verify the calendar name, day/year/month tags, member uniqueness, date role, feature availability and observed results around year and leap boundaries.

**Why it fits this model:** The checklist confirms the tags (Day to Date, Year to RetailYear, Month to YearMonth), then tests the boundary: RetailYTD at January 31, 2025 covers February 1, 2024 to January 31, 2025, which is 67 (S4, S5, S6). February 2 restarts at 20 and February 3 reaches 56.

**Tempting mistake:** Checking only one mid-year anchor will not catch a year that starts a day early or late; a wrong boundary would show up at January 31 or February 1.

**How to confirm:** At January 31, 2025 expect 67; at February 1, BLANK; at February 2, 20; at February 3, 56.

### Exercise 4

Diagnose copying the second query into a model with only a Date table.

The reference is missing an input contract there. A similarly named table or column does not automatically create RetailCalendar.

**Why it fits this model:** RetailCalendar is a calendar object defined in model metadata. In a model with only the Date table, the query refers to something that does not exist.

**Tempting mistake:** Adding a table named RetailCalendar with a RetailYear column, and expecting TOTALYTD to read it as a calendar, still lacks the configured tags.

**How to confirm:** Without the metadata the query fails to resolve; with the specified calendar it returns 56 at February 3.

### Exercise 5

Explain why sparse-calendar support does not prove complete observation data.

A feature accepting sparse dates does not certify that every relevant event or reporting period was observed.

**Why it fits this model:** A calendar feature can accept sparse dates, but coverage is a separate fact. Here coverage is declared through 2025-02-28, and February 1, 2025 is an observed day with no sales.

**Tempting mistake:** Building a calendar from the 7 order dates and concluding that coverage is complete because the feature accepts it. Observed zero days and unobserved days look the same in that list.

**How to confirm:** Compare the 59 calendar days of January and February 2025 with the declared coverage, separately from the 5 order dates in that period.

### Exercise 6

Transfer the distinction to a week-based retail calendar.

Define the 4-4-5 pattern, year boundary and extra-week policy, then test date sets and measures rather than treating calendar labels as interchangeable.

**Why it fits this model:** A week-based year has 364 days, with a 53rd week at intervals. Its periods follow a 4-4-5 pattern, and its start falls on a fixed weekday, not on February 1.

**Tempting mistake:** Reusing the February-start RetailYear as a week calendar assumes every year starts on the same date and ignores the extra week.

**How to confirm:** Check that each defined year has 364 or 371 days, that each quarter has 28, 28 and 35 days, and that the YTD set for a known anchor matches a hand-built list.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
