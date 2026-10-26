# dax-025: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-025_reference.dax) and [named model](../models/unknown-member/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Stored keys versus semantic members

Unknown-member model; stored Product keys 1..4; Sales also has key 999.

| ValuesMembers | StoredDistinctKeys |
| --- | --- |
| 5 | 4 |

The unknown member can represent multiple unmatched keys. It does not tell you how many distinct bad source codes exist; inspect fact-minus-dimension keys for that diagnostic.

- DISTINCT sees the four stored Product keys.
- The unmatched regular relationship introduces one semantic blank member for VALUES.
- VALUES therefore has five members, not a new stored row with key 999.

### Case B: Reconcile the unknown amount

Unknown-member model; the first expression selects its semantic blank Product member.

| UnknownRevenue | AllRevenue |
| --- | --- |
| 7 | 194 |

An explicit unknown bucket preserves a useful data-quality signal. Replacing it with an invented valid product would conceal a modeling issue.

- S9 is the only unmatched product fact and contributes 7.
- Known-product facts still contribute 187.
- The full fact total is 194, including the unknown bucket.

## Explained practice answers

### Exercise 1

Predict these two counts in the clean retail model.

Both counts are four; that clean fixture alone cannot reveal the function difference.

### Exercise 2

Add a second unmatched source key with another fact.

VALUES still adds one blank member, while the unknown revenue grows by the new amount. A separate key-quality query must count the distinct unmatched codes.

### Exercise 3

Write the reconciliation equation for product reporting.

Known revenue 187 + unknown revenue 7 = all revenue 194.

### Exercise 4

Diagnose labeling VALUES(ProductKey) count as the number of sellable SKUs.

The count five includes the unknown bucket. Stored sellable-product policy needs its own catalog definition.

### Exercise 5

Explain why Bag is not the unknown member.

Key 4 is valid and unsold; the synthetic blank member represents facts lacking a valid product mapping.

### Exercise 6

Transfer this reconciliation to late-arriving dimensions.

Retain and report the unmatched population, then verify how reconciliation changes after the correct dimension member arrives.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
