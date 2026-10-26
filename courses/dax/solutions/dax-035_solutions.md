# dax-035: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-035_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

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

- The fiscal interval starts July 1,2024.
- The as-of boundary stops at February 28,2025, not June 30.
- The available matching sales are S4..S8, totaling 123.

## Explained practice answers

### Exercise 1

Predict FiscalYear for January 3, 2025.

The fiscal label is 2025.

### Exercise 2

Change the naming convention to the starting year.

July 1,2024 would be labeled FY 2024. Update labels and documentation without pretending the population changed.

### Exercise 3

Write a fiscal-to-date metric caption.

For example: FY 2025 order revenue through February 28,2025, fiscal year ending June 30.

### Exercise 4

Diagnose comparing this 123 with a complete prior fiscal year as if coverage matched.

A partial-versus-full comparison mixes period completeness and performance. Construct a comparable prior as-of period.

### Exercise 5

Explain why a fiscal label alone cannot define a 4-4-5 retail calendar.

Month shifting is insufficient for irregular week-based periods; provide and validate the intended calendar metadata.

### Exercise 6

Transfer the boundary review to an accounting close.

Model the chosen accounting period explicitly and retain reconciliation to transaction dates rather than silently substituting one for the other.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
