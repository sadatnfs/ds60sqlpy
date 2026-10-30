# spark-033: Explained paired reference solutions

Read the [guide](../guides/spark-033.md) and attempt one language first. The [Scala reference](spark-033_solution.scala) and [PySpark reference](spark-033_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Classify missing event identity before deduplication

Add reason missing_event_id for NULL event_id and accepted otherwise, retaining delivery_id, amount and event_time.

**Expected:** Delivery 3 is quarantined; known IDs are eligible for the separate deduplication policy.

```scala
def classify(events: DataFrame): DataFrame = {
  events.withColumn(
    "reason",
    when(col("event_id").isNull, "missing_event_id").otherwise("accepted")
  )
}
```

```python
def classify(events):
    return events.withColumn(
        "reason", F.when(F.col("event_id").isNull(), "missing_event_id").otherwise("accepted")
    )
```

The missing-identity decision is made before applying a stateful key rule. Keeping delivery_id preserves the source occurrence for later review and count reconciliation. The classified relation remains streaming and unexecuted until its sinks start; the presence of a reason column alone is not processing evidence.

**Verification evidence:** Construct the first streaming classification with all declared fields and verify the exact quarantine row after the first phase.

### Exercise 2: Define a bounded event-ID stateful operator

Filter accepted identities, drop the reason field, attach a five-minute watermark to event_time, and deduplicate within that watermark on event_id only.

**Expected:** The result remains streaming and retains delivery_id, event_id, amount, event_time. Equal amounts across distinct IDs remain distinct.

```scala
def deduplicated(classified: DataFrame): DataFrame = {
  classified
    .filter(col("reason") === "accepted")
    .drop("reason")
    .withWatermark("event_time", "5 minutes")
    .dropDuplicatesWithinWatermark(Seq("event_id"))
}
```

```python
def deduplicated(classified):
    return (
        classified.filter(F.col("reason") == "accepted")
        .drop("reason")
        .withWatermark("event_time", "5 minutes")
        .dropDuplicatesWithinWatermark(["event_id"])
    )
```

The key is the logical event identity, while delivery identity remains an output attribute showing which occurrence was retained in this controlled history. The watermark bounds the stateful retention policy. It does not create a permanent event-ID registry, and the operator does not resolve contradictory payload versions that share one ID.

**Verification evidence:** Assert output shape and use the explicit event_id key, then validate all retained identities through later sink checks.

### Exercise 3: Execute accepted and quarantine branches with separate checkpoints

Run both first-phase branches with AvailableNow: deduplicated records to accepted-output and missing-ID records to quarantine-output. Use distinct checkpoints and bounded await/stop scopes.

**Expected:** Accepted(e1, delivery 1,10),(e2, delivery 2,10); quarantine(delivery 3, NULL, missing_event_id). The raw source has 3 rows; prepared branch input metrics report 2 accepted-eligible rows and 1 quarantine row.

```scala
def runBranches(
    spark: SparkSession,
    root: Path
): (Seq[StreamingQueryProgress], Seq[StreamingQueryProgress]) = {
  val classified = classify(input(spark, root))
  val accepted = runSink(deduplicated(classified), root, "accepted")
  val rejected =
    runSink(classified.filter(col("reason") === "missing_event_id"), root, "quarantine")
  (accepted, rejected)
}
```

```python
def run_branches(spark, root):
    classified = classify(input_stream(spark, root))
    accepted = run_sink(deduplicated(classified), root, "accepted")
    rejected = run_sink(
        classified.filter(F.col("reason") == "missing_event_id"), root, "quarantine"
    )
    return accepted, rejected
```

The two sink populations are complementary business decisions. In this prepared plan, the reported source metrics reflect branch filtering:2 known-ID rows and 1 missing-ID row. A separate static read proves the raw source count 3. Separate checkpoints prevent one branch from advancing another branch source progress. The exactNULL quarantine row proves that unknown identity was retained for review rather than silently discarded ormerged into an accepted key.

**Verification evidence:** Assert both exact output populations, branch metrics 2/1 and an independent raw batch-source count 3.

### Exercise 4: Suppress a replay while retaining distinct equal-valued events

Publish the second file after the first phase terminates and run both compatible branches again. Compare the accepted business identities and their total.

**Expected:** Accepted(e1, delivery 1,10),(e2, delivery 2,10),(e3, delivery 5,10); delivery 4 replay contributes no additional row. Business total 30.

```scala
def businessRows(spark: SparkSession, root: Path): Seq[(String, Long, Long)] = {
  outputRows(spark, root).filterNot(_._1 == "__advance__")
}
```

```python
def business_rows(spark, root):
    return [row for row in output_rows(spark, root) if row[0] != "__advance__"]
```

The accepted branch reports 2 eligible input rows in this phase, but only 1 new business row is committed because e1 is a replay. The quarantine branch reports 0 because neither new delivery has a missing ID. The replay is suppressed by event_id while the equal amount 10 on e2 and e3 remains legitimate data. Sequencing the phases makes the retained delivery explicit and avoids pretending a general deduplicator chooses a deterministic payload winner among simultaneous conflicting copies. The business view removes only the declared administrative identity, not arbitrary zero-valued events.

**Verification evidence:** Assert all retained event/delivery pairs, sum 30, raw source total 5 and prepared branch metrics 2 accepted-eligible inputs versus 0 quarantined inputs for this phase.

### Exercise 5: Observe state removal and state the retention limit

Publish the 00:20 advancer and run both branches. Sum actual numRowsRemoved state metrics from the accepted branch and inspect remaining state.

**Expected:** The three old business-key states are removed under the observed watermark progression; accepted output still retains their committed rows plus the advancer.

```scala
def removedState(progress: Seq[StreamingQueryProgress]): Long = {
  require(progress.exists(_.stateOperators.nonEmpty), "Missing deduplication state evidence")
  progress.flatMap(_.stateOperators).map(_.numRowsRemoved).sum
}
```

```python
def removed_state(progress):
    operators = [operator for p in progress for operator in p.get("stateOperators", [])]
    if not operators or any("numRowsRemoved" not in operator for operator in operators):
        raise ValueError("Missing deduplication state evidence")
    return sum(operator["numRowsRemoved"] for operator in operators)
```

The metric substantiates an actual retention boundary instead of merely restating the configured watermark. Old sink rows remain committed while their key state is evicted. A later business requirement for permanent event uniqueness would need a durable identity store or another explicit protocol; this bounded operator cannot supply that guarantee once historical state is removed.

**Verification evidence:** Assert removed state rows at least 3, unchanged business rows and one advancer output. Print actual state metrics without promising perpetual deduplication.

### Exercise 6: Reconcile deliveries, quarantine, replay suppression and business totals

Read the six source deliveries once as a bounded batch and compare them with both sinks. Return source deliveries, known-ID deliveries, quarantine rows, accepted rows including advancer, and business total.

**Expected:** Ledger(6,5,1,4,30). One known-ID delivery is suppressed as an in-horizon replay; three distinct equal-valued business events remain.

```scala
def deliveryLedger(spark: SparkSession, root: Path): (Long, Long, Long, Long, Long) = {
  val source = spark.read.schema(eventSchema).json(root.resolve("input").toString)
  require(source.select("delivery_id").distinct().count() == 6L, "Delivery identity mismatch")
  (
    source.count(),
    source.filter(col("event_id").isNotNull).count(),
    spark.read.parquet(root.resolve("quarantine-output").toString).count(),
    spark.read.parquet(root.resolve("accepted-output").toString).count(),
    businessRows(spark, root).map(_._3).sum
  )
}
```

```python
def delivery_ledger(spark, root):
    source = spark.read.schema(event_schema).json(str(root / "input"))
    if source.select("delivery_id").distinct().count() != 6:
        raise ValueError("Delivery identity mismatch")
    return (
        source.count(),
        source.filter(F.col("event_id").isNotNull()).count(),
        spark.read.parquet(str(root / "quarantine-output")).count(),
        spark.read.parquet(str(root / "accepted-output")).count(),
        sum(r[2] for r in business_rows(spark, root)),
    )
```

The ledger connects physical delivery occurrences to business decisions without mixing query-processing counts with unique inputs. The rejected 99 contributes only to quarantine, not business totals. The advancer remains accounted for in accepted output while its amount 0 is excluded from the business-view definition. One replay explains the difference between five known-ID deliveries and four accepted sink rows.

**Verification evidence:** Assert the complete ledger and six unique delivery IDs; confirm no active queries remain before cleanup.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
