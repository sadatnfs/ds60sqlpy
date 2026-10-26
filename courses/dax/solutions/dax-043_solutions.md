# dax-043: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-043_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Whole-model profit graph

Clean retail model; current UnitCost is explicitly constant per product; all amounts USD.

| Revenue | Cost | Profit | Margin |
| --- | --- | --- | --- |
| 187 | 44 | 143 | 0.7647058824 |

The margin is a numeric ratio, not the text produced by a percent formatter. Its meaning would change if costs and revenues used different filters.

- Line costs are 4,1,10,6,4,5,4,10, totaling 44.
- Profit is 187 -44 =143.
- Margin is 143/187, evaluated from the same all-row population.

### Case B: The same family under Blue

Blue products only; the same measure definitions and cost assumptions.

| Revenue | Cost | Profit | Margin |
| --- | --- | --- | --- |
| 163 | 39 | 124 | 0.7607361963 |

A reusable definition remains context-dependent. Reuse should preserve a formula's policy while allowing the question's population to change.

- Notebook cost is 14 and Mug cost is 25, totaling 39.
- Blue revenue 163 minus 39 gives profit 124.
- The filtered margin is 124/163, not the unfiltered 143/187.

## Explained practice answers

### Exercise 1

Predict Pen profit.

Profit is 19 and margin is 19/24.

### Exercise 2

Change UnitCost for Notebook to 3 in a hypothetical refreshed model.

Notebook cost rises from 14 to 21 and total profit falls by 7. This illustrates why overwriting a current cost can change historical reports.

### Exercise 3

Draw the dependency graph and annotate units.

NetRevenue USD and Cost USD feed Profit USD; Profit/NetRevenue gives a dimensionless margin.

### Exercise 4

Diagnose FORMAT([NetMargin],"0.0%") being reused in arithmetic.

Keep NetMargin numeric and apply display formatting separately; arithmetic should depend on the numeric measure.

### Exercise 5

Explain a zero or missing revenue denominator.

DIVIDE returns BLANK for an invalid denominator unless a separate explicit policy is chosen.

### Exercise 6

Transfer the graph to an adjusted revenue family.

Define each adjustment once, document its sign and population, then compose the final metric with an auditable dependency graph.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
