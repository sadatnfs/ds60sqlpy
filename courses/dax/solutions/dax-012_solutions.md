# dax-012: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-012_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Binding before a new filter

Start unfiltered; bind the variable before introducing Blue.

| FrozenInBlue | RecomputedInBlue |
| --- | --- |
| 187 | 163 |

The wrong result is not repaired by renaming the variable. Its defining location or the expression passed to CALCULATE must change.

- The variable binds NetRevenue in the original all-row context: 187.
- CALCULATE around that scalar cannot recreate its earlier measure expression.
- The direct measure reference is evaluated with Blue and returns 163.

### Case B: Binding inside Blue before removing it

The outer CALCULATETABLE supplies Blue before the variable is bound.

| FrozenWithoutColor | RecomputedWithoutColor |
| --- | --- |
| 163 | 187 |

Variables and filter modifiers are both predictable when the sequence is explicit. Do not infer that a variable called Total always means an unfiltered grand total.

- Blue makes NetRevenue 163 at variable binding time.
- Removing the color filter around the scalar still returns 163.
- Removing color before evaluating the measure restores the full revenue 187.

## Explained practice answers

### Exercise 1

Predict the first case when the added color is Red.

FrozenInRed remains 187; the direct measure under Red returns 24.

### Exercise 2

Move the variable binding inside the Blue calculation.

Binding [NetRevenue] inside Blue produces 163. Later uses still reuse that scalar.

### Exercise 3

Rewrite a filtered share with separately named numerator and denominator.

Bind numerator=[NetRevenue] and denominator=CALCULATE([NetRevenue],REMOVEFILTERS(Product[Color])), then DIVIDE(numerator,denominator).

### Exercise 4

Diagnose a denominator that remains equal to the numerator after REMOVEFILTERS.

CALCULATE(FrozenRevenue,REMOVEFILTERS(...)) preserves the frozen value. Reevaluate the measure in the intended denominator context.

### Exercise 5

Explain whether a variable defined before SUMX changes per row.

An outer scalar is shared. A variable declared in the iterator body can bind a different result for each row's context.

### Exercise 6

Describe a debugging trace that exposes the bug without engine access.

Write a ledger with original filters, variable binding, later filters and reused versus reevaluated values; reconcile 187 and 163 from their fact rows.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
