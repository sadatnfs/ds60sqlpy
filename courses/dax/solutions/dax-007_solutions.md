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

### Exercise 2

Change the displayed currency prefix without changing NumericRevenue.

A different label or format string changes text only; it does not convert USD into another currency.

### Exercise 3

Write a result row containing quantity, revenue and revenue per unit.

Use SUM(Sales[Quantity]), [NetRevenue] and DIVIDE([NetRevenue],SUM(Sales[Quantity])); the values are 17, 187 and 11.

### Exercise 4

Diagnose sorting currency text alphabetically.

Lexical order need not match numeric order. Sort by the numeric measure rather than its formatted string.

### Exercise 5

Explain whether multiplying a percentage by an amount preserves a meaningful unit.

Multiplying 0.1 by 187 gives 18.7 USD. Multiplying by 10 instead would be a hundredfold scaling error.

### Exercise 6

Transfer the distinction to a duration shown as 02:30.

Define the stored numeric duration and unit separately from the formatted label before aggregation.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
