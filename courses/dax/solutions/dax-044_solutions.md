# dax-044: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-044_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Current measures before an item

No calculation item applied; baseline measure definitions.

| Revenue | Units |
| --- | --- |
| 187 | 17 |

A shared visual can contain both measures without implying that every calculation item should transform them identically.

- The eligible Sales rows total 187 USD.
- Their quantities total 17 units.
- These quantities have different units and transformation policies.

### Case B: Expanded guarded fee item

Algebraic expansion of the named revenue-only item; no live calculation-group execution.

| RevenueAfterFee | UnitsUnchanged |
| --- | --- |
| 168.3 | 17 |

An expanded query is a useful semantic reference. It does not establish that a particular external model's group selection, precedence or formatting is configured correctly.

- The revenue branch multiplies 187 by 0.9, giving 168.3.
- The guard leaves the quantity measure at 17.
- The transformation changes a defined revenue policy, not the observed transaction counts.

## Explained practice answers

### Exercise 1

Predict the guarded item for Blue revenue.

The transformed revenue is 146.7; Blue units remain 12.

### Exercise 2

Remove the applicability guard conceptually.

Quantity 17 would become 15.3, which is inappropriate for this observed-unit measure.

### Exercise 3

Write the calculation-item expression and its applicability contract.

IF(ISSELECTEDMEASURE([NetRevenue]),SELECTEDMEASURE()*0.9,SELECTEDMEASURE()); document that only NetRevenue receives the fee.

### Exercise 4

Diagnose pasting SELECTEDMEASURE into an ordinary query-local measure.

It does not name a normal measure argument there. Expand a named measure for offline arithmetic or create the appropriate model object externally.

### Exercise 5

Explain whether selecting two calculation items has a universal default result.

Record the group's selection-expression policy and test no-selection/multiple-selection cases in a real supported model before deployment.

### Exercise 6

Transfer the guard to a prior-period calculation group.

Define which measures represent period flows, balances or labels, then test each intended transformation and excluded measure.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
