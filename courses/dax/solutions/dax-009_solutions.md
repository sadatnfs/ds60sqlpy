# dax-009: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-009_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Stored row amounts and their formula

Two first SaleID values; each projection evaluates its own Sales row.

| Line | Stored | Reconstructed |
| --- | --- | --- |
| S1 | 20 | 20 |
| S2 | 4 | 4 |

Agreement verifies this tiny fixture's arithmetic. It does not prove that a source system applies every discount or tax policy correctly.

- S1: 2 times 10 minus 0 equals 20.
- S2: 1 times 5 minus 1 equals 4.
- The supplied NetAmount column agrees with the documented row formula.

### Case B: A measure over a selected population

North customers and order year 2025.

| Revenue | Quantity |
| --- | --- |
| 83 | 9 |

The context changes the measure result from 187 to 83. It does not change S4's line value from 27 into a regional total.

- Eligible lines are S4, S5 and S8.
- Their stored amounts are 27, 20 and 36, totaling 83.
- Their quantities are 3, 4 and 2, totaling 9.

## Explained practice answers

### Exercise 1

Predict S4's stored NetAmount after selecting South.

It remains 27 in the data, but S4 is not eligible for the South measure result.

### Exercise 2

Change the case B year to 2024.

Revenue is 24 and quantity is 3.

### Exercise 3

Write a calculated-column expression for a line's gross amount.

Sales[Quantity] * Sales[UnitPrice] is the expression; its values would be stored per row if added as a calculated column externally.

### Exercise 4

Diagnose storing a region-wide total on every sales line and summing it later.

The total would be counted once per line. Use a context-dependent measure or model a separate aggregate fact with its own grain.

### Exercise 5

Explain why a measure cannot serve as a stable product-category key.

Use a column with a declared domain and grain for relationships or category membership.

### Exercise 6

Choose a lifetime for a sales-band label that must reflect refreshed row values.

A processed row classification may be a calculated column or upstream attribute; a dynamic threshold over selected totals requires a measure/table expression.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
