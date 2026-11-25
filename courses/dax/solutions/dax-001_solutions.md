# dax-001: explained reference and practice reasoning

The reference defines NetRevenue once and reuses it in both cases, so the only difference between 187 and 67 is the filter argument. Confirm that your draft names its outputs and states USD as the unit. Read it beside the [reference source](dax-001_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: All eight lines

No filters; regular active relationships; USD sales-line grain.

| NetRevenue |
| --- |
| 187 |

The answer is attached to a defined population of lines. It is not proof that every business revenue policy has been represented. Changing the question to refunded revenue would require another fact or calculation.

- Eligible lines are S1 through S8.
- Add 20 + 4 + 40 + 27 + 20 + 20 + 20 + 36.
- The total is 187 USD before returns and tax.

### Case B: Notebook product only

ProductKey 1; the Product-to-Sales relationship is active and single-direction.

| NetRevenue |
| --- |
| 67 |

The measure text did not change. Its eligible rows did. A report selection must be part of the explanation whenever someone compares this 67 with the overall 187.

- ProductKey 1 identifies Notebook, not all products in the Paper category.
- The key filter admits Sales S1, S4 and S7.
- 20 + 27 + 20 = 67 USD.

## Explained practice answers

### Exercise 1

Predict the all-line quantity alongside revenue.

Quantity is 17; revenue is 187 USD. Their units differ.

**Why it fits this model:** QuantitySold sums Sales[Quantity] over the same eight unfiltered lines that produce 187, so both measures share one context: 2 + 1 + 2 + 3 + 4 + 1 + 2 + 2 = 17 units beside 187 USD of NetAmount.

**Tempting mistake:** Counting distinct Sales[ProductKey] values returns 3 and COUNTROWS(Sales) returns 8. Neither is a unit total, and placing 17 and 187 in one sum would add units to dollars.

**How to confirm:** `DEFINE MEASURE Sales[NetRevenue] = SUM ( Sales[NetAmount] ) MEASURE Sales[QuantitySold] = SUM ( Sales[Quantity] ) EVALUATE ROW ( "Revenue", [NetRevenue], "Units", [QuantitySold] )` should return 187 and 17 in a single row.

### Exercise 2

Change the product question from Notebook to Mug and list the contributing lines.

S3, S6 and S8 contribute 40 + 20 + 36 = 96.

**Why it fits this model:** Mug is ProductKey 3, and the active one-to-many Product relationship carries that key to Sales, keeping S3 (40), S6 (20) and S8 (36). The worked Notebook case follows the same path through S1, S4 and S7 to reach 67.

**Tempting mistake:** Filtering Product[Category] = "Home" also gives 96 today only because Mug is the sole Home product. It answers a category question and would drift silently once another Home item sells.

**How to confirm:** Run `CALCULATETABLE ( VALUES ( Sales[SaleID] ), Product[Product] = "Mug" )` and expect exactly S3, S6 and S8, then confirm the revenue row shows 96.

### Exercise 3

Write a one-row query that names the output QuantitySold.

EVALUATE ROW ( "QuantitySold", SUM ( Sales[Quantity] ) ) gives 17.

**Why it fits this model:** EVALUATE needs a table, so ROW turns one named scalar into a one-row result. SUM(Sales[Quantity]) has no filters here, so it sees all eight lines and returns 17.

**Tempting mistake:** Writing SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]) under the QuantitySold label returns 195, which is gross revenue in dollars, not a count of units.

**How to confirm:** The result has one column named QuantitySold and one value, 17. Add `DEFINE MEASURE Sales[QuantitySold] = SUM ( Sales[Quantity] )` to the query and return `[QuantitySold]` beside it under the same empty filter context: both columns read 17.

### Exercise 4

Diagnose a report labeled net profit that displays 187.

The fixture total is sales after line discounts, before cost, returns and tax. Profit is a different measure.

**Why it fits this model:** NetAmount already subtracts line discounts: gross revenue is 195 and the discounts on S2, S4 and S8 are 1 + 3 + 4 = 8, so 187 is discounted sales. Product cost is a separate column on Product.

**Tempting mistake:** Relabeling 187 as profit ignores UnitCost entirely. Cost on these lines is Notebook 7 x 2, Pen 5 x 1 and Mug 5 x 5, or 44 in total, so a margin before returns and tax would be 143.

**How to confirm:** `SUMX ( Sales, Sales[Quantity] * RELATED ( Product[UnitCost] ) )` returns 44, and [NetRevenue] minus that cost returns 143 rather than 187.

### Exercise 5

Explain what happens in this classroom after editing 187 into a draft comment.

Only the draft changes. The hand-derived reference table remains bound to the reference file and model.

**Why it fits this model:** The worked result table is tied to the saved reference file and model.json, which are the only inputs that reference-results.json hashes. A comment in a draft is neither.

**Tempting mistake:** Seeing 187 in the reference table after editing the draft and concluding that the draft formula ran. The table did not change because nothing it depends on changed.

**How to confirm:** Compare reference-results.json before and after the edit; its hash and its 187 stay identical, while only the draft file timestamp moves.

### Exercise 6

Describe the evidence needed to call an exported formula engine-tested.

Record the actual engine/version, model, filter context, exact submitted source and observed output. Offline comparison supplies none of those execution observations.

**Why it fits this model:** Engine testing is a claim about an execution, so it needs the observations an execution produces: which engine and version, which model file, what filter context, which exact query text and what value came back.

**Tempting mistake:** Treating an offline match of 187 as an engine result. The comparison checks arithmetic against a hand-derived table and never submits the formula to any engine.

**How to confirm:** A complete record reads like: engine and build, retail model, no filters, the exact submitted ROW query and an observed 187. A missing field means the claim is unverified.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
