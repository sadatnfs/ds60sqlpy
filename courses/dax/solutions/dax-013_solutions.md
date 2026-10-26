# dax-013: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-013_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A row label beside an unfiltered sum

No outer filters; SELECTCOLUMNS supplies a Product row context only.

| Product | RawSum |
| --- | --- |
| Bag | 187 |
| Mug | 187 |
| Notebook | 187 |
| Pen | 187 |

The repeated total is not evidence of a broken relationship. It is evidence that the formula never supplied that relationship with a Product filter.

- The Product label changes on each iteration.
- The raw SUM has no transitioned Product filter.
- Every iteration therefore adds the same eight sales lines and returns 187.

### Case B: Transition the current product into a filter

The same Product rows, now with explicit context transition for the raw SUM.

| Product | Revenue |
| --- | --- |
| Bag | BLANK |
| Mug | 96 |
| Notebook | 67 |
| Pen | 24 |

The sum of the three nonblank product results reconciles to 187 because these product populations partition the fact rows in the clean model.

- CALCULATE turns each current Product row into filters.
- The active key relationship restricts Sales for that product.
- Bag has no matching fact rows; the other products contribute 96, 67 and 24.

## Explained practice answers

### Exercise 1

Predict the second projection if it uses [NetRevenue] instead of CALCULATE(SUM(...)).

It returns the same per-product values for this model.

### Exercise 2

Add an outer North filter to the raw-SUM case.

RawSum repeats the North total 107 for every visible product.

### Exercise 3

Write a projection that shows both raw and transitioned sums.

Each row can show RawSum 187 beside its own Revenue; this makes the missing transition directly observable.

### Exercise 4

Diagnose replacing the relationship because every row shows 187.

The relationship can be correct; the raw aggregation has no Product filter to propagate.

### Exercise 5

Explain why Bag remains a returned row in case B.

Blank output is not a row-removal rule for this function. Other table functions may have different blank-row behavior.

### Exercise 6

Transfer the distinction to a Customer calculated column containing total sales.

A raw Sales SUM repeats the outer total; CALCULATE or a model measure transitions the customer row so the relationship can filter its sales.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
