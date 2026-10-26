# dax-057: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-057_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A mapped synthetic principal

Assume the declared dynamic Customer policy is enforced for north.learner@example.test in a role-restricted Viewer context.

| VisibleCustomers | VisibleRevenue |
| --- | --- |
| 2 | 107 |

The identity string selects an expected mapping in this teaching specification. No external account was authenticated and no role-test result is being claimed.

- The Access mapping supplies North.
- Customer 10 and 30 are allowed.
- Their revenues 51 and 56 total 107.

### Case B: An unmapped principal is denied by the declared policy

Assume the same enforced policy for unmapped.learner@example.test; its allowed-region set is empty.

| VisibleCustomers | VisibleRevenue | HasVisibleRows |
| --- | --- | --- |
| BLANK | BLANK | FALSE |

This is an explicit deny expectation, not a fallback to all regions. Test it under an actual applicable role before relying on a deployed model.

- No Access row matches that principal.
- The policy's allowed Region set is empty and no Customer row qualifies.
- COUNTROWS and SUM are BLANK on their empty populations; the positive-row comparison is FALSE.

## Explained practice answers

### Exercise 1

Predict the permitted population for the synthetic south principal.

One customer,Bo, is permitted; expected revenue is 80.

### Exercise 2

AddWest to a principal's allowed-region set conceptually.

The allowed-customer count can increase while revenue stays unchanged; permission population and fact activity are different.

### Exercise 3

Write a default-deny mapping test matrix.

Record each fictional principal, allowed regions, expected Customer keys and amounts, plus the required real identity/role evidence before deployment.

### Exercise 4

Diagnose granting all regions when no mapping exists.

That reverses the supplied default-deny contract and risks unintended access. Keep an explicit denial and investigate provisioning.

### Exercise 5

Explain why securing Customer does not prove Access itself is protected.

Review mapping-table visibility and disconnected data independently; do not infer complete protection from one correctly filtered sales result.

### Exercise 6

Transfer the policy to tenant identifiers.

Validate authenticated identity, membership changes, allowed tenant keys and every query surface; an editable tenant filter is not an access-control system.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
