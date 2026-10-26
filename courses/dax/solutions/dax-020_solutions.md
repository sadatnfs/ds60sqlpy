# dax-020: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-020_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Share within the retained category

Paper and Blue selected; remove only Color in the denominator.

| Numerator | CategoryDenominator | Share |
| --- | --- | --- |
| 67 | 91 | 0.7362637363 |

The denominator does not become 187 because the Category filter was deliberately retained.

- The numerator contains Notebook: 67.
- Removing Color restores Pen within Paper, giving 67 + 24 = 91.
- The share is 67/91; Home remains outside the category population.

### Case B: All products within North

Paper, Blue and North selected; remove Product filters only in the denominator.

| Numerator | RegionalDenominator | Share |
| --- | --- | --- |
| 47 | 107 | 0.4392523364 |

An 'all products' denominator can still be regional and temporal. The model does not interpret the word all as an instruction to remove every other dimension.

- North Notebook sales are S1 and S4: 47.
- Removing Product restrictions admits North Pen 24? In North Pen contributes S2 4 plus S5 20, totaling 24, and Mug contributes 36.
- The retained North population totals 47 + 24 + 36 = 107; share is 47/107.

## Explained practice answers

### Exercise 1

Predict case A after removing the entire Product table instead of Color.

The denominator becomes 187 and the share becomes 67/187.

### Exercise 2

Restrict case B to year 2025.

The numerator is 27 and the North-year denominator is 83, so the share is 27/83.

### Exercise 3

Write the denominator contract in plain language before coding.

For case B: all products among North customers, within any other unchanged date or report constraints.

### Exercise 4

Diagnose a 100-percent share produced by a frozen denominator variable.

Removing filters around a precomputed scalar does not reevaluate revenue. Bind CALCULATE([NetRevenue],REMOVEFILTERS(...)) instead.

### Exercise 5

Explain the denominator for a selected unsold product.

The numerator may remain BLANK even with a positive denominator. Decide whether the display should expose absence or coalesce it deliberately.

### Exercise 6

Transfer the pattern to a departmental cost share.

Remove the department selection only if the denominator should cover all departments in that same compatible population.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
