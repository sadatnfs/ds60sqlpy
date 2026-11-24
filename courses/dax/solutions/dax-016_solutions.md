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

**Why it fits this model:** MAX(Product[ProductKey]) is evaluated in the incoming Paper context, so it returns 2. Red with key 2 leaves Pen, whose revenue is 24.

**Tempting mistake:** Taking 24 as proof that the filters ran from left to right overlooks that Pen is both the incoming maximum and the only Red Paper product.

**How to confirm:** The row reads IncomingMaxKey 2 and Revenue 24, from S2 (4) and S5 (20).

### Exercise 2

Predict case B with Color = Red.

The inner maximum is 2 and revenue is 24; this fixture would hide the sequencing difference if only Red were tested.

**Why it fits this model:** The outer Red filter is applied first, so the inner MAX sees only Pen and returns 2. Revenue is 24, the same as case A with Red.

**Tempting mistake:** Assuming the outer Red replaces Paper confuses the columns. Color and Category differ, so Paper stays, though here both readings happen to give Pen.

**How to confirm:** Inside the outer Red context COUNTROWS(Product) is 1 and MAX(Product[ProductKey]) is 2, so revenue is 24.

### Exercise 3

Write a context ledger for each sibling expression.

Start Paper {1,2}; bind maximum 2; form Blue; combine key 2 with Blue; identify the empty intersection.

**Why it fits this model:** Ledger: Paper gives keys {1, 2}; MAX bound there is 2; Blue gives {1, 3}; key 2 gives {2}. Their intersection with Paper is empty.

**Tempting mistake:** A ledger written in argument order, applying Blue before computing MAX, binds key 1 and predicts Notebook's 67, which is case B's answer, not case A's.

**How to confirm:** Case A returns IncomingMaxKey 2 and Revenue BLANK, which matches the empty intersection.

### Exercise 4

Diagnose testing only the Red variant and declaring equivalence.

Blue distinguishes the two evaluation orders, returning BLANK versus 67.

**Why it fits this model:** Red returns 24 under both forms, so it cannot show which order is used. Blue can: the incoming maximum stays 2 in case A, while the nested inner MAX sees {1} in case B.

**Tempting mistake:** Declaring the forms equivalent after one passing Red test treats agreement on one input as proof for all inputs.

**How to confirm:** Run both forms with Blue and expect BLANK for case A and 67 for case B.

### Exercise 5

Explain why a variable bound before the outer modifier can reintroduce the bug.

Capturing max key 2 before Blue preserves 2 even inside the nested calculation.

**Why it fits this model:** A variable is evaluated where it is defined. `VAR K = MAX ( Product[ProductKey] )` under Paper binds 2 before the outer Blue filter exists.

**Tempting mistake:** Moving the MAX into a variable to tidy case B brings back the bug, because the inner filter then uses the stored 2 rather than the key under Blue.

**How to confirm:** The variable version returns BLANK under Paper, while the nested form with MAX inline returns 67.

### Exercise 6

Transfer the principle to selecting the last eligible period.

Define the population whose maximum period is needed, then evaluate the maximum in that context. Do not assume sibling arguments form a procedural pipeline.

**Why it fits this model:** Find the last Paper sale date inside the Paper filter. Paper's last order is S7 on 2025-02-02, worth 20.

**Tempting mistake:** Computing MAX(Sales[OrderDate]) as a sibling of the Paper filter evaluates it over all sales, which gives 2025-02-03, the date of the Mug line S8, so the result is BLANK.

**How to confirm:** Nested as `CALCULATE ( CALCULATE ( [NetRevenue], 'Date'[Date] = MAX ( Sales[OrderDate] ) ), Product[Category] = "Paper" )`, expect 20.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
