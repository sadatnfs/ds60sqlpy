# spark-024: AQE, skew and bounded salting experiments

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-023`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-024` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-024.scala) and [PySpark learner](../lessons/spark-024.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-024_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-024_solution.scala) and [PySpark reference](../solutions/spark-024_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Diagnose a skewed key and compare adaptive execution with an explicit, reversible skew strategy.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Key skew:** An uneven key-frequency distribution that can concentrate work even when total row count is moderate.

- **Adaptive Query Execution:** A mechanism that can revise physical decisions using runtime shuffle statistics while preserving the logical query.

- **Initial and final adaptive plans:** The plan before execution and the revised plan after materialization; they are separate observations of the same query.

- **Salting:** Adding a temporary subkey to divide a hot key into several join groups, with a matching replication policy for the small side.

- **Composite join identity:** The full equality key after salting; uniqueness must be checked on key plus salt rather than on key alone.

- **Task-size proxy:** An observed row-load distribution that helps explain skew but does not measure record bytes, CPU cost or task duration.

The source has 10000 facts. Key 0 appears 9000 times, and each key 1 through 10 appears 100 times. The hot-key fraction is therefore 90 percent. A hash redistribution by key sends all 9000 hot-key occurrences to one destination partition, regardless of whether the source was read through four input partitions. Increasing the total partition count alone cannot divide an individual equality key across several join groups.

The dimension contains one row per key with factor=key+1. Every fact has exactly one match. The expected amount total is 10000 and the weighted total is 9000 plus 100 times the sum of factors 2 through 11, which is 15500. Original fact identity remains the primary output key. These invariants are checked across the baseline, AQE and salted implementations so a strategy that accidentally multiplies or loses facts cannot be described as an improvement.

The baseline disables automatic and adaptive broadcasting and runs with AQE disabled. This isolates an ordinary shuffle join rather than allowing a tiny dimension broadcast to bypass the skew mechanism. The choice is intentional for teaching; with this tiny bounded dimension, a broadcast may be a practical alternative. A real investigation should consider that alternative before introducing a more complex salting design.

The adaptive case enablesAQE and skew-join handling, keeps automatic broadcasting disabled, and records initial and final plans around materialization of the same DataFrame. Small demonstration thresholds are explicitly set for this bounded fixture. They are not recommended production defaults. The final plan must be observed rather than assumed to split skew: actual decisions depend on bytes, map-output blocks, partition statistics and eligibility, not only a logical 90-percent hot-key fraction.

A successful adaptive execution can leave the relevant join arrangement unchanged. That outcome is evidence, not a reason to alter the test until a desired operator appears. The reference requires an adaptive plan to reach its final state and the full logical result to match. It prints the plan text so any coalescing or skew-related changes can be inspected. It does not claim that a configuration flag proves a split occurred or that a local elapsed-time difference proves a cluster speedup.

The explicit alternative gives each hot fact a deterministic salt=fact_id modulo 4 and gives every cold fact salt 0. This divides the 9000 hot facts into four logical buckets of 2250. The dimension hot row is replicated to salts 0 through 3, while its ten cold rows keep only salt 0. The expanded dimension has 14 rows and is unique on(key, salt). Each fact still finds exactly one composite-key match. Replicating the fact side as well would multiply the business population and violate the result contract.

The salt is a physical helper, not a business identifier. It is removed from the final projected relation, which again contains fact_id, key, amount, factor. Deterministic assignment makes debugging and repeated runs easier than a fresh random salt. If a workload uses event IDs with a biased modulo pattern, the bucket balance should be measured rather than presumed. This fixture uses consecutive identities so the exact 2250-per-salt population can be checked independently.

The partition-load helper redistributes to eight partitions and records occupied partition row counts for the unsalted and salted keys. All loads must reconcile to 10000. The unsalted ledger contains a partition with at least 9000 rows. The salted ledger is printed as observed evidence. Distinct salted keys can hash to the same physical partition, so the test does not invent a perfect four-way or eight-way physical split. Logical salt buckets and actual partition loads are different levels of the explanation.

This row-load ledger is only a task-size proxy. Wide records, expensive expressions, serialization, spill and network transfer can make equally sized row partitions have very different costs. A production comparison would examine task-duration and byte distributions, peak state, spills and failure/retry behavior. The local experiment demonstrates correctness, adaptive-plan observation and a reversible skew strategy without treating row balance alone as a complete performance model.

All 10000 result tuples are deliberately bounded for this demonstration and collected only for an exact bag oracle. Larger workloads need distributed reconciliation and bounded diagnostics. No external source, checkpoint or service is created. The owned SparkSession is stopped in finally after every action or failure.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold","-1")
spark.conf.set("spark.sql.join.preferSortMergeJoin","true")
spark.conf.set("spark.sql.shuffle.partitions","4")
val facts = spark.range(0L,10000L,1L,4).withColumnRenamed("id","fact_id").withColumn("key",when(col("fact_id") < 9000L,0L).otherwise((col("fact_id") - 9000L) % 10L + 1L)).withColumn("amount",lit(1L))
val dimension = spark.range(0L,11L,1L,2).withColumnRenamed("id","key").withColumn("factor",col("key") + 1L)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold","-1")
spark.conf.set("spark.sql.join.preferSortMergeJoin","true")
spark.conf.set("spark.sql.shuffle.partitions","4")
facts = spark.range(0,10000,1,4).withColumnRenamed("id","fact_id").withColumn("key",F.when(F.col("fact_id")<9000,0).otherwise((F.col("fact_id")-9000)%10+1)).withColumn("amount",F.lit(1).cast("long"))
dimension = spark.range(0,11,1,2).withColumnRenamed("id","key").withColumn("factor",F.col("key")+1)
```

## Worked example / walkthrough

### Worked example 1

```scala
val hot = facts.filter(col("key") === 0L).count()
assert(hot == 9000L && hot.toDouble / 10000.0 == 0.9)
println("Observed hot-key fraction=" + hot.toDouble/10000.0)
```

```python
hot = facts.filter(F.col("key")==0).count()
assert hot == 9000 and hot/10000 == 0.9
print("Observed hot-key fraction=",hot/10000)
```

The hot-key fraction quantifies the input imbalance before choosing a remedy. It does not prove how much time a task will take, but it explains why key-only distribution can concentrate a large share of this relation in one destination.

### Worked example 2

```scala
val expectedWeighted = 9000L + 100L * (2L to 11L).sum
assert(expectedWeighted == 15500L)
println("Weighted-total conservation oracle=" + expectedWeighted)
```

```python
expected_weighted = 9000 + 100*sum(range(2,12))
assert expected_weighted == 15500
print("Weighted-total conservation oracle=",expected_weighted)
```

The formula derives from the declared key frequencies and dimension factors, independently of any Spark join strategy. A salting implementation that duplicates hot facts would fail this total even if its partition layout looked more balanced.

## Exercises

### Exercise 1: Measure the key-frequency imbalance

Return ordered(key, n) counts for the fact relation. Derive total population and the hot-key fraction from this ledger.

**Expected result/shape:** Key 0 has 9000; keys 1..10 each 100. Total 10000 and hot fraction 0.9.

**Verify:** Assert all 11 ledger rows and the exact population/fraction.

**Progressive hint:** Measure the actual key distribution rather than inferring skew from an overall table size.

### Exercise 2: Establish a baseline join with exact identity conservation

Build an inner join with AQE disabled and broadcasting thresholds disabled, returning fact_id, key, amount, factor. Materialize the bounded result and compare every tuple with the generation formula.

**Expected result/shape:** 10000 unique fact identities, amount total 10000 and weighted total 15500. The baseline plan contains a join and is printed.

**Verify:** Assert all 10000 literal formula tuples and both totals before examining any optimization.

**Progressive hint:** Keep the projected business contract identical across all variants.

### Exercise 3: Observe an adaptive plan before and after execution

Build a freshAQE-enabled join with skew handling enabled, coalescing disabled, skew factor 2, threshold 1024 bytes and advisory size 16384 bytes. Capture the initial plan, materialize the same DataFrame and capture the final plan.

**Expected result/shape:** Initial/final text identifies AdaptiveSparkPlan; after materialization isFinalPlan=true. Every result tuple matches the baseline. Actual skew splitting is reported only if visible.

**Verify:** Assert adaptive finalization and full row parity; print both plans and the small demonstration thresholds.

**Progressive hint:** A configuration flag enables a decision mechanism; it does not prove that runtime conditions triggered a split.

### Exercise 4: Split the hot logical key with a deterministic helper

Add salt=fact_id modulo 4 only for key 0 and salt 0 otherwise. WithAQE disabled, compare eight-partition row-load ledgers by key and by(key, salt).

**Expected result/shape:** Hot salt buckets 0..3 each have 2250 rows; cold facts all have salt 0. Both physical ledgers reconcile to 10000, and the unsalted maximum is at least 9000.

**Verify:** Assert all four hot bucket counts and both reconciled ledgers; print actual salted loads without inventing perfect hash balance.

**Progressive hint:** Split each fact once. Different salt buckets can still collide in the same execution partition.

### Exercise 5: Replicate only the matching small-side hot row

Expand dimension key 0 to salts 0,1,2,3 and every other dimension key to salt 0. Retain factor and verify uniqueness on the composite key.

**Expected result/shape:** 14 dimension rows, with four key 0 variants and ten cold rows. Every(key, salt) pair is unique.

**Verify:** Assert row count 14, distinct composite keys 14 and exact hot/cold salt populations.

**Progressive hint:** Use an array of salts chosen by key and explode it on the dimension side only.

### Exercise 6: Remove the physical helper and reconcile the business relation

Join salted facts to the expanded dimension on key and salt, then project only fact_id, key, amount, factor. Compare the complete result with baseline and adaptive variants.

**Expected result/shape:** All 10000 fact tuples remain exactly equal, with amount 10000 and weighted total 15500. Salt is absent from the final schema.

**Verify:** Assert exact canonical bag equality and final column names; report the salted plan and row-load evidence separately from any speed claim.

**Progressive hint:** The matching relation needs the helper key; the business output contract does not.

## Common pitfalls

Do not infer actual skew splitting from spark.sql.adaptive.skewJoin.enabled alone. Inspect the final plan after the same DataFrame is materialized. Do not salt with fresh randomness when reproducible mapping is required, replicate both sides accidentally, or forget the composite equality key. A balanced row ledger does not prove balanced bytes or CPU work. Keep the tiny demonstration thresholds out of production recommendations, and retain a simple broadcast alternative when the dimension is genuinely bounded.

## Self-check

Explain the contract of `keyFrequencies` / `key_frequencies` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 adaptive execution and skew criteria](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)

- [Spark 4.0.1 monitoring and instrumentation](https://spark.apache.org/docs/4.0.1/monitoring.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-024: AQE, skew and bounded salting experiments.
Read courses/scala-spark/guides/spark-024.md and courses/scala-spark/lessons/spark-024.scala;the paired sources are courses/scala-spark/lessons/spark-024.scala and courses/scala-spark/lessons/spark-024.py.
Direct prerequisites: spark-023. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
