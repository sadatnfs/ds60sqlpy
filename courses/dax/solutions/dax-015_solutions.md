# dax-015: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-015_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Replace Blue with Red

Start with Product.Color = Blue; the inner calculation sets Color = Red.

| Original | RedRevenue |
| --- | --- |
| 163 | 24 |

The second result is not a Blue-and-Red intersection. That would have no product rows in this fixture.

- The original measure includes Notebook and Mug, totaling 163.
- The inner predicate replaces the filter on the same Color column.
- Red admits Pen and produces 24.

### Case B: Add Color while retaining Category

Start with Category = Paper; add Color = Blue on a different column.

| PaperRevenue | BluePaperRevenue |
| --- | --- |
| 91 | 67 |

Replacing one column's selection and retaining a different column's selection are compatible behaviors. Always specify which column the expression modifies.

- Paper supplies Notebook and Pen: 91.
- Blue is added while Paper remains active.
- Only Notebook satisfies both; revenue is 67.

## Explained practice answers

### Exercise 1

Predict setting Color = Green inside the Blue context.

Green selects Bag, whose revenue is BLANK because it has no facts.

**Why it fits this model:** Product[Color] = "Red" replaces the incoming Blue filter on that same column. Green replaces it the same way, leaving Bag, which has no sales.

**Tempting mistake:** Reading BLANK as proof that Blue and Green were intersected is the mistake. The intersection is also empty, so revenue cannot tell the two rules apart.

**How to confirm:** Under Blue, `CALCULATE ( COUNTROWS ( Product ), Product[Color] = "Green" )` returns 1 (Bag), while the KEEPFILTERS version returns BLANK.

### Exercise 2

Change case B's Color to Red.

The modified revenue is 24.

**Why it fits this model:** Color and Category are different columns, so the Red filter is added beside Paper. Only Pen is both, and its lines S2 and S5 give 24.

**Tempting mistake:** Offering Red as proof that Paper survived proves nothing, because all-Red revenue is also 24. Blue is the case that tells them apart: 67 against 163.

**How to confirm:** Under Paper, CALCULATE with Red returns 24 and COUNTROWS(Product) returns 1.

### Exercise 3

Write a measure that forces year 2025 but retains region.

CALCULATE([NetRevenue],'Date'[Year]=2025) retains an independent Customer.Region filter; under North the result is 83.

**Why it fits this model:** CALCULATE([NetRevenue], 'Date'[Year] = 2025) replaces only the year. A Customer[Region] filter stays, so under North it returns 83.

**Tempting mistake:** `CALCULATE ( [NetRevenue], FILTER ( ALL ( Sales ), RELATED ( 'Date'[Year] ) = 2025 ) )` also removes the region filter through ALL(Sales) and returns 123 under North.

**How to confirm:** Expect 83 under North, 40 under South and 123 with no region selected.

### Exercise 4

Diagnose saying CALCULATE removed every report filter.

They can remain active. Case B retains Category and therefore does not return all-Blue revenue 163.

**Why it fits this model:** CALCULATE replaces filters only on the columns its arguments name. In case B the Color filter is new, so the incoming Category filter stays.

**Tempting mistake:** If CALCULATE cleared every filter, BluePaperRevenue would be all-Blue revenue, 163, and would include the Mug lines.

**How to confirm:** BluePaperRevenue is 67, the Notebook lines S1 (20), S4 (27) and S7 (20).

### Exercise 5

Explain when a constant filter is inappropriate for an interactive metric.

A fixed-year or fixed-color measure should be clearly named; use an intersection policy when the metric should respect the selection.

**Why it fits this model:** A fixed-color measure answers a fixed question. Named Blue Revenue, it returns 163 under any color slicer, which is right only if readers know it ignores that selection.

**Tempting mistake:** Naming it Revenue and showing 163 under a Red slicer contradicts the user's choice; an intersection with KEEPFILTERS would return BLANK there.

**How to confirm:** Under Red, the base measure returns 24, the fixed measure 163 and the KEEPFILTERS version BLANK.

### Exercise 6

Transfer the distinction to a share denominator.

Preserve filters defining the comparable population while changing only the category or time dimension required by the denominator's definition.

**Why it fits this model:** For a category share within the current region and year, remove only the category filter. North 2025 Paper is 47 (S4 and S5) out of 83, about 0.566.

**Tempting mistake:** Using ALL or REMOVEFILTERS on everything makes the denominator 187, and Paper's share drops to about 0.251 of a total outside the selection.

**How to confirm:** Under North and 2025, Paper is 47 / 83 and Home is 36 / 83, and the two shares add to 1.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
