# spark-031: Explained paired reference solutions

Read the [guide](../guides/spark-031.md) and attempt one language first. The [Scala reference](spark-031_solution.scala) and [PySpark reference](spark-031_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Publish complete input files atomically

Write each declared file in the owned staging directory, then atomically move it into input under a new batch-N.json name. Reject invalid names or an existing destination.

**Expected:** Three input files, each with 3 completeJSON records; no staging temporary file remains. Reusing batch-0.json is rejected.

```scala
def publishFile(root: Path, name: String, lines: Seq[String]): Unit = {
  require(name.matches("batch-[0-9]+\\.json"), "Invalid input filename")
  val target = root.resolve("input").resolve(name)
  require(!Files.exists(target), "Input file already exists")
  val pending = Files.createTempFile(root.resolve("staging"), "arrival-", ".tmp")
  try {
    Files.writeString(
      pending,
      lines.mkString("\n") + "\n",
      StandardCharsets.UTF_8,
      StandardOpenOption.TRUNCATE_EXISTING
    )
    Files.move(pending, target, StandardCopyOption.ATOMIC_MOVE)
  } finally Files.deleteIfExists(pending)
}
```

```python
def publish_file(root, name, lines):
    if re.fullmatch(r"batch-[0-9]+\.json", name) is None:
        raise ValueError("Invalid input filename")
    target = root / "input" / name
    if target.exists():
        raise ValueError("Input file already exists")
    pending = root / "staging" / (uuid.uuid4().hex + ".tmp")
    try:
        with pending.open("x", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        os.replace(pending, target)
    finally:
        pending.unlink(missing_ok=True)
```

The source sees complete new files rather than an in-progress write. Staging and input share the owned local filesystem, which is the scope of the atomic move assumption. Reusing a filename is rejected because a file source discovery/checkpoint contract is not an in-place record-update protocol. The final cleanup removes only this run staged artifacts.

**Verification evidence:** Assert the file count and explicit existing-name rejection before starting any query.

### Exercise 2: Construct an explicit streaming relation without starting it

Read the owned JSON input through readStream with the declared schema and maxFilesPerTrigger 1. Return the streamingDataFrame; do not call an ordinary batch collect on it.

**Expected:** isStreaming is true, columns are id, team, amount and their types are bigint, string, bigint. No query is started by construction alone.

```scala
def inputStream(spark: SparkSession, root: Path): DataFrame = {
  spark.readStream
    .schema(eventSchema)
    .option("maxFilesPerTrigger", 1)
    .json(root.resolve("input").toString)
}
```

```python
def input_stream(spark, root):
    return (
        spark.readStream.schema(event_schema)
        .option("maxFilesPerTrigger", 1)
        .json(str(root / "input"))
    )
```

The explicit schema makes parsing independent of whichever file happens to be discovered first. isStreaming describes the relation execution model, not proof that any data has been processed. The empty active-query list demonstrates the distinction between constructing a plan and starting its execution.

**Verification evidence:** Assert streaming status and exact type mapping while the active query list remains empty.

### Exercise 3: Define a cumulative aggregate with separate completeness counts

Group by team and compute row_count, known_amounts and total_amount. Use the same expression for streaming and batch relations without filling unknown amounts.

**Expected:** The streaming result remains streaming and has one state/result row per team. Its eventual literal result isA(4,3,15), B(3,2,35), C(2,2,30).

```scala
def teamSummary(frame: DataFrame): DataFrame = {
  frame
    .groupBy("team")
    .agg(
      count(lit(1)).as("row_count"),
      count("amount").as("known_amounts"),
      sum("amount").as("total_amount")
    )
}
```

```python
def team_summary(frame):
    return frame.groupBy("team").agg(
        F.count(F.lit(1)).alias("row_count"),
        F.count("amount").alias("known_amounts"),
        F.sum("amount").alias("total_amount"),
    )
```

The aggregate is a cumulative state definition rather than a per-file table. Known-amount counts preserve measurement completeness while row_count preserves event population. Complete mode is appropriate for displaying this finite cumulative result, but an unbounded growth of grouping keys would require an explicit state-retention design.

**Verification evidence:** Assert output columns and streaming status now; verify the exact final tuples after bounded execution.

### Exercise 4: Run AvailableNow with a deadline and owned cleanup

Start the aggregate in a uniquely named memory sink with complete mode, a fresh checkpoint and AvailableNow. Await at most 30 seconds, require termination and always stop the query in finally.

**Expected:** The query terminates and isActive is false. The memory table holds the final finite aggregate; the checkpoint belongs only to this run.

```scala
def runAvailable(summary: DataFrame, checkpoint: Path, table: String): StreamingQuery = {
  val query = summary.writeStream
    .format("memory")
    .queryName(table)
    .outputMode("complete")
    .option("checkpointLocation", checkpoint.toString)
    .trigger(Trigger.AvailableNow())
    .start()
  try {
    require(query.awaitTermination(30000L), "AvailableNow deadline exceeded")
    require(!query.isActive && query.exception.isEmpty, "Query did not terminate cleanly")
    query
  } finally query.stop()
}
```

```python
def run_available(summary, checkpoint, table):
    query = (
        summary.writeStream.format("memory")
        .queryName(table)
        .outputMode("complete")
        .option("checkpointLocation", str(checkpoint))
        .trigger(availableNow=True)
        .start()
    )
    try:
        if not query.awaitTermination(30):
            raise RuntimeError("AvailableNow deadline exceeded")
        if query.isActive or query.exception() is not None:
            raise RuntimeError("Query did not terminate cleanly")
        return query
    finally:
        query.stop()
```

The trigger defines a finite processing boundary for the files available at query start. The explicit deadline prevents a demonstration from hanging indefinitely, and finally-based stop handles success and failure paths. The memory sink is useful for this owned session inspection, but its presence must not be described as a durable production publication.

**Verification evidence:** Assert bounded await success, no query exception and inactive state. No sleep or external producer is used.

### Exercise 5: Reconcile processed input through progress evidence

Return(batch_id, num_input_rows) from retained query progress. Sum input rows and inspect positive-input batches without confusing cumulative sink snapshots with new input.

**Expected:** Three positive-input batches of 3 records and total input 9. Any zero-input progress entry contributes zero to that total.

```scala
def inputProgress(query: StreamingQuery): Seq[(Long, Long)] = {
  query.recentProgress.toSeq.map(progress => (progress.batchId, progress.numInputRows))
}
```

```python
def input_progress(query):
    return [(p["batchId"], p["numInputRows"]) for p in query.recentProgress]
```

The progress ledger measures what this query consumed, not just what the fixture intended to contain. Positive-input batches correspond to the finite file arrivals under the one-file trigger limit. The aggregate table can grow or update across those batches, but its snapshots are not independent facts to sum. Retained progress is bounded live evidence rather than a permanent audit log.

**Verification evidence:** Assert total 9, three positive batches of 3 and unique recorded batch IDs; print the actual ledger.

### Exercise 6: Compare final streaming output with batch and literal oracles

Read the final memory table, compare its ordered summary tuples with a batch read of the same nine source records, and compare both with the literalA/B/C oracle.

**Expected:** ExactlyA(4,3,15), B(3,2,35), C(2,2,30), whose record counts sum 9, known counts 7 and amounts 80.

```scala
def summaryRows(frame: DataFrame): Seq[(String, Long, Long, Long)] = {
  frame
    .orderBy("team")
    .collect()
    .toSeq
    .map(r => (r.getString(0), r.getLong(1), r.getLong(2), r.getLong(3)))
}
```

```python
def summary_rows(frame):
    return [tuple(r) for r in frame.orderBy("team").collect()]
```

The final table is checked against an independent value contract as well as the batch interpretation. This separates stream scheduling/source-progress behavior from aggregation correctness. The final inactive-query check establishes that the owned query has stopped before its memory view and scratch files are removed; it does not claim a fault-tolerant external sink.

**Verification evidence:** Assert both path comparisons and the independent literal tuple list; confirm no active query remains before cleanup.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
