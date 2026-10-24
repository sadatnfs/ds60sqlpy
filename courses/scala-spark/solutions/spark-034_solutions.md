# spark-034: Explained paired reference solutions

Read the [guide](../guides/spark-034.md) and attempt one language first. The [Scala reference](spark-034_solution.scala) and [PySpark reference](spark-034_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Declare both streaming schemas and watermark policies

Read the owned impression and click file directories with their explicit schemas, maxFilesPerTrigger 1 and five-minute watermarks on their respective event-time columns.

**Expected:** Both relations are streaming; the minimum multiple-watermark policy is explicit and no query runs merely from construction.

```scala
def inputs(spark: SparkSession, root: Path): (DataFrame,DataFrame) = {
  val impressions = spark.readStream.schema(impressionSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(root.resolve("impressions").toString).withWatermark("impression_time","5 minutes")
  val clicks = spark.readStream.schema(clickSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(root.resolve("clicks").toString).withWatermark("click_time","5 minutes")
  (impressions,clicks)
}
```

```python
def inputs(spark, root):
    impressions = spark.readStream.schema(impression_schema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(root/"impressions")).withWatermark("impression_time","5 minutes")
    clicks = spark.readStream.schema(click_schema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(str(root/"clicks")).withWatermark("click_time","5 minutes")
    return impressions,clicks
```

The schemas and watermarks define the stateful interpretation before any query starts. The minimum policy preserves the slower side progress as a constraint on combined eviction. A single fast source therefore cannot be assumed to finalize every unmatched record, and construction alone supplies no processed-row evidence.

**Verification evidence:** Assert both streaming flags, the declared timestamp fields and policymin before execution.

### Exercise 2: Express key equality and the exact time range

Build either an inner orleft_outer join using key equality, click_time>=impression_time and click_time<impression_time+10 minutes. Project impression_id, click_id and both timestamps.

**Expected:** A streaming relation with the four declared columns. The condition can matchi 1/c1 and i3/c2 but not boundaryclickc 3.

```scala
def boundedJoin(impressions: DataFrame, clicks: DataFrame, kind: String): DataFrame = {
  require(Set("inner","left_outer").contains(kind),"Unsupported join kind")
  val i = impressions.as("i");val c = clicks.as("c")
  val condition = col("i.key") === col("c.key") && col("c.click_time") >= col("i.impression_time") && col("c.click_time") < col("i.impression_time") + expr("INTERVAL 10 MINUTES")
  i.join(c,condition,kind).select(col("i.impression_id"),col("c.click_id"),col("i.impression_time"),col("c.click_time"))
}
```

```python
def bounded_join(impressions, clicks, kind):
    if kind not in {"inner","left_outer"}: raise ValueError("Unsupported join kind")
    i = impressions.alias("i");c = clicks.alias("c")
    condition = (F.col("i.key")==F.col("c.key"))&(F.col("c.click_time")>=F.col("i.impression_time"))&(F.col("c.click_time")<F.col("i.impression_time")+F.expr("INTERVAL 10 MINUTES"))
    return i.join(c,condition,kind).select("i.impression_id","c.click_id","i.impression_time","c.click_time")
```

The temporal bound limits future eligibility while key equality preserves entity attribution. The exclusive upper bound is a deliberate business rule, not a syntactic preference. The projected timestamps retain diagnostic context even though the later concise pair ledger shows only identities. A valid physical strategy cannot repair a missing or incorrect predicate.

**Verification evidence:** Assert output shape and reject an unsupported kind value; later exact pair checks validate both predicates.

### Exercise 3: Run inner and outer queries with separate owned recovery state

Execute a named join kind with AvailableNow, Parquet append and its own checkpoint/output paths. Await at most 30 seconds and stop in finally. Run both kinds for the first input phase.

**Expected:** Each query consumes 7 source rows across its two inputs and terminates. The two checkpoints are distinct.

```scala
def runJoin(spark: SparkSession, root: Path, kind: String): Seq[StreamingQueryProgress] = {
  val sources = inputs(spark,root)
  val query = boundedJoin(sources._1,sources._2,kind).writeStream.format("parquet").outputMode("append").option("checkpointLocation",root.resolve(kind+"-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve(kind+"-output").toString)
  try { require(query.awaitTermination(30000L),"Finite join deadline exceeded");require(query.exception.isEmpty && !query.isActive,"Join failed");query.recentProgress.toSeq } finally query.stop()
}
```

```python
def run_join(spark, root, kind):
    left,right = inputs(spark,root)
    query = bounded_join(left,right,kind).writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(root/(kind+"-checkpoint"))).trigger(availableNow=True).start(str(root/(kind+"-output")))
    try:
        if not query.awaitTermination(30): raise TimeoutError("Finite join deadline exceeded")
        if query.exception() is not None or query.isActive: raise RuntimeError("Join failed")
        return list(query.recentProgress)
    finally: query.stop()
```

The independent recovery namespaces prevent one comparison query from consuming or mutating the other state. Their input counters describe two separate executions over the same seven source records. Bounded termination and cleanup are execution guarantees for this finite phase, not proof that an unmatched outer row is already final.

**Verification evidence:** Assert input 7 for each query and inactive state after both bounded runs; do not combine their processing counts into 14 unique source events.

### Exercise 4: Distinguish immediate matches from pending unmatched impressions

Read either owned output as ordered(impression_id, click_id) pairs. After phase 1, compare inner and outer sinks with the two-pair literal oracle.

**Expected:** Both sinks contain(i1, c1),(i3, c2). i2/NULL is absent because its possible match interval is not yet finalized. c3 and c4 produce no pair.

```scala
def pairs(spark: SparkSession, root: Path, kind: String): Seq[(String,Option[String])] = {
  spark.read.schema(resultSchema).parquet(root.resolve(kind+"-output").toString).select("impression_id","click_id").orderBy(col("impression_id"),col("click_id").asc_nulls_last).collect().toSeq.map(r => (r.getString(0),if(r.isNullAt(1)) None else Some(r.getString(1))))
}
```

```python
def pairs(spark, root, kind):
    frame = spark.read.schema(result_schema).parquet(str(root/(kind+"-output")))
    return [tuple(r) for r in frame.select("impression_id","click_id").orderBy(F.col("impression_id"),F.col("click_id").asc_nulls_last()).collect()]
```

The exact identities expose both the key condition and the half-open temporal edge. The outer sink does not yet includei 2 because future eligibleB clicks are still possible under the policy. Returning from AvailableNow means the currently available files were processed, not that the business interval has become final by wall-clock passage.

**Verification evidence:** Assert exact pair lists and absence of prematurei 2/NULL; do not rely only on output count 2.

### Exercise 5: Advance both sides and observe delayed outer finalization

Publish distinct-key 00:30 advancers to both sources, rerun both compatible queries and extract actual watermark/state-removal evidence.

**Expected:** Inner remains two pairs. Outer becomes(i1, c1),(i2, NULL),(i3, c2). Actual watermark reaches at least 00:25 and state removal is positive; the new advancer impression remains pending.

```scala
def progressEvidence(progress: Seq[StreamingQueryProgress]): (Long,Seq[String],Long) = {
  require(progress.exists(_.stateOperators.nonEmpty),"Missing join state evidence")
  (progress.map(_.numInputRows).sum,progress.flatMap(p => Option(p.eventTime.get("watermark"))),progress.flatMap(_.stateOperators).map(_.numRowsRemoved).sum)
}
```

```python
def progress_evidence(progress):
    operators = [operator for p in progress for operator in p.get("stateOperators",[])]
    if not operators or any("numRowsRemoved" not in operator for operator in operators): raise ValueError("Missing join state evidence")
    marks = [p["eventTime"]["watermark"] for p in progress if p.get("eventTime",{}).get("watermark") is not None]
    return sum(p["numInputRows"] for p in progress),marks,sum(operator["numRowsRemoved"] for operator in operators)
```

The two-sided advancers move the conservative progress boundary far enough to close old eligibility intervals. The output and state-removal receipt together establish why the unmatchedNULL row appears now. The administrative impression isnewer and remains pending, so the test does not equate finite source exhaustion with finalization of every left record.

**Verification evidence:** Assert the complete outer ledger, input 2 for each new run, observed progress boundary and removed-state count.

### Exercise 6: Reject an outer join without an event-time bound

In a separate owned checkpoint/output namespace, attempt a stream-stream left outer join using only key equality despite input watermarks. Require analysis rejection and stop any unexpectedly created query.

**Expected:** AnalysisException because this design lacks the required bounded match/finalization condition. The valid inner/outer sinks remain unchanged and no query is active.

```scala
def rejectUnboundedOuter(spark: SparkSession, root: Path): Unit = {
  val sources = inputs(spark,root)
  val invalid = sources._1.as("i").join(sources._2.as("c"),col("i.key") === col("c.key"),"left_outer").select(col("i.impression_id"),col("c.click_id"))
  var query: StreamingQuery = null;var rejected = false
  try {
   query = invalid.writeStream.format("parquet").outputMode("append").option("checkpointLocation",root.resolve("invalid-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve("invalid-output").toString)
   query.awaitTermination(30000L)
  } catch { case _: org.apache.spark.sql.AnalysisException => rejected = true }
  finally { if(query != null) query.stop() }
  require(rejected,"Unbounded outer join unexpectedly accepted")
}
```

```python
def reject_unbounded_outer(spark, root):
    left,right = inputs(spark,root)
    invalid = left.alias("i").join(right.alias("c"),F.col("i.key")==F.col("c.key"),"left_outer").select("i.impression_id","c.click_id")
    query = None; rejected = False
    try:
        query = invalid.writeStream.format("parquet").outputMode("append").option("checkpointLocation",str(root/"invalid-checkpoint")).trigger(availableNow=True).start(str(root/"invalid-output"))
        query.awaitTermination(30)
    except AnalysisException:
        rejected = True
    finally:
        if query is not None: query.stop()
    if not rejected: raise AssertionError("Unbounded outer join unexpectedly accepted")
```

The negative control distinguishes an event-time retention declaration from an actual bounded join relationship. Key equality alone leaves a left row eligible for an arbitrarily timed right match. The separate namespace protects the valid query state, and finally cleanup remains necessary even if a future engine behaves differently from the expected analysis rejection.

**Verification evidence:** Assert the named rejection, inactive state and unchanged final valid outer pairs.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
