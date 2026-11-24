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

**Why it fits this model:** DISTINCTCOUNT(Sales[CustomerKey]) is evaluated in each category. Paper reaches Ada, Bo and Cy (3); Home reaches Bo and Cy (2). Bo and Cy bought in both.

**Tempting mistake:** Adding the category counts gives 5 customers, but the whole model has only three customers with sales. Overlapping populations are not additive.

**How to confirm:** `SUMMARIZECOLUMNS ( ROLLUPADDISSUBTOTAL ( Product[Category], "IsTotal" ), "Customers", DISTINCTCOUNT ( Sales[CustomerKey] ) )` shows 3, 2 and a total of 3.

### Exercise 2

Restrict Paper to 2025 and predict order count.

Orders 201, 202 and 204 remain: three orders.

**Why it fits this model:** Removing 2024 drops order 101, which held two Paper lines (S1 and S2). Paper keeps S4, S5 and S7 in orders 201, 202 and 204, for 3 orders and 67 USD.

**Tempting mistake:** Subtracting the two removed lines from Paper's four orders gives 2. That treats lines as orders, though both removed lines came from one order.

**How to confirm:** `CALCULATE ( [OrderCount], Product[Category] = "Paper", 'Date'[Year] = 2025 )` returns 3, and NetRevenue under the same filters returns 67.

### Exercise 3

Write two separate measures for catalog customers and customers with sales.

COUNTROWS(Customer) counts catalog members; DISTINCTCOUNT(Sales[CustomerKey]) counts purchasing identities in eligible facts.

**Why it fits this model:** COUNTROWS(Customer) counts catalog members (4, including Di), while DISTINCTCOUNT(Sales[CustomerKey]) counts buyers in eligible facts (3). Under West these are 1 and BLANK.

**Tempting mistake:** Using COUNTROWS(Customer) as "customers who bought Paper" returns 4, because the single-direction relationship does not filter Customer from Product through Sales.

**How to confirm:** Under Paper expect a catalog count of 4 and a buyer count of 3; under West expect 1 and BLANK.

### Exercise 4

Diagnose a grand total built by adding per-category distinct customers.

The same customer can be counted repeatedly. Reevaluate the distinct-count measure in total context.

**Why it fits this model:** Each product has two buyers: Notebook (Ada, Bo), Pen (Ada, Cy) and Mug (Bo, Cy). The total row must reevaluate DISTINCTCOUNT over all eight lines, which gives 3.

**Tempting mistake:** `SUMX ( VALUES ( Product[Product] ), [Customers] )` adds 2 + 2 + 2 and reports 6 customers, double counting every buyer.

**How to confirm:** The per-product rows show 2, 2 and 2 while the total row shows 3, the same as the whole-model case.

### Exercise 5

Explain how blank keys change DISTINCTCOUNT.

A blank can count as one distinct value. Decide whether it is an unknown bucket or excluded quality failure.

**Why it fits this model:** DISTINCTCOUNT treats BLANK as one more distinct value. If one sales line lacked a CustomerKey, the count would rise from 3 to 4 without any new person.

**Tempting mistake:** Reporting 4 as customers counts an unknown bucket as a buyer; quietly dropping the line instead hides a data-quality failure.

**How to confirm:** With such a row, DISTINCTCOUNT returns 4, DISTINCTCOUNTNOBLANK returns 3 and COUNTBLANK(Sales[CustomerKey]) returns 1, so all three can be reported.

### Exercise 6

Transfer the reasoning to daily active users.

The sum of daily distinct users measures user-days, not monthly unique users; both can be useful if named correctly.

**Why it fits this model:** In 2025 each sales date has one buyer: Ada on January 2, Cy on January 3, Bo on January 5, Bo on February 2 and Cy on February 3. Their sum, 5, is a count of customer-days.

**Tempting mistake:** Calling that 5 the unique 2025 customers overstates the population, because only Ada, Bo and Cy bought that year; Bo and Cy are counted twice.

**How to confirm:** Under 2025, `SUMX ( VALUES ( 'Date'[Date] ), DISTINCTCOUNT ( Sales[CustomerKey] ) )` returns 5 and DISTINCTCOUNT alone returns 3.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
