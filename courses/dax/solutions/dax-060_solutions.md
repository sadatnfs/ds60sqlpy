# dax-060: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-060_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Expected NorthViewer regression row

Assume enforced NorthViewer policy on the analytical model; all available dates; constant UnitCost per product.

| Revenue | LineCost | GroupedCost | AfterCustomerFilterRemoval |
| --- | --- | --- | --- |
| 107 | 25 | 25 | 107 |

This expected row combines numerical parity with a policy boundary. It does not certify either on a live model until actual evidence is recorded.

- North permits Ada and Cy, giving revenue 51 +56 =107.
- Their product quantities are 5 Notebook,5 Pen and 2 Mug, costing 10 +5 +10 =25.
- Both cost forms agree; a real security restriction must remain after ordinary Customer-filter removal.

### Case B: Expected SouthViewer regression row

Assume enforced SouthViewer policy; the same model and measure definitions with a different allowed Customer population.

| Revenue | LineCost | GroupedCost | AfterCustomerFilterRemoval |
| --- | --- | --- | --- |
| 80 | 19 | 19 | 80 |

North plus South reconciles to the unrestricted 187 revenue and 44 cost in this complete fixture. That reconciliation does not replace testing each denied or unmapped identity separately.

- South permits Bo, whose three lines total 80.
- TwoNotebook units cost 4 and three Mug units cost 15, totaling 19.
- The grouped result agrees and the restricted revenue remains 80 after ordinary filter removal.

## Explained practice answers

### Exercise 1

Reconcile the two role-specific cost rows.

25 +19 =44, matching the unrestricted constant-product-cost calculation.

### Exercise 2

Add an unmatched principal to the acceptance matrix.

Expected Customer and Sales populations are empty under that policy; record the corresponding BLANK measures and real role-test requirement.

### Exercise 3

Produce an offline change-review packet for the grouped-cost rewrite.

Include the exact formulas, constant-rate assumption, missing-key/rate policy, North/South and ordinary-filter cases, hashes, rollback plan and explicit unperformed external checks.

### Exercise 4

Diagnose approving a release because the exported DAX matches the reference text.

It proves only source identity. Actual model loading, role enforcement, refresh and performance need their own observed evidence.

### Exercise 5

Explain the acceptance impact of changing a relationship to bidirectional.

Revisit the full context/role matrix and ambiguity analysis; do not assume a previously correct formula retains identical behavior.

### Exercise 6

Describe a bounded next extension to this model.

For example, add return-event dates with an explicit role, fixture, reconciliation and expected matrix before attempting external model execution. Avoid importing an unrelated platform merely to increase scope.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
