# dax-013: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-013_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A row label beside an unfiltered sum

No outer filters; SELECTCOLUMNS supplies a Product row context only.

| Product | RawSum |
| --- | --- |
| Bag | 187 |
| Mug | 187 |
| Notebook | 187 |
| Pen | 187 |

The repeated total is not evidence of a broken relationship. It is evidence that the formula never supplied that relationship with a Product filter.

- The Product label changes on each iteration.
- The raw SUM has no transitioned Product filter.
- Every iteration therefore adds the same eight sales lines and returns 187.

### Case B: Transition the current product into a filter

The same Product rows, now with explicit context transition for the raw SUM.

| Product | Revenue |
| --- | --- |
| Bag | BLANK |
| Mug | 96 |
| Notebook | 67 |
| Pen | 24 |

The sum of the three nonblank product results reconciles to 187 because these product populations partition the fact rows in the clean model.

- CALCULATE turns each current Product row into filters.
- The active key relationship restricts Sales for that product.
- Bag has no matching fact rows; the other products contribute 96, 67 and 24.

## Explained practice answers

### Exercise 1

Predict the second projection if it uses [NetRevenue] instead of CALCULATE(SUM(...)).

It returns the same per-product values for this model.

**Why it fits this model:** A model measure reference carries an implicit CALCULATE, so each Product row becomes a ProductKey filter that the relationship passes to Sales. The values match case B.

**Tempting mistake:** Pasting the measure's body, SUM(Sales[NetAmount]), in place of the reference drops that implicit transition and brings back 187 on every row, as in case A.

**How to confirm:** Expect Bag BLANK, Mug 96, Notebook 67 and Pen 24, which add to 187.

### Exercise 2

Add an outer North filter to the raw-SUM case.

RawSum repeats the North total 107 for every visible product.

**Why it fits this model:** The outer North filter does reach Sales through Customer, so the raw SUM sees Ada's and Cy's five lines. The Product row context still adds no filter, so each row repeats 107.

**Tempting mistake:** Expecting North's per-product split from RawSum is the error. That split (Notebook 47, Pen 24, Mug 36) needs a transition, not just an outer filter.

**How to confirm:** Under `Customer[Region] = "North"` RawSum reads 107 on all four rows, while a transitioned column reads 47, 24, 36 and BLANK.

### Exercise 3

Write a projection that shows both raw and transitioned sums.

Each row can show RawSum 187 beside its own Revenue; this makes the missing transition directly observable.

**Why it fits this model:** Two labeled columns in one SELECTCOLUMNS share each Product row, so RawSum (no transition) and Revenue (with CALCULATE) differ only by the transition.

**Tempting mistake:** Iterating with SUMX(Product, SUM(Sales[NetAmount])) to get a total adds 187 four times and returns 748, the same missing transition hidden in one number.

**How to confirm:** Expect rows Bag 187 and BLANK, Mug 187 and 96, Notebook 187 and 67, Pen 187 and 24.

### Exercise 4

Diagnose replacing the relationship because every row shows 187.

The relationship can be correct; the raw aggregation has no Product filter to propagate.

**Why it fits this model:** The ProductKey relationship is active and one to many, and it works whenever a Product filter exists. Case A simply creates no filter, so nothing travels to Sales.

**Tempting mistake:** Making the relationship bidirectional or rebuilding it changes nothing here, because a row context is still not a filter, and every row still shows 187.

**How to confirm:** `CALCULATE ( SUM ( Sales[NetAmount] ), Product[ProductKey] = 3 )` returns 96, which shows the relationship already filters correctly.

### Exercise 5

Explain why Bag remains a returned row in case B.

Blank output is not a row-removal rule for this function. Other table functions may have different blank-row behavior.

**Why it fits this model:** SELECTCOLUMNS keeps one output row per input row, so all four Product rows appear. Bag's Revenue is BLANK because no Sales line carries key 4.

**Tempting mistake:** Expecting SELECTCOLUMNS to drop Bag mixes it up with SUMMARIZECOLUMNS, which removes rows whose measures are all blank and would return three rows.

**How to confirm:** COUNTROWS of case B returns 4, while `SUMMARIZECOLUMNS ( Product[Product], "Revenue", SUM ( Sales[NetAmount] ) )` returns 3 rows without Bag.

### Exercise 6

Transfer the distinction to a Customer calculated column containing total sales.

A raw Sales SUM repeats the outer total; CALCULATE or a model measure transitions the customer row so the relationship can filter its sales.

**Why it fits this model:** In a Customer calculated column, CALCULATE or [NetRevenue] turns the row into a CustomerKey filter, which gives Ada 51, Bo 80, Cy 56 and Di BLANK.

**Tempting mistake:** A raw SUM(Sales[NetAmount]) column stores 187 for every customer. Summing that column over four customers reports 748.

**How to confirm:** The transitioned column sums to 187, and Di's BLANK stays BLANK rather than 0.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
