# spark-042: Explained paired reference solutions

Read the [guide](../guides/spark-042.md) and attempt one language first. The [Scala reference](spark-042_solution.scala) and [PySpark reference](spark-042_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Validate and canonicalize each raw microbatch

Require the explicit four-field schema, at most 8 rows and unique delivery IDs 1..12. Preserve NULL/business-invalid fields for classification and emit deterministic JSON.

**Expected:** BatchA has four occurrences with IDsA, B, A, NULL;NULL is preserved in canonical input. An oversized batch is rejected before collection.

```scala
def canonicalProductInput(frame: DataFrame): String = {
  require(
    frame.schema.fields.map(f => (f.name, f.dataType.simpleString)).toSeq == Seq(
      ("delivery", "bigint"),
      ("id", "string"),
      ("event_second", "bigint"),
      ("cents", "bigint")
    )
  )
  val countRows = frame.count(); require(countRows <= 8L)
  require(
    frame
      .filter(col("delivery").isNull || col("delivery") < 1L || col("delivery") > 12L)
      .count() == 0L
  )
  require(
    frame.select("delivery").distinct().count() == countRows,
    "Delivery IDs must be unique within a microbatch"
  )
  val array = productMapper.createArrayNode()
  frame.orderBy("delivery").collect().foreach { row =>
    val node = array.addObject()
    if (row.isNullAt(3)) node.putNull("cents") else node.put("cents", row.getLong(3))
    node.put("delivery", row.getLong(0))
    if (row.isNullAt(2)) node.putNull("event_second") else node.put("event_second", row.getLong(2))
    if (row.isNullAt(1)) node.putNull("id") else node.put("id", row.getString(1))
  }
  productMapper.writeValueAsString(array)
}
```

```python
def canonical_product_input(frame):
    expected = [
        ("delivery", "bigint"),
        ("id", "string"),
        ("event_second", "bigint"),
        ("cents", "bigint"),
    ]
    if [(f.name, f.dataType.simpleString()) for f in frame.schema.fields] != expected:
        raise ValueError("Product schema mismatch")
    count_rows = frame.count()
    if (
        count_rows > 8
        or frame.filter(
            F.col("delivery").isNull() | (F.col("delivery") < 1) | (F.col("delivery") > 12)
        ).count()
    ):
        raise ValueError("Bounded delivery IDs required")
    if frame.select("delivery").distinct().count() != count_rows:
        raise ValueError("Delivery IDs must be unique within a microbatch")
    rows = [
        {
            "delivery": row.delivery,
            "id": row.id,
            "event_second": row.event_second,
            "cents": row.cents,
        }
        for row in frame.orderBy("delivery").collect()
    ]
    return json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

The canonical input contains every occurrence, including rejected business data, so replay identity covers the complete batch rather than only successful rows. The structural delivery key makes accounting possible. A duplicated delivery ID or oversized batch is a fatal input-contract error;an ordinary NULL business ID is retained for the invalid ledger.

**Verification evidence:** Compare decoded delivery IDs 1..4 and the NULL marker;reject a 12-row union.

### Exercise 2: Implement the explicit state and lateness policy

Freeze cutoff at previous committed max_event_second minus 10. Validate domain, then classify existing equal ID payload as duplicate, conflicting payload as invalid, new old event as late, and remaining event as accepted.

**Expected:** AfterA:accepted 2, duplicate 1, late 0, invalid 1, total 30, max 105. An invalid far-future row does not advance max time.

```scala
def advancePolicy(previous: ProductState, events: Seq[ProductEvent]): ProductState = {
  require(previous.deliveries.size + events.size <= 12, "Product occurrence budget exceeded")
  val cutoff = previous.maxEvent.map(_ - 10L)
  var next = previous
  for (event <- events.sortBy(_.delivery)) {
    require(
      !next.deliveries.contains(event.delivery),
      "Delivery identity repeated across logical batches"
    )
    next = next.copy(deliveries = next.deliveries + event.delivery)
    val valid = event.id.exists(_.matches("[A-Z]")) && event.second.exists(t =>
      t >= 0L && t <= 1000L
    ) && event.cents.exists(c => c >= 0L && c <= 1000L)
    if (!valid) next = next.copy(invalid = next.invalid + 1L)
    else {
      val id = event.id.get; val value = (event.second.get, event.cents.get)
      next.accepted.get(id) match {
        case Some(existing) if existing == value =>
          next = next.copy(duplicates = next.duplicates + 1L)
        case Some(_)                             => next = next.copy(invalid = next.invalid + 1L)
        case None if cutoff.exists(value._1 < _) => next = next.copy(late = next.late + 1L)
        case None                                =>
          next = next.copy(
            accepted = next.accepted + (id -> value),
            maxEvent = Some(next.maxEvent.fold(value._1)(old => math.max(old, value._1)))
          )
      }
    }
  }
  require(
    next.accepted.size.toLong + next.duplicates + next.late + next.invalid == next.deliveries.size.toLong
  )
  next
}
```

```python
def advance_policy(previous, events):
    import re

    if len(previous["deliveries"]) + len(events) > 12:
        raise ValueError("Product occurrence budget exceeded")
    cutoff = None if previous["max_event"] is None else previous["max_event"] - 10
    next_state = {
        **previous,
        "accepted": dict(previous["accepted"]),
        "deliveries": set(previous["deliveries"]),
    }
    for event in sorted(events, key=lambda row: row["delivery"]):
        if event["delivery"] in next_state["deliveries"]:
            raise ValueError("Delivery identity repeated across logical batches")
        next_state["deliveries"].add(event["delivery"])
        valid = (
            isinstance(event["id"], str)
            and re.fullmatch(r"[A-Z]", event["id"]) is not None
            and type(event["event_second"]) is int
            and 0 <= event["event_second"] <= 1000
            and type(event["cents"]) is int
            and 0 <= event["cents"] <= 1000
        )
        if not valid:
            next_state["invalid"] += 1
            continue
        key = event["id"]
        value = (event["event_second"], event["cents"])
        if key in next_state["accepted"]:
            next_state["duplicates" if next_state["accepted"][key] == value else "invalid"] += 1
        elif cutoff is not None and value[0] < cutoff:
            next_state["late"] += 1
        else:
            next_state["accepted"][key] = value
            next_state["max_event"] = (
                value[0]
                if next_state["max_event"] is None
                else max(next_state["max_event"], value[0])
            )
    if len(next_state["accepted"]) + next_state["duplicates"] + next_state["late"] + next_state[
        "invalid"
    ] != len(next_state["deliveries"]):
        raise ValueError("Occurrence conservation failed")
    return next_state
```

The classification order makes categories mutually exclusive and reviewable. A known equal event is duplicate even if its timestamp is now older than the admission cutoff;an ID conflict is invalid rather than a silent last-write-wins update. Only accepted events advance the committed maximum. The policy is application-managed bounded state, not a claim about Spark native watermark eviction.

**Verification evidence:** Assert exact state and an invalid future control;preserve the original state value.

### Exercise 3: Inject failure after publication but before query completion

Run the actual foreachBatch query with one injected exception after the atomic commit file becomes visible.

**Expected:** The query fails with injected_after_publication;commit 0 is readable and contains the correct first-state ledger.

```scala
def failAfterCommit(spark: SparkSession, input: Path, checkpoint: Path, sink: Path): Unit = {
  var failed = false
  try runProduct(spark, input, checkpoint, sink, true)
  catch {
    case e: org.apache.spark.sql.streaming.StreamingQueryException
        if e.toString.contains("injected_after_publication") =>
      failed = true
  }
  require(failed, "Expected after-publication query failure")
}
```

```python
def fail_after_commit(spark, input_path, checkpoint, sink):
    from pyspark.errors import StreamingQueryException

    try:
        run_product(spark, input_path, checkpoint, sink, True)
    except StreamingQueryException as error:
        if "injected_after_publication" not in str(error):
            raise
    else:
        raise AssertionError("Expected after-publication query failure")
```

The external effect exists even though the streaming query reports failure. That is the classic uncertain-outcome boundary requiring idempotency. The complete input, derived state and predecessor digest are published together in one local atomic file. The test does not erase this committed file during error cleanup or pretend the failed query completed normally.

**Verification evidence:** Inspect the expected streaming exception, attempt 0 and unchanged source/checkpoint ownership.

### Exercise 4: Replay the committed batch without applying it twice

Restart the same compatible query and checkpoint. Validate the existing batch input/content/chain and reuse its state.

**Expected:** Attempts 0,0 and callback rows 4,4;commit 0 bytes and logical state remain unchanged.

```scala
def recoverProduct(spark: SparkSession, input: Path, checkpoint: Path, sink: Path): RunReceipt = {
  runProduct(spark, input, checkpoint, sink, false)
}
```

```python
def recover_product(spark, input_path, checkpoint, sink):
    return run_product(spark, input_path, checkpoint, sink, False)
```

The same batch is delivered again because Spark did not record its successful completion before the injected error. The sink recognizes identical logical input and validates the committed state instead of incrementing counters again. This demonstrates replay-safe local effects, not exactly-once execution of the callback or a universal distributed transaction.

**Verification evidence:** Compare query/run identities, exact bytes and all first-state counters.

### Exercise 5: Process late, boundary, duplicate and conflicting events

PublishBatchB thenBatchC as separate immutable files and run each finite invocation against the same checkpoint.

**Expected:** Final accepted IDsA, B, D, E, F, total 75;duplicate 2, late 1, invalid 2;10 logical occurrences. Zero-valuedD and cutoff-boundaryF remain accepted.

```scala
def finishProduct(
    spark: SparkSession,
    root: Path,
    input: Path,
    checkpoint: Path,
    sink: Path
): ProductState = {
  publishFile(
    root,
    input,
    "batch-02.json",
    Seq(
      """{"delivery":5,"id":"E","event_second":120,"cents":40}""",
      """{"delivery":6,"id":"D","event_second":95,"cents":0}""",
      """{"delivery":7,"id":"C","event_second":94,"cents":7}""",
      """{"delivery":8,"id":"B","event_second":105,"cents":20}"""
    )
  )
  runProduct(spark, input, checkpoint, sink, false)
  val afterB = loadProduct(sink, 1L)
  require(
    afterB.accepted.size == 4 && afterB.duplicates == 2L && afterB.late == 1L && afterB.invalid == 1L && afterB
      .accepted("D") == ((95L, 0L))
  )
  publishFile(
    root,
    input,
    "batch-03.json",
    Seq(
      """{"delivery":9,"id":"B","event_second":105,"cents":999}""",
      """{"delivery":10,"id":"F","event_second":110,"cents":5}"""
    )
  )
  runProduct(spark, input, checkpoint, sink, false)
  loadProduct(sink, 2L)
}
```

```python
def finish_product(spark, root, input_path, checkpoint, sink):
    publish_file(
        root,
        input_path,
        "batch-02.json",
        [
            '{"delivery":5,"id":"E","event_second":120,"cents":40}',
            '{"delivery":6,"id":"D","event_second":95,"cents":0}',
            '{"delivery":7,"id":"C","event_second":94,"cents":7}',
            '{"delivery":8,"id":"B","event_second":105,"cents":20}',
        ],
    )
    run_product(spark, input_path, checkpoint, sink, False)
    after_b = load_product(sink, 1)
    if not (
        len(after_b["accepted"]) == 4
        and after_b["duplicates"] == 2
        and after_b["late"] == 1
        and after_b["invalid"] == 1
        and after_b["accepted"]["D"] == (95, 0)
    ):
        raise ValueError("BatchB oracle failed")
    publish_file(
        root,
        input_path,
        "batch-03.json",
        [
            '{"delivery":9,"id":"B","event_second":105,"cents":999}',
            '{"delivery":10,"id":"F","event_second":110,"cents":5}',
        ],
    )
    run_product(spark, input_path, checkpoint, sink, False)
    return load_product(sink, 2)
```

BatchB deliberately presents eventE at 120 before eventD at 95. A mistaken moving cutoff would rejectD even though 95 is exactly the frozen boundary. BatchC distinguishes a conflictingB payload from an equal duplicate and acceptsF at the new boundary 110. The independent accepted-ID list catches a zero-dropping bug that the total alone would miss.

**Verification evidence:** Compare intermediateB counts and the final literal state;the high-timeE must not make same-batchD late.

### Exercise 6: Hand off correctness, recovery and resource evidence

Return the exact final canonical state, record callback work 14 versus logical occurrences 10, and reject binding the existing sink to a different checkpoint.

**Expected:** Literal golden state matches;attempt IDs 0,0,1,2;callback rows 4,4,4,2;only owned inactive queries are eligible for cleanup.

```scala
def handoffState(state: ProductState): String = {
  require(
    state.accepted.size.toLong + state.duplicates + state.late + state.invalid == state.deliveries.size.toLong
  )
  stateJson(state)
}
```

```python
def handoff_state(state):
    if len(state["accepted"]) + state["duplicates"] + state["late"] + state["invalid"] != len(
        state["deliveries"]
    ):
        raise ValueError("Conservation mismatch")
    return state_json(state)
```

The final state is compared with an independent literal JSON oracle, not only with the other language implementation. Four extra callback rows come from replayingBatchA, while the logical event ledger remains ten occurrences. The namespace guard refuses a new checkpoint before launching a query. Counts, retained keys, commit files and bounded attempts form a resource-work packet;they are not a measured cloud bill or proof of distributed durability.

**Verification evidence:** Compare the complete state JSON and namespace-refusal negative;state the single-writer/local-filesystem limitations.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
