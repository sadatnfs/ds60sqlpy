# spark-022: Shuffles, stages, tasks and aggregation cost

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-021`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-022` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-022.scala) and [PySpark learner](../lessons/spark-022.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-022_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-022_solution.scala) and [PySpark reference](../solutions/spark-022_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Explain why a wide transformation moves data and distinguish partition count from row count.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Wide transformation:** An operation requiring records from different upstream partitions to meet, such as grouping equal keys.

- **Shuffle map stage:** The upstream work that prepares intermediate records for destination partitions.

- **Reduce partition:** A destination partition consuming its share of shuffled data; its count is distinct from input partitions and worker threads.

- **Partial aggregation:** Combining same-key records locally before redistribution to reduce intermediate records when the aggregate supports it.

- **Task receipt:** Observed stage/task metadata associated with one named action, including the configuration that produced it.

- **Internal exchange metric:** A version-specific measurement from the actual executed Spark exchange operator; its units and API stability must be stated explicitly.

The fixture generates 20000 rows across four input partitions and assigns key=id modulo 1000. Every key occurs 20 times. Grouping by key must bring contributions from different input partitions together, because each input partition contains occurrences of every key. The result has 1000 rows, not 20000 tasks or 1000 necessarily occupied input partitions. These are different quantities and the first task establishes them independently.

Spark can compute partial counts within an input partition before shuffling. In this fixture each of four input partitions sees 1000 keys, so an ideal local count aggregation can reduce 5000 source rows to 1000 partial counts per mapper. At most 4000 such partial key counts need meet downstream for this particular arrangement. A high-cardinality aggregation with nearly every key unique would get much less reduction. The arithmetic model explains a possible mechanism; actual executed metrics remain separate observations.

The controlled comparison sets shuffle partitions to two and then five, with AQE disabled. Each query is built and executed after its setting is applied. Both results must contain the same 1000 key/count pairs and total 20000. Increasing the reduce-partition count changes how downstream work is divided; it cannot change the correct counts. The local worker has two execution threads, so five reduce tasks can run in waves and incur more scheduling overhead even if each task handles less state.

Each collection action gets a unique job-group label. The status tracker locates jobs and stages associated with that action and reports task counts. This is stronger than guessing stage count from source code, but the tracker is a live, retention-limited view. A missing record would be unavailable evidence rather than proof of zero tasks. The fixture's completed action is inspected immediately, within one owned application. The lesson records available completed/failed counts without pretending the status tracker is a durable production audit log.

The exchange metrics exercise intentionally crosses into classic Spark's JVM execution internals. Scala inspects queryExecution.executedPlan; Python uses its _jdf bridge. This is a diagnostic recipe pinned to Spark 4.0.1, not a stable Spark Connect or public cross-version application interface. The reader should understand the boundary: ordinary transformations stay on the public DataFrame API, while this small evidence helper reads the actual executed Exchange metric map after the action.

The verified Spark 4.0.1 exchange implementation exposes dataSize and numPartitions metrics. Here dataSize is serialized data represented by that exchange, not automatically compressed network bytes, remote network transfer or a cluster billing measure. The reference asserts positive observed dataSize and the requested partition count, and prints the metric map with the action's configuration. It does not invent a byte count from the input row count. More detailed task metrics and durable event logs would be needed for a production performance investigation.

The result comparison sorts only the bounded 1000 collected group rows on the driver, so it does not introduce an extra Spark global-order exchange into the measured aggregate plan. This scope choice matters. Calling orderBy before collection would add another physical operation, and a later metrics reader could accidentally attribute that extra work to the original groupBy. The helper retains the same DataFrame object whose action ran so the observed metric tree belongs to the measured query.

The final task computes a transparent workload model:5000 source rows per input partition, at most 4000 partial group records under the stated local-combine assumption, and average output groups per reducer of 500 or 200. Actual hash placement need not be perfectly balanced. No elapsed-time ordering is asserted. A warm JVM, cache state, task startup, serialization and contention can dominate this tiny run; none of them is controlled well enough here to call two or five partitions a universally better choice.

A production comparison would keep logical inputs and outputs fixed, record versions and configuration, collect task-duration and spill distributions, inspect skew and memory pressure, and repeat under a representative workload. This lesson supplies the prerequisite evidence discipline and a bounded runnable mechanism, while preserving the distinction between a local demonstration and a tuning recommendation.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val source = spark.range(0L, 20000L, 1L, 4).withColumn("key", col("id") % 1000L)
val originalShuffle = spark.conf.get("spark.sql.shuffle.partitions")
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    IntegerType,
    StringType,
    DoubleType,
    BooleanType,
    ArrayType,
    MapType,
    TimestampType,
    DecimalType,
)

