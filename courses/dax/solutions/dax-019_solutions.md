# dax-019: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-019_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A disjoint subgroup stays empty

Original allowed color {Blue}; compare replacement with intersection by {Red}.

| ForcedRed | RedWithinSelection |
| --- | --- |
| 24 | BLANK |

An intersection measure should not escape its selected population to manufacture a nonblank result.

- Replacement changes the allowed set to Red and admits Pen.
- Intersection computes {Blue} intersect {Red}, an empty set.
- ForcedRed is 24; the selected-subgroup result is BLANK.

### Case B: An overlapping subgroup is retained

Original allowed colors {Blue, Red}; restrict to Blue without expanding selection.

| SelectedRevenue | BlueWithinSelection |
| --- | --- |
| 187 | 163 |

KEEPFILTERS does not freeze the original total. It can narrow a population while preserving the fact that the starting selection is an outer constraint.

- All products with recorded sales are Blue or Red, totaling 187.
- Intersecting with Blue removes Pen's 24.
- Notebook and Mug remain and total 163.

## Explained practice answers

### Exercise 1

Predict BlueWithinSelection if only Red is selected.

It is BLANK because {Red} and {Blue} do not overlap.

### Exercise 2

Replace the new subgroup by Color IN {Blue, Green}.

The intersection is Blue; Green does not get added. Revenue remains 163.

### Exercise 3

Write a selected-subgroup measure for Trade customers.

CALCULATE([NetRevenue],KEEPFILTERS(Customer[Segment]="Trade")) retains only selected Trade customers.

### Exercise 4

Diagnose changing KEEPFILTERS to a plain filter because blanks look untidy.

A disjoint selection would be replaced rather than respected. Decide the intended metric before changing its appearance.

### Exercise 5

Explain whether KEEPFILTERS restores a removed earlier filter.

It does not remember arbitrary historical selections or undo unrelated filter-removal operations.

### Exercise 6

Transfer the policy to a quality metric for failed events.

Intersect a failure subgroup with the selected cohort when reporting failures among that population; label any intentionally global failure metric separately.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
