# dax-011: explained reference and practice reasoning

Check that the reference computes NetPerUnit from the two model measures with DIVIDE and that the literal case returns BLANK, 0 and 0. Your draft should explain which of those zeroes is a chosen display and which is measured. Read it beside the [reference source](dax-011_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: A ratio of sufficient totals

All sales; numerator USD and denominator sold units.

| Revenue | Units | NetPerUnit |
| --- | --- | --- |
| 187 | 17 | 11 |

Changing the denominator to OrderCount would produce an average order value, a different metric even though its source data are identical.

- Sum net revenue to 187 and quantities to 17.
- 187 / 17 = 11.
- The resulting unit is USD per sold unit, not USD per order.

### Case B: Explicit undefined-ratio policy

Literal values distinguish no denominator from a positive denominator with zero outcome.

| DefaultResult | ChosenDisplay | ZeroNumerator |
| --- | --- | --- |
| BLANK | 0 | 0 |

A table showing two zeroes can therefore combine two different situations. Retain an eligibility count or availability marker to preserve that distinction.

- Zero divided by zero is not a defined observed rate.
- DIVIDE's default is BLANK; the third argument deliberately replaces it with zero.
- Zero divided by five is a defined zero rate.

## Explained practice answers

### Exercise 1

Predict net revenue per unit in 2025.

2025 revenue is 123 and units are 12, so the ratio is 10.25.

**Why it fits this model:** The 2025 lines are S4 to S8, with 123 USD over 12 units. Dividing the two totals weights each line by its units, so 10.25 USD per unit is the pooled rate.

**Tempting mistake:** Averaging the line ratios (9, 5, 20, 10 and 18) gives 62 / 5 = 12.4. S6's single 20 USD Mug then counts as much as S5's four Pens.

**How to confirm:** `CALCULATE ( DIVIDE ( [NetRevenue], [QuantitySold] ), 'Date'[Year] = 2025 )` returns 10.25, and 10.25 x 12 = 123.

### Exercise 2

Change the denominator to distinct orders.

The result is 187/7, approximately 26.7143 USD per order.

**Why it fits this model:** OrderCount uses DISTINCTCOUNT on OrderID because order 101 has two lines. Seven orders share 187 USD, about 26.7143 USD per order.

**Tempting mistake:** Dividing by COUNTROWS(Sales) uses 8 lines and returns 23.375. That is revenue per line, not per order, because S1 and S2 belong to one order.

**How to confirm:** `DIVIDE ( [NetRevenue], DISTINCTCOUNT ( Sales[OrderID] ) )` returns about 26.7143, and 26.7143 x 7 reproduces 187.

### Exercise 3

Write a measure that leaves undefined rates blank.

DIVIDE([NetRevenue],[QuantitySold]) leaves an empty or zero-denominator population blank.

**Why it fits this model:** DIVIDE with two arguments returns BLANK for an empty or zero denominator. Bag has no units, so its rate stays blank, while Notebook returns 67 / 7, about 9.571.

**Tempting mistake:** Supplying 0 as the third argument shows Bag at 0 USD per unit, as if it sold units for free. Using `/` after coalescing units to 0 would produce infinity or NaN.

**How to confirm:** By product expect Notebook about 9.571, Pen 24 / 5 = 4.8, Mug 96 / 5 = 19.2 and Bag BLANK.

### Exercise 4

Diagnose averaging the 2024 and 2025 unit-price ratios.

An equal-year mean of 12.8 and 10.25 is 11.525, while the pooled unit-weighted ratio is 11.

**Why it fits this model:** Units are the denominator, so the pooled ratio weights each year by its units: 12.8 x 5 + 10.25 x 12 = 64 + 123 = 187, and 187 / 17 = 11.

**Tempting mistake:** `AVERAGEX ( VALUES ( 'Date'[Year] ), [NetPerUnit] )` gives each year equal weight and returns 11.525, as if 2024's five units mattered as much as 2025's twelve.

**How to confirm:** The pooled measure returns 11 at the total, while the yearly rows show 12.8 and 10.25.

### Exercise 5

Explain when zero is a legitimate numerator result.

Zero conversions among five eligible units is a valid zero; no eligible units gives an undefined conversion rate.

**Why it fits this model:** A zero is observed when the denominator shows real opportunity. Bo's lines S3, S6 and S7 have 80 USD gross and no discount, so his discount rate is a true 0 / 80 = 0.

**Tempting mistake:** Using DIVIDE ( 0, 0, 0 ) for Di, who has no lines, shows his undefined rate as 0, so he looks exactly like Bo in the report.

**How to confirm:** The case row shows DefaultResult BLANK but ZeroNumerator 0. By customer, Bo's discount rate is 0 and Di's is BLANK.

### Exercise 6

Transfer the rule to experiment conversion rates.

Choose the unit and eligibility policy first, then divide conversions by that population. Repeated events must not silently inflate the denominator.

**Why it fits this model:** The design assigns two units per arm, so the denominator is assigned units. Control converts 1 of 2 (0.5) and Treatment converts 2 of 2 (1.0).

**Tempting mistake:** Building the denominator from exposure rows counts U3 twice, because it was exposed twice, and drops U4, which was assigned but never exposed.

**How to confirm:** The rates should match ExperimentSummary: Assigned 2 and Rate 0.5 for Control, and Assigned 2 and Rate 1 for Treatment.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
