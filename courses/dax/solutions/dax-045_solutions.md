# dax-045: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-045_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Scale has higher precedence

Specified items: AddTen = SELECTEDMEASURE()+10 at lower precedence; Scale = SELECTEDMEASURE()*0.9 at higher precedence.

| ExpandedValue |
| --- |
| 177.3 |

The literal 10 represents an illustrative compatible amount for this algebra example. A real fee policy would also define which population and measures receive it.

- The outer Scale expression receives the lower-precedence AddTen expression.
- The expansion is(187 +10)*0.9.
- 197 multiplied by 0.9 is 177.3.

### Case B: Addition has higher precedence

The same two item definitions with AddTen as the higher-precedence outer expression.

| ExpandedValue |
| --- |
| 178.3 |

Passing tests for each group alone does not prove their combined behavior. Include interacting groups in a measure/context regression matrix.

- The expansion is(187*0.9)+10.
- The scale first yields 168.3.
- Adding 10 gives 178.3, one more than the other order.

## Explained practice answers

### Exercise 1

Predict both expansions for a base value 100.

Scale-after-add gives 99; add-after-scale gives 100.

### Exercise 2

Replace the additive 10 by zero.

Both expressions become 0.9 times the base, so that case cannot validate the intended order.

### Exercise 3

Write a regression grid for two interacting groups.

Record each group's selection, precedence, underlying measure, filters, expanded numeric expression and expected format pattern.

### Exercise 4

Diagnose fixing a wrong number by changing its format string.

Repair composition or the business policy first. Formatting can only change how the numeric result is displayed.

### Exercise 5

Explain a percentage format on the value 177.3.

It would imply a different unit and misleading scale; keep currency and ratio measures' format policies distinct.

### Exercise 6

Transfer precedence reasoning to currency conversion and time intelligence.

Expand the combined expressions and verify transaction/rate grain and date-role behavior; arithmetic examples alone do not qualify a real currency/time group combination.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
