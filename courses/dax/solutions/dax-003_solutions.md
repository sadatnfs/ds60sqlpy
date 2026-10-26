# dax-003: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-003_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Paper products

Product.Category = Paper; other dimensions unrestricted.

| Revenue |
| --- |
| 91 |

The result includes several customers and years. A category selection does not implicitly select the latest year or a region.

- Paper maps to product keys 1 and 2.
- Eligible lines are S1, S2, S4, S5 and S7.
- 20 + 4 + 27 + 20 + 20 = 91.

### Case B: Paper in the North

Product.Category = Paper AND Customer.Region = North.

| Revenue |
| --- |
| 71 |

A relationship graph plus eligible-row list explains the reduction without guessing which visual control caused it. Both filters remain part of the measure's question.

- North admits customer keys 10 and 30.
- Intersect those customers with Paper's product keys.
- S7 is excluded because customer 20 is South; 91 - 20 = 71.

## Explained practice answers

### Exercise 1

Predict Home revenue in North.

Only S8 remains, so revenue is 36.

### Exercise 2

Change Paper to Home while leaving North selected.

The customer filter remains; the result is 36 rather than all-Home revenue 96.

### Exercise 3

Draw the two paths that meet at Sales.

Product.ProductKey -> Sales.ProductKey and Customer.CustomerKey -> Sales.CustomerKey, each one-to-many and active.

### Exercise 4

Diagnose a report that adds 91 and 107 to represent Paper-and-North revenue.

91 + 107 counts the overlap twice and includes other rows. The intersection revenue is 71.

### Exercise 5

Predict a selection of West customers.

SUM over the empty eligible set is BLANK, not evidence of a missing West dimension row.

### Exercise 6

Explain how an event-time customer region requirement changes the model.

Use a documented historical key or event-time classification. Repeatedly changing a current Region label can rewrite historical report membership.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
