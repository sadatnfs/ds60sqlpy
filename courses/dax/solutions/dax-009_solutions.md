# dax-009: explained reference and practice reasoning

In the reference, verify that the Reconstructed column repeats the arithmetic per row and matches Stored for S1 and S2, while the North 2025 case uses model measures. That split mirrors the column versus measure decision you drafted. Read it beside the [reference source](dax-009_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Stored row amounts and their formula

Two first SaleID values; each projection evaluates its own Sales row.

| Line | Stored | Reconstructed |
| --- | --- | --- |
| S1 | 20 | 20 |
| S2 | 4 | 4 |

Agreement verifies this tiny fixture's arithmetic. It does not prove that a source system applies every discount or tax policy correctly.

- S1: 2 times 10 minus 0 equals 20.
- S2: 1 times 5 minus 1 equals 4.
- The supplied NetAmount column agrees with the documented row formula.

### Case B: A measure over a selected population

North customers and order year 2025.

| Revenue | Quantity |
| --- | --- |
| 83 | 9 |

The context changes the measure result from 187 to 83. It does not change S4's line value from 27 into a regional total.

- Eligible lines are S4, S5 and S8.
- Their stored amounts are 27, 20 and 36, totaling 83.
- Their quantities are 3, 4 and 2, totaling 9.

## Explained practice answers

### Exercise 1

Predict S4's stored NetAmount after selecting South.

It remains 27 in the data, but S4 is not eligible for the South measure result.

**Why it fits this model:** A filter only decides which rows a measure can see. Selecting South keeps S3 (40), S6 (20) and S7 (20) for 80, and S4 still stores 27 because Ada is in North.

**Tempting mistake:** A calculated column that rewrites S4 to 0 whenever the region is not South would make stored data depend on one slicer, and North would lose 27 of its 107.

**How to confirm:** `CALCULATE ( [NetRevenue], Customer[Region] = "South" )` returns 80, while `CALCULATE ( SUM ( Sales[NetAmount] ), Sales[SaleID] = "S4" )` with no region filter still returns 27.

### Exercise 2

Change the case B year to 2024.

Revenue is 24 and quantity is 3.

**Why it fits this model:** In 2024 the only North lines are Ada's S1 (20) and S2 (4), so revenue is 24 and quantity is 3. Both filters must hold at once, so Bo's S3 is excluded.

**Tempting mistake:** Changing the year but also dropping the region filter returns 64 and 5, because Bo's 40 USD Mug line from order 102 joins the result.

**How to confirm:** The 2024 row reads 24 and 3. Adding the 2025 row (83 and 9) gives the North totals of 107 and 12.

### Exercise 3

Write a calculated-column expression for a line's gross amount.

Sales[Quantity] * Sales[UnitPrice] is the expression; its values would be stored per row if added as a calculated column externally.

**Why it fits this model:** A calculated column evaluates per Sales row, so S1 gets 2 x 10 = 20 and S2 gets 1 x 5 = 5. S2's stored NetAmount is 4 because its 1 USD discount is already removed.

**Tempting mistake:** A measure written as SUM(Sales[Quantity]) * SUM(Sales[UnitPrice]) multiplies totals, 17 x 100 = 1,700, instead of summing row products.

**How to confirm:** Summing the gross column, or running `SUMX ( Sales, Sales[Quantity] * Sales[UnitPrice] )`, returns 195, and 195 minus 8 of discounts equals 187.

### Exercise 4

Diagnose storing a region-wide total on every sales line and summing it later.

The total would be counted once per line. Use a context-dependent measure or model a separate aggregate fact with its own grain.

**Why it fits this model:** North has five lines: Ada's S1, S2 and S4 and Cy's S5 and S8. A measure filtered to North returns 107 once, whatever grain the visual uses.

**Tempting mistake:** Writing 107 onto each North line and summing it gives 5 x 107 = 535, five times the real revenue, and the multiple would change as lines are added.

**How to confirm:** Under North, SUM of the stored column returns 535 while `CALCULATE ( [NetRevenue], Customer[Region] = "North" )` returns 107.

### Exercise 5

Explain why a measure cannot serve as a stable product-category key.

Use a column with a declared domain and grain for relationships or category membership.

**Why it fits this model:** Product[Category] is a stored column with the members Paper, Home and Travel. Bag stays in Travel even with no sales, so relationships and slicers have a fixed domain.

**Tempting mistake:** Deriving a category from a measure such as revenue over 50 makes membership move with filters: Mug is 96 overall but 36 under North, so its category would flip with the region slicer.

**How to confirm:** `VALUES ( Product[Category] )` returns three rows under any Customer filter, while the Mug revenue changes from 96 to 36.

### Exercise 6

Choose a lifetime for a sales-band label that must reflect refreshed row values.

A processed row classification may be a calculated column or upstream attribute; a dynamic threshold over selected totals requires a measure/table expression.

**Why it fits this model:** A band from the row itself, such as NetAmount of at least 30 for S3 and S8, may be stored and recomputed at refresh. A share of the selected total depends on the filter, so it must be a measure.

**Tempting mistake:** A column storing NetAmount divided by the refresh total gives S8 36 / 187, about 0.193, and keeps it under North, where S8's real share is 36 / 107, about 0.336.

**How to confirm:** Under North the measure returns about 0.336 for S8 and about 0.193 with no filter; the column shows 0.193 in both views.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
