# dax-014: explained reference and practice reasoning

The reference changes only the Region filter between its two cases, from one value to an IN list, while the 2025 year filter stays fixed. Check that your ledger explains 83 and 123 without appealing to 187. Read it beside the [reference source](dax-014_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: One region in one year

Customer.Region = North and Date.Year = 2025, using active OrderDate.

| Revenue |
| --- |
| 83 |

The same regional total across all years would be 107. Omitting the year from an explanation would conceal why those two correct values differ.

- North supplies customer keys 10 and 30.
- Year 2025 removes S1, S2 and S3.
- S4, S5 and S8 remain: 27 + 20 + 36 = 83.

### Case B: A multi-selection retains the year

Region is the allowed set {North, South}; order year remains 2025.

| Revenue |
| --- |
| 123 |

Broadening one filter does not remove the others. The answer does not return to the all-year total 187.

- The region set admits all three customers with sales.
- The year filter still excludes the three 2024 lines.
- S4 through S8 total 123.

## Explained practice answers

### Exercise 1

Predict 2025 South revenue.

S6 and S7 contribute 20 each, totaling 40.

**Why it fits this model:** Customer 20 (Bo) is the only South customer. Under 2025 his lines are S6 and S7 at 20 each, so South revenue is 40.

**Tempting mistake:** Leaving out the year returns 80, because Bo's 2024 Mug line S3 (40) joins the result.

**How to confirm:** `CALCULATE ( [NetRevenue], Customer[Region] = "South", 'Date'[Year] = 2025 )` returns 40, and 83 + 40 equals case B's 123.

### Exercise 2

Add Product.Category = Paper to case B.

S4, S5 and S7 remain, totaling 67.

**Why it fits this model:** The region set, the year and the category all apply together. Among 2025 lines, Paper keeps S4 (27), S5 (20) and S7 (20), so revenue is 67.

**Tempting mistake:** Letting the category filter replace the earlier filters returns all-years Paper revenue of 91, which adds the 2024 lines S1 and S2.

**How to confirm:** Case B with `Product[Category] = "Paper"` added returns 67, and dropping Paper returns 123 again.

### Exercise 3

Write a context ledger for North, Home and 2025.

North admits customers 10/30, Home admits product 3, and 2025 keeps S8; revenue is 36.

**Why it fits this model:** North admits customers 10 and 30, Home admits product 3 and 2025 admits S4 to S8. Only S8 (Cy's Mug, 36) passes all three.

**Tempting mistake:** A ledger that writes down only the visible Home slicer predicts 96, because it forgets the region and year filters on other tables.

**How to confirm:** The three filters together return 36, the NetAmount of S8.

### Exercise 4

Diagnose a report comparing North 2025 with South across all years.

The comparison mixes 83 with 80 rather than comparable-year 83 with 40. Define the intended period consistently.

**Why it fits this model:** A fair comparison uses the same period on both sides: North 83 against South 40 in 2025, or North 107 against South 80 for all years.

**Tempting mistake:** Comparing North 2025 (83) with South all years (80) suggests the regions are nearly equal, when in the same year North sold about twice as much.

**How to confirm:** Query both regions under one year filter and expect 83 and 40, then without it and expect 107 and 80.

### Exercise 5

Predict a West-plus-2025 selection.

The result is BLANK because customer 40 has no Sales rows.

**Why it fits this model:** West is a valid Customer member (Di, key 40) with no Sales rows, so the year makes no difference and revenue is BLANK.

**Tempting mistake:** Taking BLANK as a broken relationship or an invalid selection leads to model changes, when it is simply a population with no facts.

**How to confirm:** Under West and 2025, COUNTROWS(Customer) returns 1 while `ISEMPTY ( Sales )` returns TRUE and revenue is BLANK.

### Exercise 6

Transfer the ledger to a dashboard with several pages.

Capture effective filters, date role and relationship assumptions for each reported number, not only the visible slicer caption.

**Why it fits this model:** Each number needs its full context written down. A card showing 83 may have a visible North slicer and a hidden 2025 page filter, and it uses the active OrderDate relationship.

**Tempting mistake:** Documenting only the visible North caption leads a reader to expect 107. Switching the date role also matters: January 2025 is 67 by order date and 47 by ship date.

**How to confirm:** Replaying CALCULATE with every captured filter should reproduce 83; S6, ordered January 5 and shipped February 1, explains the date-role difference.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
