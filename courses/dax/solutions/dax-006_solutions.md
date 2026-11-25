# dax-006: explained reference and practice reasoning

The reference pairs a row count against a distinct-key count (3 against 2) with an EXCEPT that returns 999. Verify that your ledger cites each result as evidence for a different defect rather than one combined error. Read it beside the [reference source](dax-006_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: A duplicate-key diagnostic, not a loaded dimension

A query-local candidate table; it is not related to Sales.

| Rows | UniqueKeys |
| --- | --- |
| 3 | 2 |

This diagnostic explains why the intended dimension cannot be accepted as unique. Summing its labels or choosing the first row is not a principled repair.

- The candidate contains keys 1, 1 and 2.
- Projecting Key then taking DISTINCT leaves 1 and 2.
- Three rows and two keys prove the one-row-per-key contract fails.

### Case B: An unmatched fact key

Unknown-member model; no filters; S9 references absent ProductKey 999.

| ProductKey |
| --- |
| 999 |

An unmatched key is not the same as an absent fact. S9 still represents seven dollars of recorded activity, subject to the explicit unknown-member policy.

- Fact keys are 1, 2, 3 and 999.
- Stored Product keys are 1, 2, 3 and 4.
- The fact-minus-dimension set contains only 999.

## Explained practice answers

### Exercise 1

Reconcile all amounts after adding S9.

Known products contribute 187, unknown product 7, and the whole fact total is 194.

**Why it fits this model:** S9 is a real sale whose key 999 has no Product row. The regular relationship places it under the blank Product member, so known products still total 187 and the fact total becomes 194.

**Tempting mistake:** Filtering out the blank product, or trusting an inner join, and calling 187 the total. That hides Ada's seventh dollar of 2025 revenue.

**How to confirm:** ROW("Total", [NetRevenue]) returns 194, and CALCULATE ( [NetRevenue], Sales[ProductKey] = 999 ) returns 7.

### Exercise 2

Predict the missing-key result after adding a valid Product row for key 999.

EXCEPT would return an empty table. Descriptive attributes and uniqueness still need review.

**Why it fits this model:** Adding Product key 999 gives S9 a matching row, so EXCEPT has nothing left to return and the blank member disappears. The total stays 194; only the attribution changes.

**Tempting mistake:** Expecting the grand total to move when the member is added. The rows in Sales are the same, so only the label on 7 of revenue changes.

**How to confirm:** EXCEPT returns an empty table, COUNTROWS(Product) becomes 5, and the grand total still reads 194.

### Exercise 3

Write an issue ledger with type, evidence and disposition.

Record duplicate key 1 in the candidate as a uniqueness failure, and key 999 in Sales as unmatched membership; each needs a distinct upstream/model decision.

**Why it fits this model:** The two findings fail different contracts. The candidate table has 3 rows but 2 unique keys because key 1 carries two labels, while key 999 exists in Sales without any Product member.

**Tempting mistake:** Logging one generic data-quality issue and repairing it by removing duplicates from Sales. Neither problem is a duplicate fact row, so the ledger would close the wrong ticket.

**How to confirm:** The ledger has two rows: duplicate key 1 with evidence 3 rows and 2 unique keys, and unmatched key 999 on S9 with amount 7. Each row names a separate owner and decision.

### Exercise 4

Diagnose removing S9 solely to make category totals match.

That deletes recorded activity from the report rather than repairing its classification. Expose exclusions and reconcile the retained population.

**Why it fits this model:** Category totals cover only matched products, Paper 91 and Home 96, which is 187, while the fact total is 194. The 7 difference is a known, explainable population, not an error in the measure.

**Tempting mistake:** Deleting S9 so the categories reconcile. Ada's revenue then falls from 58 (S1, S2, S4 and S9) to 51, and the report no longer matches recorded sales.

**How to confirm:** Show an Unknown row worth 7 beside Paper and Home; the three rows add to 194 and Ada still totals 58.

### Exercise 5

Explain the role of ProductKey 4, which has no sales.

It is a valid unsold product, not an unmatched fact key or a duplicate dimension row.

**Why it fits this model:** Bag is the mirror image of S9: a dimension row with no fact rows, not a fact row with no dimension. EXCEPT in the other direction, from Product to Sales keys, returns 4.

**Tempting mistake:** Treating Bag as a data error and deleting it. That shrinks the catalog to three products and removes a legitimate zero-sales item from assortment reports.

**How to confirm:** Bag's [NetRevenue] is BLANK, COUNTROWS(Product) is 4, and DISTINCTCOUNT(Sales[ProductKey]) is also 4 here, but for keys 1, 2, 3 and 999.

### Exercise 6

Transfer the review to assignments and exposure events in an experiment.

Check assignment uniqueness and exposure foreign keys; repeated exposure events do not become extra independent randomized units.

**Why it fits this model:** Assignments hold the randomized units U1 to U4, one row each, while Exposures repeat U3 twice and never mention U4. The unit list is the identity table; exposures are events against it.

**Tempting mistake:** Counting exposure rows as units. That gives 4 exposures but only 3 exposed units, and it would count U3 twice in any per-unit rate.

**How to confirm:** COUNTROWS(Assignments) and DISTINCTCOUNT(Assignments[UnitID]) both return 4, DISTINCTCOUNT(Exposures[UnitID]) returns 3, and EXCEPT from exposure keys to assignment keys is empty.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
