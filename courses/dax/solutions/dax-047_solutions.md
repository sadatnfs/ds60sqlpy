# dax-047: explained reference and practice reasoning

Verify that the two reference functions share a body and differ only in VAL versus EXPR, giving 187 and 163, then 24 and 163. Read it beside the [reference source](dax-047_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

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

**Why it fits this model:** A VAL parameter is computed in the caller's context before the body runs. Under Paper that value is 91. The EXPR version is evaluated inside CALCULATE, which replaces the Color filter with Blue and keeps Category Paper.

**Tempting mistake:** Expecting the deferred call to return 163 as in case A. The Paper filter is still there, so only Notebook is Blue and Paper.

**How to confirm:** Under Product[Category] = "Paper", EagerValue is 91 and DeferredExpression 67.

### Exercise 2

Replace the body's plain Blue filter by KEEPFILTERS(Blue).

For a Red caller the deferred expression would be BLANK; the eager scalar would remain 24 because it was already computed.

**Why it fits this model:** KEEPFILTERS intersects Blue with the caller's filters instead of replacing them. For a Red caller, Red and Blue have nothing in common.

**Tempting mistake:** Assuming KEEPFILTERS also affects the VAL function. Its argument, 24, was already computed before the body ran.

**How to confirm:** Under Color = "Red", the KEEPFILTERS EXPR version returns BLANK and the VAL version still returns 24.

### Exercise 3

Write documentation warning callers about context changes.

State that the EXPR function reevaluates its numeric argument under a Blue Color replacement while preserving unrelated filters.

**Why it fits this model:** The documentation should say that BlueExpression re-evaluates its argument with Product[Color] replaced by Blue and other Product filters kept.

**Tempting mistake:** Documenting it as "returns Blue revenue". A Paper caller gets 67, not 163, which surprises anyone who read the short label.

**How to confirm:** Run the documented examples: no filter 163, Red caller 163, Paper caller 67.

### Exercise 4

Diagnose changing a VAL parameter to EXPR as a purely performance refactor.

It is a semantic change and requires result comparison across caller filters and row contexts.

**Why it fits this model:** Changing VAL to EXPR changes meaning. The same written call is evaluated in the function's context instead of the caller's.

**Tempting mistake:** Treating the change as a performance refactor. For a Red caller the result moves from 24 to 163.

**How to confirm:** Compare both modes across callers before shipping: unfiltered 187 versus 163, Red 24 versus 163, Paper 91 versus 67.

### Exercise 5

Explain why this lesson does not validate an arbitrary row-context caller.

Deferred arguments have documented context-inheritance rules; add explicit iterator and reference-parameter cases before relying on another calling pattern.

**Why it fits this model:** Both cases use filter context only. With a row context, for example inside ADDCOLUMNS over Product names, the argument picks up each row through context transition, which these cases do not cover.

**Tempting mistake:** Concluding from cases A and B that BlueExpression behaves the same inside any iterator.

**How to confirm:** Add an iterator case, such as ADDCOLUMNS(VALUES(Product[ProductName]), ...), with expected values for each product before relying on it.

### Exercise 6

Transfer the distinction to a reusable period-selection UDF.

Use an appropriately declared deferred expression/reference when period context must change, and document compatibility and evaluation scope.

**Why it fits this model:** Shifting periods needs the deferred form, because a VAL argument arrives as one number. Under January 2025 that number is 67 and cannot be moved to January 2024.

**Tempting mistake:** Declaring the measure parameter as VAL in a prior-period UDF. `CALCULATE ( amount, SAMEPERIODLASTYEAR ( 'Date'[Date] ) )` in the body still returns 67.

**How to confirm:** With an EXPR argument, the function returns 64 under January 2025, the January 2024 value.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
