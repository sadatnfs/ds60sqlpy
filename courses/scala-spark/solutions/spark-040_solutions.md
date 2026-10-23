# spark-040: Explained architecture references

Compare these answers after an attempt at the [worksheet](../lessons/spark-040.md). Each answer states the mechanism, a failure case and a reviewable contract. No remote resource was contacted to author or validate this reading lesson.

## Exercises and reasoning

### Exercise 1: Define grain, population and bounded read scope

**Expected:** One row per event_id within one immutable export_id;at most 5000 rows and no unbounded collect.

The approved input is an immutable export identified by demo-2026, with a unique event_id and a known maximum of 5000 rows. The reader selects only the five reviewed columns. A count and countDistinct(event_id) check must agree with the manifest for that same immutable export. A bounded sample can help diagnose types, but it cannot substitute for population checks.

The contract should also state who produced the export, its capture cutoff, schema and digest or equivalent lineage identifier. A new export is a new input identity rather than an in-place update of a file being read. Driver collection is limited to small validated summaries or a declared tiny teaching sample;the existence of 5000 as a source budget does not authorize collecting an unknown production table. No connection is opened by this worksheet.

**Verification evidence:** Write the row-grain and population contract, plus the count/uniqueness/readback checks that would reject an oversized or duplicate export.

### Exercise 2: Map four tricky SQL values without losing meaning

**Expected:** LongType 125;DecimalType(10,2)12345678.90;the same instant rendered 19:00:00UTC under the baseline;NULL remains missing, not an empty string.

bigint cents maps to a signed 64-bit integer representation when the qualified connector schema confirms it;the unit remains cents, so 125 is not automatically 125 currency units. numeric(10,2) can hold the supplied eight-digit integer part and two fractional digits. Preserve DecimalType(10,2), not a binary float whose rounding may change exact decimal comparisons. A value outside precision 10 must fail or follow an explicitly chosen error policy, not be silently truncated.

The timestamp with time zone value denotes an instant. PostgreSQL does not preserve the original named zone/offset as a separate semantic field merely because it used that spelling at input. Under Spark's declared UTC session, the instant renders 2026-10-23T19:00:00Z. A timestamp without time zone instead represents local wall-clock fields and needs a separate zone/NTZ policy. JDBC options and driver mappings can affect the inferred Spark timestamp type, so inspect the actual schema in a future qualification.

SQLNULL note stays a nullable missing value. Converting it to an empty string changes comparisons, counts and downstream interpretation. The four checks are independent:an exact row count does not prove any of these conversions preserved meaning.

**Verification evidence:** State source and target type, unit, precision/timezone policy and one rejected conversion for each.

### Exercise 3: Reject the lowerBound/upperBound filter misconception

**Expected:** All 6 supplied rows can be read. Bounds choose partition stride, not a WHERE filter restricting IDs to[0,10).

The first illustrative partition contains -10,0 and NULL;the second contains 5,10 and 99. The lower/upper options determine how Spark divides read work, not which rows belong to the dataset. Assuming they filter would silently widen the read and potentially include data outside the intended population.

If the authorized population is 0<=id<10, the SQL source itself needs that predicate, with an explicit NULL policy. A fixed reviewed dbtable subquery with an alias can express a filtered source while partitioning its numeric/date/timestamp column. The query option cannot simply be combined with partitionColumn under Spark's documented option constraints. Predicate pushdown is an execution optimization to verify, not authorization to request extra columns or rows.

**Verification evidence:** Assign each supplied ID to the two predicates and write an explicit SQL filter for the intended population if one is required.

### Exercise 4: Bound connection concurrency and read consistency

**Expected:** A nominal 2-partition connection bound plus an explicit immutable-export or separately qualified coordinated-snapshot strategy.

Set the planned read to at most two JDBC partitions, with reviewed query/fetch/connection timeouts and source-side access limits. numPartitions bounds the configured parallel read partitions, but operational qualification must still examine driver behavior, retries, cancellation and database resource limits. A driver pool or database policy may be needed to enforce a hard connection ceiling under failures.

Separate PostgreSQL REPEATABLE READ transactions can begin with different snapshots. If a row moves between key ranges or its amount changes between partition reads, the combined Spark result can represent no single point in time. The simplest bounded handoff here is an immutable export with a stable export_id, so every partition reads the same frozen population.

A live alternative could use a deliberately coordinated PostgreSQL snapshot export/import protocol, but its transaction lifetimes, connector initialization and cleanup require a real reviewed adapter. A generic sessionInitStatement is not proof that all partitions share one snapshot. This lesson does not implement or execute that protocol.

**Verification evidence:** Name connection/time/fetch controls and show how concurrent source updates would otherwise produce a mixed-time result.

### Exercise 5: Remove credentials from source and evidence

**Expected:** No password, user, URL or credential-bearing connection string in the saved source/evidence;only approved operational settings are retained.

A suitable sanitized diagnostic object is {"numPartitions":2,"fetchsize":1000,"queryTimeout":30}. The full URL, user and password are omitted from the portable packet. The dummy value is a teaching marker, not a credential to try. A real runtime would obtain identity through the approved host mechanism and keep it out of checked-in source, process arguments, logs and portable progress.

Redacting only a field literally named password is insufficient because credentials can appear in URL parameters, nested options or free-form exception messages. Use a reviewed allowlist for exported diagnostic fields and inspect error reporting separately. A hash of a low-entropy secret is not automatically a safe public substitute. No secret retrieval or database authentication occurs in this reading exercise.

**Verification evidence:** Write the exact sanitized object and identify the approved runtime credential source without inventing a real account.

### Exercise 6: Write a future acceptance and failure contract

**Expected:** A reviewable acceptance matrix with unavailable runtime rows, not a fabricated successful connection.

The acceptance matrix records Spark 4.0.1, Scala 2.13, JDK 17, Python and exact JDBC driver/database versions. A future bounded fixture must confirm the inferred schema, all tricky values, population/uniqueness, source filter, partition connection behavior and snapshot strategy. It also needs an expected missing-driver failure, a forbidden-write control, a timeout/cancellation case and proof that connections are closed afterward.

The current row is unavailable because neither the connector nor a remote target is qualified in this lesson. That is the honest result of the design review. Do not download a driver or choose an ambient database to make the example runnable. The local immutable-export alternative can be tested separately with the ordinary file profile. sql-quality-01 and sql-test-01 are optional SQL quality/testing enrichment, not additional entry prerequisites for understanding this chapter.

**Verification evidence:** List positive and negative cases, exact version tuple, source identity, output oracle, connection closure and no-write privileges.

## Evidence boundary

These explanations are design-review references. They do not establish a completed deployment, package installation, live database snapshot or remote compatibility result. A future execution must use the named bounded inputs and record its own versioned receipts. Preserve the distinction between a proposed control, an inspected configuration and an observed result.
