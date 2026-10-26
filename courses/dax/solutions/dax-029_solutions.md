# dax-029: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-029_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: January order versus shipment attribution

Date year 2025/month 1; compare active OrderDate with the explicitly selected ShipDate relationship.

| OrderRevenue | ShipRevenue |
| --- | --- |
| 67 | 47 |

The 20 difference is explained by a timing boundary, not a lost transaction or a changed revenue formula.

- Orders S4,S5,S6 belong to January and total 67.
- Shipments S4 and S 5 occur in January and total 47.
- S6's 20 moves to shipment month February.

### Case B: February absorbs the delayed shipment

Date year 2025/month 2 with the same role comparison.

| OrderRevenue | ShipRevenue |
| --- | --- |
| 56 | 76 |

Monthly attribution changes while the combined-period amount reconciles. A wider window is useful for checking that a role change has not duplicated facts.

- Orders S7,S8 total 56 in February.
- Shipments include S6,S7,S8, totaling 76.
- Across January and February, both date-role totals reconcile to 123.

## Explained practice answers

### Exercise 1

Predict all-2025 totals for both roles.

Both totals are 123; an annual-only test would hide the monthly role difference.

### Exercise 2

Move S6's shipment back into January conceptually.

January ShipRevenue would rise from 47 to 67 and February ShipRevenue fall from 76 to 56.

### Exercise 3

Write a clearly named shipment-revenue measure.

ShipRevenue = CALCULATE([NetRevenue],USERELATIONSHIP(Sales[ShipDate],'Date'[Date])).

### Exercise 4

Diagnose using a nonexistent computed date expression in USERELATIONSHIP.

Model the required relationship or a separate date role first; the function does not create an arbitrary join.

### Exercise 5

Explain why active/inactive status is not a security bypass.

Real RLS behavior and model compatibility require explicit external validation; a hand-derived period comparison does not prove security propagation.

### Exercise 6

Choose between one shared Date table and separate OrderDate/ShipDate dimensions.

Separate role-playing dimensions can make independent slicers clearer; a shared dimension with explicit role measures can suit comparable-period analysis.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
