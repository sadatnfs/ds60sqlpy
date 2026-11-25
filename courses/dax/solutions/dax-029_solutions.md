# dax-029: explained reference and practice reasoning

Verify that the reference evaluates both role columns under the same Date filter and that the only change is USERELATIONSHIP on Sales[ShipDate]. January 67 and 47, February 56 and 76, should reconcile to 123 per role. Read it beside the [reference source](dax-029_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: January order versus shipment attribution

Date year 2025/month 1; compare active OrderDate with the explicitly selected ShipDate relationship.

| OrderRevenue | ShipRevenue |
| --- | --- |
| 67 | 47 |

The 20 difference is explained by a timing boundary, not a lost transaction or a changed revenue formula.

- Orders S4, S5, S6 belong to January and total 67.
- Shipments S4 and S5 occur in January and total 47.
- S6's 20 moves to shipment month February.

### Case B: February absorbs the delayed shipment

Date year 2025/month 2 with the same role comparison.

| OrderRevenue | ShipRevenue |
| --- | --- |
| 56 | 76 |

Monthly attribution changes while the combined-period amount reconciles. A wider window is useful for checking that a role change has not duplicated facts.

- Orders S7, S8 total 56 in February.
- Shipments include S6, S7, S8, totaling 76.
- Across January and February, both date-role totals reconcile to 123.

## Explained practice answers

### Exercise 1

Predict all-2025 totals for both roles.

Both totals are 123; an annual-only test would hide the monthly role difference.

**Why it fits this model:** Every 2025 order also ships in 2025 (the latest is S8, shipped 2025-02-04), so the year contains the same five lines, S4 to S8, in both roles.

**Tempting mistake:** Testing ShipRevenue only at the year level and calling it validated. 123 against 123 passes even if the measure ignored the ship role completely.

**How to confirm:** For Year 2025 both return 123; January returns 67 against 47 and February 56 against 76.

### Exercise 2

Move S6's shipment back into January conceptually.

January ShipRevenue would rise from 47 to 67 and February ShipRevenue fall from 76 to 56.

**Why it fits this model:** Only the ship role reads ShipDate. Moving S6's 20 USD shipment to January makes ship revenue 47 + 20 = 67 in January and 76 - 20 = 56 in February.

**Tempting mistake:** Editing S6's OrderDate instead moves OrderRevenue as well, so the comparison loses the very difference it is meant to show.

**How to confirm:** After the change OrderRevenue stays 67 and 56, and ShipRevenue becomes 67 and 56.

### Exercise 3

Write a clearly named shipment-revenue measure.

ShipRevenue = CALCULATE([NetRevenue],USERELATIONSHIP(Sales[ShipDate],'Date'[Date])).

**Why it fits this model:** Put USERELATIONSHIP inside the measure, so every visual that uses ShipRevenue attributes by ShipDate and the active OrderDate relationship is switched off.

**Tempting mistake:** Adding `TREATAS ( VALUES ( 'Date'[Date] ), Sales[ShipDate] )` while the order relationship stays active requires both dates in the month. January still shows 47, but February drops S6 and shows 56 instead of 76.

**How to confirm:** Check February, not January: the measure must return 76 under Year 2025 and MonthNumber 2.

### Exercise 4

Diagnose using a nonexistent computed date expression in USERELATIONSHIP.

Model the required relationship or a separate date role first; the function does not create an arbitrary join.

**Why it fits this model:** USERELATIONSHIP switches on a relationship already defined between two columns. The inactive Sales[ShipDate] to 'Date'[Date] link exists, so case A works.

**Tempting mistake:** Passing an expression such as `Sales[OrderDate] + 7` for an expected delivery date fails, because the arguments must be columns in an existing relationship.

**How to confirm:** Store an ExpectedDate column with an inactive relationship, then test it. Each 2025 order plus 7 days stays in its order month here (S6 lands on January 12), so January reads 67 and February 56.

### Exercise 5

Explain why active/inactive status is not a security bypass.

Real RLS behavior and model compatibility require explicit external validation; a hand-derived period comparison does not prove security propagation.

**Why it fits this model:** Choosing a relationship changes which date a fact is filed under. It does not change which rows a security role exposes, and Microsoft documents limits on using USERELATIONSHIP where row-level security applies to a related table.

**Tempting mistake:** Assuming the ship role could reveal rows a North-only role hides, or that a correct 67 against 47 proves the measure works under security, when that comparison ran with no role at all.

**How to confirm:** Under a tested North-only role, January order and ship revenue should both be 47 (S4 and S5); verify with the engine's role testing, not by hand.

### Exercise 6

Choose between one shared Date table and separate OrderDate/ShipDate dimensions.

Separate role-playing dimensions can make independent slicers clearer; a shared dimension with explicit role measures can suit comparable-period analysis.

**Why it fits this model:** Separate OrderDate and ShipDate dimensions allow two independent selections. Ordered in January 2025 and shipped in February 2025 selects S6 alone, 20.

**Tempting mistake:** Expecting one shared Date slicer to express that question. A single selection applies to whichever role each measure activates, so no visual can show the 20.

**How to confirm:** With separate dimensions, OrderDate January 2025 and ShipDate February 2025 return 20; with one Date table, use role measures for side-by-side comparisons such as 67 against 47.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
