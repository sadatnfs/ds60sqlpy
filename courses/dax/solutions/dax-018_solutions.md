# dax-018: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-018_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Products above fifty

No incoming filters; consider each visible ProductKey independently.

| Products | Revenue |
| --- | --- |
| 2 | 163 |

The threshold is applied to each product's measure result. A single comparison of the grand total would not perform this segmentation.

- Candidate revenues are Notebook 67, Pen 24, Mug 96 and Bag BLANK.
- Keys 1 and 3 exceed 50.
- Applying those retained keys yields 67 + 96 = 163.

### Case B: A stricter threshold

Same candidate population, threshold changed from 50 to 90.

| Products | Revenue |
| --- | --- |
| 1 | 96 |

Changing the threshold changes membership, not the source's definition of revenue. Keep both decisions visible in a segmentation specification.

- Notebook no longer qualifies because 67 is not greater than 90.
- Mug's 96 still qualifies.
- The retained one-key table filters the final measure to 96.

## Explained practice answers

### Exercise 1

Predict the retained products at threshold 24 using >.

Notebook and Mug qualify; Pen at exactly 24 does not.

### Exercise 2

Change > 24 to >= 24.

Pen is added, so three products qualify and their revenue is 187.

### Exercise 3

Write a selection for customers with revenue above 55.

Bo at 80 and Cy at 56 qualify; Ada at 51 and Di at BLANK do not. Their total is 136.

### Exercise 4

Diagnose CALCULATE([NetRevenue], [NetRevenue] > 50).

Use FILTER over a deliberate candidate table so the measure has a per-candidate evaluation context.

### Exercise 5

Predict a threshold above every product's revenue.

No product qualifies. COUNTROWS(Qualifying) and the final SUM result are BLANK in this case.

### Exercise 6

Transfer the pattern to dynamic customer segments.

A segment based on current-period revenue must state its period and whether unsold or previously filtered customers are eligible candidates.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
