# dax-028: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-028_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Intersection and one-sided difference

Distinct Paper keys{1,2} and Blue keys{1,3} from the clean model.

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
- DISTINCT removes repeated key rows, leaving 1,2,3.
- The two counts represent memberships versus unique product identities.

## Explained practice answers

### Exercise 1

List EXCEPT(BlueKeys,PaperKeys), not just its count.

It contains key 3, Mug.

### Exercise 2

Add a repeated key 1 to an input before UNION.

The combined row count increases, while DISTINCT over the combined keys remains three.

### Exercise 3

Write an eligible-product union that should contain each key once.

Use DISTINCT(UNION(PaperKeys,BlueKeys)) for this one-column key example.

### Exercise 4

Diagnose deleting duplicates from Sales to imitate a unique product list.

Repeated ProductKey values in Sales can be valid transactions; deduplicating them would lose revenue.

### Exercise 5

Explain why matching column counts is insufficient for a safe union.

Combining product codes with customer codes can be semantically wrong even if both are integers in one column.

### Exercise 6

Transfer the distinction to campaign audiences.

Unique reach uses a deduplicated person set, while audience memberships can count the same person several times; label them separately.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
