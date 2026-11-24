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
- The expected fact population totals 51 + 56 = 107.
- Removing ordinary Customer filters must not remove the security restriction.

## Explained practice answers

### Exercise 1

Predict the ordinary unfiltered total in case A.

It is 187.

**Why it fits this model:** Case A has no role, so the North filter is the only restriction. Without it, every sales line is visible.

**Tempting mistake:** Assuming that because users normally see North, North is the unfiltered total. A report filter is a default view, not a limit.

**How to confirm:** EVALUATE ROW("Total", [NetRevenue]) with no filters returns 187, and REMOVEFILTERS(Customer) under North also returns 187.

### Exercise 2

Change the declared role to SouthViewer.

Expected revenue is 80, including after an ordinary Customer-filter removal.

**Why it fits this model:** SouthViewer allows only Bo (customer 20), whose lines are S3 (40), S6 (20) and S7 (20). RLS filters the rows before any measure runs.

**Tempting mistake:** Expecting REMOVEFILTERS(Customer) to return 187 as in case A. It removes filter context, not the role.

**How to confirm:** Under an enforced SouthViewer role, VisibleRevenue and AfterRemovingCustomerFilters both return 80.

### Exercise 3

Write a real RLS acceptance record template.

Record test identity/workspace role, model/role version, relationships, submitted query, expected allowed rows and actual observed result, including denial cases.

**Why it fits this model:** An acceptance record proves who ran what, under which role, and that disallowed rows stayed hidden.

**Tempting mistake:** Recording only "North shows 107". That does not show whether a South user is blocked from Ada's 51 and Cy's 56.

**How to confirm:** Each row lists identity, role, model version, query, expected rows and observed value, including denial cases: North 107, South 80, together 187.

### Exercise 4

Diagnose testing only as the workspace administrator.

Use the documented applicable role and identity; an unrestricted result cannot certify Viewer RLS behavior.

**Why it fits this model:** Workspace Admin, Member and Contributor roles are not restricted by RLS the way a Viewer is, so they see every row.

**Tempting mistake:** Signing off NorthViewer after an administrator saw 187 or applied a filter that returned 107. Neither result came from the role.

**How to confirm:** Test with a Viewer identity assigned to NorthViewer and expect 107, including after REMOVEFILTERS(Customer).

### Exercise 5

Explain why hidden report pages or disabled buttons are insufficient.

A real security boundary must constrain allowed data through the supported engine/service controls, not just the visible navigation.

**Why it fits this model:** Hiding a South page only changes navigation. The model still answers any query the user's permissions allow.

**Tempting mistake:** Considering South hidden because the page is gone, while the user can build a new query and read Bo's 80.

**How to confirm:** As the restricted user, run a query with REMOVEFILTERS(Customer); an enforced role returns 107, an unenforced one returns 187.

### Exercise 6

Transfer the distinction to a SQL dashboard WHERE clause.

A removable predicate does not protect data from another authorized query path; test actual role/permission boundaries separately.

**Why it fits this model:** A SQL dashboard's WHERE region = 'North' plays the same role as case A's ordinary filter: any other query can omit it.

**Tempting mistake:** Writing the predicate into every dashboard query and treating that as access control.

**How to confirm:** Connect as the restricted database login and run SELECT SUM(net) with no WHERE clause; enforced row security returns 107 instead of 187.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
