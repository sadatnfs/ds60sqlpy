# dax-022: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-022_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: One shared total versus one value per product

No outer filters; four Product rows, including unsold Bag.

| SharedScalarSum | PerProductSum |
| --- | --- |
| 748 | 187 |

The shared value is not blank for Bag because it was never evaluated for Bag. Variable movement can therefore change both population and missing-value behavior.

- IncomingRevenue is bound once to 187.
- The shared scalar contributes 187 on four iterations, totaling 748.
- The inner measure binding transitions each product and sums 67 + 24 + 96 = 187.

### Case B: An incoming filtered total is still shared

Paper is established before either variable binding; Product has two eligible rows.

| SharedScalarSum | PerProductSum |
| --- | --- |
| 182 | 91 |

Context is not simply filtered versus unfiltered. The exact point at which a scalar is bound determines which filtered total gets repeated.

- The incoming measure total is 91.
- An outer scalar is reused for Notebook and Pen, giving 182.
- Binding inside the iterator evaluates 67 and 24 separately, totaling 91.

## Explained practice answers

### Exercise 1

Predict the shared-scalar sum under Home.

It is 96, coincidentally equal to the correct result. A one-member test hides the bug.

### Exercise 2

Add a second unsold product to the unfiltered model.

The incorrect sum rises to 5 * 187 = 935 while the per-product additive total remains 187.

### Exercise 3

Write an iterator whose variable intentionally holds one global denominator.

Bind a deliberate total outside, then evaluate each member's [NetRevenue] inside and DIVIDE by that total.

### Exercise 4

Diagnose a refactor that moves all variables above SUMX for readability.

Move only expressions intended to be invariant. Keep row-dependent measure bindings in the iterator body.

### Exercise 5

Explain why the variables are not updated mutable loop counters.

Each inner evaluation binds its own value; there is no assignment that mutates one outer variable across iterations.

### Exercise 6

Transfer the lesson to allocating a shared monthly target.

Keep the target and validated weight denominator shared, but compute each member's weight in the appropriate row/filter context.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
