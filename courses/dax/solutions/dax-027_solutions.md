# dax-027: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-027_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A direct key projection retains its model identity

No outer filters; direct projection of the two Paper ProductKey values.

| CandidateRows | Revenue |
| --- | --- |
| 2 | 91 |

The result depends on the association with ProductKey, not on the output alias Key.

- The projected values are 1 and 2.
- The direct model-column projection retains ProductKey lineage.
- Using that table as a filter selects Paper sales and revenue 91.

### Case B: Restore an explicitly detached mapping

Expression-derived values {1,2}; compare a lineage-free table filter with an explicit target mapping.

| WithoutTarget | WithTarget |
| --- | --- |
| 187 | 91 |

This is why copying a virtual table's printed rows does not fully document a DAX expression. Record its originating columns or explicit target mapping.

- Adding zero preserves the numbers but changes the projected expression's lineage contract.
- Without a model target, that detached column does not select the Product rows for revenue.
- TREATAS maps the values to ProductKey, restoring the intended 91.

## Explained practice answers

### Exercise 1

Predict TREATAS({1,999},Product[ProductKey]) in the clean model.

Key 1 selects Notebook revenue 67; unmatched key 999 is ignored. This differs from the separate unknown-member model.

### Exercise 2

Rename the direct projected column without changing its expression.

A direct reference can retain lineage despite renaming; renaming alone is not the same as calculating a new expression.

### Exercise 3

Write a disconnected selection mapping for product keys 1 and 3.

CALCULATE([NetRevenue],TREATAS({1,3},Product[ProductKey])) selects Notebook and Mug, totaling 163.

### Exercise 4

Diagnose mapping a customer-code table to ProductKey because both are integers.

A numeric match would filter the wrong domain. The target column must represent the same entity or an explicitly defined mapping.

### Exercise 5

Explain a two-column TREATAS mapping.

Each input column maps to the corresponding target column; swapping year and month changes meaning or causes invalid matches.

### Exercise 6

Transfer lineage reasoning to an imported segment list.

Validate its key domain and duplicates, then define a physical relationship or an explicit virtual mapping, retaining unmatched-key diagnostics.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
