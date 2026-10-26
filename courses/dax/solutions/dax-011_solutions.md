# dax-011: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-011_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

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

### Exercise 2

Change the denominator to distinct orders.

The result is 187/7, approximately 26.7143 USD per order.

### Exercise 3

Write a measure that leaves undefined rates blank.

DIVIDE([NetRevenue],[QuantitySold]) leaves an empty or zero-denominator population blank.

### Exercise 4

Diagnose averaging the 2024 and 2025 unit-price ratios.

An equal-year mean of 12.8 and 10.25 is 11.525, while the pooled unit-weighted ratio is 11.

### Exercise 5

Explain when zero is a legitimate numerator result.

Zero conversions among five eligible units is a valid zero; no eligible units gives an undefined conversion rate.

### Exercise 6

Transfer the rule to experiment conversion rates.

Choose the unit and eligibility policy first, then divide conversions by that population. Repeated events must not silently inflate the denominator.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
