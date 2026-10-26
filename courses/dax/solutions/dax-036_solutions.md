# dax-036: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-036_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

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
- Its year-to-date date set begins February 1,2025.
- S7 and S 8 contribute 20 +36 =56; January belongs to the prior retail year.

## Explained practice answers

### Exercise 1

Predict the retail-year label for January 31,2025.

It is RetailYear 2025; February 1 begins RetailYear 2026.

### Exercise 2

Change the declared calendar to Gregorian year tags.

At the same anchor the intended calendar YTD population would match the Gregorian set and total 123.

### Exercise 3

Write a review checklist for adding an external calendar object.

Verify the calendar name, day/year/month tags, member uniqueness, date role, feature availability and observed results around year and leap boundaries.

### Exercise 4

Diagnose copying the second query into a model with only a Date table.

The reference is missing an input contract there. A similarly named table or column does not automatically create RetailCalendar.

### Exercise 5

Explain why sparse-calendar support does not prove complete observation data.

A feature accepting sparse dates does not certify that every relevant event or reporting period was observed.

### Exercise 6

Transfer the distinction to a week-based retail calendar.

Define the 4-4-5 pattern, year boundary and extra-week policy, then test date sets and measures rather than treating calendar labels as interchangeable.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
