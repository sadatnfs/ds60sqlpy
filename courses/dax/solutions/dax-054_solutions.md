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
- Grouped costs are 14,5 and 25, totaling 44.
- The eight line-level costs independently sum to the same 44.

### Case B: Parity under a region and year selection

North and order year 2025 remain active while the grouped expression iterates product keys.

| LineCost | GroupedCost |
| --- | --- |
| 20 | 20 |

This filtered case checks that a rewrite does not accidentally remove region or period constraints. Add missing-key and changing-rate cases before generalizing.

- S4,S5,S8 are the eligible lines.
- Their costs are 6,4 and 10.
- The grouped quantities 3,4,2 at rates 2,1,5 also yield 20.

## Explained practice answers

### Exercise 1

Predict the parity result for Paper.

Both expressions give 19 under the stated constant-rate assumptions.

### Exercise 2

Introduce a transaction-specific historical cost.

The rewrite is no longer justified; preserve the effective-rate grain or use a trusted stored line cost.

### Exercise 3

Write a release decision for this proposed rewrite.

Accept it only as a semantics candidate under documented assumptions, retain the context test grid, and require real comparable performance evidence before claiming improvement.

### Exercise 4

Diagnose replacing a product's unique cost with MAX across conflicting rate rows.

MAX chooses a value rather than repairing ambiguous rate data. Validate rate keys and effective dates first.

### Exercise 5

Explain a product with no matching dimension cost.

Expose a missing-cost quality failure and block or label incomplete profit; do not claim the surviving sum is complete.

### Exercise 6

Transfer the capstone to currency conversion.

Group only by keys that preserve the full rate domain, then compare row-level and grouped results across temporal and missing-rate boundaries.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
