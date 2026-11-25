# dax-020: explained reference and practice reasoning

The reference repeats one numerator in both cases and changes only the REMOVEFILTERS argument, from a column to a table. Check that your shares come from DIVIDE over the stated populations: 67 of 91 and 47 of 107. Read it beside the [reference source](dax-020_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Share within the retained category

Paper and Blue selected; remove only Color in the denominator.

| Numerator | CategoryDenominator | Share |
| --- | --- | --- |
| 67 | 91 | 0.7362637363 |

The denominator does not become 187 because the Category filter was deliberately retained.

- The numerator contains Notebook: 67.
- Removing Color restores Pen within Paper, giving 67 + 24 = 91.
- The share is 67/91; Home remains outside the category population.

### Case B: All products within North

Paper, Blue and North selected; remove Product filters only in the denominator.

| Numerator | RegionalDenominator | Share |
| --- | --- | --- |
| 47 | 107 | 0.4392523364 |

An 'all products' denominator can still be regional and temporal. The model does not interpret the word all as an instruction to remove every other dimension.

- North Notebook sales are S1 and S4: 47.
- Removing Product restrictions admits the other North products: Pen contributes S2 4 plus S5 20, totaling 24, and Mug contributes S8 36.
- The retained North population totals 47 + 24 + 36 = 107; share is 47/107.

## Explained practice answers

### Exercise 1

Predict case A after removing the entire Product table instead of Color.

The denominator becomes 187 and the share becomes 67/187.

**Why it fits this model:** REMOVEFILTERS(Product) clears both Category and Color. With no other filters, the denominator becomes all sales, 187, and the share is 67 / 187, about 0.358.

**Tempting mistake:** Treating table removal as the same as removing Color keeps expecting 91, so the label would still say share of Paper.

**How to confirm:** The row reads Numerator 67, denominator 187 and Share about 0.3583, compared with 0.7363 in case A.

### Exercise 2

Restrict case B to year 2025.

The numerator is 27 and the North-year denominator is 83, so the share is 27/83.

**Why it fits this model:** The year filter is not removed, so it applies to both parts. North Blue Paper in 2025 is S4 alone (27), and North 2025 is 83, for about 0.325.

**Tempting mistake:** Also removing the Date filter in the denominator uses all-years North, 107, and gives 27 / 107, about 0.252, a ratio across different periods.

**How to confirm:** Expect Numerator 27, RegionalDenominator 83 and Share about 0.3253.

### Exercise 3

Write the denominator contract in plain language before coding.

For case B: all products among North customers, within any other unchanged date or report constraints.

**Why it fits this model:** The contract is: all products bought by North customers, with every other filter unchanged. The numerator is Notebook's North lines S1 and S4 (47) and the denominator is 107.

**Tempting mistake:** Writing the contract as all sales leads to REMOVEFILTERS() or ALL, a denominator of 187 and a share of about 0.251 that ignores the region.

**How to confirm:** Case B returns numerator 47, denominator 107 and share about 0.4393, and each removed and kept filter appears in the written contract.

### Exercise 4

Diagnose a 100-percent share produced by a frozen denominator variable.

Removing filters around a precomputed scalar does not reevaluate revenue. Bind CALCULATE([NetRevenue],REMOVEFILTERS(...)) instead.

**Why it fits this model:** The denominator must be CALCULATE([NetRevenue], REMOVEFILTERS(Product[Color])) evaluated in place, which returns 91 under Paper and Blue.

**Tempting mistake:** Binding `VAR D = [NetRevenue]` under Paper and Blue holds 67. Wrapping D in REMOVEFILTERS keeps 67, and the share reads exactly 1.

**How to confirm:** Show the denominator as its own column: 91 is correct and 67 means it is frozen. The share should be about 0.7363.

### Exercise 5

Explain the denominator for a selected unsold product.

The numerator may remain BLANK even with a positive denominator. Decide whether the display should expose absence or coalesce it deliberately.

**Why it fits this model:** Bag (key 4) has no sales, so its numerator is BLANK. With no other filters a REMOVEFILTERS(Product) denominator is 187, and case A's color-only removal leaves Travel, also BLANK. DIVIDE returns BLANK, which correctly says nothing was sold.

**Tempting mistake:** Treating the BLANK share as a denominator bug sends you to debug a healthy 187. Coalescing it to 0 without saying so hides the difference between unsold and sold at zero.

**How to confirm:** Under ProductKey 4 with the table-level removal, the numerator is BLANK, the denominator 187 and the share BLANK; a deliberate COALESCE shows 0.

### Exercise 6

Transfer the pattern to a departmental cost share.

Remove the department selection only if the denominator should cover all departments in that same compatible population.

**Why it fits this model:** For a category cost share within a year, remove only Category. In 2025 Paper cost is Notebook 5 x 2 plus Pen 4 x 1, or 14, out of 29 in total, about 0.483.

**Tempting mistake:** Removing all filters in the denominator uses the all-years cost of 44, so Paper's 2025 share drops to 14 / 44, about 0.318.

**How to confirm:** Under 2025, Paper 14 / 29 and Home (Mug, 3 x 5 = 15) 15 / 29 add to 1.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