source = spark.range(0, 20000, 1, 4).withColumn("key", F.col("id") % 1000)
original_shuffle = spark.conf.get("spark.sql.shuffle.partitions")
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(source.count() == 20000L && source.rdd.getNumPartitions == 4)
assert(source.select("key").distinct().count() == 1000L)
println("Input:20000 rows,1000 keys,4 partitions,local[2]")
```

```python
assert source.count() == 20000 and source.rdd.getNumPartitions() == 4
assert source.select("key").distinct().count() == 1000
print("Input:20000 rows,1000 keys,4 partitions,local[2]")
```

The quantities describe row population, key cardinality, input layout and local execution capacity separately. None can substitute for another when explaining how many tasks or intermediate records a grouped query needs.

### Worked example 2

```scala
val partialUpper = 4L * 1000L
assert(partialUpper == 4000L && partialUpper < 20000L)
println("Local partial aggregation can reduce occurrences before redistribution;this is a model")
```

```python
partial_upper = 4 * 1000
assert partial_upper == 4000 and partial_upper < 20000
print("Local partial aggregation can reduce occurrences before redistribution;this is a model")
```

The bound assumes the four input partitions each observe at most 1000 keys and can combine their counts locally. It is not a measured shuffle-record count or byte estimate. The later metric helper reads actual exchange evidence rather than substituting this arithmetic model for measurement.

## Exercises

### Exercise 1: Establish the high-cardinality fixture oracle

Compute input row count, distinct key count and total id sum. Confirm the key formula supports exactly 20 occurrences per key.

**Expected result/shape:** Metrics(20000,1000,199990000); keys 0..999 each occur 20 times by construction.

**Verify:** Assert the aggregate tuple and independent arithmetic sum 0+...+19999.

**Progressive hint:** Separate generated-population reasoning from execution-partition reasoning.

### Exercise 2: Build and execute a controlled grouped query

Require 1..16 shuffle partitions, set that configuration in the owned session and return key, n from groupBy/count. Execute the two-partition case under the supplied unique job group.

**Expected result/shape:** Sorted output[(0,20),...,(999,20)], with total counts 20000 and an Exchange in the executed plan.

**Verify:** Assert every key/count pair and the plan Exchange marker. Reject an out-of-budget partition request.

**Progressive hint:** Set configuration before building and materializing the new query; keep driver-side sorting outside the measured Spark plan.

### Exercise 3: Read actual exchange metrics after the action

Traverse the executed classic Spark plan, collecting each Exchange metric map. Use the version-pinned internal diagnostic API only for evidence after collection.

**Expected result/shape:** One exchange map for this aggregate, with numPartitions 2 and dataSize>0. Record other available metrics without inventing units or missing values.

**Verify:** Assert one observed exchange, its partition metric and positive serialized data size; print the complete available map.

**Progressive hint:** Visit children recursively; Python accesses the same JVM plan through _jdf and Scala collection iterators.

### Exercise 4: Attach stage and task evidence to the named action

Use the status tracker to find jobs for a supplied group and their retained stages. Return stage_id, num_tasks, completed_tasks, failed_tasks ordered by stage identity.

**Expected result/shape:** Nonempty retained stage evidence for the p2 action, including a stage with 2 tasks. All task counters are nonnegative.

**Verify:** Assert nonempty stage rows and a two-task stage, and print the actual counters rather than asserting a universal stage count.

**Progressive hint:** Job-group identity scopes the observation; deduplicate stage IDs before reading them.

### Exercise 5: Change reduce parallelism while preserving the complete result

Run the same source aggregation with 5 shuffle partitions under its own job group. Compare all 1000 group tuples, then report exchange and stage evidence tied to p5.

**Expected result/shape:** Exact output matches p2 and the literal oracle. Exchange numPartitions 5 and positive dataSize; retained task evidence includes a five-task stage.

**Verify:** Assert result parity before inspecting the 5-partition metric and corresponding action-group stages.

**Progressive hint:** Reuse the same logical source but build a fresh grouped DataFrame after changing the setting.

### Exercise 6: Separate a workload model from measured evidence

For the declared 20000-row,1000-key, four-mapper fixture, return source_rows_per_mapper, partial_group_upper and average_output_groups_per_reducer for a positive reducer count. Label them as arithmetic estimates and print version/configuration beside the actual metrics.

**Expected result/shape:** For reducers 2:5000,4000,500. For reducers 5:5000,4000,200. These values do not assert actual balanced hash buckets or network bytes.

**Verify:** Assert the two model tuples and print Spark 4.0.1, AQEfalse, local[2] with the distinct p2/p5 observations.

**Progressive hint:** The local-combine bound is mappers times distinct keys; the average is groups divided by reducers.

## Common pitfalls

Do not equate 20000 input rows with 20000 tasks or 1000 output groups with 1000 partitions. Do not inspect a newly constructed unexecuted plan and call its zero counters measurements of the completed query. Keep the exact DataFrame and action group together. Internal JVM metric access is version-specific and unavailable under some remote APIs; it is an explicit diagnostic boundary. A status-tracker gap is unavailable evidence, not zero work. The default worker does not start a UI or history server and does not contact a remote cluster.

## Self-check

Explain the contract of `sourceMetrics` / `source_metrics` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 monitoring and task metrics](https://spark.apache.org/docs/4.0.1/monitoring.html)

- [Apache Spark 4.0.1 ShuffleExchangeExec source](https://github.com/apache/spark/blob/v4.0.1/sql/core/src/main/scala/org/apache/spark/sql/execution/exchange/ShuffleExchangeExec.scala)

- [Spark 4.0.1 SQL performance configuration](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-022: Shuffles, stages, tasks and aggregation cost.
Read courses/scala-spark/guides/spark-022.md and courses/scala-spark/lessons/spark-022.py;the paired sources are courses/scala-spark/lessons/spark-022.scala and courses/scala-spark/lessons/spark-022.py.
Direct prerequisites: spark-021. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
