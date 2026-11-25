# dax-019: explained reference and practice reasoning

In the reference, compare the plain Color filter in ForcedRed with the KEEPFILTERS wrapper beside it. Verify that the outer selection is the only thing that changes between cases and that 24, BLANK, 187 and 163 follow from it. Read it beside the [reference source](dax-019_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: A disjoint subgroup stays empty

Original allowed color {Blue}; compare replacement with intersection by {Red}.

| ForcedRed | RedWithinSelection |
| --- | --- |
| 24 | BLANK |

An intersection measure should not escape its selected population to manufacture a nonblank result.

- Replacement changes the allowed set to Red and admits Pen.
- Intersection computes {Blue} intersect {Red}, an empty set.
- ForcedRed is 24; the selected-subgroup result is BLANK.

### Case B: An overlapping subgroup is retained

Original allowed colors {Blue, Red}; restrict to Blue without expanding selection.

| SelectedRevenue | BlueWithinSelection |
| --- | --- |
| 187 | 163 |

KEEPFILTERS does not freeze the original total. It can narrow a population while preserving the fact that the starting selection is an outer constraint.

- All products with recorded sales are Blue or Red, totaling 187.
- Intersecting with Blue removes Pen's 24.
- Notebook and Mug remain and total 163.

## Explained practice answers

### Exercise 1

Predict BlueWithinSelection if only Red is selected.

It is BLANK because {Red} and {Blue} do not overlap.

**Why it fits this model:** KEEPFILTERS intersects the new Blue condition with the existing Red selection. The two color sets share nothing, so no product remains and revenue is BLANK.

**Tempting mistake:** A plain Blue filter replaces Red and returns 163 inside a Red-only report, showing a number for products the user never selected.

**How to confirm:** Under Red, SelectedRevenue is 24, the KEEPFILTERS version is BLANK and the plain version is 163.

### Exercise 2

Replace the new subgroup by Color IN {Blue, Green}.

The intersection is Blue; Green does not get added. Revenue remains 163.

**Why it fits this model:** The intersection of {Blue, Green} with the selected {Blue, Red} is {Blue}, so Notebook and Mug remain and revenue is 163.

**Tempting mistake:** A plain IN filter replaces the selection with Blue and Green and adds Bag. Revenue still reads 163 because Bag has no sales, so revenue alone cannot show the error.

**How to confirm:** Count products instead: COUNTROWS(Product) is 2 with KEEPFILTERS and 3 with the plain filter.

### Exercise 3

Write a selected-subgroup measure for Trade customers.

CALCULATE([NetRevenue],KEEPFILTERS(Customer[Segment]="Trade")) retains only selected Trade customers.

**Why it fits this model:** Cy (key 30) is the only Trade customer, at 56. KEEPFILTERS keeps Trade only where the user's segment selection allows it.

**Tempting mistake:** A plain Segment filter under a Retail slicer replaces Retail and shows Cy's 56, a Trade number in a Retail view.

**How to confirm:** Under Segment = Retail the KEEPFILTERS version is BLANK and the plain one is 56. With no segment filter both return 56.

### Exercise 4

Diagnose changing KEEPFILTERS to a plain filter because blanks look untidy.

A disjoint selection would be replaced rather than respected. Decide the intended metric before changing its appearance.

**Why it fits this model:** BLANK in RedWithinSelection says that Red lies outside the selected Blue products. That is the intended population rule, not a display flaw.

**Tempting mistake:** Switching to a plain filter fills the cell with ForcedRed's 24, so a Blue-only report then shows Pen revenue the user excluded.

**How to confirm:** Case A shows the two policies side by side: 24 for replacement and BLANK for intersection under the same Blue selection.

### Exercise 5

Explain whether KEEPFILTERS restores a removed earlier filter.

It does not remember arbitrary historical selections or undo unrelated filter-removal operations.

**Why it fits this model:** KEEPFILTERS intersects with the context that exists when it is applied. If an outer REMOVEFILTERS(Product[Color]) has already cleared Red, nothing is left to intersect.

**Tempting mistake:** Expecting the user's earlier Red choice to come back predicts BLANK. The color filter is gone, so the KEEPFILTERS Blue condition returns 163.

**How to confirm:** Under Red, `CALCULATE ( CALCULATE ( [NetRevenue], KEEPFILTERS ( Product[Color] = "Blue" ) ), REMOVEFILTERS ( Product[Color] ) )` returns 163.

### Exercise 6

Transfer the policy to a quality metric for failed events.

Intersect a failure subgroup with the selected cohort when reporting failures among that population; label any intentionally global failure metric separately.

**Why it fits this model:** With a discounted line standing in for a failed event, count flagged lines inside the selected cohort. North has five lines (S1, S2, S4, S5, S8), and three of them (S2, S4 and S8) carry a discount, a rate of 0.6.

**Tempting mistake:** `FILTER ( ALL ( Sales ), Sales[Discount] > 0 )` ignores the cohort and returns 3 under every region, so South looks discounted although Bo's lines had none.

**How to confirm:** The cohort version returns 3 under North and BLANK under South; the global version, labeled as global, returns 3 everywhere.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
