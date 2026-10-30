# spark-022: Explained paired reference solutions

Read the [guide](../guides/spark-022.md) and attempt one language first. The [Scala reference](spark-022_solution.scala) and [PySpark reference](spark-022_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Establish the high-cardinality fixture oracle

Compute input row count, distinct key count and total id sum. Confirm the key formula supports exactly 20 occurrences per key.

**Expected:** Metrics(20000,1000,199990000); keys 0..999 each occur 20 times by construction.

```scala
def sourceMetrics(source: DataFrame): (Long, Long, Long) = {
  val row = source.agg(count(lit(1)), countDistinct("key"), sum("id")).first()
  (row.getLong(0), row.getLong(1), row.getLong(2))
}
```

```python
def source_metrics(source):
    return tuple(source.agg(F.count(F.lit(1)), F.countDistinct("key"), F.sum("id")).first())
```

These checks establish the exact population before changing execution settings. The modulo construction gives each key 20 occurrences because 20000 is 20 complete cycles of 1000 keys. The independent arithmetic identity sum helps detect source-range mistakes without depending on the same Spark grouping implementation being studied.

**Verification evidence:** Assert the aggregate tuple and independent arithmetic sum 0+...+19999.

### Exercise 2: Build and execute a controlled grouped query

Require 1..16 shuffle partitions, set that configuration in the owned session and return key, n from groupBy/count. Execute the two-partition case under the supplied unique job group.

**Expected:** Sorted output[(0,20),...,(999,20)], with total counts 20000 and an Exchange in the executed plan.

```scala
def buildGrouped(source: DataFrame, partitions: Int): DataFrame = {
  require(partitions >= 1 && partitions <= 16, "Partition budget is1..16")
  source.sparkSession.conf.set("spark.sql.shuffle.partitions", partitions.toString)
  source.groupBy("key").agg(count(lit(1)).as("n"))
}
```

```python
def build_grouped(source, partitions):
    if isinstance(partitions, bool) or not isinstance(partitions, int) or not 1 <= partitions <= 16:
        raise ValueError("Partition budget is1..16")
    source.sparkSession.conf.set("spark.sql.shuffle.partitions", str(partitions))
    return source.groupBy("key").agg(F.count(F.lit(1)).alias("n"))
```

The controlled setting is applied to a newly built query in an owned session, then the actual action runs under a named group. The exact output oracle rules out semantic drift. Sorting the collected small group tuples avoids adding a second Spark sort/exchange to the measurement. The partition guard bounds this educational experiment rather than accepting an arbitrary scheduler workload.

**Verification evidence:** Assert every key/count pair and the plan Exchange marker. Reject an out-of-budget partition request.

### Exercise 3: Read actual exchange metrics after the action

Traverse the executed classic Spark plan, collecting each Exchange metric map. Use the version-pinned internal diagnostic API only for evidence after collection.

**Expected:** One exchange map for this aggregate, with numPartitions 2 and dataSize>0. Record other available metrics without inventing units or missing values.

```scala
def exchangeMetrics(frame: DataFrame): Seq[Map[String, Long]] = {
  frame.queryExecution.executedPlan.collect {
    case node if node.nodeName == "Exchange" =>
      node.metrics.map { case (key, metric) => key -> metric.value }.toMap
  }
}
```

```python
def exchange_metrics(frame):
    result = []
    pending = [frame._jdf.queryExecution().executedPlan()]
    while pending:
        node = pending.pop()
        if node.nodeName() == "Exchange":
            metrics = {}
            iterator = node.metrics().iterator()
            while iterator.hasNext():
                entry = iterator.next()
                metrics[str(entry._1())] = int(entry._2().value())
            result.append(metrics)
        children = node.children().iterator()
        while children.hasNext():
            pending.append(children.next())
    return result
```

The helper reads metrics belonging to the executed DataFrame rather than estimating bytes from logical rows. It intentionally depends on the prepared classic Spark 4.0.1 internal plan shape and must be reviewed when upgrading. The dataSize measurement is not a universal network-byte metric. An absent metric would need to be reported as unavailable instead of silently replaced with zero.

**Verification evidence:** Assert one observed exchange, its partition metric and positive serialized data size; print the complete available map.

### Exercise 4: Attach stage and task evidence to the named action

Use the status tracker to find jobs for a supplied group and their retained stages. Return stage_id, num_tasks, completed_tasks, failed_tasks ordered by stage identity.

**Expected:** Nonempty retained stage evidence for the p2 action, including a stage with 2 tasks. All task counters are nonnegative.

```scala
def stageEvidence(spark: SparkSession, group: String): Seq[(Int, Int, Int, Int)] = {
  val tracker = spark.sparkContext.statusTracker
  val stages = tracker
    .getJobIdsForGroup(group)
    .flatMap(id => tracker.getJobInfo(id).toSeq.flatMap(_.stageIds))
    .distinct
    .sorted
  stages
    .flatMap(id =>
      tracker
        .getStageInfo(id)
        .map(info => (id, info.numTasks, info.numCompletedTasks, info.numFailedTasks))
    )
    .toSeq
}
```

```python
def stage_evidence(spark, group):
    tracker = spark.sparkContext.statusTracker()
    stages = set()
    for job_id in tracker.getJobIdsForGroup(group):
        job = tracker.getJobInfo(job_id)
        if job is not None:
            stages.update(job.stageIds)
    result = []
    for stage_id in sorted(stages):
        info = tracker.getStageInfo(stage_id)
        if info is not None:
            result.append((stage_id, info.numTasks, info.numCompletedTasks, info.numFailedTasks))
    return result
```

The named action connects task metadata to its configuration. Stage IDs are runtime identities and are not hard-coded into the oracle. The status tracker can discard old entries and has weak consistency, so the recipe reports retained observations rather than calling missing entries zero work. A production audit would use durable event evidence and task-attempt identity where retries matter.

**Verification evidence:** Assert nonempty stage rows and a two-task stage, and print the actual counters rather than asserting a universal stage count.

### Exercise 5: Change reduce parallelism while preserving the complete result

Run the same source aggregation with 5 shuffle partitions under its own job group. Compare all 1000 group tuples, then report exchange and stage evidence tied to p5.

**Expected:** Exact output matches p2 and the literal oracle. Exchange numPartitions 5 and positive dataSize; retained task evidence includes a five-task stage.

```scala
def compareResults(left: Seq[(Long, Long)], right: Seq[(Long, Long)]): Unit = {
  require(
    left == right && left.size == 1000 && left.map(_._2).sum == 20000L,
    "Grouped result contract changed"
  )
}
```

```python
def compare_results(left, right):
    if left != right or len(left) != 1000 or sum(n for _, n in left) != 20000:
        raise ValueError("Grouped result contract changed")
```

The comparison changes a single distribution setting while preserving the entire grouped relation. The measured exchange and task evidence belong to the distinct named action, avoiding accidental reuse of an earlier run counters. Neither a lower per-task average nor a greater task count establishes a better runtime choice on its own.

**Verification evidence:** Assert result parity before inspecting the 5-partition metric and corresponding action-group stages.

### Exercise 6: Separate a workload model from measured evidence

For the declared 20000-row,1000-key, four-mapper fixture, return source_rows_per_mapper, partial_group_upper and average_output_groups_per_reducer for a positive reducer count. Label them as arithmetic estimates and print version/configuration beside the actual metrics.

**Expected:** For reducers 2:5000,4000,500. For reducers 5:5000,4000,200. These values do not assert actual balanced hash buckets or network bytes.

```scala
def workModel(reducers: Int): (Long, Long, Double) = {
  require(reducers > 0, "Positive reducer count required")
  (20000L / 4L, 4L * 1000L, 1000.0 / reducers)
}
```

```python
def work_model(reducers):
    if isinstance(reducers, bool) or not isinstance(reducers, int) or reducers <= 0:
        raise ValueError("Positive reducer count required")
    return 20000 // 4, 4 * 1000, 1000 / reducers
```

The arithmetic explains why local aggregation and reduce partition count can matter while keeping estimates distinct from observed metrics. Hash distribution can be uneven and task overhead can offset smaller per-task state. The reference intentionally makes no faster/slower assertion. A useful tuning conclusion would require representative data, controlled repeats and measured task/spill distributions beyond this lesson.

**Verification evidence:** Assert the two model tuples and print Spark 4.0.1, AQEfalse, local[2] with the distinct p2/p5 observations.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
