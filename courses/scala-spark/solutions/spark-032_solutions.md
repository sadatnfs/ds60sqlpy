# spark-032: Explained paired reference solutions

Read the [guide](../guides/spark-032.md) and attempt one language first. The [Scala reference](spark-032_solution.scala) and [PySpark reference](spark-032_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Define watermark placement and window state

Apply withWatermark(event_time,5 minutes) before grouping by a 5-minute window and team. Aggregate records and total amount, retaining the window struct in the result.

**Expected:** A streaming aggregate with window, team, records, total. The watermark is attached to the same event-time column used by the window.

```scala
def windowed(events: DataFrame): DataFrame = {
  events.withWatermark("event_time","5 minutes").groupBy(window(col("event_time"),"5 minutes"),col("team")).agg(count(lit(1)).as("records"),sum("amount").as("total"))
}
```

```python
def windowed(events):
    return events.withWatermark("event_time","5 minutes").groupBy(F.window("event_time","5 minutes"),"team").agg(F.count(F.lit(1)).alias("records"),F.sum("amount").alias("total"))
```

Watermark metadata must be associated with the event-time expression that drives the stateful window. The aggregate retains the window boundaries so finalization and later output interpretation remain inspectable. Constructing this plan does not yet prove that any watermark has advanced orany window has been emitted.

**Verification evidence:** Assert streaming status and the four output fields before starting the first phase.

### Exercise 2: Record actual watermark progress after the first phase

Run phase 1 and extract nonmissing watermark strings from retained progress. Parse them as instants rather than wall-clock elapsed duration.

**Expected:** Exactly 2 input rows processed. At least one watermark observation exists; the final observed watermark is no later than 00:00 for this phase.

```scala
def watermarks(progress: Seq[StreamingQueryProgress]): Seq[String] = {
  progress.flatMap(p => Option(p.eventTime.get("watermark")))
}
```

```python
def watermarks(progress):
    return [p["eventTime"]["watermark"] for p in progress if p.get("eventTime",{}).get("watermark") is not None]
```

The receipt establishes what the query actually reported rather than equating a configured delay with progress. The first maximum event time is 00:04, so a five-minute delay leaves the first window open. Zero-input progress can be meaningful for stateful finalization, which is why it is retained instead of discarded as noise.

**Verification evidence:** Assert input count 2 and actual watermark presence/order; do not infer finalization from the file count alone.

### Exercise 3: Accept a retained out-of-order event and observe finalization

Publish phase 2, run the compatible query again and read finalized sink rows as(start, team, records, total). Verify the 00:03 event contributed before the first window closed.

**Expected:** The finalized sink contains only(00:00, A,3,35) at this point. The actual watermark reaches at least 00:07.

```scala
def finalRows(spark: SparkSession, root: Path): Seq[(String,String,Long,Long)] = {
  spark.read.schema(resultSchema).parquet(root.resolve("output").toString).select(date_format(col("window.start"),"HH:mm").as("start"),col("team"),col("records"),col("total")).orderBy("start","team").collect().toSeq.map(r => (r.getString(0),r.getString(1),r.getLong(2),r.getLong(3)))
}
```

```python
def final_rows(spark, root):
    frame = spark.read.schema(result_schema).parquet(str(root/"output"))
    return [tuple(r) for r in frame.select(F.date_format("window.start","HH:mm").alias("start"),"team","records","total").orderBy("start","team").collect()]
```

The three-count,35-total output is direct evidence that the out-of-order event was accepted while its window state was retained. The actual watermark then explains append finalization. A two-count,30-total result would reveal a wrong sequencing orlate-data interpretation even if both runs completed successfully.

**Verification evidence:** Assert the exact first-window tuple and the observed progress boundary.

### Exercise 4: Observe a far-late drop after the window has closed

Publish phase 3 after phase 2 has terminated. Read the actual state-operator dropped-by-watermark counters and verify the 999 event does not change the finalized first window.

**Expected:** Two new source rows consumed, one observed watermark drop and unchanged first-window result 35. B at 00:13 remains in pending state.

```scala
def droppedRows(progress: Seq[StreamingQueryProgress]): Long = {
  require(progress.exists(_.stateOperators.nonEmpty),"No state-operator evidence")
  progress.flatMap(_.stateOperators).map(_.numRowsDroppedByWatermark).sum
}
```

```python
def dropped_rows(progress):
    operators = [operator for p in progress for operator in p.get("stateOperators",[])]
    if not operators or any("numRowsDroppedByWatermark" not in operator for operator in operators):
        raise ValueError("No complete state-operator evidence")
    return sum(operator["numRowsDroppedByWatermark"] for operator in operators)
```

The drop counter and unchanged emitted result jointly substantiate the tested policy. Counting source rows alone would incorrectly suggest every consumed row updated business state. This is one controlled beyond-retention outcome; it does not reverse Spark one-sided guarantee into a promise that every event beyond the configured delay is always dropped.

**Verification evidence:** Assert input 2, drop counter 1 and the unchanged sink tuple. Preserve missing metric evidence as an error rather than guessing zero.

### Exercise 5: Advance event time and distinguish finalized frompending output

Publish the 00:30 administrative advancer, run phase 4 and return a ledger of total source inputs, observed drops and final business-window records.

**Expected:** Seven total inputs, one observed drop, five finalized business records across three tuples:(00:00, A,3,35),(00:10, A,1,30),(00:10, B,1,7). The advancer window remains pending.

```scala
def eventLedger(phases: Seq[Seq[StreamingQueryProgress]], output: Seq[(String,String,Long,Long)]): (Long,Long,Long) = {
  (phases.flatten.map(_.numInputRows).sum,phases.map(droppedRows).sum,output.map(_._3).sum)
}
```

```python
def event_ledger(phases, output):
    return sum(p["numInputRows"] for phase in phases for p in phase),sum(dropped_rows(phase) for phase in phases),sum(row[2] for row in output)
```

The reconciliation separates consumed input, discarded late state updates and finalized business output. The administrative event is neither lost norpart of the five business records; its own window has not crossed the finalization threshold. This prevents a finite test from mislabeling pending state as missing output orclaiming every source record must immediately appear in append mode.

**Verification evidence:** Assert all final tuples, input/drop reconciliation and actual watermark at least 00:25.

### Exercise 6: Verify output-mode and sink eligibility through explicit failures

Attempt two invalid configurations in separate owned paths: Update mode to Parquet, and Append mode for an unwatermarked team aggregate. Require analysis rejection and stop any unexpectedly created query in finally.

**Expected:** Both configurations raiseAnalysisException; no active query remains. The valid windowed append sink stays intact.

```scala
def rejectUnsupported(spark: SparkSession, root: Path, kind: String): Unit = {
  require(Set("update-file","append-unwatermarked").contains(kind),"Unknown invalid case")
  val relation = if(kind == "update-file") windowed(stream(spark,root)) else stream(spark,root).groupBy("team").count()
  val mode = if(kind == "update-file") "update" else "append"
  var query: StreamingQuery = null
  var rejected = false
  try {
   query = relation.writeStream.format("parquet").outputMode(mode).option("checkpointLocation",root.resolve(kind+"-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve(kind+"-output").toString)
   query.awaitTermination(30000L)
  } catch { case _: org.apache.spark.sql.AnalysisException => rejected = true }
  finally { if(query != null) query.stop() }
  require(rejected,"Unsupported output configuration was accepted")
}
```

```python
def reject_unsupported(spark, root, kind):
    if kind not in {"update-file","append-unwatermarked"}: raise ValueError("Unknown invalid case")
    relation = windowed(stream(spark,root)) if kind == "update-file" else stream(spark,root).groupBy("team").count()
    mode = "update" if kind == "update-file" else "append"
    query = None; rejected = False
    try:
        query = relation.writeStream.format("parquet").outputMode(mode).option("checkpointLocation",str(root/(kind+"-checkpoint"))).trigger(availableNow=True).start(str(root/(kind+"-output")))
        query.awaitTermination(30)
    except AnalysisException:
        rejected = True
    finally:
        if query is not None: query.stop()
    if not rejected: raise AssertionError("Unsupported output configuration was accepted")
```

The negative cases validate actual engine eligibility rather than relying only on terminology. A file append sink accepts finalized new rows, not arbitrary in-place aggregate updates. The separate owned namespaces prevent a rejected configuration from changing the valid checkpoint or output. Query cleanup remains mandatory even if an unexpected runtime version accepts a case.

**Verification evidence:** Assert each named analysis failure and the unchanged three-row valid sink after the checks.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
