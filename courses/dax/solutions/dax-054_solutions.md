# dax-054: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-054_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Whole-model parity under a constant product cost

Clean retail model; UnitCost is constant per product and unique on ProductKey.

| LineCost | GroupedCost |
| --- | --- |
| 44 | 44 |

The data model supplies the rate constancy that permits this grouping. The formula alone does not prove that assumption in another dataset.

- Notebook has 7 units at 2, Pen 5 units at 1 and Mug 5 units at 5.
- Grouped costs are 14, 5 and 25, totaling 44.
- The eight line-level costs independently sum to the same 44.

### Case B: Parity under a region and year selection

North and order year 2025 remain active while the grouped expression iterates product keys.

| LineCost | GroupedCost |
| --- | --- |
| 20 | 20 |

This filtered case checks that a rewrite does not accidentally remove region or period constraints. Add missing-key and changing-rate cases before generalizing.

- S4, S5, S8 are the eligible lines.
- Their costs are 6, 4 and 10.
- The grouped quantities 3, 4, 2 at rates 2, 1, 5 also yield 20.

## Explained practice answers

### Exercise 1

Predict the parity result for Paper.

Both expressions give 19 under the stated constant-rate assumptions.

**Why it fits this model:** With one cost per product, multiplying each product's quantity by its cost equals the line sum. Paper's products are Notebook (7 x 2 = 14) and Pen (5 x 1 = 5).

**Tempting mistake:** Multiplying Paper's total quantity, 12, by MAX(UnitCost) over Paper, 2, gives 24. The grouping has to be by product.

**How to confirm:** Under Category = "Paper", LineCost and GroupedCost both return 19.

### Exercise 2

Introduce a transaction-specific historical cost.

The rewrite is no longer justified; preserve the effective-rate grain or use a trusted stored line cost.

**Why it fits this model:** If Notebook's 2024 line S1 had cost 1.5 instead of 2, the line form gives 3 + 6 + 4 = 13 for Notebook, while grouping by product applies one rate to all 7 units.

**Tempting mistake:** Keeping the grouped rewrite. MAX picks 2 and returns 14, so it overstates cost by 1.

**How to confirm:** Line cost 13 versus grouped 14 for Notebook; group by the key that defines the rate, or store the line cost.

### Exercise 3

Write a release decision for this proposed rewrite.

Accept it only as a semantics candidate under documented assumptions, retain the context test grid, and require real comparable performance evidence before claiming improvement.

**Why it fits this model:** The rewrite matches here only because each product has one cost. Case A gives 44 and 44, and case B gives 20 and 20.

**Tempting mistake:** Releasing it as faster without timings, or as correct without the context grid from cases A and B.

**How to confirm:** Accept it as correct under the one-cost-per-product rule, keep both cases as regressions, and require a real benchmark before claiming speed.

### Exercise 4

Diagnose replacing a product's unique cost with MAX across conflicting rate rows.

MAX chooses a value rather than repairing ambiguous rate data. Validate rate keys and effective dates first.

**Why it fits this model:** Two cost rows for one product break the one-cost rule. MAX hides that by choosing one value.

**Tempting mistake:** If Notebook had rows at 2 and 3, MAX returns 3 and cost becomes 21, with no warning that the input was ambiguous.

**How to confirm:** Check that each ProductKey has one cost; COUNTROWS of cost rows per ProductKey should be 1 before either formula runs.

### Exercise 5

Explain a product with no matching dimension cost.

Expose a missing-cost quality failure and block or label incomplete profit; do not claim the surviving sum is complete.

**Why it fits this model:** In the unknown-member model, S9 has ProductKey 999 and Net 7, with no matching Product row, so RELATED(Product[UnitCost]) is BLANK.

**Tempting mistake:** Reporting cost 44 against revenue 194. S9's cost is missing, not zero, so profit is overstated.

**How to confirm:** Count sales lines whose cost is BLANK (1 here), and label profit incomplete until it is fixed.

### Exercise 6

Transfer the capstone to currency conversion.

Group only by keys that preserve the full rate domain, then compare row-level and grouped results across temporal and missing-rate boundaries.

**Why it fits this model:** Rates depend on date and currency. Grouping by (SaleDate, Currency) matches the row-level sum: 100 x 1 + 100 x 1.1 + 50 x 1.2 = 270.

**Tempting mistake:** Grouping by currency only and taking MAX of EUR rates converts 150 EUR at 1.2 for 180 USD instead of 170.

**How to confirm:** Row-level and (SaleDate, Currency)-grouped conversions both return 270; the currency-only grouping does not.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
