# dax-025: explained reference and practice reasoning

In the reference, verify that the 5 and 4 counts come from VALUES and DISTINCT over the same column, and that ISBLANK selects the blank member for the 7 USD. Your reconciliation should read 187 plus 7 equals 194. Read it beside the [reference source](dax-025_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Stored keys versus semantic members

Unknown-member model; stored Product keys 1..4; Sales also has key 999.

| ValuesMembers | StoredDistinctKeys |
| --- | --- |
| 5 | 4 |

The unknown member can represent multiple unmatched keys. It does not tell you how many distinct bad source codes exist; inspect fact-minus-dimension keys for that diagnostic.

- DISTINCT sees the four stored Product keys.
- The unmatched regular relationship introduces one semantic blank member for VALUES.
- VALUES therefore has five members, not a new stored row with key 999.

### Case B: Reconcile the unknown amount

Unknown-member model; the first expression selects its semantic blank Product member.

| UnknownRevenue | AllRevenue |
| --- | --- |
| 7 | 194 |

An explicit unknown bucket preserves a useful data-quality signal. Replacing it with an invented valid product would conceal a modeling issue.

- S9 is the only unmatched product fact and contributes 7.
- Known-product facts still contribute 187.
- The full fact total is 194, including the unknown bucket.

## Explained practice answers

### Exercise 1

Predict these two counts in the clean retail model.

Both counts are four; that clean fixture alone cannot reveal the function difference.

**Why it fits this model:** In the clean retail model every Sales ProductKey (1, 2 or 3) matches a stored Product row, so the engine adds no blank member. VALUES and DISTINCT both return the four stored keys.

**Tempting mistake:** Using the clean fixture as the only test and concluding that VALUES and DISTINCT are interchangeable. The unknown-member model, with S9 on key 999, returns 5 and 4.

**How to confirm:** Run case A on both models: retail gives 4 and 4, unknown-member gives 5 and 4.

### Exercise 2

Add a second unmatched source key with another fact.

VALUES still adds one blank member, while the unknown revenue grows by the new amount. A separate key-quality query must count the distinct unmatched codes.

**Why it fits this model:** Every unmatched code joins the same blank member. A hypothetical S10 on key 998 with Net 5 leaves VALUES at 5, raises UnknownRevenue from 7 to 12 and AllRevenue to 199.

**Tempting mistake:** Expecting COUNTROWS(VALUES(Product[ProductKey])) to reach 6, one per bad code, mistakes the semantic bucket for a list of codes, so a key-quality count built that way stays at one.

**How to confirm:** `COUNTROWS ( EXCEPT ( DISTINCT ( Sales[ProductKey] ), DISTINCT ( Product[ProductKey] ) ) )` returns 2 for {998, 999}, while VALUES still counts 5.

### Exercise 3

Write the reconciliation equation for product reporting.

Known revenue 187 + unknown revenue 7 = all revenue 194.

**Why it fits this model:** Known revenue is everything mapped to a stored key: Notebook 67 + Pen 24 + Mug 96 = 187. Adding the blank bucket's 7 gives AllRevenue 194.

**Tempting mistake:** A product visual that hides the blank row lists rows that sum to 187 under a grand total of 194, and a reader who adds the rows reports a 7 USD gap as a calculation bug.

**How to confirm:** Case B returns UnknownRevenue 7 and AllRevenue 194, and `CALCULATE ( [NetRevenue], NOT ISBLANK ( Product[ProductKey] ) )` returns 187.

### Exercise 4

Diagnose labeling VALUES(ProductKey) count as the number of sellable SKUs.

The count five includes the unknown bucket. Stored sellable-product policy needs its own catalog definition.

**Why it fits this model:** The sellable catalog is the stored Product table, four rows, or the three that sold if the policy requires sales. The fifth VALUES member exists only because S9's key 999 has no match.

**Tempting mistake:** Publishing 5 as the SKU count adds a product nobody can buy, and the count shifts as soon as the bad key is repaired, although no catalog change occurred.

**How to confirm:** Under the unknown-member model, COUNTROWS(Product) is 4, DISTINCT is 4 and VALUES is 5; only the first two belong in a catalog measure.

### Exercise 5

Explain why Bag is not the unknown member.

Key 4 is valid and unsold; the synthetic blank member represents facts lacking a valid product mapping.

**Why it fits this model:** Bag (key 4) is a real Product row with no Sales lines, so its revenue is BLANK. The blank member holds S9's 7 USD, which has no valid product.

**Tempting mistake:** Treating Bag as the unknown bucket because both look empty in a report confuses no facts with no dimension row, and sends the data-quality fix to the wrong table.

**How to confirm:** `CALCULATE ( [NetRevenue], Product[ProductKey] = 4 )` is BLANK, and `CALCULATE ( [NetRevenue], ISBLANK ( Product[ProductKey] ) )` is 7.

### Exercise 6

Transfer this reconciliation to late-arriving dimensions.

Retain and report the unmatched population, then verify how reconciliation changes after the correct dimension member arrives.

**Why it fits this model:** A late product row is the same pattern over time. Until key 999 arrives, S9's 7 sits in the blank bucket; afterward it moves to the new product, and the total stays 194.

**Tempting mistake:** Filtering out unmatched facts until the dimension catches up reports 187 today and 194 later, so the same period's total changes for no business reason.

**How to confirm:** Before the fix: unknown 7, total 194. After a Product row for 999 is loaded: unknown BLANK, product 999 at 7, total still 194.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
