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

**Why it fits this model:** With only Notebook selected, ALLSELECTED(Product[Product]) gives the same single product, so the denominator is 67 and the share is 1.

**Tempting mistake:** Reading 1 as Notebook's share of all sales ignores the denominator; against all products Notebook is 67 / 187, about 0.358.

**How to confirm:** Expect a selected share of 1 and an all-product share of about 0.3583.

### Exercise 2

Select Notebook and Mug instead.

The selected total is 163 and their shares are 67/163 and 96/163.

**Why it fits this model:** ALLSELECTED restores the outer selection {Notebook, Mug}, so the denominator is 67 + 96 = 163. The shares are about 0.411 and 0.589.

**Tempting mistake:** Using REMOVEFILTERS here gives 187 and shares of about 0.358 and 0.513, which do not add to 1 across the visible rows.

**How to confirm:** Under the Notebook and Mug selection, SelectedTotal reads 163 on both rows and the shares add to 1.

### Exercise 3

Write a denominator specification for a chart with a year slicer.

State that product selection/grouping changes while the chosen year remains; then verify the exact query rather than inferring from the chart's appearance.

**Why it fits this model:** Say which filters stay: the year stays, and only the product grouping is widened. In 2025 Notebook is 47 (S4, S7) and Pen 20 (S5), so the selected total is 67.

**Tempting mistake:** Also removing the Date filter in the denominator uses all-years 91 and gives Notebook 47 / 91, about 0.516, comparing 2025 sales with a multiyear total.

**How to confirm:** Under 2025 and {Notebook, Pen}, expect a denominator of 67 and shares of about 0.701 and 0.299.

### Exercise 4

Diagnose calling ALLSELECTED inside an arbitrary nested SUMX.

The simple selected-total derivation no longer proves the nested expression. Trace that iterator or bind a deliberate denominator before it.

**Why it fits this model:** Case A works because ALLSELECTED runs where the outer selection is the only shadow context. Inside an iterator that sets its own filters, that simple account no longer applies.

**Tempting mistake:** Assuming a nested SUMX over VALUES(Product[Product]) still sees 91 at every step skips the trace, and the iterator's own context may change what ALLSELECTED restores.

**How to confirm:** Bind `VAR SelectedTotal = CALCULATE ( [NetRevenue], ALLSELECTED ( Product[Product] ) )` before the iterator, confirm it reads 91, then use it inside.

### Exercise 5

Explain whether rows hidden by a visual necessarily disappear from the denominator.

Not necessarily. State and inspect the actual grouping, filter and measure context instead of reasoning only from visible pixels.

**Why it fits this model:** What is visible and what is in the query are different. In case B only Notebook and Pen are visible, but REMOVEFILTERS widens the denominator to all products, 187.

**Tempting mistake:** Assuming the visible shares must add to 1 suggests a bug, but 0.358 + 0.128 is about 0.487 because Mug's 96 is in the denominator without being shown.

**How to confirm:** Add the denominator as a column. Case B reads 187 on both rows, which explains why the visible shares add to about 0.487.

### Exercise 6

Transfer the distinction to a selected cohort versus all assigned units.

Both selected-cohort and all-assignment rates can be meaningful, but the population and exclusion policy must be explicit and consistent.

**Why it fits this model:** Within the Treatment arm, 2 of 2 assigned units converted (1.0). Over all four assigned units, Treatment's conversions are 2 of 4 (0.5). Both are valid when named.

**Tempting mistake:** Labeling 0.5 as Treatment's conversion rate puts Control's units into its denominator and halves the reported effect.

**How to confirm:** ExperimentSummary shows Treatment Rate 1 and Control Rate 0.5, and the pooled rate is (1 + 2) / 4 = 0.75.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
