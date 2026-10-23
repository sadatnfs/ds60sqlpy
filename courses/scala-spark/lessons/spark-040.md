# spark-040: Learner architecture worksheet

Read the [guide](../guides/spark-040.md). These are sanitized reasoning fixtures, not executable deployment instructions. Retain an independent answer and the evidence supporting it for each task.

## Worked example / walkthrough

### Worked example 1: Partition stride is not a data filter

```text
Source IDs: -10,0,5,10,99,NULL
Illustrative partition0: id < 5 OR id IS NULL
Illustrative partition1: id >= 5
Configured lowerBound=0,upperBound=10,numPartitions=2
```

Partition 0 includes -10,0, NULL;partition 1 includes 5,10,99. All six source rows can be read. To select only[0,10), the reviewed SQL must contain that population predicate and a deliberate NULL policy. This is a reasoning fixture, not an executed JDBC query.

### Worked example 2: Map an exact decimal,instant and missing field

```json
{
  "event_id": 7,
  "cents": 125,
  "price_decimal_text": "12345678.90",
  "event_time_with_offset": "2026-10-23T12:00:00-07:00",
  "note": null
}
```

The proposed Spark contract retains cents 125 as bigint, price as decimal(10,2), the event instant as 19:00UTC under the UTC baseline, and note as NULL. This exact-value fixture can falsify a float conversion, timezone reinterpretation or null-to-empty-string shortcut before any large read is approved.

## Exercises

### Exercise 1: Define grain, population and bounded read scope

Review the fixed approved_export design and state its unique row key, export identity, predicate and maximum row count before any JDBC operation.

**Inputs/evidence:** For spark-040 Exercise 1, Synthetic export_id demo-2026, unique event_id, at most 5000 rows, approved columns event_id, cents, price, event_time, note.

**Expected result/shape:** For spark-040 Exercise 1, One row per event_id within one immutable export_id;at most 5000 rows and no unbounded collect.

**Verify:** Write the row-grain and population contract, plus the count/uniqueness/readback checks that would reject an oversized or duplicate export.

**Progressive hint:** A table name and a connection URL are not a data contract.

### Exercise 2: Map four tricky SQL values without losing meaning

Map bigint cents, decimal price, timestamp with time zone and nullable note into the proposed Spark contract.

**Inputs/evidence:** For spark-040 Exercise 2, cents 125;price 12345678.90 as numeric(10,2);event_time2026-10-23T12:00:00-07:00;noteSQLNULL.

**Expected result/shape:** For spark-040 Exercise 2, LongType 125;DecimalType(10,2)12345678.90;the same instant rendered 19:00:00UTC under the baseline;NULL remains missing, not an empty string.

**Verify:** State source and target type, unit, precision/timezone policy and one rejected conversion for each.

**Progressive hint:** Money, wall-clock text, instants and missingness have different semantics.

### Exercise 3: Reject the lowerBound/upperBound filter misconception

Predict which IDs can be read when partitionColumn=id, lowerBound 0, upperBound 10, numPartitions 2 are used without a SQL row filter.

**Inputs/evidence:** For spark-040 Exercise 3, IDs[-10,0,5,10,99, NULL]. Illustrative partition predicates:id<5 OR id IS NULL, and id>=5.

**Expected result/shape:** For spark-040 Exercise 3, All 6 supplied rows can be read. Bounds choose partition stride, not a WHERE filter restricting IDs to[0,10).

**Verify:** Assign each supplied ID to the two predicates and write an explicit SQL filter for the intended population if one is required.

**Progressive hint:** The first and last JDBC partitions cover outside the stride bounds.

### Exercise 4: Bound connection concurrency and read consistency

Design a maximum-two-partition read and explain why separate repeatable-read transactions do not automatically share one snapshot.

**Inputs/evidence:** For spark-040 Exercise 4, Two JDBC partitions;source rows can change;no live snapshot-coordination adapter is provided.

**Expected result/shape:** For spark-040 Exercise 4, A nominal 2-partition connection bound plus an explicit immutable-export or separately qualified coordinated-snapshot strategy.

**Verify:** Name connection/time/fetch controls and show how concurrent source updates would otherwise produce a mixed-time result.

**Progressive hint:** Isolation level per connection is not the same as one shared snapshot across connections.

### Exercise 5: Remove credentials from source and evidence

Review a fake options record containing a URL, user, password and operational settings. Keep only the approved diagnostic fields.

**Inputs/evidence:** For spark-040 Exercise 5, Synthetic passwordDUMMY_LESSON_ONLY, URLjdbc:postgresql://db.invalid:5432/course, numPartitions 2, fetchsize 1000, queryTimeout 30.

**Expected result/shape:** For spark-040 Exercise 5, No password, user, URL or credential-bearing connection string in the saved source/evidence;only approved operational settings are retained.

**Verify:** Write the exact sanitized object and identify the approved runtime credential source without inventing a real account.

**Progressive hint:** Do not depend on one regex matching every possible secret-bearing string.

### Exercise 6: Write a future acceptance and failure contract

Specify the evidence required before enabling a JDBC profile, including missing-driver, mapping, timeout, cancellation and least-privilege checks.

**Inputs/evidence:** For spark-040 Exercise 6, Current profile bundles no qualified JDBC driver/remote database;synthetic export and schema mapping only. Optional enrichment IDssql-quality-01 and sql-test-01.

**Expected result/shape:** For spark-040 Exercise 6, A reviewable acceptance matrix with unavailable runtime rows, not a fabricated successful connection.

**Verify:** List positive and negative cases, exact version tuple, source identity, output oracle, connection closure and no-write privileges.

**Progressive hint:** A proposed option map is not a connector implementation.
