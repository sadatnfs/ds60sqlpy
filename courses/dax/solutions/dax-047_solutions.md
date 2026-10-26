# dax-047: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-047_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Unfiltered caller

No incoming filter; both calls receive the same written measure argument with different parameter modes.

| EagerValue | DeferredExpression |
| --- | --- |
| 187 | 163 |

Parameter annotations change observable behavior. They are not merely documentation for an otherwise identical function.

- VAL evaluates [NetRevenue] before the body and passes 187.
- Changing color around that scalar cannot recreate its original expression.
- EXPR evaluates the measure under Blue and returns 163.

### Case B: Red caller and a Blue-transforming function

Incoming Color=Red; the function body requests Color=Blue.

| EagerValue | DeferredExpression |
| --- | --- |
| 24 | 163 |

A function intended to stay inside the caller's population would need a different filter policy, such as an appropriate intersection, plus its own tests.

- The eager argument is evaluated in Red and becomes 24.
- The deferred argument is evaluated after the body's Color replacement.
- Its Blue result is 163, not a Red-and-Blue intersection.

## Explained practice answers

### Exercise 1

Predict the eager call when the caller selects Paper.

It receives 91. The deferred Blue expression retains Paper and returns 67.

### Exercise 2

Replace the body's plain Blue filter by KEEPFILTERS(Blue).

For a Red caller the deferred expression would be BLANK; the eager scalar would remain 24 because it was already computed.

### Exercise 3

Write documentation warning callers about context changes.

State that the EXPR function reevaluates its numeric argument under a Blue Color replacement while preserving unrelated filters.

### Exercise 4

Diagnose changing a VAL parameter to EXPR as a purely performance refactor.

It is a semantic change and requires result comparison across caller filters and row contexts.

### Exercise 5

Explain why this lesson does not validate an arbitrary row-context caller.

Deferred arguments have documented context-inheritance rules; add explicit iterator and reference-parameter cases before relying on another calling pattern.

### Exercise 6

Transfer the distinction to a reusable period-selection UDF.

Use an appropriately declared deferred expression/reference when period context must change, and document compatibility and evaluation scope.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
