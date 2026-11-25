# dax-003: explained reference and practice reasoning

Compare the reference's CALCULATETABLE filters with your draft: each filter argument names one dimension column, and together they return 91 and then 71. Check that no filter is placed on a Sales column. Read it beside the [reference source](dax-003_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Paper products

Product.Category = Paper; other dimensions unrestricted.

| Revenue |
| --- |
| 91 |

The result includes several customers and years. A category selection does not implicitly select the latest year or a region.

- Paper maps to product keys 1 and 2.
- Eligible lines are S1, S2, S4, S5 and S7.
- 20 + 4 + 27 + 20 + 20 = 91.

### Case B: Paper in the North

Product.Category = Paper AND Customer.Region = North.

| Revenue |
| --- |
| 71 |

A relationship graph plus eligible-row list explains the reduction without guessing which visual control caused it. Both filters remain part of the measure's question.

- North admits customer keys 10 and 30.
- Intersect those customers with Paper's product keys.
- S7 is excluded because customer 20 is South; 91 - 20 = 71.

## Explained practice answers

### Exercise 1

Predict Home revenue in North.

Only S8 remains, so revenue is 36.

**Why it fits this model:** Product[Category] = "Home" keeps only ProductKey 3, and Customer[Region] = "North" keeps keys 10 and 30. Each filter flows down its own active relationship, and Sales keeps only rows that pass both, which leaves S8.

**Tempting mistake:** CALCULATE ( [NetRevenue], ALL ( Customer ), Product[Category] = "Home" ) on a North row returns 96, because ALL removes the region filter that should restrict the Mug lines.

**How to confirm:** `CALCULATETABLE ( VALUES ( Sales[SaleID] ), Product[Category] = "Home", Customer[Region] = "North" )` should list S8 alone, worth 36.

### Exercise 2

Change Paper to Home while leaving North selected.

The customer filter remains; the result is 36 rather than all-Home revenue 96.

**Why it fits this model:** Filters on Product and on Customer are independent, so replacing Paper with Home changes only the product side. The North customer filter stays and still removes Bo's Mug lines S3 and S6.

**Tempting mistake:** Reading the Home figure from a card that has no region filter shows 96 and silently drops the North condition that the question still carries.

**How to confirm:** Paper in North (71) plus Home in North (36) should equal North revenue: S1, S2, S4, S5 and S8 give 107.

### Exercise 3

Draw the two paths that meet at Sales.

Product.ProductKey -> Sales.ProductKey and Customer.CustomerKey -> Sales.CustomerKey, each one-to-many and active.

**Why it fits this model:** Each dimension sits on the one side of a single-direction relationship and filters Sales on the many side. Product and Customer meet at Sales but never filter each other.

**Tempting mistake:** Drawing an arrow from Product through Sales into Customer. That would mean a Paper filter shrinks the Customer table, which single-direction relationships do not do.

**How to confirm:** Under Product[Category] = "Paper", COUNTROWS(Customer) still returns 4, while DISTINCTCOUNT(Sales[CustomerKey]) returns 3 for customers 10, 20 and 30.

### Exercise 4

Diagnose a report that adds 91 and 107 to represent Paper-and-North revenue.

91 + 107 counts the overlap twice and includes other rows. The intersection revenue is 71.

**Why it fits this model:** Paper rows (S1, S2, S4, S5, S7) and North rows (S1, S2, S4, S5, S8) share four lines worth 71. The question asks for that intersection, which one CALCULATE with both filters returns.

**Tempting mistake:** Adding 91 and 107 to get 198 counts the shared 71 twice and also includes Paper sales to Bo and Mug sales to Cy, neither of which is Paper in the North.

**How to confirm:** The union is 91 + 107 - 71 = 127, and the intersection query returns 71; neither equals 198.

### Exercise 5

Predict a selection of West customers.

SUM over the empty eligible set is BLANK, not evidence of a missing West dimension row.

**Why it fits this model:** Customer[Region] = "West" keeps Di, key 40, but no Sales row carries key 40. SUM over zero eligible rows returns BLANK, which means no sales, not a missing dimension member.

**Tempting mistake:** Wrapping the measure as [NetRevenue] + 0 to show zero. It turns every empty combination, such as Bag in the West, into a visible row and erases the difference between no activity and a zero amount.

**How to confirm:** Under the West filter, COUNTROWS(Customer) returns 1, COUNTROWS(Sales) returns BLANK and ISBLANK([NetRevenue]) returns TRUE.

### Exercise 6

Explain how an event-time customer region requirement changes the model.

Use a documented historical key or event-time classification. Repeatedly changing a current Region label can rewrite historical report membership.

**Why it fits this model:** Region is a current attribute on a single Customer row. If Bo moved from South to North, every Bo line (S3, S6 and S7, worth 80) would move into North history, including 2024.

**Tempting mistake:** Editing Customer[Region] in place for the move. North 2024 revenue would jump from 24 to 64, rewriting a year that has already been reported.

**How to confirm:** With a historical key or an event-time region on Sales, North 2024 should stay at 24 (S1 and S2) after the change, while new sales follow the new region.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
