# Original DAX model fixtures

These small data sets are invented for this course. They describe a model contract for hand reasoning; opening a CSV or JSON file does not install a semantic model. Every named reference states which model and context it assumes.

## Retail grain and units

A Sales row is an order line, not an order or customer. NetAmount is quantity times unit price minus a line discount, in USD before tax and returns. Order 101 has two lines. Product and Customer keys are unique; Bag and Di intentionally have no sales. The Date table contains every day in 2024 and 2025, including leap day.

Active one-to-many filters flow from Product, Customer and Date to Sales through OrderDate. The alternative Date-to-ShipDate relationship is inactive. Additional relationships below are explicit; matching names alone never create a join or filter path.

## Eight-line retail model

[Typed specification](retail/model.json)

Original synthetic USD sales. NetAmount = Quantity * UnitPrice - line Discount. No tax or returns are included in NetAmount.

- Dates have no time component.
- All ordinary retail amounts are USD.
- The one side is unique; normal foreign keys are complete.
- Relationships are regular Import-style relationships for hand reasoning, not live engine metadata.
- The Date table contains 731 dates; guides show relevant slices rather than hide unselected dates.

### Product (retail)

**Grain:** one row per product. **Key:** ProductKey. **Rows:** 4.

[Complete CSV](retail/Product.csv)

Types: `ProductKey` (integer), `Product` (text), `Category` (text), `Color` (text), `UnitCost` (number).

| ProductKey | Product | Category | Color | UnitCost |
| --- | --- | --- | --- | --- |
| 1 | Notebook | Paper | Blue | 2 |
| 2 | Pen | Paper | Red | 1 |
| 3 | Mug | Home | Blue | 5 |
| 4 | Bag | Travel | Green | 10 |

### Customer (retail)

**Grain:** one row per customer. **Key:** CustomerKey. **Rows:** 4.

[Complete CSV](retail/Customer.csv)

Types: `CustomerKey` (integer), `Customer` (text), `Region` (text), `Segment` (text).

| CustomerKey | Customer | Region | Segment |
| --- | --- | --- | --- |
| 10 | Ada | North | Retail |
| 20 | Bo | South | Retail |
| 30 | Cy | North | Trade |
| 40 | Di | West | Retail |

### Sales (retail)

**Grain:** one order line; OrderID can repeat. **Key:** SaleID. **Rows:** 8.

[Complete CSV](retail/Sales.csv)

Types: `SaleID` (text), `OrderID` (integer), `ProductKey` (integer), `CustomerKey` (integer), `OrderDate` (date), `ShipDate` (date), `Quantity` (integer), `UnitPrice` (number), `Discount` (number), `NetAmount` (number).

| SaleID | OrderID | ProductKey | CustomerKey | OrderDate | ShipDate | Quantity | UnitPrice | Discount | NetAmount |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | 101 | 1 | 10 | 2024-01-02 | 2024-01-04 | 2 | 10 | 0 | 20 |
| S2 | 101 | 2 | 10 | 2024-01-02 | 2024-01-04 | 1 | 5 | 1 | 4 |
| S3 | 102 | 3 | 20 | 2024-01-03 | 2024-01-05 | 2 | 20 | 0 | 40 |
| S4 | 201 | 1 | 10 | 2025-01-02 | 2025-01-04 | 3 | 10 | 3 | 27 |
| S5 | 202 | 2 | 30 | 2025-01-03 | 2025-01-08 | 4 | 5 | 0 | 20 |
| S6 | 203 | 3 | 20 | 2025-01-05 | 2025-02-01 | 1 | 20 | 0 | 20 |
| S7 | 204 | 1 | 20 | 2025-02-02 | 2025-02-03 | 2 | 10 | 0 | 20 |
| S8 | 205 | 3 | 30 | 2025-02-03 | 2025-02-04 | 2 | 20 | 4 | 36 |

### Date (retail)

**Grain:** one calendar day, complete 2024 and 2025. **Key:** Date. **Rows:** 731.

[Complete CSV](retail/Date.csv)

Types: `Date` (date), `Year` (integer), `MonthNumber` (integer), `MonthKey` (integer), `YearMonth` (text), `DayOfMonth` (integer), `FiscalYear` (integer), `RetailYear` (integer).

The following is an explicitly selected calendar slice. Use the complete CSV for all dates; absent rows in this display are not missing model dates.

