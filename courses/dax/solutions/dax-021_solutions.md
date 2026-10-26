# dax-021: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-021_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Calculate additive row amounts

All eight Sales rows; Discount is a currency amount per line.

| Gross | Net |
| --- | --- |
| 195 | 187 |

If Discount represented a percentage or per-unit amount, this expression would be wrong even though its arithmetic is valid. The data dictionary is part of the formula contract.

- The line gross amounts are 20, 5, 40, 30, 20, 20, 20 and 40.
- Their sum is 195; the line discounts sum to 8.
- Subtracting each line's discount yields net total 187.

### Case B: Average sold products or the complete catalog

All four Product rows; Bag has no sales and a blank revenue measure.

| NonblankProducts | AllCatalogProducts |
| --- | --- |
| 62.33333333 | 46.75 |

The lower second average reflects a broader denominator, not worse arithmetic. Label the population as sold products or all catalog products.

- Per-product results are 67, 24, 96 and BLANK.
- AVERAGEX over the nonblank numerical results divides 187 by 3.
- COALESCE changes Bag to zero, so the average divides 187 by 4.

## Explained practice answers

### Exercise 1

Predict the net amount if each line's discount is subtracted twice.

The incorrect total would be 195 - 16 = 179.

### Exercise 2

Filter to Blue before calculating gross and net.

Gross is 170 and net is 163; blue-line discounts total 7.

### Exercise 3

Write a customer-level average revenue for customers with sales.

AVERAGEX(Customer,[NetRevenue]) averages 51,80,56 and excludes Di's BLANK, yielding 187/3.

### Exercise 4

Diagnose calling the mean product revenue an average unit price.

AVERAGEX(Product,[NetRevenue]) is USD per contributing product. Net unit price is 187/17 = 11.

### Exercise 5

Explain what adding another unsold catalog product does to the two averages.

The nonblank average stays 187/3; the zero-filled catalog average becomes 187/5.

### Exercise 6

Transfer the choice to average regional performance.

An equal-region average and a pooled customer-weighted rate answer different questions; state the estimand before selecting the iterator.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
