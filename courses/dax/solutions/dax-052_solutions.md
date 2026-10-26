# dax-052: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-052_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Fact-table removal reaches related dimensions

Regular Import-style star; starting filters are North and order year 2025; no bidirectional or limited relationships.

| Original | ClearExpandedSales | ClearAmountOnly |
| --- | --- | --- |
| 83 | 187 | 83 |

The scope of a table modifier matters. A relationship or storage-mode redesign can change assumptions and requires fresh semantic checks.

- The starting context totals 83.
- ALL(Sales) as a modifier clears filters over its expanded table, restoring the whole-model 187.
- Removing only Sales.NetAmount does not remove Customer.Region or Date.Year, so the result stays 83.

### Case B: Requested values are not all existing pairs

Explicit domain comparison: requested Paper/Red and Home/Red versus stored Product combinations.

| RequestedPairs | ExistingPairs |
| --- | --- |
| 2 | 1 |

This explains information that can matter when filters are coalesced. It does not by itself determine every ALL or ALLSELECTED result under every value-filter configuration.

- Two requested categories times one requested color gives two candidate pairs.
- Only Paper/Red exists in Product, represented by Pen.
- Home/Red is not a stored combination; the existing pair count is one.

## Explained practice answers

### Exercise 1

Predict ALL(Product) under the North/year 2025 starting context.

With no initial Product restriction, the measure remains 83; unrelated Customer and Date filters remain.

### Exercise 2

Change requested color from Red to Blue.

Requested and existing pair counts both become two.

### Exercise 3

Write a denominator-debugging ledger.

Record incoming filters, regular/limited relationships, expanded-table scope, requested versus surviving combinations and the exact query's value-filter behavior.

### Exercise 4

Diagnose using ALL(Sales) to remove only a product-color selection.

It can remove related dimension filters that should remain. Prefer a deliberately scoped modifier when that is the intended question.

### Exercise 5

Explain why an Independent versus Coalesced value-filter setting needs explicit qualification.

Record the setting and engine/version, then test same-table filter combinations and totals; do not invent an execution result from the setting's name.

### Exercise 6

Transfer the domain check to size/color inventory selections.

Keep requested values, existing combinations and unavailable inventory distinct, especially when calculating shares or removing only one filter.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
