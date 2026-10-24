# Scala and Apache Spark track design

Status: planned, reviewed against primary documentation on 2026-10-22. This is a design artifact, not an active catalog extension. The existing 168 lessons and current runner capabilities are unchanged. The machine-readable companion is [scala-spark.json](../plans/scala-spark.json); the complete sample is [the pilot guide](../samples/scala-spark-pilot.md) with [separate solutions](../samples/scala-spark-pilot-solutions.md).

## Purpose and entry routes

The outcome is a learner who can preserve the meaning of data, implement the same product in Scala and PySpark, test it independently, explain its execution, and recover it after a controlled failure. Forty-two lessons are intentional: ten short JVM/Scala foundations prevent Spark syntax from becoming an unexplained language barrier; fourteen beginner lessons establish a trustworthy row model; fourteen intermediate lessons connect correctness to physical execution; fourteen advanced lessons develop recovery and operational judgment. Three capstones require a reviewable product rather than a list of APIs.

There are no mandatory entry prerequisites. A person new to programming starts with `spark-001`, completes Scala lessons `spark-002` through `spark-010`, then enters `spark-012`. A learner who already writes and tests Python can take `spark-001`, the PySpark bridge `spark-011`, then `spark-012`. The bridge names existing `python-10` as a concrete Python competency checkpoint. A new Python learner can use the existing Python foundation route before taking that branch. Neither route requires the complete historical SQL course. SQL syntax is introduced where used; existing `sql-02`, `sql-quality-01` and `sql-test-01` provide optional deeper practice.

