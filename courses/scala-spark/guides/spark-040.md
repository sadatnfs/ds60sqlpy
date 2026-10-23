# spark-040: SQL bridge, JDBC boundaries and data handling

This architecture lesson uses fixed, sanitized reasoning fixtures. It does not connect to a cluster, open a database, install dependencies or perform a deployment.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisite: `spark-039`. The prepared execution baseline elsewhere in this course is classic Spark4.0.1, Scala binary2.13 and JDK17. This reading lesson distinguishes that actual local boundary from proposed remote designs.

## How to use this lesson

Read the mechanisms and two worked examples, then complete the [learner worksheet](../lessons/spark-040.md). Write one evidence-backed response per task before opening the [explained reference](../solutions/spark-040_solutions.md). The classroom reading profile does not execute the schematic examples. No remote account or service is required.

## Learning objectives

- Design a bounded database handoff with explicit row, type, concurrency and privacy contracts.
- Identify each responsibility, input boundary and missing acceptance receipt explicitly.
- Reject a plausible but unsupported design using concrete counterexamples and a bounded validation plan.

## Vocabulary and concepts

- **JDBC:** A JVM database connectivity interface whose actual driver, server and authentication path must be supplied and qualified.

- **Partitioned read:** Multiple source queries dividing work by a declared partition column;the bounds do not themselves filter the dataset.

- **Snapshot consistency:** A result representing one defined database state rather than a mixture of independently timed reads.

- **Decimal precision/scale:** The total digits and fractional digits in an exact decimal type, such as numeric(10,2).

- **Timestamp instant:** A point on the time axis, distinct from local wall-clock fields without a zone.

- **Least privilege:** An identity limited to the approved read population and operations, with no unnecessary write or administrative access.

A database handoff adds boundaries that a local DataFrame example can hide:source authorization, driver compatibility, connection concurrency, transaction consistency, type mapping and sensitive-data handling. This chapter reviews those contracts without opening a database. The supplied export and connection options are synthetic reasoning material. The normal classroom Spark profiles do not claim a prepared JDBC connector or a live PostgreSQL target.

Start with row grain and population. The proposed product has one row per event_id in an immutable export_id. It includes only event_id, cents, price, event_time and note, and it is bounded to 5000 rows. The export identity ties schema, count and capture cutoff together. A SELECT against a mutable production table would require additional consistency reasoning;renaming that table as an export would not make it immutable.

## Trace types before choosing a connector option

Integer cents are a unit-bearing count. Keep them as an exact integer and document the range. Decimal money has separate precision and scale;numeric(10,2) allows ten total digits, including two fractional digits. Converting 12345678.90 to a binary float can lose the exact decimal representation even when a rounded display looks unchanged. A destination schema should reject unsupported range/scale rather than silently changing a business value.

A PostgreSQL timestamp with time zone represents an instant. Session settings affect display, and the original offset spelling is not retained as a separate named-zone field. The sample 12:00 at offset-07:00 is 19:00UTC. A timestamp without time zone has different semantics:it may represent local wall time whose interpretation requires a zone and daylight-saving policy. Spark's JDBC timestamp mappings/options must be checked in the exact qualified version;do not assume TimestampType and TimestampNTZType are interchangeable.

SQLNULL is missingness, not the empty string, zero or the wordNULL. Preserve nullability through reads and tests. COUNT(*) and COUNT(note) can differ because the latter excludes NULL. A schema match alone does not show that a driver retained nulls, decimal scale or timestamp meaning, so the acceptance fixture needs exact value checks as well.

## Read partition bounds correctly

Spark's lowerBound and upperBound options choose the stride used to split JDBC read work. They are not row-selection predicates. For a numeric partition column with illustrative bounds 0 and 10 and two partitions, the first predicate can include id<5 or NULL and the last can include id>=5. Values below 0 or above 10 can therefore still be read. Put an authorized population filter in the reviewed SQL source itself when one is required.

