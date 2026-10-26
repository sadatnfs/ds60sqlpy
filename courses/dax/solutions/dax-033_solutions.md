# dax-033: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-033_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Completed January versus completed January

Full January 2025 versus the shifted January 2024 date set; both periods are within available data.

| Current | Prior | Growth |
| --- | --- | --- |
| 67 | 64 | 0.046875 |

That is approximately 4.69 percent growth for this defined monthly population, not a universal growth rate across every date role.

- Current January contains S4,S5,S6, totaling 67.
- Prior January contains S1,S2,S3, totaling 64.
- The difference 3 divided by prior 64 is 0.046875.

### Case B: An explicit as-of comparison

January 1..3,2025 compared with January 1..3,2024; explicitly as-of rather than full-month.

| Current | Prior | Growth |
| --- | --- | --- |
| 47 | 64 | -0.265625 |

The changed result is explained by the period definition. Do not repair it by choosing the more attractive percentage.

- The current interval excludes S6 on January 5, leaving 47.
- The prior interval still contains all three prior-year fixture lines, totaling 64.
- The difference-17 divided by 64 is-0.265625.

## Explained practice answers

### Exercise 1

Predict current revenue through January 5,2025.

It is 67; the selected current interval now contains all January fixture sales.

### Exercise 2

Add a hypothetical prior-year sale on January 20.

Only the first case's prior denominator changes; the two comparison windows must stay distinct.

### Exercise 3

Write a metric title that exposes the as-of boundary.

For example: Order revenue, January 1-3 versus the same dates last year, data available through the stated watermark.

### Exercise 4

Diagnose selecting a period merely because it makes growth positive.

That is outcome-driven selection. State and retain a defensible completeness policy before inspecting the effect.

### Exercise 5

Explain a zero prior revenue denominator.

Report the absolute difference and an explicit undefined or special-case growth policy rather than silently dividing by zero.

### Exercise 6

Transfer the issue to experiment cohorts enrolled at different times.

Compare the same observation age or explicitly model differing follow-up; calendar-month labels alone do not make cohorts comparable.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
