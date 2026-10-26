# dax-010: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-010_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Whole-model populations

All rows; complete nonblank order/customer fact keys.

| Revenue | Lines | Orders | CustomersWithSales |
| --- | --- | --- | --- |
| 187 | 8 | 7 | 3 |

Counting Customer rows would produce four, which is a valid catalog population but a different metric.

- Eight SaleID values represent eight lines.
- Order 101 repeats across two lines, leaving seven orders.
- The fact includes customer keys 10, 20 and 30.

### Case B: Paper's overlapping order population

Paper products 1 and 2; all years and customers otherwise allowed.

| Revenue | Lines | Orders | CustomersWithSales |
| --- | --- | --- | --- |
| 91 | 5 | 4 | 3 |

A lower revenue total does not imply fewer distinct customers. One population can remain unchanged while another metric changes substantially.

- Five eligible lines total 91.
- Their order keys are 101, 101, 201, 202 and 204.
- All three purchasing customers still appear, but only four distinct orders remain.

## Explained practice answers

### Exercise 1

Predict customer counts for Paper and Home separately.

Paper has 3 customers and Home has 2; their sum 5 exceeds the whole-model distinct count 3.

### Exercise 2

Restrict Paper to 2025 and predict order count.

Orders 201, 202 and 204 remain: three orders.

### Exercise 3

Write two separate measures for catalog customers and customers with sales.

COUNTROWS(Customer) counts catalog members; DISTINCTCOUNT(Sales[CustomerKey]) counts purchasing identities in eligible facts.

### Exercise 4

Diagnose a grand total built by adding per-category distinct customers.

The same customer can be counted repeatedly. Reevaluate the distinct-count measure in total context.

### Exercise 5

Explain how blank keys change DISTINCTCOUNT.

A blank can count as one distinct value. Decide whether it is an unknown bucket or excluded quality failure.

### Exercise 6

Transfer the reasoning to daily active users.

The sum of daily distinct users measures user-days, not monthly unique users; both can be useful if named correctly.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
