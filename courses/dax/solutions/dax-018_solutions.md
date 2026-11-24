# dax-018: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-018_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Products above fifty

No incoming filters; consider each visible ProductKey independently.

| Products | Revenue |
| --- | --- |
| 2 | 163 |

The threshold is applied to each product's measure result. A single comparison of the grand total would not perform this segmentation.

- Candidate revenues are Notebook 67, Pen 24, Mug 96 and Bag BLANK.
- Keys 1 and 3 exceed 50.
- Applying those retained keys yields 67 + 96 = 163.

### Case B: A stricter threshold

Same candidate population, threshold changed from 50 to 90.

| Products | Revenue |
| --- | --- |
| 1 | 96 |

Changing the threshold changes membership, not the source's definition of revenue. Keep both decisions visible in a segmentation specification.

- Notebook no longer qualifies because 67 is not greater than 90.
- Mug's 96 still qualifies.
- The retained one-key table filters the final measure to 96.

## Explained practice answers

### Exercise 1

Predict the retained products at threshold 24 using >.

Notebook and Mug qualify; Pen at exactly 24 does not.

**Why it fits this model:** FILTER evaluates [NetRevenue] once per ProductKey. Notebook (67) and Mug (96) exceed 24, while Pen equals 24 and Bag is BLANK, so revenue is 163.

**Tempting mistake:** Filtering lines with Sales[NetAmount] > 24 answers a different question. It keeps S3, S4 and S8 for 103, because it tests lines, not product totals.

**How to confirm:** The candidate table has 2 rows and CALCULATE over it returns 163.

### Exercise 2

Change > 24 to >= 24.

Pen is added, so three products qualify and their revenue is 187.

**Why it fits this model:** With >= 24, Pen's 24 also qualifies. Bag's BLANK compares as 0, which is below 24, so three products qualify and revenue is 187.

**Tempting mistake:** Lowering the threshold to >= 0 would also admit Bag, because BLANK >= 0 is TRUE, so a product with no sales would join the list.

**How to confirm:** Expect Products 3 and Revenue 187, and check that Bag is not in the list.

### Exercise 3

Write a selection for customers with revenue above 55.

Bo at 80 and Cy at 56 qualify; Ada at 51 and Di at BLANK do not. Their total is 136.

**Why it fits this model:** Iterate VALUES(Customer[CustomerKey]) and invoke [NetRevenue] per key. Bo (80) and Cy (56) exceed 55, Ada (51) does not and Di is BLANK.

**Tempting mistake:** `FILTER ( Sales, Sales[NetAmount] > 55 )` checks single lines, and the largest line is 40, so the result is BLANK.

**How to confirm:** Expect 2 customers with revenue 80 + 56 = 136.

### Exercise 4

Diagnose CALCULATE([NetRevenue], [NetRevenue] > 50).

Use FILTER over a deliberate candidate table so the measure has a per-candidate evaluation context.

**Why it fits this model:** A simple Boolean filter in CALCULATE must test a column. FILTER over VALUES(Product[ProductKey]) gives the measure one product context per candidate.

**Tempting mistake:** `FILTER ( Sales, [NetRevenue] > 50 )` runs but transitions to single lines, and since no line exceeds 50 it returns an empty table and BLANK.

**How to confirm:** The ProductKey candidate version returns 2 products and 163, as in case A.

### Exercise 5

Predict a threshold above every product's revenue.

No product qualifies. COUNTROWS(Qualifying) and the final SUM result are BLANK in this case.

**Why it fits this model:** Mug's 96 is the largest product total, so a threshold of 100 leaves the candidate table empty. CALCULATE with an empty filter table sees no rows.

**Tempting mistake:** Assuming an empty filter means no filter predicts 187. It actually admits no products, so revenue is BLANK.

**How to confirm:** At > 100 the row should read Products BLANK and Revenue BLANK.

### Exercise 6

Transfer the pattern to dynamic customer segments.

A segment based on current-period revenue must state its period and whether unsold or previously filtered customers are eligible candidates.

**Why it fits this model:** State the period and the candidates. Under 2025, Ada has 27, Bo 40 and Cy 56, so only Cy exceeds 50. Over all years, Ada (51), Bo (80) and Cy (56) all do.

**Tempting mistake:** Building the segment over all years but reporting it in a 2025 view labels Ada high value, though her 2025 revenue is 27.

**How to confirm:** Under 2025 the FILTER returns Cy alone with 56; with no year filter it returns three customers and 187.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
