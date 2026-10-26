# dax-014: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-014_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: One region in one year

Customer.Region = North and Date.Year = 2025, using active OrderDate.

| Revenue |
| --- |
| 83 |

The same regional total across all years would be 107. Omitting the year from an explanation would conceal why those two correct values differ.

- North supplies customer keys 10 and 30.
- Year 2025 removes S1, S2 and S3.
- S4, S5 and S8 remain: 27 + 20 + 36 = 83.

### Case B: A multi-selection retains the year

Region is the allowed set {North, South}; order year remains 2025.

| Revenue |
| --- |
| 123 |

Broadening one filter does not remove the others. The answer does not return to the all-year total 187.

- The region set admits all three customers with sales.
- The year filter still excludes the three 2024 lines.
- S4 through S8 total 123.

## Explained practice answers

### Exercise 1

Predict 2025 South revenue.

S6 and S7 contribute 20 each, totaling 40.

### Exercise 2

Add Product.Category = Paper to case B.

S4, S5 and S7 remain, totaling 67.

### Exercise 3

Write a context ledger for North, Home and 2025.

North admits customers 10/30, Home admits product 3, and 2025 keeps S8; revenue is 36.

### Exercise 4

Diagnose a report comparing North 2025 with South across all years.

The comparison mixes 83 with 80 rather than comparable-year 83 with 40. Define the intended period consistently.

### Exercise 5

Predict a West-plus-2025 selection.

The result is BLANK because customer 40 has no Sales rows.

### Exercise 6

Transfer the ledger to a dashboard with several pages.

Capture effective filters, date role and relationship assumptions for each reported number, not only the visible slicer caption.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
