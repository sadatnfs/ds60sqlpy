# dax-056: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-056_reference.dax) and [named model](../models/analytics/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: An ordinary filter can be removed

Unrestricted model; North is only an ordinary report/query filter.

| SelectedRevenue | AfterRemovingCustomerFilters |
| --- | --- |
| 107 | 187 |

The removable filter never constituted an access-control boundary.

- The report filter selects Ada and Cy, whose revenue totals 107.
- REMOVEFILTERS(Customer) removes that analytical selection.
- Bo's 80 becomes eligible, restoring 187.

### Case B: Expected behavior under an enforced NorthViewer role

Assume a role-restricted Viewer with the declared NorthViewer RLS policy enforced by a compatible engine; no ordinary Customer filter is needed.

| VisibleRevenue | AfterRemovingCustomerFilters |
| --- | --- |
| 107 | 107 |

These expected values belong in a real role-test matrix. Their presence in a source file does not prove that the external role was configured or applied.

- The security policy permits Customer 10 and 30 only.
- The expected fact population totals 51 +56 =107.
- Removing ordinary Customer filters must not remove the security restriction.

## Explained practice answers

### Exercise 1

Predict the ordinary unfiltered total in case A.

It is 187.

### Exercise 2

Change the declared role to SouthViewer.

Expected revenue is 80, including after an ordinary Customer-filter removal.

### Exercise 3

Write a real RLS acceptance record template.

Record test identity/workspace role, model/role version, relationships, submitted query, expected allowed rows and actual observed result, including denial cases.

### Exercise 4

Diagnose testing only as the workspace administrator.

Use the documented applicable role and identity; an unrestricted result cannot certify Viewer RLS behavior.

### Exercise 5

Explain why hidden report pages or disabled buttons are insufficient.

A real security boundary must constrain allowed data through the supported engine/service controls, not just the visible navigation.

### Exercise 6

Transfer the distinction to a SQL dashboard WHERE clause.

A removable predicate does not protect data from another authorized query path; test actual role/permission boundaries separately.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
