# dax-006: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-006_reference.dax) and [named model](../models/unknown-member/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

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

### Exercise 2

Predict the missing-key result after adding a valid Product row for key 999.

EXCEPT would return an empty table. Descriptive attributes and uniqueness still need review.

### Exercise 3

Write an issue ledger with type, evidence and disposition.

Record duplicate key 1 in the candidate as a uniqueness failure, and key 999 in Sales as unmatched membership; each needs a distinct upstream/model decision.

### Exercise 4

Diagnose removing S9 solely to make category totals match.

That deletes recorded activity from the report rather than repairing its classification. Expose exclusions and reconcile the retained population.

### Exercise 5

Explain the role of ProductKey 4, which has no sales.

It is a valid unsold product, not an unmatched fact key or a duplicate dimension row.

### Exercise 6

Transfer the review to assignments and exposure events in an experiment.

Check assignment uniqueness and exposure foreign keys; repeated exposure events do not become extra independent randomized units.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
