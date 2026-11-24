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

**Why it fits this model:** The pooled ratio weights each category's ratio by its units: Home 19.2 x 5 = 96 and Paper (91 / 12) x 12 = 91, so 187 / 17 = 11.

**Tempting mistake:** A simple mean of 19.2 and about 7.583 is about 13.39. That gives Home's five units as much weight as Paper's twelve.

**How to confirm:** The weighted formula returns 11, which matches PooledNetPerUnit in case B.

### Exercise 2

Filter the model to Paper only.

The pooled ratio and sum of category ratios both equal 91/12. This restricted test does not establish general equivalence.

**Why it fits this model:** Under Paper only one category contributes, so DIVIDE over the total and SUMX over one category both give 91 / 12, about 7.583.

**Tempting mistake:** Concluding from this match that the sum of ratios is a valid total is the error. With both categories present they differ: 11 against about 26.78.

**How to confirm:** Under Paper both measures return about 7.5833; with no filter they return 11 and about 26.7833.

### Exercise 3

Write a separately named equal-category average.

AVERAGEX(VALUES(Product[Category]),DIVIDE([NetRevenue],[QuantitySold])) averages the two nonblank ratios equally; label it accordingly.

**Why it fits this model:** AVERAGEX over VALUES(Product[Category]) gives each category equal weight. Travel's ratio is BLANK and skipped, so the result is (19.2 + 7.583) / 2, about 13.39.

**Tempting mistake:** Adding a third argument of 0 to DIVIDE turns Travel into a 0 and drags the average to about 8.93, as if Travel had sold units for free.

**How to confirm:** Expect about 13.3917 under a name such as Equal Category Net Per Unit, shown beside the pooled 11.

### Exercise 4

Diagnose changing a distinct-customer total to SUMX over categories.

That counts customer-category memberships rather than unique customers. A matching visual row sum does not preserve the metric.

**Why it fits this model:** DISTINCTCOUNT(Sales[CustomerKey]) evaluated at the total counts Ada, Bo and Cy once each, 3, even though Bo and Cy appear in both categories.

**Tempting mistake:** SUMX over categories adds Paper's 3 and Home's 2 and returns 5. The visual total may match the sum of rows, but the measure now counts customer-category pairs.

**How to confirm:** The grand total of the distinct measure is 3, while the SUMX version is 5.

### Exercise 5

Explain why Travel is absent from the first table.

SUMMARIZECOLUMNS omits that all-blank result row. A SELECTCOLUMNS projection or zero-filled measure can have different row-retention behavior.

**Why it fits this model:** Travel has only Bag, which has no sales, so Revenue, Units and NetPerUnit are all BLANK and SUMMARIZECOLUMNS drops the row.

**Tempting mistake:** Adding COALESCE(..., 0) to make Travel appear changes the measures, so Travel now shows 0 revenue and 0 units, which looks like an observed outcome.

**How to confirm:** The case returns two rows. `ADDCOLUMNS ( VALUES ( Product[Category] ), "Revenue", [NetRevenue] )` returns three, with Travel BLANK.

### Exercise 6

Transfer total reasoning to inventory at month end.

The total over time should use the intended closing or average-balance definition, not sum all snapshots.

**Why it fits this model:** A stock balance adds across products but not across dates. A closing-balance total over a quarter should take the last snapshot, not the sum.

**Tempting mistake:** If Notebook held 10 units on January 31 and 6 on February 28, summing snapshots reports 16 units in stock, which never existed on any day.

**How to confirm:** A closing-balance measure over both months returns 6, and an average balance returns 8; the sum, 16, matches neither.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
