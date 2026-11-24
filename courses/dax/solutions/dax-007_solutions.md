# dax-007: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-007_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: A row of distinct types

Literal expressions; no model filter is needed.

| Count | Ratio | Larger | Day |
| --- | --- | --- | --- |
| 3 | 1.5 | TRUE | 2025-01-02 |

Putting values in the same row does not make them interchangeable. The ratio is not a count of one and a half transactions; its unit depends on its numerator and denominator.

- The whole-number literal is 3.
- Three divided by two is 1.5, while the comparison is TRUE.
- DATE constructs 2025-01-02; a different display format would not change that date.

### Case B: A number and its text label

All retail sales; a numeric result and an explicitly formatted text representation.

| NumericRevenue | DisplayText |
| --- | --- |
| 187 | $187.00 |

Replacing every revenue measure with FORMAT can break numerical behavior even when the report looks correct. Numeric measures and display policy should remain separate.

- The measure evaluates to numeric 187.
- FORMAT renders the same amount as the text $187.00.
- The original number remains available for later arithmetic.

## Explained practice answers

### Exercise 1

Predict 2 + 3 * 4 and (2 + 3) * 4.

The results are 14 and 20. Parentheses change the expression's structure.

**Why it fits this model:** DAX binds multiplication tighter than addition, so 2 + 3 * 4 first forms 12 and then adds 2. The parentheses build a different tree whose sum 5 is multiplied by 4.

**Tempting mistake:** Reading the expression strictly left to right gives 20 for both forms, which hides the fact that the parentheses changed the structure rather than the style.

**How to confirm:** `EVALUATE ROW ( "Plain", 2 + 3 * 4, "Grouped", ( 2 + 3 ) * 4 )` returns 14 and 20.

### Exercise 2

Change the displayed currency prefix without changing NumericRevenue.

A different label or format string changes text only; it does not convert USD into another currency.

**Why it fits this model:** NumericRevenue is SUM(Sales[NetAmount]), a USD number of 187. FORMAT only produces DisplayText, so a euro sign in place of the dollar sign changes a string and leaves the number alone.

**Tempting mistake:** Showing 187.00 with a euro sign claims a conversion that never happened. At an assumed 1.10 USD per EUR the same sales would be about 170 EUR, so the label would overstate them.

**How to confirm:** Both rows keep NumericRevenue at 187; only the DisplayText column differs, and no rate table appears anywhere in the query.

### Exercise 3

Write a result row containing quantity, revenue and revenue per unit.

Use SUM(Sales[Quantity]), [NetRevenue] and DIVIDE([NetRevenue],SUM(Sales[Quantity])); quantity is 17, revenue is 187 and revenue per unit is 11.

**Why it fits this model:** Each output keeps its own unit: 17 units, 187 USD and their ratio of totals, 11 USD per unit. The ratio pools all eight lines, so heavy lines such as S5's four Pens weigh more.

**Tempting mistake:** AVERAGE(Sales[UnitPrice]) returns 100 / 8 = 12.5. It averages list prices per line and ignores both quantities and the 8 USD of discounts.

**How to confirm:** The row reads quantity 17, revenue 187 and per unit 11, and 11 x 17 reproduces 187.

### Exercise 4

Diagnose sorting currency text alphabetically.

Lexical order need not match numeric order. Sort by the numeric measure rather than its formatted string.

**Why it fits this model:** FORMAT returns text, and text compares character by character. The line amounts 4, 20, 27, 36 and 40 become strings whose order follows their first digits, not their size.

**Tempting mistake:** Sorting the DisplayText column puts S2's "$4.00" after "$36.00" and before "$40.00", because "." sorts before "0". The smallest line then looks mid-sized.

**How to confirm:** Order the rows by Sales[NetAmount] and expect 4, 20, 20, 20, 20, 27, 36, 40; the text labels can then follow that numeric order.

### Exercise 5

Explain whether multiplying a percentage by an amount preserves a meaningful unit.

Multiplying 0.1 by 187 gives 18.7 USD. Multiplying by 10 instead would be a hundredfold scaling error.

**Why it fits this model:** A rate of 0.1 is dimensionless, so 0.1 x 187 USD stays in USD and gives 18.7. The percent sign in a label is only a display convention for that fraction.

**Tempting mistake:** Typing the displayed "10" into the formula multiplies 187 by 10 and reports 1,870 USD, a hundredfold error that still looks like a plausible dollar figure.

**How to confirm:** `ROW ( "Fee", 0.1 * [NetRevenue] )` returns 18.7, and 18.7 / 187 returns the 0.1 rate back.

### Exercise 6

Transfer the distinction to a duration shown as 02:30.

Define the stored numeric duration and unit separately from the formatted label before aggregation.

**Why it fits this model:** The label 02:30 could mean 150 minutes, 150 seconds or half past two at night. Storing a number with a declared unit, such as 150 minutes, lets SUM and AVERAGE mean something.

**Tempting mistake:** Parsing the string as minutes and seconds gives 150 seconds while hours and minutes gives 150 minutes, a sixtyfold disagreement that no formatting choice reveals.

**How to confirm:** Two stored durations of 150 minutes sum to 300 minutes, which you may then format as 05:00 after an explicit conversion from minutes to hours.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
