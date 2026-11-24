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

- North permits Ada and Cy, giving revenue 51 + 56 = 107.
- Their product quantities are 5 Notebook,5 Pen and 2 Mug, costing 10 + 5 + 10 = 25.
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

25 + 19 = 44, matching the unrestricted constant-product-cost calculation.

**Why it fits this model:** NorthViewer allows Ada and Cy and SouthViewer allows Bo. Di (West) has no sales, so the two roles cover every sales line once.

**Tempting mistake:** Adding role rows as a reconciliation where principals can map to overlapping regions; overlap would count lines twice.

**How to confirm:** Cost 25 + 19 = 44 and revenue 107 + 80 = 187, matching the unrestricted results.

### Exercise 2

Add an unmatched principal to the acceptance matrix.

Expected Customer and Sales populations are empty under that policy; record the corresponding BLANK measures and real role-test requirement.

**Why it fits this model:** The declared policy denies unmapped principals, so every measure sees empty Customer and Sales tables.

**Tempting mistake:** Expecting zeros, or the unrestricted 187, for an unmapped principal.

**How to confirm:** The expected row is Revenue, LineCost, GroupedCost and AfterCustomerFilterRemoval all BLANK, with a note that a real role test is still required.

### Exercise 3

Produce an offline change-review packet for the grouped-cost rewrite.

Include the exact formulas, constant-rate assumption, missing-key/rate policy, North/South and ordinary-filter cases, hashes, rollback plan and explicit unperformed external checks.

**Why it fits this model:** The packet ties formula, assumptions and expected results together so another reviewer can check each claim.

**Tempting mistake:** A packet with only the new formula and the word "faster", which does not show what must stay equal.

**How to confirm:** Include unrestricted 44 and 44, North 25 and 25, South 19 and 19, unmapped BLANK, the one-cost-per-product assumption, and the checks not yet run.

### Exercise 4

Diagnose approving a release because the exported DAX matches the reference text.

It proves only source identity. Actual model loading, role enforcement, refresh and performance need their own observed evidence.

**Why it fits this model:** Matching text proves the source is the one reviewed. It says nothing about how an engine loads or secures it.

**Tempting mistake:** Approving the release because the exported DAX is byte-identical to the reference.

**How to confirm:** In the target service, run the role rows: NorthViewer revenue 107, line and grouped cost 25 each, 107 after customer filter removal; SouthViewer revenue 80, costs 19 each, 80 after removal.

### Exercise 5

Explain the acceptance impact of changing a relationship to bidirectional.

Revisit the full context/role matrix and ambiguity analysis; do not assume a previously correct formula retains identical behavior.

**Why it fits this model:** Customer to GroupMembership is single-direction, so an Audience filter does not reach Sales today. Making it bidirectional lets it.

**Tempting mistake:** Assuming the measures still return what they did. Under NorthViewer, a visual by Audience currently repeats 107 for each audience; after the change Newsletter (Ada, Bo) shows 51 and Prospects (Bo, Cy) shows 56.

**How to confirm:** Rerun the full matrix after the change, including role rows and audience breakdowns (unrestricted Newsletter 131 and Prospects 136).

### Exercise 6

Describe a bounded next extension to this model.

For example, add return-event dates with an explicit role, fixture, reconciliation and expected matrix before attempting external model execution. Avoid importing an unrelated platform merely to increase scope.

**Why it fits this model:** One new requirement with its own evidence is a bounded extension. Return-event dates fill the gap from the commercial capstone.

**Tempting mistake:** Adding a live platform deployment as the next step, which increases scope without answering a new business question.

**How to confirm:** Add ReturnDate to R1 and R2 with a stated date role, then check that refunds still total 13 and adjusted revenue 174 across refund months.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
