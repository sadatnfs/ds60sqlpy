# dax-027: explained reference and practice reasoning

In the reference, compare the direct projection of Product[ProductKey] with the + 0 variant. Verify that 91, 187 and 91 follow from lineage alone, and that TREATAS names its target column explicitly. Read it beside the [reference source](dax-027_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

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

**Why it fits this model:** TREATAS applies only values that exist in the target column. Product has no key 999 in the clean model, so the filter keeps key 1 and returns Notebook's 67.

**Tempting mistake:** Reading 67 as proof that code 999 has no sales. TREATAS drops unmatched values silently, so a code with real facts and no Product row would vanish from this result too.

**How to confirm:** `CALCULATE ( [NetRevenue], TREATAS ( { 1, 999 }, Product[ProductKey] ) )` equals `CALCULATE ( [NetRevenue], Product[ProductKey] = 1 )`, 67.

### Exercise 2

Rename the direct projected column without changing its expression.

A direct reference can retain lineage despite renaming; renaming alone is not the same as calculating a new expression.

**Why it fits this model:** Lineage follows the expression, not the name. A direct reference to Product[ProductKey] renamed PaperKey still filters Product, so case A still returns 2 rows and 91.

**Tempting mistake:** Expecting the rename to behave like the `+ 0` projection and return 187. Only the arithmetic in case B creates new values without model lineage.

**How to confirm:** Rerun case A with the column renamed; CandidateRows stays 2 and Revenue stays 91.

### Exercise 3

Write a disconnected selection mapping for product keys 1 and 3.

CALCULATE([NetRevenue],TREATAS({1,3},Product[ProductKey])) selects Notebook and Mug, totaling 163.

**Why it fits this model:** A table constructor has no lineage, so TREATAS must name Product[ProductKey] as the target. Keys 1 and 3 are Notebook and Mug, 67 + 96 = 163.

**Tempting mistake:** Passing `{ 1, 3 }` straight to CALCULATE filters a column that is not in the model, as in case B's WithoutTarget, so the result is 187.

**How to confirm:** The TREATAS measure returns 163, which matches the Blue revenue because Notebook and Mug are the Blue products.

### Exercise 4

Diagnose mapping a customer-code table to ProductKey because both are integers.

A numeric match would filter the wrong domain. The target column must represent the same entity or an explicitly defined mapping.

**Why it fits this model:** The target must be the same entity. Customer codes 10 and 20 belong on Customer[CustomerKey], where they select Ada and Bo for 51 + 80 = 131.

**Tempting mistake:** Mapping them to Product[ProductKey] because both are integers finds no matching product and returns BLANK, which reads as no sales rather than a wrong domain. With overlapping numbers it would filter the wrong products.

**How to confirm:** TREATAS({10, 20}, Customer[CustomerKey]) gives 131 and TREATAS({10, 20}, Product[ProductKey]) gives BLANK.

### Exercise 5

Explain a two-column TREATAS mapping.

Each input column maps to the corresponding target column; swapping year and month changes meaning or causes invalid matches.

**Why it fits this model:** Columns map by position. `TREATAS ( { ( 2025, 1 ) }, 'Date'[Year], 'Date'[MonthNumber] )` filters January 2025, which is S4, S5 and S6, or 67.

**Tempting mistake:** Writing the tuple as (1, 2025) asks for year 1 and month 2025. Nothing matches, and the result is BLANK with no error.

**How to confirm:** (2025, 1) returns 67, (2025, 2) returns 56 and the swapped tuple returns BLANK.

### Exercise 6

Transfer lineage reasoning to an imported segment list.

Validate its key domain and duplicates, then define a physical relationship or an explicit virtual mapping, retaining unmatched-key diagnostics.

**Why it fits this model:** An imported list of keys has no relationship. Check its domain and duplicates, then map it with TREATAS. A list {20, 30, 50} selects Bo and Cy for 136 and leaves 50 unmatched.

**Tempting mistake:** Using the list directly as a CALCULATE filter has no lineage and returns 187, as DetachedKeys does in case B, so the segment silently becomes everyone.

**How to confirm:** The TREATAS measure returns 136, and `EXCEPT ( SegmentList, VALUES ( Customer[CustomerKey] ) )` returns the orphan 50 for the diagnostics column.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
