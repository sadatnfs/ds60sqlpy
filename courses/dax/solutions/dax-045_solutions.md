# dax-045: explained reference and practice reasoning

Verify that the reference's two cases differ only in which item expression is outermost, returning 177.3 and 178.3. Your notes should name the precedence assumption behind each number. Read it beside the [reference source](dax-045_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: Scale has higher precedence

Specified items: AddTen = SELECTEDMEASURE()+10 at lower precedence; Scale = SELECTEDMEASURE()*0.9 at higher precedence.

| ExpandedValue |
| --- |
| 177.3 |

The literal 10 represents an illustrative compatible amount for this algebra example. A real fee policy would also define which population and measures receive it.

- The outer Scale expression receives the lower-precedence AddTen expression.
- The expansion is (187 + 10)*0.9.
- 197 multiplied by 0.9 is 177.3.

### Case B: Addition has higher precedence

The same two item definitions with AddTen as the higher-precedence outer expression.

| ExpandedValue |
| --- |
| 178.3 |

Passing tests for each group alone does not prove their combined behavior. Include interacting groups in a measure/context regression matrix.

- The expansion is (187*0.9)+10.
- The scale first yields 168.3.
- Adding 10 gives 178.3, one more than the other order.

## Explained practice answers

### Exercise 1

Predict both expansions for a base value 100.

Scale-after-add gives 99; add-after-scale gives 100.

**Why it fits this model:** Precedence sets nesting. In case A, Scale (higher) is applied outside AddTen, giving (100 + 10) x 0.9. In case B, AddTen is outside, giving 100 x 0.9 + 10.

**Tempting mistake:** Treating the two items as commutative because both are simple arithmetic. They differ by 1 at base 100, as at 187.

**How to confirm:** (100 + 10) x 0.9 = 99 and 100 x 0.9 + 10 = 100.

### Exercise 2

Replace the additive 10 by zero.

Both expressions become 0.9 times the base, so that case cannot validate the intended order.

**Why it fits this model:** With an additive 0, both orders reduce to 0.9 times the base: 187 x 0.9 = 168.3 in either order.

**Tempting mistake:** Using this zero case as the regression test and concluding precedence is correct, when it cannot tell the orders apart.

**How to confirm:** Both expansions return 168.3. Keep a nonzero offset, as in case A's 177.3 and case B's 178.3, in the test grid.

### Exercise 3

Write a regression grid for two interacting groups.

Record each group's selection, precedence, underlying measure, filters, expanded numeric expression and expected format pattern.

**Why it fits this model:** The grid covers each item alone, both items, and an unaffected measure: base 187, AddTen alone 197, Scale alone 168.3, both 177.3 with Scale higher, and QuantitySold 17 if guarded.

**Tempting mistake:** Testing only the combined row. A wrong expression in one item can be hidden by the other.

**How to confirm:** Each grid row lists its selection, precedence, measure, filter context, expanded expression, expected value and expected format string.

### Exercise 4

Diagnose fixing a wrong number by changing its format string.

Repair composition or the business policy first. Formatting can only change how the numeric result is displayed.

**Why it fits this model:** A format string changes only how a number is shown. If 178.3 is expected and 177.3 appears, the items are nested in the wrong order.

**Tempting mistake:** Changing the format to zero decimals and calling it fixed: 177.3 shows as 177, still not 178, and the nesting is unchanged.

**How to confirm:** Fix the precedence or item expression first, then confirm the raw value, 178.3 or 177.3 as specified, before applying a format.

### Exercise 5

Explain a percentage format on the value 177.3.

It would imply a different unit and misleading scale; keep currency and ratio measures' format policies distinct.

**Why it fits this model:** 177.3 is a USD amount. A percentage format multiplies the display by 100.

**Tempting mistake:** Applying "0.0%" to this measure shows 17730.0%, a unit change that makes a revenue figure look like a ratio.

**How to confirm:** Keep currency formats on currency measures, and use percentage formats only on fractions such as NetMargin (about 0.765).

### Exercise 6

Transfer precedence reasoning to currency conversion and time intelligence.

Expand the combined expressions and verify transaction/rate grain and date-role behavior; arithmetic examples alone do not qualify a real currency/time group combination.

**Why it fits this model:** Combining a currency item with a time item works like the AddTen and Scale nesting, except that conversion depends on transaction-date rates.

**Tempting mistake:** Converting a shifted total with one rate. Lesson dax-042 shows 150 EUR at transaction rates is 170 USD, but at the highest rate it is 180.

**How to confirm:** Expand both orders for a known case and compare with row-level conversion; the date-role and rate-grain cases need their own tests.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