| Date | Year | MonthNumber | MonthKey | YearMonth | DayOfMonth | FiscalYear | RetailYear |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2024-01-01 | 2024 | 1 | 202401 | 2024-01 | 1 | 2024 | 2024 |
| 2024-02-29 | 2024 | 2 | 202402 | 2024-02 | 29 | 2024 | 2025 |
| 2024-12-31 | 2024 | 12 | 202412 | 2024-12 | 31 | 2025 | 2025 |
| 2025-01-02 | 2025 | 1 | 202501 | 2025-01 | 2 | 2025 | 2025 |
| 2025-02-01 | 2025 | 2 | 202502 | 2025-02 | 1 | 2025 | 2026 |
| 2025-06-30 | 2025 | 6 | 202506 | 2025-06 | 30 | 2025 | 2026 |
| 2025-07-01 | 2025 | 7 | 202507 | 2025-07 | 1 | 2026 | 2026 |
| 2025-12-31 | 2025 | 12 | 202512 | 2025-12 | 31 | 2026 | 2026 |

### Declared relationship paths

| One side | Many side | Active | Direction |
| --- | --- | --- | --- |
| Product[ProductKey] | Sales[ProductKey] | True | One to many |
| Customer[CustomerKey] | Sales[CustomerKey] | True | One to many |
| Date[Date] | Sales[OrderDate] | True | One to many |
| Date[Date] | Sales[ShipDate] | False | One to many |

## Deliberately unmatched product model

[Typed specification](unknown-member/model.json)

Original synthetic USD sales. NetAmount = Quantity * UnitPrice - line Discount. No tax or returns are included in NetAmount.

- Dates have no time component.
- All ordinary retail amounts are USD.
- S9 ProductKey 999 is deliberately absent from Product. A regular relationship's synthetic blank member is required in the reference reasoning.

### Sales (unknown-member)

**Grain:** one sales line; S9 has a deliberately unmatched product. **Key:** SaleID. **Rows:** 9.

[Complete CSV](unknown-member/Sales.csv)

Types: `SaleID` (text), `OrderID` (integer), `ProductKey` (integer), `CustomerKey` (integer), `OrderDate` (date), `ShipDate` (date), `Quantity` (integer), `UnitPrice` (number), `Discount` (number), `NetAmount` (number).

| SaleID | OrderID | ProductKey | CustomerKey | OrderDate | ShipDate | Quantity | UnitPrice | Discount | NetAmount |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | 101 | 1 | 10 | 2024-01-02 | 2024-01-04 | 2 | 10 | 0 | 20 |
| S2 | 101 | 2 | 10 | 2024-01-02 | 2024-01-04 | 1 | 5 | 1 | 4 |
| S3 | 102 | 3 | 20 | 2024-01-03 | 2024-01-05 | 2 | 20 | 0 | 40 |
| S4 | 201 | 1 | 10 | 2025-01-02 | 2025-01-04 | 3 | 10 | 3 | 27 |
| S5 | 202 | 2 | 30 | 2025-01-03 | 2025-01-08 | 4 | 5 | 0 | 20 |
| S6 | 203 | 3 | 20 | 2025-01-05 | 2025-02-01 | 1 | 20 | 0 | 20 |
| S7 | 204 | 1 | 20 | 2025-02-02 | 2025-02-03 | 2 | 10 | 0 | 20 |
| S8 | 205 | 3 | 30 | 2025-02-03 | 2025-02-04 | 2 | 20 | 4 | 36 |
| S9 | 206 | 999 | 10 | 2025-02-03 | 2025-02-04 | 1 | 7 | 0 | 7 |

### Declared relationship paths

| One side | Many side | Active | Direction |
| --- | --- | --- | --- |
| Product[ProductKey] | Sales[ProductKey] | True | One to many |
| Customer[CustomerKey] | Sales[CustomerKey] | True | One to many |
| Date[Date] | Sales[OrderDate] | True | One to many |
| Date[Date] | Sales[ShipDate] | False | One to many |

## Retail and analytical extensions

[Typed specification](analytics/model.json)

Original synthetic USD sales. NetAmount = Quantity * UnitPrice - line Discount. No tax or returns are included in NetAmount.

- Dates have no time component.
- All ordinary retail amounts are USD.
- The one side is unique; normal foreign keys are complete.
- Relationships are regular Import-style relationships for hand reasoning, not live engine metadata.
- The Date table contains 731 dates; guides show relevant slices rather than hide unselected dates.
- Budget, ForeignSales and ExchangeRate are disconnected; formulas explicitly transfer keys or look up a unique rate.
- Cohorts and experiments are independent synthetic populations, not renamed retail customers.
- Outcome data are complete for all four assignments; exposure is a separate event stream.

