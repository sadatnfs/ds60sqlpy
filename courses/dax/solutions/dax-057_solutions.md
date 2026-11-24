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

One customer, Bo, is permitted; expected revenue is 80.

**Why it fits this model:** The Access table maps south.learner@example.test to South, and only Bo (customer 20) is in South.

**Tempting mistake:** Comparing USERNAME() (often DOMAIN\user) with the email-style Principal column. Nothing matches, so a mapped user sees nothing.

**How to confirm:** As the south principal, VisibleCustomers returns 1 and VisibleRevenue returns 80.

### Exercise 2

AddWest to a principal's allowed-region set conceptually.

The allowed-customer count can increase while revenue stays unchanged; permission population and fact activity are different.

**Why it fits this model:** Di (customer 40, West) has no sales, so permission to see her changes the customer count but not revenue.

**Tempting mistake:** Treating unchanged revenue as proof that adding West failed, or expecting revenue to rise because the mapping grew.

**How to confirm:** For the north principal with North and West, VisibleCustomers goes from 2 to 3 and VisibleRevenue stays 107.

### Exercise 3

Write a default-deny mapping test matrix.

Record each fictional principal, allowed regions, expected Customer keys and amounts, plus the required real identity/role evidence before deployment.

**Why it fits this model:** A default-deny matrix lists mapped, unmapped and invalid-domain principals with their expected rows.

**Tempting mistake:** Testing only north.learner, which returns 2 customers and 107, and assuming unmapped and bad-value cases behave.

**How to confirm:** Rows: north 2 and 107, south 1 and 80, unmapped empty (HasVisibleRows False), and a principal mapped to "East", a region not in Customer, also empty.

### Exercise 4

Diagnose granting all regions when no mapping exists.

That reverses the supplied default-deny contract and risks unintended access. Keep an explicit denial and investigate provisioning.

**Why it fits this model:** The declared rule filters Customer to regions the principal maps to. An empty mapping gives an empty set, which is a denial.

**Tempting mistake:** Adding a fallback such as returning TRUE() when the mapping is empty. The unmapped principal would then see all 4 customers and 187.

**How to confirm:** As unmapped.learner@example.test, VisibleCustomers and VisibleRevenue are BLANK and HasVisibleRows is False, as in case B.

### Exercise 5

Explain why securing Customer does not prove Access itself is protected.

Review mapping-table visibility and disconnected data independently; do not infer complete protection from one correctly filtered sales result.

**Why it fits this model:** The rule filters Customer, but Access is a separate table. Without its own rule or hiding it, any reader can query it.

**Tempting mistake:** Concluding that the model is protected because the north principal sees 107, while COUNTROWS(Access) still returns 2 and shows the south mapping.

**How to confirm:** As north.learner, query the Access table; the policy should decide whether 2, 1 or no rows are acceptable, and test that result.

### Exercise 6

Transfer the policy to tenant identifiers.

Validate authenticated identity, membership changes, allowed tenant keys and every query surface; an editable tenant filter is not an access-control system.

**Why it fits this model:** Tenant access follows the same contract: authenticated identity, an explicit mapping to tenant keys, and denial when nothing maps.

**Tempting mistake:** Taking the tenant ID from a URL parameter or slicer, so a user can change one value and read another tenant.

**How to confirm:** Test a mapped user, an unmapped user (no rows) and a user who edits the tenant parameter; only the mapped tenant's rows may appear.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
