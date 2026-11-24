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

**Why it fits this model:** Home has one product, Mug, so the shared scalar 96 is added once. That matches the correct per-product sum by coincidence.

**Tempting mistake:** Passing this one-member test and shipping the formula is the mistake. Under Paper, with two products, the shared version returns 182, not 91.

**How to confirm:** Test both: Home gives 96 and 96, and Paper gives 182 and 91.

### Exercise 2

Add a second unsold product to the unfiltered model.

The incorrect sum rises to 5 * 187 = 935 while the per-product additive total remains 187.

**Why it fits this model:** The variable outside SUMX holds 187 and is added once per Product row. With a fifth row, an unsold product, the wrong sum becomes 5 x 187 = 935.

**Tempting mistake:** Expecting the extra product to do nothing applies the correct sum's behavior to the shared scalar. Only the per-product version ignores the blank row.

**How to confirm:** Today the results are 748 (4 x 187) and 187. After adding the product expect 935 and 187.

### Exercise 3

Write an iterator whose variable intentionally holds one global denominator.

Bind a deliberate total outside, then evaluate each member's [NetRevenue] inside and DIVIDE by that total.

**Why it fits this model:** Bind `VAR Total = [NetRevenue]` before SUMX, and evaluate [NetRevenue] inside the body for each product. The shares are Notebook 0.358, Pen 0.128, Mug 0.513 and Bag BLANK.

**Tempting mistake:** Binding the numerator outside too divides 187 by 187 on every row, and SUMX over the four products returns 4 rather than 1.

**How to confirm:** The shares should add to 1, and each share times 187 should give 67, 24 and 96.

### Exercise 4

Diagnose a refactor that moves all variables above SUMX for readability.

Move only expressions intended to be invariant. Keep row-dependent measure bindings in the iterator body.

**Why it fits this model:** Only values meant to stay constant belong above SUMX. The per-product [NetRevenue] must be bound inside the body, so that each product's transition happens there.

**Tempting mistake:** Moving ProductRevenue above SUMX makes the per-product column equal SharedScalarSum, 748 unfiltered and 182 under Paper.

**How to confirm:** After any refactor, rerun both cases and expect PerProductSum to stay 187 and 91.

### Exercise 5

Explain why the variables are not updated mutable loop counters.

Each inner evaluation binds its own value; there is no assignment that mutates one outer variable across iterations.

**Why it fits this model:** A VAR is a name for one value within its scope. Each iteration that defines ProductRevenue creates a new binding and changes nothing outside.

**Tempting mistake:** Writing `VAR Counter = 0` and expecting `Counter + 1` to number the products gives 1 on every row, so SUMX returns 4, not 1 + 2 + 3 + 4 = 10.

**How to confirm:** `SUMX ( Product, Counter + 1 )` returns 4, which shows that nothing accumulated.

### Exercise 6

Transfer the lesson to allocating a shared monthly target.

Keep the target and validated weight denominator shared, but compute each member's weight in the appropriate row/filter context.

**Why it fits this model:** Keep the target shared and compute each weight inside the iterator. In February 2025, Notebook has 20 and Mug 36, so an assumed 200 USD target splits as about 71.43 and 128.57.

**Tempting mistake:** Binding the weight [NetRevenue] outside the iterator gives every product a weight of 1, and the full 200 is allocated to each of four products, 800 in total.

**How to confirm:** The allocations should add to 200, with Pen and Bag BLANK because they had no February 2025 sales.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