### Returns (analytics)

**Grain:** one return event; multiple returns per sale could exist. **Key:** ReturnID. **Rows:** 2.

[Complete CSV](analytics/Returns.csv)

Types: `ReturnID` (text), `SaleID` (text), `Refund` (number).

| ReturnID | SaleID | Refund |
| --- | --- | --- |
| R1 | S2 | 4 |
| R2 | S4 | 9 |

### Budget (analytics)

**Grain:** one month and category. **Key:** MonthKey, Category. **Rows:** 4.

[Complete CSV](analytics/Budget.csv)

Types: `MonthKey` (integer), `Category` (text), `Amount` (number).

| MonthKey | Category | Amount |
| --- | --- | --- |
| 202501 | Paper | 60 |
| 202501 | Home | 30 |
| 202502 | Paper | 25 |
| 202502 | Home | 50 |

### Inventory (analytics)

**Grain:** one product at an end-of-day snapshot. **Key:** SnapshotDate, ProductKey. **Rows:** 6.

[Complete CSV](analytics/Inventory.csv)

Types: `SnapshotDate` (date), `ProductKey` (integer), `Units` (integer).

| SnapshotDate | ProductKey | Units |
| --- | --- | --- |
| 2025-01-31 | 1 | 10 |
| 2025-01-31 | 2 | 20 |
| 2025-01-31 | 3 | 5 |
| 2025-02-28 | 1 | 8 |
| 2025-02-28 | 2 | 15 |
| 2025-02-28 | 3 | 7 |

### ForeignSales (analytics)

**Grain:** one foreign-currency transaction. **Key:** ForeignID. **Rows:** 3.

[Complete CSV](analytics/ForeignSales.csv)

Types: `ForeignID` (text), `SaleDate` (date), `Currency` (text), `LocalAmount` (number).

| ForeignID | SaleDate | Currency | LocalAmount |
| --- | --- | --- | --- |
| F1 | 2025-01-02 | USD | 100 |
| F2 | 2025-01-02 | EUR | 100 |
| F3 | 2025-02-03 | EUR | 50 |

### ExchangeRate (analytics)

**Grain:** one currency rate per date, expressed as USD per local currency unit. **Key:** RateDate, Currency. **Rows:** 3.

[Complete CSV](analytics/ExchangeRate.csv)

Types: `RateDate` (date), `Currency` (text), `USDPerUnit` (number).

| RateDate | Currency | USDPerUnit |
| --- | --- | --- |
| 2025-01-02 | USD | 1 |
| 2025-01-02 | EUR | 1.1 |
| 2025-02-03 | EUR | 1.2 |

### CohortMember (analytics)

**Grain:** one enrolled member. **Key:** MemberKey. **Rows:** 4.

[Complete CSV](analytics/CohortMember.csv)

Types: `MemberKey` (integer), `CohortMonth` (integer).

| MemberKey | CohortMonth |
| --- | --- |
| 100 | 202501 |
| 200 | 202501 |
| 300 | 202502 |
| 400 | 202502 |

### Activity (analytics)

**Grain:** one observed member-month activity in this small fixture. **Key:** ActivityID. **Rows:** 4.

[Complete CSV](analytics/Activity.csv)

Types: `ActivityID` (text), `MemberKey` (integer), `MonthKey` (integer).

| ActivityID | MemberKey | MonthKey |
| --- | --- | --- |
| A1 | 100 | 202501 |
| A2 | 100 | 202502 |
| A3 | 200 | 202501 |
| A4 | 300 | 202502 |

### Assignments (analytics)

**Grain:** one assigned experimental unit. **Key:** UnitID. **Rows:** 4.

[Complete CSV](analytics/Assignments.csv)

Types: `UnitID` (text), `Arm` (text).

| UnitID | Arm |
| --- | --- |
| U1 | Control |
| U2 | Control |
| U3 | Treatment |
| U4 | Treatment |

### Outcomes (analytics)

**Grain:** one finalized outcome per assigned unit. **Key:** UnitID. **Rows:** 4.

[Complete CSV](analytics/Outcomes.csv)

Types: `UnitID` (text), `Converted` (integer), `Revenue` (number).