Shared Spark lessons have a default preview/runtime language and paired Scala/PySpark implementations. Completing both languages is a parity challenge after the primary route works; a learner may first demonstrate each concept in the language they understand. Scala typed `Dataset[T]` is taught as a Scala/Java API. PySpark uses DataFrames and explicit schemas, with no invented typed Dataset equivalent. [Spark SQL programming guide](https://spark.apache.org/docs/4.2.0/sql-programming-guide.html).

The current plan schema supports AND prerequisites only. Therefore `spark-012` lists the common structural prerequisite `spark-001` and states its visible readiness gate in the lab: demonstrate `spark-010` competency **or** complete `spark-011`. The teacher must check that gate; this preview does not pretend that an OR edge has been enforced by the active catalog.

## Proposed compatibility and execution boundary

The proposed course tuple is Spark **4.2.0**, Scala **2.13.18**, JDK **21**, and Python **3.12**. Apache documents Spark 4.2.0 with Java 17/21/25, Scala 2.13 and Python 3.10+. Its tagged build selects Scala 2.13.18. Scala's compatibility table supports this Scala line on JDK 21. These facts justify a candidate tuple; they do not prove an image, Windows host, CPU architecture, Scala compiler or course adapter has passed acceptance. No JDK, Spark distribution or image is installed by this design phase. [Spark supported environments](https://spark.apache.org/docs/4.2.0/), [tagged build configuration](https://raw.githubusercontent.com/apache/spark/v4.2.0/pom.xml), [Scala/JDK compatibility](https://docs.scala-lang.org/overviews/jdk-compatibility/overview.html).

| Proposed profile | Use | Required future acceptance |
| --- | --- | --- |
| `reading` | Explanations, version/deployment worksheets, planning | Preview and notes work without a runtime |
| `scala-jvm` | Scala 2.13 foundations, assertions, compilation | Pinned compiler/JDK, bounded child process, truthful source errors, no arbitrary dependency downloads |
| `spark-local-scala` | Scala Spark batch and finite streaming labs | Pinned Spark/JVM tuple, local[2], loopback binding, private work/checkpoints, bounded resources and teardown |
| `spark-local-python` | PySpark equivalents and Python bridge | The same Spark engine, pinned Python, bounded child/JVM process tree, API and fixture parity |

These names are planned runtime profiles, not newly registered executable runners. The teacher preview must show unavailable/planned status and keep Run disabled until an adapter passes its tests. Saving an attempt, prediction, notes and retrieval answers is still useful. Actual provisioning must make one connected, checksum-verified preparation step explicit, then prove offline reuse. It must not silently reuse a remote Spark session, install dependencies on Run, inherit cloud credentials, start a Spark UI on a public interface, or modify a learner's unrelated JVM installation.

The initial budget proposal is `local[2]`, a proposed 2 GiB JVM driver heap within the shared 4 to 6 GiB whole-worker experiment envelope, normal generated fixtures no larger than 20000 rows, skew fixtures capped at 100000 rows, at most four input batches per streaming scenario, and a course-owned scratch root. These are proposed test budgets to validate on supported platforms, not claims of measured memory or speed. Every streaming query must be awaited with a deadline and stopped in `finally`. Checkpoints are durable evidence until the learner explicitly resets that lesson; cleanup is restricted to the query's own root. Default labs use inline/generated rows and local files. Kafka, object stores, JDBC services and real clusters are discussed as separate integrations, not prerequisites.

## Coverage and lesson sequence

Every row below gives a concrete outcome, bounded lab and inspectable check. Times are working estimates excluding first-time provisioning and include prediction, implementation, retrieval and review. Dependency IDs refer to the JSON plan, with the alternative entry gate described above.

### Language foundations and trustworthy rows

Enter through Scala foundations or a tested Python bridge, then preserve identity, NULL meaning and a deterministic report contract.

#### spark-001: Choose a Scala-first or PySpark-first local route

45 minutes; proposed profile `reading`; prerequisites: none.

**Objective:** Explain the JVM, Scala binary version, Python driver, Spark engine, and the difference between a proposed profile and an available runner.

**Lab:** Annotate a provided version report and choose a route. Scala-first takes 002-010 before 012; PySpark-first demonstrates python-10 skills, takes 011, then 012. Check the classroom capability notice for the prepared Scala and PySpark runtime profiles.

**Expected check:** The worksheet identifies Spark 4.2.0, Scala binary 2.13, proposed Scala patch 2.13.18, JDK 21 and Python 3.12; it rejects a Scala 3 Spark artifact and a remote master URL. No installation is required.

#### spark-002: Scala values, types, expressions, and the REPL

60 minutes; proposed profile `scala-jvm`; prerequisites: `spark-001`.

**Objective:** Read Scala 2.13 syntax and use immutable typed values and expression results.

**Lab:** Calculate a three-item basket using val, Int, Long, String and an if expression. Change a price and predict the inferred result type before compiling in the future local profile.

**Expected check:** Prices 125L, 200L and 75L sum to 400L; a 450L budget leaves 50L. A deliberate reassignment to val fails at compile time and the learner explains the message.

#### spark-003: Functions, arguments, and explicit return contracts

60 minutes; proposed profile `scala-jvm`; prerequisites: `spark-002`.

**Objective:** Write small pure Scala functions with named inputs and explicit return types.

**Lab:** Implement feeCents(amount: Long, isMember: Boolean): Long. Nonpositive amounts have zero fee; members pay zero below 500 cents and 5 percent at or above 500 (integer division); nonmembers pay a flat 20 cents on positive amounts. Table-test the boundaries.

**Expected check:** For amounts 0, 100 and 500, member fees are 0, 0 and 25, while nonmember fees are 0, 20 and 20. Tests distinguish Boolean branches and the zero amount boundary.

#### spark-004: Immutable collections and transformations

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-003`.

**Objective:** Use Seq and Map with map, filter and fold without mutating shared state.

**Lab:** Transform five local order amounts, reject negatives into a separate collection, and produce a count and total from the accepted bag.

**Expected check:** Input Seq(100L, -5L, 0L, 100L, 25L) yields accepted Seq(100L, 0L, 100L, 25L), rejected Seq(-5L), count 4 and sum 225L. Duplicate 100L values remain.

#### spark-005: Option, missing values, and total functions

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-004`.

**Objective:** Represent absence explicitly and distinguish None, zero, empty text and JVM null.

**Lab:** Parse optional amount text into Option[Long]; retain a rejected-input ledger rather than converting every invalid value to zero.

**Expected check:** Inputs Some("0"), Some("25"), None and Some("bad") produce observed 0L and 25L, one missing value and one rejected token. No .get is used on an unchecked Option.

#### spark-006: Case classes, pattern matching, and domain states

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-005`.

**Objective:** Model a small event domain with case classes and exhaustive pattern matching.

**Lab:** Create Paid and Voided event states using a sealed trait; classify four fixtures and carry event identity independently from amount.

**Expected check:** Two paid events with equal values retain separate IDs. Every defined state has a match branch; adding a Refunded state makes the omitted-case warning visible before the match is repaired.

#### spark-007: Either and validation without hidden data loss

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-006`.

**Objective:** Return accepted data or an explicit validation reason without throwing away invalid rows.

**Lab:** Combine ID, status and amount parsers with Either and a for comprehension for six bounded CSV-like records.

**Expected check:** The fixture has 3 accepted and 3 rejected records; rejection reasons are missing_id, invalid_amount and unknown_status, one each. Accepted plus rejected equals 6 and original IDs remain in evidence.

#### spark-008: Assertions, numeric boundaries, and independent oracles

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-007`.

**Objective:** Test functions with exact integer money values and recognize overflow and order-sensitive comparisons.

**Lab:** Build assertion helpers for sequences and bags; compare a hand-calculated fixture with a fold, then investigate Int overflow without using floating-point money.

**Expected check:** A bag comparison treats Seq(1,1,2) as different from Seq(1,2), while sorting makes Seq(2,1,1) equivalent. 2147483647L + 1L is 2147483648L; the Int example demonstrates why the type matters.

#### spark-009: Packages, build inputs, and closure serialization

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-008`.

**Objective:** Separate source code, compiled artifacts and dependency coordinates before distributing functions.

**Lab:** Inspect a small proposed Scala build and a closure that accidentally captures a nonserializable owner. Rewrite it to capture a plain value, without downloading dependencies in this design preview.

**Expected check:** The dependency uses a _2.13 artifact with the selected Spark version; the rewritten function has only a serializable numeric capture. A dependency lock/report records Scala, Java and Spark versions.

#### spark-010: Laziness, iterators, and safe side effects

75 minutes; proposed profile `scala-jvm`; prerequisites: `spark-009`.

**Objective:** Predict when local lazy transformations run and explain why retryable distributed work must not hide side effects.

**Lab:** Trace an Iterator pipeline and a pure collection pipeline over four values; compare a repeated evaluation with an external counter as a deliberately unsafe design.

**Expected check:** A lazy iterator emits no trace before consumption, produces accepted doubled values Seq(4,8), and is exhausted after one traversal. The learner rejects a counter as an exactly-once payment mechanism.

#### spark-011: PySpark bridge: Python values versus Spark Columns

75 minutes; proposed profile `spark-local-python`; prerequisites: `spark-001`, `python-10`.

**Objective:** Translate known Python collections and tests into explicit Spark expressions while keeping Python and engine execution distinct.

**Lab:** In the prepared PySpark profile, compare a Python Boolean with a Column predicate over IDs 1-4. Read the paired Scala syntax card rather than completing every Scala foundation lesson first.

**Expected check:** Filtering amounts greater than 10 keeps IDs [2,4] from [(1,0),(2,20),(3,None),(4,20)]. Python and/or on Columns is diagnosed and replaced with parenthesized &, | or ~ as appropriate.

#### spark-012: SparkSession, explicit schemas, and bounded actions

90 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-001`.

**Objective:** Create an owned local session and a typed schema, then distinguish transformations from actions in either API.

**Lab:** Entry gate: demonstrate Scala 010 competency OR complete the PySpark 011 branch. Create four explicit-schema rows, filter lazily, inspect schema, collect only this tiny result, and stop the owned session. Provide Scala and PySpark variants.

**Expected check:** Both variants report fields event_id: long, team: string and amount_cents: long with declared nullability; an action returns IDs [1,3]. Session master is local[2], UI is disabled, and teardown stops only the session this lab created.

#### spark-013: One row, one event: NULL-aware aggregates

90 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-012`.

**Objective:** Preserve event grain and compare NULL-aware aggregates using Scala, PySpark and SQL with deterministic result ordering.

**Lab:** Use the seven-row pilot fixture. Reconcile raw and paid rows, aggregate by team, isolate NULL and zero cases, expose projection-plus-distinct loss, and compare canonical results after repartitioning.

**Expected check:** Paid metrics are (rows=6, valued=4, total_cents=250); ordered groups are A:(3,2,200), B:(1,1,0), C:(1,0,NULL), NULL:(1,1,50). A wrong projected distinct yields 5 rows and 150 cents. Both APIs and SQL match the golden fixture.

#### spark-014: Capstone: a reconciled local revenue report

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-013`.

**Objective:** Build and explain a small revenue product whose input, rejected and reported rows reconcile.

**Lab:** Extend the pilot to 12 documented events with one invalid status, one missing ID, a zero amount and repeated equal-valued events. Deliver paired implementations, a tiny plain-language oracle and a report contract.

**Expected check:** Input count 12 equals 10 accepted plus 2 quarantined; each rejection has a reason. Both API outputs match the declared golden groups and cents totals, and a NULL-only group remains distinguishable from a zero group.

### Relational correctness and measured execution

Test equivalent Scala/PySpark/SQL results and explain plans, partitions, shuffles, join strategy and columnar I/O using bounded evidence.

#### spark-015: SQL and DataFrame expressions with ANSI boundaries

90 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-014`.

**Objective:** Express the same relational result with SQL and Columns and make casting/error policy explicit.

**Lab:** Create a temporary view from eight local rows, compare SQL and DataFrame projections, and exercise invalid integer casts with ANSI behavior explicitly set. Use SQL syntax introduced in the lesson; sql-02 is optional enrichment.

**Expected check:** Both paths produce the same six valid IDs and exact cents. Invalid casts either raise under the declared strict mode or enter a separately counted tolerant parse branch; no silent zero replacement occurs.

#### spark-016: Join cardinality, fanout, semi joins and NULL-safe keys

105 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-015`.

**Objective:** Predict join output counts from key multiplicities before running a join.

**Lab:** Join six fact rows to a dimension with a deliberately duplicated key and a NULL key. Compare inner, left, semi, anti and null-safe equality variants in both APIs and SQL.

**Expected check:** For the supplied multiplicity ledger, key A has 2 facts and 3 dimension matches, so that key contributes 6 inner rows. A semi join retains only the 2 fact rows for A; the NULL match is present only in the explicit null-safe branch.

#### spark-017: Nested records, JSON and explode row accounting

90 minutes; proposed profile `spark-local-python`; prerequisites: `spark-016`.

**Objective:** Flatten nested data while preserving parent identity and accounting for empty or missing arrays.

**Lab:** Parse four inline JSON strings with an explicit nested schema; compare explode and explode_outer for arrays of lengths 2, 0, NULL and 1. Implement the same schema and transformations in Scala.

**Expected check:** explode yields 3 rows; explode_outer yields 5 rows and retains one placeholder for each empty or NULL array. Rejected malformed input is counted separately from valid nested records.

#### spark-018: Timestamp types, time zones and interval boundaries

105 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-017`.

**Objective:** Distinguish an instant from a local timestamp and define event windows with explicit time-zone policy.

**Lab:** Use UTC strings and documented daylight-saving boundary fixtures, compare timestamp and timestamp_ntz semantics, and filter a half-open daily interval. Cross-check the same inputs in PySpark.

**Expected check:** An event exactly at the lower boundary is included and one at the upper boundary is excluded. Two textual offsets denoting the same instant compare equal after the declared parse; local-clock ambiguity is surfaced rather than guessed.

#### spark-019: Windows, ties and deterministic deduplication

90 minutes; proposed profile `spark-local-python`; prerequisites: `spark-018`.

**Objective:** Choose a stable winner per key without relying on partition arrival order.

**Lab:** Rank eight events with a duplicated timestamp using row_number over a complete order (event_time, event_id). Compare a deterministic winner policy with an intentionally incomplete order in both APIs.

**Expected check:** The declared winners are event IDs [3,6,8]; repartitioning does not change them when the final tie-breaker is included. The learner explains why dropDuplicates alone cannot promise the newest row.

#### spark-020: Partitions, repartition, coalesce and output order

90 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-019`.

**Objective:** Separate logical rows, physical partitions and a presentation order.

**Lab:** Distribute a 24-row fixture through repartition and coalesce; compare per-partition evidence with canonical content. Demonstrate sortWithinPartitions versus a final global order.

**Expected check:** All variants retain 24 IDs with the same multiset and sum. Only final orderBy with a complete tie-breaker is accepted as the global display contract; no fixed raw collect sequence is asserted.

#### spark-021: Read logical and physical plans

90 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-020`.

**Objective:** Use explain output to connect filters, projections and exchanges to the written query.

**Lab:** Run a filtered projection and grouped aggregate over the same bounded file fixture, capture explain formatted and extended views, and annotate relevant operators. Record configuration and normalize unstable operator IDs.

**Expected check:** The evidence locates the requested filter, projected columns and aggregate in each plan, and identifies any Exchange rather than assuming one exact plan string. Logical output is checked independently of the plan.

#### spark-022: Shuffles, stages, tasks and aggregation cost

90 minutes; proposed profile `spark-local-python`; prerequisites: `spark-021`.

**Objective:** Explain why a wide transformation moves data and distinguish partition count from row count.

**Lab:** Aggregate a generated 20000-row fixture by a high-cardinality key, compare two shuffle-partition settings with AQE explicitly disabled for the controlled observation, and inspect bounded task evidence.

**Expected check:** Both configurations produce the same 1000 groups and total 20000. Recorded task and shuffle metrics are tied to the run configuration; elapsed-time variation alone is not treated as proof of improvement.

#### spark-023: Broadcast joins, statistics and strategy evidence

105 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-022`.

**Objective:** Choose and verify a join strategy without turning a hint into a correctness assumption.

**Lab:** Join 20000 facts to a 20-row dimension, compare automatic planning with a broadcast hint, and capture plans plus bounded metrics. Record the estimated dimension size and the configured threshold.

**Expected check:** Both outputs retain 20000 fact identities and the same exact aggregate. The learner reports the observed strategy, including when a hint is ignored, and rejects broadcasting an unbounded table.

#### spark-024: AQE, skew and bounded salting experiments

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-023`.

**Objective:** Diagnose a skewed key and compare adaptive execution with an explicit, reversible skew strategy.

**Lab:** Generate at most 100000 rows with one hot key, record a key-frequency ledger, then compare AQE on/off and a small salted-join design. Keep correctness and runtime evidence separate.

**Expected check:** All variants match the reference bag and cents total. Evidence includes the hot-key fraction, initial and final adaptive plans when available, and task-size imbalance; salting must remove the helper key from the final contract.

#### spark-025: Parquet, column pruning and file layout

105 minutes; proposed profile `spark-local-python`; prerequisites: `spark-024`.

**Objective:** Use a columnar local file layout and verify that schema and logical results survive round trips.

**Lab:** Write at most 20000 explicit-schema rows into a fresh owned directory, read only two columns with a filter, inspect plan evidence and file counts, then compare a deliberately excessive partition layout.

**Expected check:** Round-trip canonical content matches the input contract, filtered output has the declared IDs, and plan evidence identifies selected columns and supported pushdown. The report distinguishes directory partitions, Spark partitions and file counts.

#### spark-026: Built-ins, UDFs and Python-JVM columnar boundaries

105 minutes; proposed profile `spark-local-python`; prerequisites: `spark-025`.

**Objective:** Prefer engine expressions when possible and make Python/JVM conversion and NULL behavior measurable.

**Lab:** Implement the same normalized-label rule using a built-in expression, Scala UDF and Python UDF over 12 edge-case rows. Inspect the Arrow/pandas path only in an explicitly provisioned optional profile.

**Expected check:** All enabled variants match 12 golden values including NULL, empty and Unicode inputs. A plan annotation identifies Python evaluation when present; no claim is made that Arrow eliminates serialization or that a UDF is automatically faster.

#### spark-027: Persistence lifecycle and cross-language golden tests

105 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-026`.

**Objective:** Cache only reusable work and test Scala/PySpark results with schema and bag-aware comparisons.

**Lab:** Reuse a bounded transform twice with and without persistence, materialize it deliberately, unpersist in finally, and run shared golden fixtures across both implementations. Introduce one type mismatch and one dropped duplicate.

**Expected check:** The correct variants pass schema, multiplicity and value checks; the deliberate Long/String mismatch and duplicate loss each fail a named assertion. The cache lifecycle records materialization and cleanup without relying on a speed threshold.

#### spark-028: Capstone: a skewed join with correctness and cost evidence

150 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-027`.

**Objective:** Deliver a defensible batch-optimization change backed by a reference result and bounded measurements.

**Lab:** Process a generated fact/dimension product with duplicate dimension keys, a hot key and a nullable amount. Repair the data contract first, then compare a baseline with one chosen strategy in Scala and PySpark.

**Expected check:** Accepted, rejected and joined grains reconcile; both APIs match the independent golden result. A before/after evidence packet includes configuration, plans, key frequencies and resource metrics, with a rollback and no unbounded collect.

### Recoverable batch and streaming products

Design finite streaming tests, explicit state and recovery policies, operational evidence and a defensible handoff without overstating delivery guarantees.

#### spark-029: Restartable batch writes and data-quality contracts

120 minutes; proposed profile `spark-local-python`; prerequisites: `spark-028`.

**Objective:** Make a bounded batch product repeatable without confusing overwrite, append and transactional publication.

**Lab:** Write a 30-row local product into run-specific staging directories, validate schema and counts, publish a small manifest only after validation, and inject a failure before publication. Use Scala and Python writer variants.

**Expected check:** A successful run publishes one manifest with row count 30 and a declared schema; an interrupted run leaves the prior manifest intact. Re-running the same input does not append another 30 rows to the published logical product.

#### spark-030: Deployment topology and dependency boundaries

90 minutes; proposed profile `reading`; prerequisites: `spark-029`.

**Objective:** Explain driver/executor responsibilities and distinguish local classic Spark from Connect and cluster deployment.

**Lab:** Annotate three provided deployment diagrams and a sanitized submit specification. Trace where Scala jars, Python dependencies, credentials and local paths must exist. No cluster or cloud account is required.

**Expected check:** The design correctly locates driver and executor work, rejects a driver-only local file as executor-visible storage, and labels Connect support as a separate adapter with its own compatibility and lifecycle tests.

#### spark-031: Structured Streaming with finite microbatches

105 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-030`.

**Objective:** Model an unbounded relation while running a finite, reproducible local streaming exercise.

**Lab:** Place three known files atomically into an owned input directory and use a bounded available-now microbatch run. Compare input, processed and sink counts with a batch oracle in Scala and PySpark.

**Expected check:** The run terminates after processing the finite files, reports exactly 9 input records and produces the declared batch-equivalent aggregate. Every query is awaited and stopped in finally; no socket or Kafka service is required.

#### spark-032: Event time, watermarks and late-data policy

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-031`.

**Objective:** State what a watermark does and test a declared late-event policy with controlled event-time progression.

**Lab:** Use three explicit microbatches containing on-time, out-of-order and far-late events. Add a final event-time-advancing batch, inspect progress watermarks and compare append/update output-mode eligibility.

**Expected check:** The event ledger distinguishes accepted late data from data outside the tested state-retention policy. The learner records actual watermark advancement and does not equate the configured delay with a universal wall-clock drop deadline.

#### spark-033: Stateful deduplication and event identity

105 minutes; proposed profile `spark-local-python`; prerequisites: `spark-032`.

**Objective:** Bound deduplication state while distinguishing duplicate delivery from legitimate equal-valued events.

**Lab:** Replay an event twice within the declared watermark policy, include two distinct equal-valued events and a NULL event ID, then compare the stream with a hand-written identity ledger.

**Expected check:** The repeated delivery contributes once, the two distinct event IDs both contribute, and the NULL ID enters a quarantine result. Evidence states the deduplication horizon and avoids promising perpetual deduplication.

#### spark-034: Stream-stream joins and bounded state

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-033`.

**Objective:** Express a time-bounded streaming join and explain which unmatched rows can be finalized.

**Lab:** Join finite impression and click file streams with explicit event-time bounds and watermarks. Provide a match ledger with one unmatched and one outside-window click; compare inner and supported outer behavior.

**Expected check:** Only pairs meeting both identity and interval predicates appear. The report explains delayed outer-row emission and records state/progress evidence rather than assuming immediate unmatched output.

#### spark-035: Checkpoints, restart and delivery guarantees

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-034`.

**Objective:** Explain how source offsets, state, checkpoints and sink behavior jointly determine recovery semantics.

**Lab:** Run two finite batches, stop the owned query, restart the same compatible query with the same checkpoint, then compare with a new checkpoint in a separate output namespace.

**Expected check:** Same-checkpoint recovery does not treat processed file offsets as fresh input. New-checkpoint behavior is recorded separately and never pointed at an existing append sink without an idempotency plan. A recovery ledger names source and sink assumptions.

#### spark-036: foreachBatch, idempotent sinks and failure injection

135 minutes; proposed profile `spark-local-python`; prerequisites: `spark-035`.

**Objective:** Design an idempotent microbatch sink instead of assuming foreachBatch is exactly once.

**Lab:** Use an owned local batch ledger keyed by query identity and batch ID. Inject a failure after a staged write and before publication, replay, and compare against an intentionally non-idempotent append implementation.

**Expected check:** The repaired sink publishes each logical batch once under the documented recovery model; the unsafe append variant visibly duplicates rows. The report separates a local teaching ledger from a transactional production sink guarantee.

#### spark-037: Deterministic streaming tests without sleep-based guesses

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-036`.

**Objective:** Test finite streaming scenarios with explicit batch progression and bounded cleanup.

**Lab:** Build a shared case matrix for restart, duplicate delivery, late events and invalid input using local files or the deterministic rate-micro-batch source. Keep every checkpoint and sink inside the test-owned root.

**Expected check:** Four scenario tests compare exact canonical results and progress evidence, terminate within a declared timeout, and remove only their own temporary roots. Tests fail meaningfully when duplicate suppression or publication is deliberately broken.

#### spark-038: Observability: plans, progress, event logs and incidents

105 minutes; proposed profile `spark-local-python`; prerequisites: `spark-037`.

**Objective:** Turn a slow or stalled job report into a bounded evidence-based diagnosis.

**Lab:** Inspect sanitized batch event logs and streaming progress for three seeded incidents: skew, a growing state store and an input starvation case. Capture equivalent local evidence where the future profile supports it.

**Expected check:** Each incident report cites a relevant metric or operator, distinguishes observation from hypothesis, proposes one reversible check and names a success condition. No UI screenshot alone is accepted as an end-to-end correctness check.

#### spark-039: Resource budgets, spill and cost tradeoffs

105 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-038`.

**Objective:** Choose a resource-aware strategy from measured work rather than a single elapsed time.

**Lab:** Compare two bounded configurations for the same generated dataset, recording rows, file counts, shuffle bytes, spill and task imbalance. Use a hypothetical unit-price sheet only as a separate cost model.

**Expected check:** Both runs pass the same correctness oracle; the report has explicit units and assumptions and distinguishes measured local resource work from an estimated cloud bill. It proposes a stop condition before increasing data size.

#### spark-040: SQL bridge, JDBC boundaries and data handling

105 minutes; proposed profile `reading`; prerequisites: `spark-039`.

**Objective:** Design a bounded database handoff with explicit row, type, concurrency and privacy contracts.

**Lab:** Review a supplied PostgreSQL export and JDBC design without opening a live connection. Map cents, decimals, timestamps and NULLs; identify predicate pushdown and partitioned-read assumptions and redact a fake secret from logs.

**Expected check:** The contract limits source concurrency, defines a consistent-read strategy, maps four tricky types, and rejects credentials in source or an unbounded collect. sql-quality-01 and sql-test-01 are optional cross-track enrichment, not entry requirements.

#### spark-041: Compatibility and recovery change rehearsal

120 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-040`.

**Objective:** Assess a Spark/runtime change without reusing incompatible state or trusting a version string alone.

**Lab:** Compare a documented source/target compatibility report and run the shared golden suite in each future provisioned profile. Rehearse a checkpoint-incompatible query change using a separate owned recovery path and an explicit rollback.

**Expected check:** The evidence records Spark, Scala binary/patch, JDK, Python and optional Arrow versions; all golden fixtures pass or the change is rejected. No existing checkpoint is silently reset, migrated or deleted.

#### spark-042: Capstone: a recoverable late-event data product

180 minutes; proposed profile `spark-local-scala`; prerequisites: `spark-041`.

**Objective:** Deliver a bounded streaming product with credible correctness, recovery and operational evidence.

**Lab:** Combine finite late and duplicate events, paired Scala/PySpark implementations, a state policy, an idempotent sink and failure injection. Hand off a runbook and a cost/evidence packet to a second learner acting as reviewer.

**Expected check:** The product matches an independent identity-and-event-time oracle before and after one injected restart. The packet accounts for accepted, duplicate, late and invalid rows, proves cleanup ownership and explains every source/sink guarantee without a blanket exactly-once claim.

## Three capstones and evidence standards

The beginner capstone (`spark-014`) submits a twelve-event report, two quarantined rows with reasons, paired implementations and a hand-written oracle. The intermediate capstone (`spark-028`) fixes join correctness before proposing one optimization and submits comparable plans, configurations and measured resource work. The advanced capstone (`spark-042`) submits a finite late-event product, an interruption/recovery transcript, explicit sink assumptions and a runbook that another learner can reproduce. The JSON specifies exact deliverable and acceptance lists for all three.

A correct answer must account for duplicate multiplicity, schema, NULL meaning and the requested order. A physical plan alone cannot establish correctness. A faster local run alone cannot establish lower cost. AQE and hints are observed decisions: hints do not guarantee a strategy, and adaptive execution can change a final plan. [Performance tuning guide](https://spark.apache.org/docs/4.2.0/sql-performance-tuning.html).

Streaming acceptance combines source replay, checkpoint/state recovery and sink behavior. `foreachBatch` is treated as at-least-once by default; an idempotent batch ledger is a teaching implementation with stated assumptions, not a blanket transaction guarantee. A watermark is tested through event-time progression and state evidence rather than described as a universal processing-clock deadline. [Structured Streaming guide](https://spark.apache.org/docs/4.2.0/streaming/apis-on-dataframes-and-datasets.html).

## Teacher preview and learning loop

The preview should open the planned lesson's concept before showing the coding surface, ask for a prediction, then let the learner save an attempt. Three progressive hints unlock one at a time. Retrieval questions ask for an explanation without copying code; a transfer fixture tests whether the idea generalizes. Official solutions are a separate document revealed after an attempt or an explicit learner request. The selected language must remain visible, and switching Scala/PySpark must preserve separate attempts. Runtime capability comes from the future adapter registry, never from guessing a filename.

For the pilot, the teacher starts with row grain and the distinction between zero and missing. A diagnostic wrong answer of five rows or 150 cents should trigger the identity hint. A claim that the all-missing group totals zero should trigger a NULL/business-rule question. A correct table with no order clause should trigger a reproducibility question. Completion is based on the six rubric items and a transfer explanation, not whether code printed without errors. The plan's `pilot` object supplies a bounded concept card, prediction, Scala starter, three hints, transfer and rubric for this workflow; the guide includes the equivalent PySpark starter.

## Release gates for a future implementation

Before activation, author all learner/guide/solution surfaces and register real practice-expansion baselines. Run both language golden suites and independent batch oracles. Verify source mapping, timeouts, child/JVM cleanup, memory limits, dependency failure messages, loopback-only sockets, offline reuse, state preservation and explicit reset ownership. Run finite restart and late-event scenarios on each supported packaged platform. Compare schema and bag multiplicity, not only sorted display strings; use official test utilities where useful and add course-specific identity checks. [Testing PySpark](https://spark.apache.org/docs/4.2.0/api/python/getting_started/testing_pyspark.html).

Inspect file layout and plan evidence for columnar labs rather than promising a specific pushdown optimization. Keep monitoring evidence bounded and redact secret-bearing configuration before learner export. [Parquet guide](https://spark.apache.org/docs/4.2.0/sql-data-sources-parquet.html), [monitoring guide](https://spark.apache.org/docs/4.2.0/monitoring.html).

Design checks can validate plan IDs, prerequisite references, fixtures and code syntax now. They cannot establish Spark execution, Scala compilation, distributed fault tolerance, real-cluster performance or operating-system provisioning. Those remain explicit implementation acceptance work.

## Primary references checked 2026-10-22

- [Spark 4.2.0 overview and supported environments](https://spark.apache.org/docs/4.2.0/): Spark version, supported Java/Scala/Python lines, local mode and classic versus Connect distinction.
- [Spark 4.2.0 tagged build configuration](https://raw.githubusercontent.com/apache/spark/v4.2.0/pom.xml): Tagged Scala 2.13.18 build and Scala binary 2.13; source-level compatibility evidence, not a tested course image.
- [Scala JDK compatibility](https://docs.scala-lang.org/overviews/jdk-compatibility/overview.html): Scala 2.13 and JDK 21 compatibility; keep the Spark-specific binary line distinct from Scala 3.
- [Spark SQL, DataFrames and Datasets](https://spark.apache.org/docs/4.2.0/sql-programming-guide.html): Shared SQL/DataFrame engine and the Scala/Java typed Dataset versus Python DataFrame API distinction.
- [Spark SQL NULL semantics](https://spark.apache.org/docs/4.2.0/sql-ref-null-semantics.html): NULL predicates, NULL-safe equality, grouping, aggregate behavior and ordering used in the pilot.
- [Spark SQL performance tuning](https://spark.apache.org/docs/4.2.0/sql-performance-tuning.html): Statistics, broadcast hints, partition tuning, persistence, AQE and skew experiments.
- [Spark Parquet data source](https://spark.apache.org/docs/4.2.0/sql-data-sources-parquet.html): Columnar file reading, schema handling and Parquet-specific I/O evidence.
- [Structured Streaming overview](https://spark.apache.org/docs/4.2.0/streaming/index.html): Microbatch conceptual model and the need to distinguish processing modes.
- [Structured Streaming DataFrame and Dataset guide](https://spark.apache.org/docs/4.2.0/streaming/apis-on-dataframes-and-datasets.html): Watermarks, stateful operations, file sources, checkpoints, recovery and foreachBatch delivery assumptions.
- [Testing PySpark](https://spark.apache.org/docs/4.2.0/api/python/getting_started/testing_pyspark.html): Local testing patterns and schema/value comparison utilities; supplement with multiplicity-aware course oracles.
- [Spark monitoring and instrumentation](https://spark.apache.org/docs/4.2.0/monitoring.html): Event logs, metrics and observable execution evidence for incident and resource labs.
- [Scala Tour: basics](https://docs.scala-lang.org/tour/basics.html): Scala 2-compatible values, types, expression blocks, functions and entry-level syntax for the language-first route.
- [Scala Tour: case classes](https://docs.scala-lang.org/tour/case-classes.html): Immutable domain records, structural equality and the distinction between equal values and application-defined event identity.
- [Scala Tour: higher-order functions](https://docs.scala-lang.org/tour/higher-order-functions.html): Function values and collection transformations used before introducing distributed expression execution.
