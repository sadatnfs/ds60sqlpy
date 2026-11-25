# dax-017: explained reference and practice reasoning

Check that the reference's two SUMX expressions differ only by CALCULATE, and that the customer case invokes the model measure directly. Your draft should reconcile 187 from both routes and explain why 1,496 is not a rounding issue. Read it beside the [reference source](dax-017_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Eight repetitions versus eight individual amounts

No outer filters; SUMX creates one Sales row context per unique SaleID.

| RawRepeated | Transitioned |
| --- | --- |
| 1496 | 187 |

The two formulas differ in context semantics, not numeric precision. Dividing the wrong result by eight would hide the mistake and fail under another population.

- Without transition, the inner SUM is 187 for every row.
- Eight iterations give 8 * 187 = 1496.
- With transition, the eight selected line amounts sum once each to 187.

### Case B: Measure invocation transitions each customer

No outer filters; a model measure is invoked within each Customer row context.

| CustomerRows | SumOfCustomerRevenue |
| --- | --- |
| 4 | 187 |

This additive reconciliation works because each sale has exactly one valid customer in this fixture. It is not a general theorem that summing any measure over any dimension equals its total.

- Ada contributes 51, Bo 80 and Cy 56.
- Di has no matching sales and contributes BLANK.
- 51 + 80 + 56 = 187.

## Explained practice answers

### Exercise 1

Predict the raw repeated formula for Paper's five lines.

It repeats 91 five times, producing 455; the transitioned sum is 91.

**Why it fits this model:** Under Paper, SUMX visits five lines. A raw SUM inside sees the whole Paper context each time and returns 91, so the result is 5 x 91 = 455.

**Tempting mistake:** Thinking the raw SUM sees only the current line, as a SQL row expression would, predicts 91. The transition is what makes that true.

**How to confirm:** Under Paper, RawRepeated returns 455 and Transitioned returns 91.

### Exercise 2

Replace the transitioned inner SUM with [NetRevenue].

The result stays 187 for unique Sales rows in this context.

**Why it fits this model:** [NetRevenue] includes an implicit CALCULATE, so each line becomes a filter on its own unique SaleID and contributes only its NetAmount. The total stays 187.

**Tempting mistake:** Expecting the measure to act like the raw SUM and return 1,496 forgets that measure references always transition.

**How to confirm:** `SUMX ( Sales, [NetRevenue] )` returns 187, while the raw version returns 1,496, which is 8 x 187.

### Exercise 3

Write the simplest formula for this additive revenue total.

SUM(Sales[NetAmount]) directly expresses the total without a per-row context transition.

**Why it fits this model:** NetAmount is stored per line and adds up across lines, so SUM(Sales[NetAmount]) gives 187 with no iterator and no transitions.

**Tempting mistake:** Keeping SUMX(Sales, [NetRevenue]) runs eight transitions to get the same 187, and it would overcount if two rows were identical (see the fifth exercise).

**How to confirm:** SUM(Sales[NetAmount]) and SUMX(Sales, Sales[NetAmount]) both return 187.

### Exercise 4

Diagnose fixing RawRepeated by dividing by COUNTROWS(Sales).

It does not express the intended measure and can hide other context or blank issues. Correct the expression instead.

**Why it fits this model:** Dividing by the row count happens to work here, because the raw SUMX adds the total once per row. It does not give per-row values.

**Tempting mistake:** Applied to a Customer iteration, the patch still shows 187 for each customer, and SUMX(Customer, SUM(Sales[NetAmount])) / COUNTROWS(Sales) returns 748 / 8 = 93.5.

**How to confirm:** Per customer, [NetRevenue] returns Ada 51, Bo 80, Cy 56 and Di BLANK; the patched expression cannot produce those.

### Exercise 5

Explain the risk of two completely identical fact rows without a unique key.

Both rows can match the transition on each iteration, so an inner aggregation can count both repeatedly.

**Why it fits this model:** A transition filters on every column's value, not on a physical row. SaleID is unique today, so each line matches only itself.

**Tempting mistake:** If S5 were loaded twice with identical values, SUM would give 207, but SUMX(Sales, [NetRevenue]) would give 247, because each copy matches both copies (40 twice).

**How to confirm:** Before relying on transitions, check that COUNTROWS(Sales) equals DISTINCTCOUNT(Sales[SaleID]); both are 8 here.

### Exercise 6

Transfer the reasoning to a per-customer cost allocation.

Define the allocation grain and denominator, then transition only where the measure should be evaluated for each customer or line.

**Why it fits this model:** To split a 100 USD charge by revenue, transition each customer with [NetRevenue] and divide by 187 bound outside the iterator: Ada gets about 27.27, Bo 42.78 and Cy 29.95.

**Tempting mistake:** A raw SUM inside SUMX(Customer, ...) gives every customer a share of 187 / 187 = 1, which allocates the full 100 to each of four customers.

**How to confirm:** The allocations should add to 100, and Di, with no sales, should receive BLANK.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
