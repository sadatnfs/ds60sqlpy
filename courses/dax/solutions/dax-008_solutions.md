# dax-008: explained reference and practice reasoning

Check that the reference evaluates loose and strict comparisons in the same row, and that COALESCE appears only in the DisplayRevenue column while Revenue stays BLANK. Your draft should keep those two columns distinct. Read it beside the [reference source](dax-008_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Blank coercion is operator-specific

Literal BLANK operations; no model context.

| LooseZero | StrictZero | PlusFive | TimesFive |
| --- | --- | --- | --- |
| TRUE | FALSE | 5 | BLANK |

A predicate written with = 0 may include missing results that the author intended to exclude. Test the intended missingness condition explicitly.

- Ordinary numeric equality coerces BLANK for the comparison with zero.
- Strict equality does not identify BLANK with numeric zero.
- Addition and multiplication have different blank behavior: 5 versus BLANK.

### Case B: An existing product with no sales

ProductKey 4, Bag; no matching Sales rows.

| Products | SalesRows | Revenue | DisplayRevenue |
| --- | --- | --- | --- |
| 1 | BLANK | BLANK | 0 |

A zero-filled display can be appropriate if unsold products are in scope. Retain a separate eligibility or availability signal when zero could otherwise mean an observed failure.

- One dimension member remains.
- The related fact table is empty, so COUNTROWS and SUM return BLANK.
- COALESCE deliberately displays zero while the original measure remains blank.

## Explained practice answers

### Exercise 1

Predict ISBLANK(0) and ISBLANK(BLANK()).

They are FALSE and TRUE.

**Why it fits this model:** ISBLANK asks whether the value itself is BLANK. Zero is a real number, so it fails the test, while BLANK() passes. Case A shows why a separate test is needed: BLANK() = 0 is TRUE.

**Tempting mistake:** Testing a result with = 0 returns TRUE for both values, because loose equality coerces BLANK to zero. A missing value and an observed zero become identical.

**How to confirm:** `ROW ( "Zero", ISBLANK ( 0 ), "Blank", ISBLANK ( BLANK () ), "Loose", BLANK () = 0 )` returns FALSE, TRUE and TRUE.

### Exercise 2

Replace the Bag filter with Pen.

Products is 1, SalesRows is 2 and Revenue/DisplayRevenue are both 24.

**Why it fits this model:** Pen is ProductKey 2, and the relationship keeps S2 (4) and S5 (20). Revenue is therefore 24 and nonblank, so COALESCE leaves it unchanged at 24.

**Tempting mistake:** Putting COALESCE([NetRevenue], 0) in the Revenue column instead of a separate display column agrees for Pen but shows 0 for Bag, which then reads as an observed zero sale.

**How to confirm:** Under ProductKey 2 the row is Products 1, SalesRows 2, Revenue 24 and DisplayRevenue 24.

### Exercise 3

Write a label distinguishing no sales from positive revenue.

IF(ISBLANK([NetRevenue]),"No matching sales","Revenue observed") avoids treating an empty result as an observed zero.

**Why it fits this model:** Checking ISBLANK first sends Bag, whose filter reaches no Sales rows, to "No matching sales". Notebook (67), Pen (24) and Mug (96) all reach "Revenue observed".

**Tempting mistake:** `IF ( [NetRevenue] <= 0, ... )` also catches Bag, because BLANK coerces to 0, but it would mislabel a real zero, such as a product whose lines were fully discounted to 0, as having no sales.

**How to confirm:** `ADDCOLUMNS ( VALUES ( Product[Product] ), "Label", ... )` should label Bag alone as no sales and the other three as observed.

### Exercise 4

Diagnose a report claiming every blank retention cell is a lost customer.

Missing observation time is different from observed inactivity. Do not coalesce the future into failures.

**Why it fits this model:** The retail facts end on 2025-02-03. February is observed: Bo and Cy bought and Ada did not, so Ada's February blank is real inactivity. March has no observation for anyone.

**Tempting mistake:** Coalescing every blank cell to "lost" marks all three buyers lost in March. That is a 100% churn claim for a month the data never covered.

**How to confirm:** `MAX ( Sales[OrderDate] )` returns 2025-02-03. Classify only months up to that date, and leave March marked as unobserved.

### Exercise 5

Explain why an empty table differs from one row containing BLANK.

An empty table has no row; a one-row table can carry a blank cell. Their membership and joins can differ.

**Why it fits this model:** Under the Bag filter Sales has no rows, so COUNTROWS(Sales) is BLANK. ROW always builds one row, so a table wrapping the blank revenue still has one member.

**Tempting mistake:** Testing ISEMPTY on the ROW result to detect missing sales returns FALSE for Bag, because the row exists even though its revenue cell is BLANK.

**How to confirm:** Under ProductKey 4, `ISEMPTY ( Sales )` is TRUE while `COUNTROWS ( ROW ( "R", [NetRevenue] ) )` is 1.

### Exercise 6

Transfer the policy to missing cost data.

Preserve missing cost as a quality issue or exclude/report it explicitly before calculating margins.

**Why it fits this model:** Cost lives on Product. Today the cost is Notebook 7 x 2, Pen 5 x 1 and Mug 5 x 5, or 44, giving a margin of 143. A missing Mug cost should surface as three unknown lines, not as cheap lines.

**Tempting mistake:** COALESCE ( RELATED ( Product[UnitCost] ), 0 ) would drop cost to 19 if Mug's cost were missing, inflating margin to 168 and making Mug look like pure profit.

**How to confirm:** Count Sales lines where RELATED(Product[UnitCost]) is BLANK. On the current data expect 0 such lines and a margin of 143.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
