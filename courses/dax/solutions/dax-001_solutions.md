# dax-001: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-001_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: All eight lines

No filters; regular active relationships; USD sales-line grain.

| NetRevenue |
| --- |
| 187 |

The answer is attached to a defined population of lines. It is not proof that every business revenue policy has been represented. Changing the question to refunded revenue would require another fact or calculation.

- Eligible lines are S1 through S8.
- Add 20 + 4 + 40 + 27 + 20 + 20 + 20 + 36.
- The total is 187 USD before returns and tax.

### Case B: Notebook product only

ProductKey 1; the Product-to-Sales relationship is active and single-direction.

| NetRevenue |
| --- |
| 67 |

The measure text did not change. Its eligible rows did. A report selection must be part of the explanation whenever someone compares this 67 with the overall 187.

- ProductKey 1 identifies Notebook, not all products in the Paper category.
- The key filter admits Sales S1, S4 and S7.
- 20 + 27 + 20 = 67 USD.

## Explained practice answers

### Exercise 1

Predict the all-line quantity alongside revenue.

Quantity is 17; revenue is 187 USD. Their units differ.

### Exercise 2

Change the product question from Notebook to Mug and list the contributing lines.

S3, S6 and S8 contribute 40 + 20 + 36 = 96.

### Exercise 3

Write a one-row query that names the output QuantitySold.

EVALUATE ROW ( "QuantitySold", SUM ( Sales[Quantity] ) ) gives 17.

### Exercise 4

Diagnose a report labeled net profit that displays 187.

The fixture total is sales after line discounts, before cost, returns and tax. Profit is a different measure.

### Exercise 5

Explain what happens in this classroom after editing 187 into a draft comment.

Only the draft changes. The hand-derived reference table remains bound to the reference file and model.

### Exercise 6

Describe the evidence needed to call an exported formula engine-tested.

Record the actual engine/version, model, filter context, exact submitted source and observed output. Offline comparison supplies none of those execution observations.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
