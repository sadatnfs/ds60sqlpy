# dax-023: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-023_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Category-level prices

One group per Category; no outer filters; all-blank Travel group omitted by this summary.

| Category | Revenue | Units | NetPerUnit |
| --- | --- | --- | --- |
| Home | 96 | 5 | 19.2 |
| Paper | 91 | 12 | 7.583333333 |

The two categories have different unit counts. An equal-weight operation over the ratios would change the weighting unit from sold units to categories.

- Home contributes 96 over 5 units.
- Paper contributes 91 over 12 units.
- Each ratio describes its own category population.

### Case B: The total and an intentionally different measure

No category grouping for the pooled total; a separate iterator explicitly sums category ratios.

| PooledNetPerUnit | SumOfCategoryRatios |
| --- | --- |
| 11 | 26.78333333 |

The contrast is a useful review test: a total-row formula should reflect the intended definition, not merely resemble the visual's arithmetic layout.

- The pooled measure reevaluates 187/17 and returns 11.
- The iterator evaluates 19.2 and 91/12 for the two nonblank categories.
- Their sum is about 26.7833, a different defined calculation.

## Explained practice answers

### Exercise 1

Derive the pooled ratio as a weighted average of the two category ratios.

(19.2 * 5 + (91/12) * 12) / 17 = 11.

### Exercise 2

Filter the model to Paper only.

The pooled ratio and sum of category ratios both equal 91/12. This restricted test does not establish general equivalence.

### Exercise 3

Write a separately named equal-category average.

AVERAGEX(VALUES(Product[Category]),DIVIDE([NetRevenue],[QuantitySold])) averages the two nonblank ratios equally; label it accordingly.

### Exercise 4

Diagnose changing a distinct-customer total to SUMX over categories.

That counts customer-category memberships rather than unique customers. A matching visual row sum does not preserve the metric.

### Exercise 5

Explain why Travel is absent from the first table.

SUMMARIZECOLUMNS omits that all-blank result row. A SELECTCOLUMNS projection or zero-filled measure can have different row-retention behavior.

### Exercise 6

Transfer total reasoning to inventory at month end.

The total over time should use the intended closing or average-balance definition, not sum all snapshots.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
