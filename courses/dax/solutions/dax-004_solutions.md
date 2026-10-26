# dax-004: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-004_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Dimension-to-fact propagation

Blue Product rows; active Product -> Sales direction.

| VisibleProducts | Lines | Revenue |
| --- | --- | --- |
| 2 | 6 | 163 |

The selected dimension supplies a key set that travels to the fact. It is not inferred from which products happen to have sales in another visual.

- Notebook and Mug are Blue.
- Their keys admit six sales lines.
- Product count is 2; their revenues 67 and 96 sum to 163.

### Case B: Fact filter does not flow backward

Direct filter Sales.SaleID = S4; no Product filter; single-direction relationships.

| VisibleProducts | Lines | Revenue |
| --- | --- | --- |
| 4 | 1 | 27 |

A product-count card showing four is consistent with the declared model. The mistake would be naming that count 'products sold in this line'.

- Sales is reduced to S4.
- The relationship does not propagate from its many side to Product.
- All four Product rows remain visible, even though S4 uses only product 1.

## Explained practice answers

### Exercise 1

Predict DISTINCTCOUNT(Sales[ProductKey]) in the S4 context.

It is 1, unlike COUNTROWS(Product), which is 4.

### Exercise 2

Predict the all-model product count and products-with-sales count.

The dimension has four products, while Sales contains three product keys.

### Exercise 3

Write a query returning both populations with unambiguous labels.

Use ROW("CatalogProducts",COUNTROWS(Product),"SoldProducts",DISTINCTCOUNT(Sales[ProductKey])).

### Exercise 4

Diagnose a proposed bidirectional fix for every empty report cell.

Review path ambiguity and intended populations first. An explicit measure can be preferable to changing every filter path.

### Exercise 5

Explain why a duplicate ProductKey is not solved by sorting the dimension.

Sorting changes display order, not duplicate keys. Repair the key or model the legitimate lower grain.

### Exercise 6

Compare an inner SQL join with this model when a sales key has no product.

Regular-model blank-member behavior can retain its amount. Match missing-key policy before using the join as an oracle.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
