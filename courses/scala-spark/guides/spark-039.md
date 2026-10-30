# spark-039: Resource budgets, spill and cost tradeoffs

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-038`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-039` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-039.scala) and [PySpark learner](../lessons/spark-039.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-039_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-039_solution.scala) and [PySpark reference](../solutions/spark-039_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Choose a resource-aware strategy from measured work rather than a single elapsed time.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Work metric:** A measured quantity such as bytes, records, partitions or operator spill, with its exact scope and unit.

- **Spill:** An operator moving intermediate data out of its in-memory working structures;the reported metric must be interpreted under that operator contract.

- **Skewed key:** A key receiving a disproportionately large share of records, which hashing alone keeps together.

- **Task granularity:** The size and number of task work units, distinct from the number of CPU execution threads.

- **Cost model:** An estimate from explicit resource quantities, prices and billing assumptions, not an observed bill.

- **Stop budget:** A predeclared resource/input bound that prevents a teaching experiment from expanding without review.

A performance choice should preserve correctness before it compares resource work. This lesson generates exactly 20000 rows and compares two versus four hash partitions under local[2], with AQE disabled and the same aggregation contract. It records actual executed SQL metrics, retained stage/task counters, physical partition row counts, file counts and elapsed time. It then evaluates a separate hypothetical price formula without pretending that the local run produced a cloud bill.

The source has IDs 0 through 19999. IDs below 16000 share key 0;the remaining 4000 use id modulo 100. Therefore key 0 occurs 16040 times and each other key 1..99 occurs 40 times. The independent oracle has 100 key/count pairs whose counts total 20000. A result that drops the hot key or changes multiplicity is wrong even if its elapsed time is attractive.

## What the comparison actually measures

The query explicitly repartitions by key, groups and counts, then collects the known 100-row result under a unique job group. The elapsed interval covers that collect action. Separate diagnostics count physical rows by spark_partition_id, and a later write/readback checks the persisted product. Those extra scans and writes are outside the reported collect interval. The guide states this boundary so the timings are not mistaken for full end-to-end pipeline duration.

Executed-plan metrics are read after the action through classic Spark 4.0.1 JVM diagnostics. dataSize is kept under its actual metric name;it is not relabeled as bytes sent over a remote network. shuffleBytesWritten and spillSize are reported when present. Missing values remain unavailable rather than zero. The program prints the observations instead of asserting one exact machine-dependent byte or time value.

The status tracker attaches retained stage/task counters to the named action. Retention and asynchronous updates mean these are bounded diagnostic observations rather than a permanent complete history. The reference requires meaningful stage evidence but does not assert one universal stage-ID sequence. Exact per-task duration distributions are not collected here. The measured max-to-mean partition-row ratio is explicitly a work-distribution proxy, not a claim about observed task runtime skew.

## More partitions do not create more local CPUs

Both configurations still use two local execution threads. Four partitions can reduce some work-unit sizes but add scheduling and file-management overhead. Hash partitioning keeps the hot key together, so simply increasing the partition count does not divide that key's records. A different aggregation strategy or deliberate salting may address some skew, but it must preserve the original grouping semantics and account for any second-stage merge.

The two configurations write into separate owned output directories. The number of actual Parquet data files is recorded, excluding metadata/CRC files. The test allows one through the configured partition count rather than assuming every partition must write a file. The files are read back and compared with every expected key/count pair. A lower file count alone is not a quality metric:oversized files, too many small files and downstream access patterns introduce different tradeoffs.

The tiny run may report zero spill. That is a valid measurement for this fixture, not proof that a larger workload will remain in memory. Deliberately forcing memory exhaustion would be a different bounded experiment and is not required here. Driver collections are restricted to known small aggregate/partition metadata results;the 20000 raw rows stay in Spark execution.

## Interpret timing and cost with visible assumptions

Record the compiler/runtime family, local[2], AQE setting, input formula, partition count and whether caches were used. This reference does not persist the source, so the diagnostic scans can recompute it. Warmup, JIT, filesystem caches and concurrent host activity can affect elapsed time. Do not assert that the four-partition run must be faster or extrapolate a single small timing to a cluster.

The cost worksheet uses deliberately hypothetical prices:0.05 currency units per vCPU-hour and 0.02 per GiB-month, with a30-day month. Two vCPUs for 3600 seconds cost 0.10 and two GiB for 30 days cost 0.04, for 0.14 total. This arithmetic does not include network, API requests, minimum charges, replication or support overhead. It is a model for reasoning about units, not financial advice or a real service quote.

The stop budget is part of the experiment design:at most 20000 source rows and 8 partitions. A proposal to increase either is rejected before constructing a larger dataset. A sensible next experiment states what uncertainty it would resolve, which metric would change and when it would stop. The goal is a measured, correct comparison with honest limitations, not a dramatic benchmark at any cost.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import org.apache.spark.sql.streaming.{StreamingQuery, Trigger}
import scala.collection.mutable.ArrayBuffer

require(spark.version == "4.0.1", "Prepared Spark4.0.1 required")
spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), "spark-039-")
val source = spark
  .range(0L, 20000L, 1L, 4)
  .withColumn("key", when(col("id") < 16000L, lit(0L)).otherwise(col("id") % 100L))
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
from pathlib import Path
import tempfile
import shutil
import json
import uuid

