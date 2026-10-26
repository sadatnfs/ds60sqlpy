# dax-049: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-049_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Fact-column cardinalities

Clean retail fact; no filters; counts describe source cardinality, not physical scan metrics.

| SalesRows | ProductKeys | OrderDates | SaleIDs |
| --- | --- | --- | --- |
| 8 | 3 | 7 | 8 |

A unique identifier has high cardinality here because it preserves necessary line identity. Its cost must be weighed against correctness and lineage requirements.

- There are eight unique sale lines.
- Three product keys repeat across them, and S1/S2 share one order date.
- Distinct counts are 3 products,7 order dates and 8 SaleIDs.

### Case B: Dimension attributes have another grain

Product dimension, including the unsold Bag member.

| ProductRows | Categories | Colors |
| --- | --- | --- |
| 4 | 3 | 3 |

A dimension count is not inferred from fact activity. Removing unsold members to shrink a model can change the intended reporting population.

- Four product rows describe four catalog keys.
- Categories are Paper,Home,Travel and colors are Blue,Red,Green.
- The dimension's domain includes valid attributes absent from current sales.

## Explained practice answers

### Exercise 1

Predict SaleID cardinality after adding one valid new line.

Row count and distinct SaleID count both increase by one; other column cardinalities depend on the new values.

### Exercise 2

Replace a long descriptive fact label with a dimension key conceptually.

The logical model can avoid repeated descriptive values, but actual storage savings require measurement rather than a fixed claimed ratio.

### Exercise 3

Write a performance-claim checklist.

Record model/source identity, storage mode, representative filters, result parity, engine/version, hardware, cache state and repeated observed timings.

### Exercise 4

Diagnose saying SUMX is always slow and SUM is always fast.

Use the simplest correct expression, inspect actual engine work and measure the intended workload; do not infer universal speed from a function name.

### Exercise 5

Explain why deleting SaleID can be a correctness regression.

A storage change must preserve the business grain and required diagnostics, not merely reduce a distinct-count statistic.

### Exercise 6

Transfer cardinality reasoning to timestamps.

Choose the temporal grain from the measurement requirement, then consider model design and encoding rather than arbitrarily truncating events.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
