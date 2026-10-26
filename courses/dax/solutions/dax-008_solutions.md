# dax-008: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-008_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Blank coercion is operator-specific

Literal BLANK operations; no model context.

| LooseZero | StrictZero | PlusFive | TimesFive |
| --- | --- | --- | --- |
| TRUE | FALSE | 5 | BLANK |

A predicate written with = 0 may include missing results that the author intended to exclude. Test the intended missingness condition explicitly.

- Ordinary numeric equality coerces BLANK for the comparison with zero.
- Strict equality does not identify BLANK with numeric zero.
- Addition and multiplication have different blank behavior: 5 versus BLANK.

### Case B: An existing product with no sales

ProductKey 4, Bag; no matching Sales rows.

| Products | SalesRows | Revenue | DisplayRevenue |
| --- | --- | --- | --- |
| 1 | BLANK | BLANK | 0 |

A zero-filled display can be appropriate if unsold products are in scope. Retain a separate eligibility or availability signal when zero could otherwise mean an observed failure.

- One dimension member remains.
- The related fact table is empty, so COUNTROWS and SUM return BLANK.
- COALESCE deliberately displays zero while the original measure remains blank.

## Explained practice answers

### Exercise 1

Predict ISBLANK(0) and ISBLANK(BLANK()).

They are FALSE and TRUE.

### Exercise 2

Replace the Bag filter with Pen.

Products is 1, SalesRows is 2 and Revenue/DisplayRevenue are both 24.

### Exercise 3

Write a label distinguishing no sales from positive revenue.

IF(ISBLANK([NetRevenue]),"No matching sales","Revenue observed") avoids treating an empty result as an observed zero.

### Exercise 4

Diagnose a report claiming every blank retention cell is a lost customer.

Missing observation time is different from observed inactivity. Do not coalesce the future into failures.

### Exercise 5

Explain why an empty table differs from one row containing BLANK.

An empty table has no row; a one-row table can carry a blank cell. Their membership and joins can differ.

### Exercise 6

Transfer the policy to missing cost data.

Preserve missing cost as a quality issue or exclude/report it explicitly before calculating margins.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
