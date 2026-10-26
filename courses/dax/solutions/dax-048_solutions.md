# dax-048: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-048_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Ascending month snapshot

A supplied flat visual snapshot in ascending month order; arithmetic expansion only.

| Position | Month | Revenue | RunningRevenue |
| --- | --- | --- | --- |
| 1 | January2025 | 67 | 67 |
| 2 | February2025 | 56 | 123 |

The snapshot values are already monthly aggregates. Reaching back to individual Sales rows would change the scope and require model-level logic.

- The first position contains January revenue 67.
- The second position includes 67 plus February 56.
- Running values are 67 and 123.

### Case B: Reversed visual order

The same monthly values in descending month order; no change to their underlying amounts.

| Position | Month | Revenue | RunningRevenue |
| --- | --- | --- | --- |
| 1 | February2025 | 56 | 56 |
| 2 | January2025 | 67 | 123 |

A cumulative-looking line can therefore change meaning when sort order changes. State its axis and ordering contract in the report.

- February 56 is now the first visible position.
- January 67 is added at the second position.
- The intermediate running value changes from 67 to 56 while the final sum remains 123.

## Explained practice answers

### Exercise 1

Predict the running result if the visual includes only February.

The running value is 56, not all-year 123, unless another explicit semantic-model measure supplies a different value.

### Exercise 2

Add a third observed month with revenue 10 at the end.

The running values become 67,123,133 for that expanded snapshot.

### Exercise 3

Write the intended visual expression and its scope contract.

RUNNINGSUM([Revenue]) on a flat monthly visual, ascending calendar order, with a stated reset policy and the required Revenue field present.

### Exercise 4

Diagnose using USERELATIONSHIP inside this visual calculation.

Move the date-role calculation into a semantic-model measure, then place that measure's results in the visual.

### Exercise 5

Explain why a hierarchical subtotal requires additional review.

Specify axis, partition and reset semantics; the flat two-row expansion does not prove hierarchical behavior.

### Exercise 6

Transfer the distinction to a report-specific moving average.

Use it only when the visual grain and order match the intended metric; retain reusable model measures for cross-report semantics.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