| UnitID | Converted | Revenue |
| --- | --- | --- |
| U1 | 0 | 0 |
| U2 | 1 | 20 |
| U3 | 1 | 30 |
| U4 | 1 | 10 |

### Exposures (analytics)

**Grain:** one exposure event; repeat events are not independent assigned units. **Key:** ExposureID. **Rows:** 4.

[Complete CSV](analytics/Exposures.csv)

Types: `ExposureID` (text), `UnitID` (text).

| ExposureID | UnitID |
| --- | --- |
| E1 | U1 |
| E2 | U2 |
| E3 | U3 |
| E4 | U3 |

### Audience (analytics)

**Grain:** one named customer audience. **Key:** GroupKey. **Rows:** 2.

[Complete CSV](analytics/Audience.csv)

Types: `GroupKey` (integer), `Audience` (text).

| GroupKey | Audience |
| --- | --- |
| 1 | Newsletter |
| 2 | Prospects |

### GroupMembership (analytics)

**Grain:** one customer membership in one audience. **Key:** GroupKey, CustomerKey. **Rows:** 4.

[Complete CSV](analytics/GroupMembership.csv)

Types: `GroupKey` (integer), `CustomerKey` (integer).

| GroupKey | CustomerKey |
| --- | --- |
| 1 | 10 |
| 1 | 20 |
| 2 | 20 |
| 2 | 30 |

### Access (analytics)

**Grain:** one allowed region per synthetic principal in this tiny fixture. **Key:** Principal, Region. **Rows:** 2.

[Complete CSV](analytics/Access.csv)

Types: `Principal` (text), `Region` (text).

| Principal | Region |
| --- | --- |
| north.learner@example.test | North |
| south.learner@example.test | South |

### ExperimentSummary (analytics)

**Grain:** one supplied statistical summary per experimental arm; marginal95percent Wilson score intervals. **Key:** Arm. **Rows:** 2.

[Complete CSV](analytics/ExperimentSummary.csv)

Types: `Arm` (text), `Assigned` (integer), `Converted` (integer), `Rate` (number), `WilsonLower` (number), `WilsonUpper` (number).

| Arm | Assigned | Converted | Rate | WilsonLower | WilsonUpper |
| --- | --- | --- | --- | --- | --- |
| Control | 2 | 1 | 0.5 | 0.09453120573423074 | 0.9054687942657693 |
| Treatment | 2 | 2 | 1 | 0.34238022750665303 | 1 |

### Declared relationship paths

| One side | Many side | Active | Direction |
| --- | --- | --- | --- |
| Product[ProductKey] | Sales[ProductKey] | True | One to many |
| Customer[CustomerKey] | Sales[CustomerKey] | True | One to many |
| Date[Date] | Sales[OrderDate] | True | One to many |
| Date[Date] | Sales[ShipDate] | False | One to many |
| Sales[SaleID] | Returns[SaleID] | True | One to many |
| Product[ProductKey] | Inventory[ProductKey] | True | One to many |
| Date[Date] | Inventory[SnapshotDate] | True | One to many |
| CohortMember[MemberKey] | Activity[MemberKey] | True | One to many |
| Assignments[UnitID] | Outcomes[UnitID] | True | One to many |
| Assignments[UnitID] | Exposures[UnitID] | True | One to many |
| Audience[GroupKey] | GroupMembership[GroupKey] | True | One to many |
| Customer[CustomerKey] | GroupMembership[CustomerKey] | True | One to many |

## Analytical conventions

Budget is monthly by category and disconnected, so formulas transfer matching month/category keys deliberately. Refunds are attributed to the original sale date, since this fixture does not provide return-event dates. Inventory is a balance at a snapshot, not an additive monthly flow. ForeignSales and ExchangeRate use a unique date/currency conversion key; mixed local currencies cannot be summed as if they shared one unit.

Cohort membership and activity are separate, with observation ending on 2025-02-28. A future unobserved period is BLANK rather than an observed zero. Experimental assignments are the unit of analysis; repeated exposures are events, not additional independent units. Supplied Wilson intervals are marginal descriptive uncertainty summaries, not a treatment-effect interval or causal proof.

The Access table contains synthetic `.test` principals. Its policy metadata states intended role behavior without installing or testing any security. Protecting the mapping itself is an additional real-model concern. The unknown-member model deliberately adds one unmatched ProductKey 999; the clean model does not contain that defect.
