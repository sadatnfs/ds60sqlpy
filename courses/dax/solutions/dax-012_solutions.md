# dax-012: explained reference and practice reasoning

In the reference, locate where each variable is bound relative to CALCULATETABLE and CALCULATE. The 187 and 163 pair should follow directly from those positions; renaming the variables would not change either value. Read it beside the [reference source](dax-012_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

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

**Why it fits this model:** The variable is bound once, with no filter, as 187. CALCULATE can change the filter around a scalar but cannot reevaluate it. Pen is the only Red product, so the direct measure returns 24.

**Tempting mistake:** Expecting FrozenInRed to show 24 treats the variable as a formula that reevaluates in its new context. VAR stores a value, not the expression.

**How to confirm:** The row should read FrozenInRed 187 and RecomputedInRed 24, the value of Pen's lines S2 and S5.

### Exercise 2

Move the variable binding inside the Blue calculation.

Binding [NetRevenue] inside Blue produces 163. Later uses still reuse that scalar.

**Why it fits this model:** Binding inside the Blue CALCULATETABLE evaluates [NetRevenue] under Blue, so the variable holds 163. Every later use reuses 163, even under another filter.

**Tempting mistake:** Binding the variable before CALCULATETABLE and expecting the outer Blue filter to reach it still returns 187, because the binding happened first.

**How to confirm:** Inside Blue the variable returns 163, the same as `CALCULATE ( [NetRevenue], Product[Color] = "Blue" )`.

### Exercise 3

Rewrite a filtered share with separately named numerator and denominator.

Bind numerator=[NetRevenue] and denominator=CALCULATE([NetRevenue],REMOVEFILTERS(Product[Color])), then DIVIDE(numerator, denominator).

**Why it fits this model:** Each variable is bound in its own context: the numerator under the current color, and the denominator after REMOVEFILTERS on Color. Under Blue that gives 163 / 187, about 0.872.

**Tempting mistake:** Binding the denominator to [NetRevenue] under Blue and wrapping it in CALCULATE with REMOVEFILTERS keeps 163, so the share becomes 1.0 for every color.

**How to confirm:** Under Blue the share returns about 0.872, under Red 24 / 187, about 0.128, and the two shares add to 1.

### Exercise 4

Diagnose a denominator that remains equal to the numerator after REMOVEFILTERS.

CALCULATE(FrozenRevenue,REMOVEFILTERS(...)) preserves the frozen value. Reevaluate the measure in the intended denominator context.

**Why it fits this model:** The denominator must reevaluate the measure, so it is CALCULATE([NetRevenue], REMOVEFILTERS(Product[Color])). That returns 187 under Blue and under Red alike.

**Tempting mistake:** Adding ALL or more CALCULATE layers around the frozen variable keeps 163 under Blue, because no wrapper can recompute a value that is already bound.

**How to confirm:** Show the denominator as its own column. It should read 187 on every color row; if it equals the numerator, it is still frozen.

### Exercise 5

Explain whether a variable defined before SUMX changes per row.

An outer scalar is shared. A variable declared in the iterator body can bind a different result for each row's context.

**Why it fits this model:** A variable defined before SUMX is one shared scalar, so `VAR Total = [NetRevenue]` holds 187 on every row. Each line divided by it gives a share, and the shares add to 1.

**Tempting mistake:** Calling [NetRevenue] inside the iterator causes context transition to each line. Each share then divides the line by itself, and the eight results add to 8.

**How to confirm:** `SUMX ( Sales, DIVIDE ( Sales[NetAmount], Total ) )` returns 1, while the in-row version returns 8.

### Exercise 6

Describe a debugging trace that exposes the bug without engine access.

Write a ledger with original filters, variable binding, later filters and reused versus reevaluated values; reconcile 187 and 163 from their fact rows.

**Why it fits this model:** A ledger records each step: the starting filter, the binding context, the value bound, the later filters and whether each use reuses or reevaluates. It can be checked against the fact rows.

**Tempting mistake:** Debugging from the final number alone cannot tell whether 187 came from a frozen variable or a missing filter, because both give the same output.

**How to confirm:** Blue is S1, S3, S4, S6, S7 and S8, which sum to 163; Red is S2 and S5, for 24; together they reconcile to 187.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