if spark.version != "4.0.1":
    raise ValueError("Prepared Spark4.0.1 required")
spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
owned_root = Path(tempfile.mkdtemp(prefix="spark-039-", dir=Path.cwd()))
source = spark.range(0, 20000, 1, 4).withColumn(
    "key", F.when(F.col("id") < 16000, F.lit(0).cast("long")).otherwise(F.col("id") % 100)
)
```

## Worked example / walkthrough

### Worked example 1

```scala
val expected = (0L until 100L).map(k => (k, if (k == 0L) 16040L else 40L))
assert(expected.size == 100 && expected.map(_._2).sum == 20000L)
```

```python
expected = [(key, 16040 if key == 0 else 40) for key in range(100)]
assert len(expected) == 100 and sum(count for _, count in expected) == 20000
```

This independent arithmetic oracle fixes the product before any performance measurement. The hot key remains a separate visible condition, not an accidental unknown in the benchmark.

### Worked example 2

```scala
val compute = 2.0 * (3600.0 / 3600.0) * 0.05
val storage = 2.0 * (30.0 / 30.0) * 0.02
assert(math.abs(compute + storage - 0.14) < 1e-12)
```

```python
compute = 2 * (3600 / 3600) * 0.05
storage = 2 * (30 / 30) * 0.02
assert abs(compute + storage - 0.14) < 1e-12
```

The hypothetical cost calculation exposes time/storage unit conversions. It is deliberately separate from actual Spark metrics and does not claim a cloud invoice.

## Exercises

### Exercise 1: Validate the generated skewed fixture

Require 20000 rows, IDs 0..19999,100 keys and total ID sum 199990000. Explain key 0 occurs 16040 times.

**Expected result/shape:** Exact population tuple 20000,20000,100,199990000;key 0 count 16040, other keys 40.

**Verify:** Compare aggregate counts and the independent formula 16000+4000/100.

**Progressive hint:** The first 16000 rows intentionally share key 0.

### Exercise 2: Measure the two-partition configuration

Execute the bounded grouped query under a unique job group, read actual executed metrics, measure partition row counts and persist/read back the product.

**Expected result/shape:** 100 exact key/count pairs, total 20000;nonempty retained stage evidence;one or two data files.

**Verify:** Compare all rows with the literal formula before accepting any work/time report.

**Progressive hint:** Measure after the action and preserve metric names/units.

### Exercise 3: Compare four partitions without assuming a speedup

Repeat with 4 partitions and a separate output directory.

**Expected result/shape:** All 100 result tuples match the same oracle;four buckets sum 20000 and one to four files are observed.

**Verify:** Assert parity and print actual elapsed time/file/metric values without an ordering claim.

**Progressive hint:** local[2] still has two execution threads.

### Exercise 4: Interpret work imbalance and spill honestly

Compute maximum bucket rows divided by mean bucket rows;report available dataSize, shuffleBytesWritten and spillSize metrics without inventing missing values.

**Expected result/shape:** Both observed work ratios exceed 1;unavailable metrics remain None/None-equivalent.

**Verify:** Assert row conservation and positive ratio, then print exact available metric maps and stage receipts.

**Progressive hint:** Bucket-row imbalance is a work-distribution proxy, not measured per-task runtime imbalance.

### Exercise 5: Compute a separate hypothetical cost model

Use a hypothetical rate 0.05 currency units per vCPU-hour and 0.02 per GiB-month. Evaluate 2 vCPUs for 1 hour plus 2 GiB retained for 30 days under a30-day month.

**Expected result/shape:** Estimated 0.14 currency units, not an actual cloud bill or a price recommendation.

**Verify:** Check each unit conversion and reject negative durations/resources.

**Progressive hint:** Keep measured local work separate from hypothetical pricing.

### Exercise 6: Enforce the stop budget before scaling data

Accept only row counts 1..20000 and partition counts 1..8 for this local exercise. Reject an attempted larger fixture before constructing it.

**Expected result/shape:** 20000/4 accepted;20001/4 and 20000/9 rejected.

**Verify:** Assert both refusals and confirm the session shuffle setting restored to 2.

**Progressive hint:** A resource experiment needs an admission budget, not just a timeout after exhaustion.

## Common pitfalls

Do not equate serialized dataSize with remote network traffic, absent spill metrics with zero spill, or partition-row imbalance with measured task-duration imbalance. Do not compare elapsed times for different result contracts or different included work. More partitions do not increase local[2] CPU threads. Keep hypothetical prices and model assumptions separate from actual runtime observations, and enforce the stop budget before expanding data.

## Self-check

Explain the contract of `fixtureMetrics` / `fixture_metrics` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 monitoring metrics](https://spark.apache.org/docs/4.0.1/monitoring.html)

- [Spark4.0.1 SQL performance tuning](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-039: Resource budgets, spill and cost tradeoffs.
Read courses/scala-spark/guides/spark-039.md and courses/scala-spark/lessons/spark-039.scala;the paired sources are courses/scala-spark/lessons/spark-039.scala and courses/scala-spark/lessons/spark-039.py.
Direct prerequisites: spark-038. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
