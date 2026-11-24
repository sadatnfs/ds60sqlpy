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

**Why it fits this model:** The filter sits on Sales[SaleID], so the fact table is reduced to the S4 line and counting keys in that filtered fact sees ProductKey 1 only. Product itself is untouched because the relationship flows from Product to Sales.

**Tempting mistake:** Reading COUNTROWS(Product) = 4 in the same context as four products involved in S4. That count measures the unfiltered dimension, not the line.

**How to confirm:** Under Sales[SaleID] = "S4", ROW("FactKeys", DISTINCTCOUNT(Sales[ProductKey]), "DimRows", COUNTROWS(Product)) returns 1 and 4.

### Exercise 2

Predict the all-model product count and products-with-sales count.

The dimension has four products, while Sales contains three product keys.

**Why it fits this model:** The dimension lists Notebook, Pen, Mug and Bag, but Sales only carries keys 1, 2 and 3. Bag is a catalog member with no fact rows, so the two counts answer different questions.

**Tempting mistake:** Labeling DISTINCTCOUNT(Product[ProductKey]) as products sold. It returns 4 and counts Bag, which has never sold.

**How to confirm:** `EXCEPT ( VALUES ( Product[ProductKey] ), VALUES ( Sales[ProductKey] ) )` should return key 4 alone, explaining the gap between 4 and 3.

### Exercise 3

Write a query returning both populations with unambiguous labels.

Use ROW("CatalogProducts",COUNTROWS(Product),"SoldProducts",DISTINCTCOUNT(Sales[ProductKey])).

**Why it fits this model:** Each count names its population, so the result stays readable under any filter. With no filter it returns 4 and 3; under Product[Color] = "Blue" both become 2 (Notebook and Mug), and under SaleID S4 they read 4 and 1.

**Tempting mistake:** Giving both columns the label Products. A reader then sees 4 and 3 side by side with no way to tell catalog size from sold assortment.

**How to confirm:** Run the query three times (no filter, Blue, S4) and expect 4 and 3, 2 and 2, then 4 and 1.

### Exercise 4

Diagnose a proposed bidirectional fix for every empty report cell.

Review path ambiguity and intended populations first. An explicit measure can be preferable to changing every filter path.

**Why it fits this model:** Setting the Product relationship to both directions changes every measure that counts Product: under SaleID S4, COUNTROWS(Product) would fall from 4 to 1. With Customer also bidirectional, Product and Customer gain a path through Sales.

**Tempting mistake:** Flipping the relationship to Both so one empty cell fills in. The other visuals that relied on single-direction behavior then change silently.

**How to confirm:** Prefer CALCULATE ( COUNTROWS ( Product ), CROSSFILTER ( Sales[ProductKey], Product[ProductKey], BOTH ) ) inside one measure, and confirm that the plain COUNTROWS(Product) under S4 still returns 4.

### Exercise 5

Explain why a duplicate ProductKey is not solved by sorting the dimension.

Sorting changes display order, not duplicate keys. Repair the key or model the legitimate lower grain.

**Why it fits this model:** A one-to-many relationship requires each ProductKey once on the Product side. Two rows for key 1 mean Notebook's 67 has two candidate labels, and display order cannot choose one.

**Tempting mistake:** Sorting the dimension so the preferred label appears first. Relationships and lookups do not read rows in display order, so the ambiguity remains.

**How to confirm:** COUNTROWS(Product) must equal DISTINCTCOUNT(Product[ProductKey]); on the clean fixture both are 4.

### Exercise 6

Compare an inner SQL join with this model when a sales key has no product.

Regular-model blank-member behavior can retain its amount. Match missing-key policy before using the join as an oracle.

**Why it fits this model:** An inner join keeps only matched rows. In the unknown-member variant, S9 has ProductKey 999 and amount 7, and the regular relationship assigns it to the blank Product member instead of dropping it.

**Tempting mistake:** Using the inner-join total of 187 as the oracle for the model. The model reports 194, and the 7 difference is S9 under the blank member, not a DAX bug.

**How to confirm:** A SQL LEFT JOIN that labels unmatched keys Unknown returns 187 for known products plus 7 for Unknown, matching the model grand total of 194.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
