# dax-017: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-017_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Eight repetitions versus eight individual amounts

No outer filters; SUMX creates one Sales row context per unique SaleID.

| RawRepeated | Transitioned |
| --- | --- |
| 1496 | 187 |

The two formulas differ in context semantics, not numeric precision. Dividing the wrong result by eight would hide the mistake and fail under another population.

- Without transition, the inner SUM is 187 for every row.
- Eight iterations give 8 * 187 = 1496.
- With transition, the eight selected line amounts sum once each to 187.

### Case B: Measure invocation transitions each customer

No outer filters; a model measure is invoked within each Customer row context.

| CustomerRows | SumOfCustomerRevenue |
| --- | --- |
| 4 | 187 |

This additive reconciliation works because each sale has exactly one valid customer in this fixture. It is not a general theorem that summing any measure over any dimension equals its total.

- Ada contributes 51, Bo 80 and Cy 56.
- Di has no matching sales and contributes BLANK.
- 51 + 80 + 56 = 187.

## Explained practice answers

### Exercise 1

Predict the raw repeated formula for Paper's five lines.

It repeats 91 five times, producing 455; the transitioned sum is 91.

### Exercise 2

Replace the transitioned inner SUM with [NetRevenue].

The result stays 187 for unique Sales rows in this context.

### Exercise 3

Write the simplest formula for this additive revenue total.

SUM(Sales[NetAmount]) directly expresses the total without a per-row context transition.

### Exercise 4

Diagnose fixing RawRepeated by dividing by COUNTROWS(Sales).

It does not express the intended measure and can hide other context or blank issues. Correct the expression instead.

### Exercise 5

Explain the risk of two completely identical fact rows without a unique key.

Both rows can match the transition on each iteration, so an inner aggregation can count both repeatedly.

### Exercise 6

Transfer the reasoning to a per-customer cost allocation.

Define the allocation grain and denominator, then transition only where the measure should be evaluated for each customer or line.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
