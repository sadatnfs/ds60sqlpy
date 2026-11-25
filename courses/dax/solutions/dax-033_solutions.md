# dax-033: explained reference and practice reasoning

Verify that both reference cases use SAMEPERIODLASTYEAR under different Date filters, giving 67 over 64 and 47 over 64. Read it beside the [reference source](dax-033_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Completed January versus completed January

Full January 2025 versus the shifted January 2024 date set; both periods are within available data.

| Current | Prior | Growth |
| --- | --- | --- |
| 67 | 64 | 0.046875 |

That is approximately 4.69 percent growth for this defined monthly population, not a universal growth rate across every date role.

- Current January contains S4, S5, S6, totaling 67.
- Prior January contains S1, S2, S3, totaling 64.
- The difference 3 divided by prior 64 is 0.046875.

### Case B: An explicit as-of comparison

January 1 to 3, 2025 compared with January 1 to 3, 2024; explicitly as-of rather than full-month.

| Current | Prior | Growth |
| --- | --- | --- |
| 47 | 64 | -0.265625 |

The changed result is explained by the period definition. Do not repair it by choosing the more attractive percentage.

- The current interval excludes S6 on January 5, leaving 47.
- The prior interval still contains all three prior-year fixture lines, totaling 64.
- The difference -17 divided by 64 is -0.265625.

## Explained practice answers

### Exercise 1

Predict current revenue through January 5, 2025.

It is 67; the selected current interval now contains all January fixture sales.

**Why it fits this model:** The current window January 1 to 5, 2025 holds S4, S5 and S6, all of January 2025's sales, so current revenue is 67. The shifted window January 1 to 5, 2024 holds S1 to S3, 64.

**Tempting mistake:** Assuming the as-of window must stay below the full month and expecting growth to stay negative. These five days already contain every January sale in the fixture.

**How to confirm:** Through January 5: Current 67, Prior 64 and Growth 0.046875, the same as case A.

### Exercise 2

Add a hypothetical prior-year sale on January 20.

Only the first case's prior denominator changes; the two comparison windows must stay distinct.

**Why it fits this model:** A hypothetical 10 USD sale on January 20, 2024 falls inside case A's full prior January but outside case B's January 1 to 3 window.

**Tempting mistake:** Changing both comparisons, or dividing case B's 47 by the new full-month 74, mixes a three-day window with a full month.

**How to confirm:** Case A becomes 67 against 74, about -0.095; case B stays 47 against 64, -0.265625.

### Exercise 3

Write a metric title that exposes the as-of boundary.

For example: Order revenue, January 1-3 versus the same dates last year, data available through the stated watermark.

**Why it fits this model:** The title should give both windows and the role: "Order revenue, January 1 to 3, 2025 vs the same dates in 2024 (47 vs 64), data through 2025-02-28".

**Tempting mistake:** A title such as "January growth -26.6%" invites comparison with full January, which grew 4.7 percent.

**How to confirm:** The dates in the title match the DATESBETWEEN arguments, and the values read 47 and 64.

### Exercise 4

Diagnose selecting a period merely because it makes growth positive.

That is outcome-driven selection. State and retain a defensible completeness policy before inspecting the effect.

**Why it fits this model:** Here the window decides the sign: January 1 to 3 gives -0.2656 and full January +0.0469. A policy fixed before looking, such as complete months only, selects case A.

**Tempting mistake:** Picking whichever window gives a positive number reports 4.7 percent growth because it looks good, then quietly switches windows next month when the sign changes.

**How to confirm:** Write the policy first, then confirm that it yields case A's 67 against 64 whatever the result.

### Exercise 5

Explain a zero prior revenue denominator.

Report the absolute difference and an explicit undefined or special-case growth policy rather than silently dividing by zero.

**Why it fits this model:** February 2024 has no sales, so the prior period for February 2025 is BLANK, and DIVIDE returns BLANK growth instead of an error.

**Tempting mistake:** Coalescing the prior to 0 and displaying growth as 0 percent, or as infinite, suggests flat or unlimited growth where no prior revenue existed.

**How to confirm:** Under Year 2025 and MonthNumber 2, Current is 56, Prior BLANK and Growth BLANK. Report the absolute change, 56, under an explicit new-period label.

### Exercise 6

Transfer the issue to experiment cohorts enrolled at different times.

Compare the same observation age or explicitly model differing follow-up; calendar-month labels alone do not make cohorts comparable.

**Why it fits this model:** Compare at equal follow-up. Each customer's first month gives Ada 24 (January 2024), Bo 40 (January 2024) and Cy 20 (January 2025).

**Tempting mistake:** Comparing lifetime totals, Ada 51 and Bo 80 against Cy 56, sets about 14 months of follow-up against 2 months for Cy, all within data through 2025-02-28.

**How to confirm:** Revenue in the month of each first order should give 24, 40 and 20; any total over unequal follow-up must say so in its label.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
