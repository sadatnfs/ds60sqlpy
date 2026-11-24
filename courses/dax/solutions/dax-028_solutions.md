# dax-028: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-028_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Intersection and one-sided difference

Distinct Paper keys {1,2} and Blue keys {1,3} from the clean model.

| IntersectionRows | PaperOnlyRows |
| --- | --- |
| 1 | 1 |

A count of one in both differences does not mean the selected entities are identical. Retain the actual key sets in a review trace.

- The shared key is 1, so the intersection has one row.
- Key 2 belongs to Paper but not Blue.
- Reversing the difference would return key 3 instead, a different population.

### Case B: UNION keeps repeated membership rows

Concatenate the two two-row key tables; key 1 occurs in each input.

| CombinedRows | DistinctKeys |
| --- | --- |
| 4 | 3 |

If the downstream calculation iterates the concatenation, key 1 can contribute twice. A filter set and an iterator's row population should not be conflated.

- UNION produces four rows, including key 1 twice.
- DISTINCT removes repeated key rows, leaving 1, 2, 3.
- The two counts represent memberships versus unique product identities.

## Explained practice answers

### Exercise 1

List EXCEPT(BlueKeys,PaperKeys), not just its count.

It contains key 3, Mug.

**Why it fits this model:** EXCEPT keeps rows of its first argument that are absent from the second. Blue keys are {1, 3}, Paper keys {1, 2}, so EXCEPT(BlueKeys, PaperKeys) is {3}, Mug.

**Tempting mistake:** Treating EXCEPT as symmetric and reusing case A's PaperOnlyRows, {2} Pen. Pen is the answer to the opposite question.

**How to confirm:** `CONCATENATEX ( EXCEPT ( BlueKeys, PaperKeys ), Product[ProductKey], "," )` returns "3", and using it as a filter returns Mug's 96.

### Exercise 2

Add a repeated key 1 to an input before UNION.

The combined row count increases, while DISTINCT over the combined keys remains three.

**Why it fits this model:** UNION concatenates every row. With an extra key 1 the inputs contribute 3 + 2 = 5 rows, while DISTINCT still finds keys 1, 2 and 3.

**Tempting mistake:** Expecting UNION to behave like SQL UNION and remove repeats, so CombinedRows stays 4 or drops to 3.

**How to confirm:** CombinedRows reads 5 and DistinctKeys reads 3.

### Exercise 3

Write an eligible-product union that should contain each key once.

Use DISTINCT(UNION(PaperKeys,BlueKeys)) for this one-column key example.

**Why it fits this model:** The eligible list is an entity list, so uniqueness is part of its contract. DISTINCT(UNION(PaperKeys, BlueKeys)) returns Notebook, Pen and Mug once each.

**Tempting mistake:** Iterating the raw union with SUMX adds Notebook twice, 67 + 67 + 24 + 96 = 254, which exceeds total revenue 187.

**How to confirm:** The distinct list has 3 rows, and SUMX over it of [NetRevenue] returns 187.

### Exercise 4

Diagnose deleting duplicates from Sales to imitate a unique product list.

Repeated ProductKey values in Sales can be valid transactions; deduplicating them would lose revenue.

**Why it fits this model:** Sales is at line grain, and repeated ProductKey values are separate sales. Notebook alone has S1, S4 and S7. A unique product list comes from VALUES(Product[ProductKey]) or DISTINCT(Sales[ProductKey]).

**Tempting mistake:** Keeping only one line per key in Sales, say S1, S2 and S3, leaves 64 USD of the 187 and discards five real transactions.

**How to confirm:** DISTINCT(Sales[ProductKey]) returns 3 rows, while COUNTROWS(Sales) stays 8 and revenue stays 187.

### Exercise 5

Explain why matching column counts is insufficient for a safe union.

Combining product codes with customer codes can be semantically wrong even if both are integers in one column.

**Why it fits this model:** UNION pairs columns by position, and both inputs must mean the same entity. Two Product key lists are compatible; Product keys and Customer keys are not.

**Tempting mistake:** Unioning PaperKeys {1, 2} with customer keys {10, 20} gives four integer rows. Mapped onto Product[ProductKey], only two of them filter anything, so the list claims 4 eligible items while revenue covers 2.

**How to confirm:** COUNTROWS of the mixed union is 4, but `CALCULATE ( COUNTROWS ( Product ), TREATAS ( MixedKeys, Product[ProductKey] ) )` is 2.

### Exercise 6

Transfer the distinction to campaign audiences.

Unique reach uses a deduplicated person set, while audience memberships can count the same person several times; label them separately.

**Why it fits this model:** Reach counts each person once, and memberships count each pair. In the analytics model Newsletter has Ada and Bo and Prospects has Bo and Cy, so reach is 3 and memberships are 4.

**Tempting mistake:** Reporting COUNTROWS(GroupMembership) as campaign reach counts Bo twice and overstates the unique audience by a third.

**How to confirm:** COUNTROWS(DISTINCT(GroupMembership[CustomerKey])) returns 3, and COUNTROWS(GroupMembership) returns 4.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
