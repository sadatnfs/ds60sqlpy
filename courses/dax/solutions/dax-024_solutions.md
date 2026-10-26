# dax-024: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-024_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Share of the selected product set

Outer selection {Notebook, Pen}; query groups by Product.Product; no nested iterator in the measure.

| Product | Revenue | SelectedTotal | Share |
| --- | --- | --- | --- |
| Notebook | 67 | 91 | 0.7362637363 |
| Pen | 24 | 91 | 0.2637362637 |

The sum of the two shares is one because the displayed groups partition this selected population. That conclusion depends on this exact denominator and query shape.

- The outer selected population totals 67 + 24 = 91.
- Each product group supplies its own numerator.
- ALLSELECTED removes this grouping restriction while preserving the named outer selection.

### Case B: Share of all products instead

Same selected rows; the denominator removes the Product.Product restriction entirely.

| Product | Revenue | AllProductTotal | Share |
| --- | --- | --- | --- |
| Notebook | 67 | 187 | 0.3582887701 |
| Pen | 24 | 187 | 0.128342246 |

This can be exactly the intended comparison to the full catalog. A chart should label the denominator so a partial sum is not mistaken for an error.

- The visible numerators remain 67 and 24.
- The denominator includes Mug's 96 as well, totaling 187.
- The selected rows' shares sum to 91/187, not one.

## Explained practice answers

### Exercise 1

Predict selected shares when only Notebook is selected.

Notebook's selected share is 1; its all-product share remains 67/187 in the stated otherwise-unfiltered context.

### Exercise 2

Select Notebook and Mug instead.

The selected total is 163 and their shares are 67/163 and 96/163.

### Exercise 3

Write a denominator specification for a chart with a year slicer.

State that product selection/grouping changes while the chosen year remains; then verify the exact query rather than inferring from the chart's appearance.

### Exercise 4

Diagnose calling ALLSELECTED inside an arbitrary nested SUMX.

The simple selected-total derivation no longer proves the nested expression. Trace that iterator or bind a deliberate denominator before it.

### Exercise 5

Explain whether rows hidden by a visual necessarily disappear from the denominator.

Not necessarily. State and inspect the actual grouping, filter and measure context instead of reasoning only from visible pixels.

### Exercise 6

Transfer the distinction to a selected cohort versus all assigned units.

Both selected-cohort and all-assignment rates can be meaningful, but the population and exclusion policy must be explicit and consistent.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
