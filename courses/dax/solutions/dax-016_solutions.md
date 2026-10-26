# dax-016: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-016_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Sibling filters use the incoming key maximum

Incoming Product.Category = Paper; sibling Color and ProductKey filters.

| IncomingMaxKey | Revenue |
| --- | --- |
| 2 | BLANK |

BLANK is the coherent answer to those combined constraints. It is not evidence that MAX or the relationship failed.

- Paper's incoming keys are 1 and 2; MAX is 2.
- Blue and ProductKey 2 are then applied together with the retained category.
- Pen is key 2 but Red, so the resulting product set is empty.

### Case B: Nested context before computing the key

Paper first; outer CALCULATE applies Blue before the inner key expression is evaluated.

| Revenue |
| --- |
| 67 |

The formulas answer differently sequenced questions. Do not call them interchangeable rewrites merely because they mention the same functions and columns.

- Paper plus Blue leaves ProductKey 1.
- The inner MAX therefore evaluates to 1.
- Notebook revenue is 67.

## Explained practice answers

### Exercise 1

Predict case A with Color = Red.

Red and key 2 agree, so revenue is 24.

### Exercise 2

Predict case B with Color = Red.

The inner maximum is 2 and revenue is 24; this fixture would hide the sequencing difference if only Red were tested.

### Exercise 3

Write a context ledger for each sibling expression.

Start Paper {1,2}; bind maximum 2; form Blue; combine key 2 with Blue; identify the empty intersection.

### Exercise 4

Diagnose testing only the Red variant and declaring equivalence.

Blue distinguishes the two evaluation orders, returning BLANK versus 67.

### Exercise 5

Explain why a variable bound before the outer modifier can reintroduce the bug.

Capturing max key 2 before Blue preserves 2 even inside the nested calculation.

### Exercise 6

Transfer the principle to selecting the last eligible period.

Define the population whose maximum period is needed, then evaluate the maximum in that context. Do not assume sibling arguments form a procedural pipeline.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
