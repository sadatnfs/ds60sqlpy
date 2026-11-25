# dax-044: explained reference and practice reasoning

Check that the reference's expanded query multiplies only NetRevenue by 0.9 and leaves QuantitySold untouched. Results of 168.3 and 17 follow from the guarded definition shown in the lesson's extra block. Read it beside the [reference source](dax-044_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Current measures before an item

No calculation item applied; baseline measure definitions.

| Revenue | Units |
| --- | --- |
| 187 | 17 |

A shared visual can contain both measures without implying that every calculation item should transform them identically.

- The eligible Sales rows total 187 USD.
- Their quantities total 17 units.
- These quantities have different units and transformation policies.

### Case B: Expanded guarded fee item

Algebraic expansion of the named revenue-only item; no live calculation-group execution.

| RevenueAfterFee | UnitsUnchanged |
| --- | --- |
| 168.3 | 17 |

An expanded query is a useful semantic reference. It does not establish that a particular external model's group selection, precedence or formatting is configured correctly.

- The revenue branch multiplies 187 by 0.9, giving 168.3.
- The guard leaves the quantity measure at 17.
- The transformation changes a defined revenue policy, not the observed transaction counts.

## Explained practice answers

### Exercise 1

Predict the guarded item for Blue revenue.

The transformed revenue is 146.7; Blue units remain 12.

**Why it fits this model:** The guarded item multiplies only NetRevenue. Under Blue, revenue is 163, so the item returns 163 x 0.9, and Blue units (Notebook 7 + Mug 5) stay 12.

**Tempting mistake:** Computing the fee once on the 187 total and subtracting 18.7 from Blue revenue gives 144.3, which charges Blue for every product's fee.

**How to confirm:** Under Product[Color] = "Blue", expect 146.7 and 12.

### Exercise 2

Remove the applicability guard conceptually.

Quantity 17 would become 15.3, which is inappropriate for this observed-unit measure.

**Why it fits this model:** Without ISSELECTEDMEASURE the item touches every measure in the group's scope, including counts measured in units.

**Tempting mistake:** The unguarded item returns 17 x 0.9 = 15.3 units and turns the 7 distinct orders into 6.3, values that cannot be observed.

**How to confirm:** QuantitySold should stay 17 and OrderCount 7 when the item is applied; only NetRevenue changes to 168.3.

### Exercise 3

Write the calculation-item expression and its applicability contract.

IF(ISSELECTEDMEASURE([NetRevenue]),SELECTEDMEASURE()*0.9,SELECTEDMEASURE()); document that only NetRevenue receives the fee.

**Why it fits this model:** `IF ( ISSELECTEDMEASURE ( [NetRevenue] ), SELECTEDMEASURE () * 0.9, SELECTEDMEASURE () )` applies the fee to one named measure and passes the rest through.

**Tempting mistake:** Writing the guard as IF(SELECTEDMEASURENAME() = "Revenue", ...) depends on a display name, so renaming the measure silently turns the fee off.

**How to confirm:** The contract lists NetRevenue as the only affected measure and expects 187 to become 168.3 and QuantitySold to stay 17.

### Exercise 4

Diagnose pasting SELECTEDMEASURE into an ordinary query-local measure.

It does not name a normal measure argument there. Expand a named measure for offline arithmetic or create the appropriate model object externally.

**Why it fits this model:** SELECTEDMEASURE is a placeholder inside calculation items. A query-local measure has no selected measure to stand for.

**Tempting mistake:** Defining MEASURE Sales[Fee] = SELECTEDMEASURE() * 0.9 in a query and expecting 168.3. The reference has nothing to resolve to.

**How to confirm:** The offline expansion `[NetRevenue] * 0.9` returns 168.3, as in case B.

### Exercise 5

Explain whether selecting two calculation items has a universal default result.

Record the group's selection-expression policy and test no-selection/multiple-selection cases in a real supported model before deployment.

**Why it fits this model:** When a slicer selects two items, or none, the result depends on the group's selection-expression settings and the product's rules, not on DAX in general.

**Tempting mistake:** Assuming two selected items stack into 187 x 0.9 x 0.9, or that the first one wins. Neither follows from this file.

**How to confirm:** Record the expected no-selection result (187 here) and the multiple-selection result for the configured group, then test both in a supported model.

### Exercise 6

Transfer the guard to a prior-period calculation group.

Define which measures represent period flows, balances or labels, then test each intended transformation and excluded measure.

**Why it fits this model:** A prior-period item should shift flows such as NetRevenue: under January 2025, the prior year's January is 64. A label such as a data-through date should not shift.

**Tempting mistake:** Applying the shift to every measure makes a freshness label read a year earlier and makes an inventory balance from another lesson behave like a flow.

**How to confirm:** Under January 2025, the prior-period item gives NetRevenue 64 and OrderCount 2 (orders 101 and 102); excluded measures return their current values.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