The partition column must satisfy the connector's supported type rules. Query text and dbtable subqueries have different option constraints;in particular, the query option is not combined directly with partitionColumn. A reviewed aliased subquery can be used when partitioning a filtered source. Predicate pushdown should be inspected as an optimization, not treated as a substitute for least-privilege authorization or a row budget.

numPartitions bounds the configured parallelism, while fetchsize controls batches of rows fetched by the driver and queryTimeout concerns query execution under driver support. None is a universal total-memory or hard-wall-clock guarantee. A complete runtime adapter also needs connection establishment limits, cancellation behavior, driver-specific options and source-side protection against excessive connections.

## Consistency across connections is a separate design

Each JDBC partition can use a different database connection. Giving each connection REPEATABLE READ does not make their snapshots identical if they start at different times. A source update between reads can produce a mixed-time result. The partition key can also move or change membership, which can create missed or duplicated rows depending on the read design.

This worksheet chooses an immutable export as the default handoff. A future live coordinated snapshot would require a PostgreSQL snapshot-export/import protocol and a connector lifecycle that keeps the exporting transaction alive until all readers are correctly initialized. That is a real implementation obligation, not a magic option string. The chapter does not execute, qualify or recommend a specific untested snapshot adapter.

## Keep credentials outside data contracts and logs

The fake options record uses db.invalid and DUMMY_LESSON_ONLY so no real target or secret is supplied. A real connection would use an approved runtime identity/credential mechanism outside checked-in source and portable evidence. Error messages and URLs can carry sensitive fields, so exporting a full options dictionary is unsafe even if one password key is replaced.

The redaction task uses a small allowlist of operational numeric settings. It does not fetch a secret or test authentication. Source-side privileges should permit only the approved reads. The future acceptance plan must reject writes, exercise cancellation/timeout and confirm connection closure without collecting unrelated user data.

The useful deliverable is a complete mapping and acceptance matrix:what is proposed, what is already known from the synthetic export, and which runtime evidence is absent. The optional SQL quality/testing modules can deepen those controls, but they are not prerequisites for this Spark reading chapter.

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

## Common pitfalls

Do not treat JDBC stride bounds as a WHERE clause, separate transactions as one shared snapshot, or a connection count as a complete resource budget. Do not coerce decimal money through float or replace NULL with an empty string silently. Never paste credentials into a guide, pad, URL or exported options dictionary. A driver declaration and synthetic schema review do not establish a working remote connector.

## Self-check

Explain the first diagram or type mapping without reading the answer. Trace one failure through its actual process or storage boundary. State which observation would falsify your preferred design, which evidence already exists and which acceptance work remains. A correct vocabulary label alone does not complete the task.

## Next step

Continue through the [course route](../README.md). Preserve the written assumptions and evidence gaps when moving into a runnable lesson; a reviewed design is not an execution receipt.

## Primary sources and official APIs

- [Spark4.0.1 JDBC options and mappings](https://spark.apache.org/docs/4.0.1/sql-data-sources-jdbc.html)

- [PostgreSQL17 transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html)

- [PostgreSQL17 date/time semantics](https://www.postgresql.org/docs/17/datatype-datetime.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-040: SQL bridge, JDBC boundaries and data handling.
Read courses/scala-spark/guides/spark-040.md and courses/scala-spark/lessons/spark-040.md. Direct prerequisites: spark-039.
Explain the new architecture or data-handling concepts, ask me to predict a concrete failure, then review my six worksheet responses. Give one hint at a time and ask retrieval questions in my own words. Require named roles, exact input/output contracts, counterexamples and inspectable acceptance evidence. Do not read solutions/ until I ask or have made an honest attempt.
This is a reading profile. Do not open remote connections, start services, install dependencies or apply the schematic configuration.
Done when all six task contracts have reviewed evidence and I can explain the assumptions, failure boundaries and unverified parts of the design.
```
