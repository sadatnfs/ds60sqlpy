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

**Why it fits this model:** ALL(Product) removes Product filters only, and none are active. North (Ada and Cy) and 2025 still select S4, S5 and S8.

**Tempting mistake:** Expecting 187 as with ALL(Sales). ALL(Sales) clears the expanded fact table, including Customer and Date, but ALL(Product) cannot reach them.

**How to confirm:** Under Region North and Year 2025, CALCULATE([NetRevenue], ALL(Product)) returns 83.

### Exercise 2

Change requested color from Red to Blue.

Requested and existing pair counts both become two.

**Why it fits this model:** Notebook is Paper and Blue, and Mug is Home and Blue, so both requested pairs exist in Product.

**Tempting mistake:** Concluding from this case that a cross product of valid values always exists. Case B's Home and Red has no product.

**How to confirm:** RequestedPairs 2 and ExistingPairs 2 for Blue, against 2 and 1 for Red.

### Exercise 3

Write a denominator-debugging ledger.

Record incoming filters, regular/limited relationships, expanded-table scope, requested versus surviving combinations and the exact query's value-filter behavior.

**Why it fits this model:** The ledger lists the incoming filters (North, 2025), the modifier and the tables it covers, the relationship type, the requested and existing pairs, and the value at each step.

**Tempting mistake:** Writing only "used ALL" in the ledger, which does not say whether 187 or 83 is expected.

**How to confirm:** For case A the ledger reads Original 83, ALL(Sales) 187 and REMOVEFILTERS(Sales[NetAmount]) 83, each with its reason.

### Exercise 4

Diagnose using ALL(Sales) to remove only a product-color selection.

It can remove related dimension filters that should remain. Prefer a deliberately scoped modifier when that is the intended question.

**Why it fits this model:** To remove only the color filter, name that column. Under Blue, North and 2025, the lines are S4 and S8.

**Tempting mistake:** Using ALL(Sales) also clears North and 2025, so the measure jumps to the whole-model 187.

**How to confirm:** Blue, North and 2025 give 63. REMOVEFILTERS(Product[Color]) gives 83, while ALL(Sales) gives 187.

### Exercise 5

Explain why an Independent versus Coalesced value-filter setting needs explicit qualification.

Record the setting and engine/version, then test same-table filter combinations and totals; do not invent an execution result from the setting's name.

**Why it fits this model:** Independent and Coalesced settings control how filters on columns of the same table combine. Formulas do not show the setting.

**Tempting mistake:** Predicting a result from the setting's name, such as assuming Independent means filters never interact, without testing.

**How to confirm:** Record the setting and engine version, then test case B's Paper or Home with Red selection and the totals in the target model.

### Exercise 6

Transfer the domain check to size/color inventory selections.

Keep requested values, existing combinations and unavailable inventory distinct, especially when calculating shares or removing only one filter.

**Why it fits this model:** Size and color selections work like Category and Color here. Each label exists, but the pair may not: Home and Red has no product.

**Tempting mistake:** Computing a share where the denominator counts requested pairs. For Paper or Home with Red, only Pen exists, so the share must be based on 1 pair, not 2.

**How to confirm:** Count existing combinations with SUMMARIZE over the dimension before computing shares; Pen's 24 USD is the only Red revenue.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
