# dax-015: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-015_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Replace Blue with Red

Start with Product.Color = Blue; the inner calculation sets Color = Red.

| Original | RedRevenue |
| --- | --- |
| 163 | 24 |

The second result is not a Blue-and-Red intersection. That would have no product rows in this fixture.

- The original measure includes Notebook and Mug, totaling 163.
- The inner predicate replaces the filter on the same Color column.
- Red admits Pen and produces 24.

### Case B: Add Color while retaining Category

Start with Category = Paper; add Color = Blue on a different column.

| PaperRevenue | BluePaperRevenue |
| --- | --- |
| 91 | 67 |

Replacing one column's selection and retaining a different column's selection are compatible behaviors. Always specify which column the expression modifies.

- Paper supplies Notebook and Pen: 91.
- Blue is added while Paper remains active.
- Only Notebook satisfies both; revenue is 67.

## Explained practice answers

### Exercise 1

Predict setting Color = Green inside the Blue context.

Green selects Bag, whose revenue is BLANK because it has no facts.

### Exercise 2

Change case B's Color to Red.

The modified revenue is 24.

### Exercise 3

Write a measure that forces year 2025 but retains region.

CALCULATE([NetRevenue],'Date'[Year]=2025) retains an independent Customer.Region filter; under North the result is 83.

### Exercise 4

Diagnose saying CALCULATE removed every report filter.

They can remain active. Case B retains Category and therefore does not return all-Blue revenue 163.

### Exercise 5

Explain when a constant filter is inappropriate for an interactive metric.

A fixed-year or fixed-color measure should be clearly named; use an intersection policy when the metric should respect the selection.

### Exercise 6

Transfer the distinction to a share denominator.

Preserve filters defining the comparable population while changing only the category or time dimension required by the denominator's definition.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
