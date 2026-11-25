# dax-043: explained reference and practice reasoning

Verify that the reference builds Profit from NetRevenue and Cost and NetMargin from Profit with DIVIDE. The whole-model row should read 187, 44, 143 and about 0.765; the Blue row 163, 39, 124 and about 0.761. Read it beside the [reference source](dax-043_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Whole-model profit graph

Clean retail model; current UnitCost is explicitly constant per product; all amounts USD.

| Revenue | Cost | Profit | Margin |
| --- | --- | --- | --- |
| 187 | 44 | 143 | 0.7647058824 |

The margin is a numeric ratio, not the text produced by a percent formatter. Its meaning would change if costs and revenues used different filters.

- Line costs are 4, 1, 10, 6, 4, 5, 4, 10, totaling 44.
- Profit is 187 - 44 = 143.
- Margin is 143/187, evaluated from the same all-row population.

### Case B: The same family under Blue

Blue products only; the same measure definitions and cost assumptions.

| Revenue | Cost | Profit | Margin |
| --- | --- | --- | --- |
| 163 | 39 | 124 | 0.7607361963 |

A reusable definition remains context-dependent. Reuse should preserve a formula's policy while allowing the question's population to change.

- Notebook cost is 14 and Mug cost is 25, totaling 39.
- Blue revenue 163 minus 39 gives profit 124.
- The filtered margin is 124/163, not the unfiltered 143/187.

## Explained practice answers

### Exercise 1

Predict Pen profit.

Profit is 19 and margin is 19/24.

**Why it fits this model:** Revenue and cost are filtered by the same Product row. Pen sold S2 (1 unit, 4 USD) and S5 (4 units, 20 USD): revenue 24, and cost 5 units x 1 = 5.

**Tempting mistake:** Using Pen's revenue with the whole-model cost, 44, gives a profit of -20. The two inputs must cover the same products.

**How to confirm:** Under Product[ProductName] = "Pen", expect Revenue 24, Cost 5, Profit 19 and Margin 19 / 24, about 0.792.

### Exercise 2

Change UnitCost for Notebook to 3 in a hypothetical refreshed model.

Notebook cost rises from 14 to 21 and total profit falls by 7. This illustrates why overwriting a current cost can change historical reports.

**Why it fits this model:** Cost reads RELATED(Product[UnitCost]) on every line. Notebook sold 2 + 3 + 2 = 7 units, so its cost moves from 7 x 2 = 14 to 7 x 3 = 21.

**Tempting mistake:** Assuming only future sales change. With current-cost lookups, the 2024 Notebook line S1 is restated too, so last year's reported profit moves.

**How to confirm:** Total Cost becomes 51, Profit 136 and NetMargin 136 / 187, about 0.727.

### Exercise 3

Draw the dependency graph and annotate units.

NetRevenue USD and Cost USD feed Profit USD; Profit/NetRevenue gives a dimensionless margin.

**Why it fits this model:** NetRevenue (USD, SUM of NetAmount) and Cost (USD, SUMX of quantity times unit cost) feed Profit (USD). NetMargin divides Profit by NetRevenue and has no unit.

**Tempting mistake:** Drawing NetMargin as depending on Cost directly, or annotating it as USD, hides that it changes when either Profit or NetRevenue changes.

**How to confirm:** Each node's value checks against case A: 187 and 44 give 143, and 143 / 187 is about 0.765.

### Exercise 4

Diagnose FORMAT([NetMargin],"0.0%") being reused in arithmetic.

Keep NetMargin numeric and apply display formatting separately; arithmetic should depend on the numeric measure.

**Why it fits this model:** FORMAT returns text such as "76.5%". Arithmetic and comparison on that text no longer follow the numeric value.

**Tempting mistake:** Comparing formatted margins as text: "9.0%" is greater than "76.5%" because "9" sorts after "7", so a threshold test on text gives the wrong answer.

**How to confirm:** Keep NetMargin numeric (about 0.765) and set the display format on the measure; ISNUMBER([NetMargin]) should be TRUE.

### Exercise 5

Explain a zero or missing revenue denominator.

DIVIDE returns BLANK for an invalid denominator unless a separate explicit policy is chosen.

**Why it fits this model:** Margin is undefined when revenue is zero or BLANK. Bag has no sales, so its revenue, cost and profit are BLANK, and DIVIDE returns BLANK for its margin.

**Tempting mistake:** Wrapping the ratio as IFERROR(..., 0) shows Bag at a 0 percent margin, which reads like break-even sales.

**How to confirm:** Under ProductName = "Bag", NetMargin is BLANK; a hypothetical 0 USD line with 5 USD cost gives Profit -5 and a BLANK margin.

### Exercise 6

Transfer the graph to an adjusted revenue family.

Define each adjustment once, document its sign and population, then compose the final metric with an auditable dependency graph.

**Why it fits this model:** Define each adjustment once with its sign: GrossRevenue 195, minus discounts 8 (S2 1, S4 3, S8 4), is NetRevenue 187. Analytics Returns refunds 4 on S2 and 9 on S4.

**Tempting mistake:** Subtracting the refunds from GrossRevenue as well as from NetRevenue, or applying the discount twice, makes the family stop reconciling.

**How to confirm:** 195 - 8 = 187, and 187 - 13 = 174 for a return-adjusted revenue; each step reconciles with the previous measure.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
