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

**Why it fits this model:** Discount is a currency amount per line, so each line is Quantity x UnitPrice minus Discount, once. The discounts are S2 1, S4 3 and S8 4, which add to 8.

**Tempting mistake:** Subtracting SUM(Sales[Discount]) again after a SUMX that already subtracted it removes 16 and returns 179.

**How to confirm:** Net is 187, and S8 alone checks as 2 x 20 - 4 = 36.

### Exercise 2

Filter to Blue before calculating gross and net.

Gross is 170 and net is 163; blue-line discounts total 7.

**Why it fits this model:** Blue keeps Notebook and Mug, lines S1, S3, S4, S6, S7 and S8. Their gross is 170, their discounts are S4 3 and S8 4, and net is 163.

**Tempting mistake:** Treating Discount as a rate, Quantity x UnitPrice x (1 - Discount), turns S4 into 30 x (1 - 3) = -60 and S8 into -120, which are impossible line amounts.

**How to confirm:** Under Blue expect Gross 170 and Net 163; the difference, 7, equals the Blue discounts.

### Exercise 3

Write a customer-level average revenue for customers with sales.

AVERAGEX(Customer,[NetRevenue]) averages 51, 80, 56 and excludes Di's BLANK, yielding 187/3.

**Why it fits this model:** AVERAGEX over Customer transitions each row, so it averages Ada 51, Bo 80 and Cy 56. Di's BLANK is skipped, which gives 187 / 3, about 62.33.

**Tempting mistake:** DIVIDE([NetRevenue], COUNTROWS(Customer)) counts Di and returns 46.75. AVERAGE(Sales[NetAmount]) gives 23.375, which is revenue per line, not per customer.

**How to confirm:** Expect about 62.33, and a matching DIVIDE ( [NetRevenue], DISTINCTCOUNT ( Sales[CustomerKey] ) ).

### Exercise 4

Diagnose calling the mean product revenue an average unit price.

AVERAGEX(Product,[NetRevenue]) is USD per contributing product. Net unit price is 187/17 = 11.

**Why it fits this model:** AVERAGEX(Product, [NetRevenue]) divides 187 by three selling products, so it is 62.33 USD per product. A unit price divides revenue by units: 187 / 17 = 11.

**Tempting mistake:** Labeling 62.33 an average unit price overstates it more than five times, since its denominator counts products, not the 17 units sold.

**How to confirm:** `DIVIDE ( [NetRevenue], SUM ( Sales[Quantity] ) )` returns 11, while the product average stays about 62.33.

### Exercise 5

Explain what adding another unsold catalog product does to the two averages.

The nonblank average stays 187/3; the zero-filled catalog average becomes 187/5.

**Why it fits this model:** AVERAGEX skips BLANK, so a new unsold product changes nothing in the nonblank average, 187 / 3. COALESCE turns it into a 0, so the catalog average becomes 187 / 5 = 37.4.

**Tempting mistake:** Expecting both averages to stay put misses that the zero-filled version counts every catalog member, as it already does for Bag (187 / 4 = 46.75).

**How to confirm:** Today the results are about 62.33 and 46.75. With one more unsold product expect about 62.33 and 37.4.

### Exercise 6

Transfer the choice to average regional performance.

An equal-region average and a pooled customer-weighted rate answer different questions; state the estimand before selecting the iterator.

**Why it fits this model:** Decide what gets equal weight. Regions give North 107 and South 80 (average 93.5). Customers give 187 / 3, about 62.33.

**Tempting mistake:** Averaging per-region customer averages, North (51 + 56) / 2 = 53.5 and South 80, gives 66.75 and presents it as the average customer, which favors Bo.

**How to confirm:** AVERAGEX over regions of [NetRevenue] returns 93.5, and AVERAGEX over Customer returns about 62.33; label each for what it weights.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
