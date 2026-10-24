# spark-038: Observability: plans, progress, event logs and incidents

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-037`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-038` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-038.scala) and [PySpark learner](../lessons/spark-038.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-038_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-038_solution.scala) and [PySpark reference](../solutions/spark-038_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Turn a slow or stalled job report into a bounded evidence-based diagnosis.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Query progress:** A structured observation of a completed streaming trigger, including input, rate, duration and state information when available.

- **State rows:** Retained entries reported by a stateful operator, not necessarily the number of source events or final output rows.

- **State memory:** An operator metric measured in bytes, distinct from total process memory.

- **Skew:** Uneven work among partitions or tasks, which needs key/work distribution evidence rather than one slow duration.

- **Event log:** Persisted execution events that can support later diagnosis when explicitly enabled and retained.

- **Hypothesis:** A proposed cause that should be distinguished from the metric already observed.

A slow-job report is not a diagnosis. It may refer to source starvation, one expensive partition, state growth, storage delay, driver work or an application correctness failure. Observability is useful when each measurement is connected to a specific question and a bounded next check. This lesson combines actual local streaming progress with three clearly labeled synthetic incident records.

The actual query reads three occurrences:1:100,1:100,2:200. Native streaming deduplication retains two keys. The program waits for finite completion, records input/state/sink metrics and reads the committed two-row product. It then adds 3:300, restarts the same checkpoint and observes state growth from two to three entries. That growth has a known explanation:new keys are retained with no eviction policy in this tiny fixture.

## Read progress without inventing unavailable values

numInputRows describes admitted input work for the reported trigger. State operators report their own row counts and memoryUsedBytes. A sink's numOutputRows can be unavailable or represented by a negative sentinel, depending on its implementation. Missing is not zero. The reference preserves that distinction and uses a separate data readback for the exact application result.

State memory is not driver RSS, executor heap size, total container memory or a cloud charge. It is one implementation-specific operator observation. Compare it with state rows, keys, watermark progress and the actual configured retention policy before deciding that growth is abnormal. An increasing state-row count can be expected when new keys arrive and no eviction exists;deleting checkpoints is not an acceptable response to an unexplained graph.

A separate empty AvailableNow run admits no source rows and terminates. That is a valid finite no-work result. It may have no progress records or no readable Parquet product. The code does not manufacture a schema by reading an empty output path. An active long-running query with zero input is a different operational situation:inspect upstream supply, source discovery, permissions and offsets before blaming compute capacity.

## Three seeded incident records

The skew fixture has task runtimes[100,100,10000]milliseconds in one stage. The max-to-median ratio is 100, but the observation alone does not establish the cause. One partition may contain a hot key, or the task may be slowed by storage or another resource. A reversible check is to inspect key/partition work distribution and compare the heavy task's input/shuffle work. Success means a changed plan or partition policy preserves the output oracle while reducing the documented imbalance, not merely hiding the slow task from the chart.

The state fixture reports retained rows 10,100,1000 while the recorded watermark remains unchanged. This motivates checking event-time parsing, the watermark column, new-key rate and retention semantics. It is not proof of a memory leak. The success condition should name expected eviction or bounded key growth under a defined late-event policy, with exact output consequences reviewed.

The input fixture reports an active query, zero admitted rows and no advancing source offset. The next check is source discovery and upstream publication, including whether files are complete and eligible. Adding executors cannot create missing source data. A successful repair should show the intended bounded input admitted and the correct output, not just a higher processing-rate number.

These three records are stored in the case ledger as synthetic diagnostic inputs. They are never mixed into the actual query's measured counters. A useful incident report labels observation, provenance, hypothesis, next check and success condition separately so a reviewer can reject unsupported causal leaps.

## Plans, event logs and data handling

A logical plan explains the requested operators;an executed plan and metrics describe a particular run. Neither is a substitute for output correctness. Classic JVM plan APIs used elsewhere in this track are version-pinned diagnostics and are not assumed available through Spark Connect. The UI is disabled in the course profile, so the lesson does not require a screenshot or expose a new listener.

Event logs can preserve execution history when explicitly enabled before application startup. They can also contain paths, SQL text and configuration. This lesson reviews sanitized supplied task-event fields rather than enabling a history server or exporting complete logs. The allowlist exercise keeps only declared IDs, timing and row-count fields from a fake credential-bearing record. It does not pretend to be a general enterprise redaction policy.

The final packet connects actual input/state/output observations to their query identity and keeps synthetic incident reasoning separate. Every query has a deadline and is stopped before its fresh root is removed. The next chapter adds controlled resource-work comparisons while preserving the same distinction between measured work and a cost estimate.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import org.apache.spark.sql.streaming.{StreamingQuery,Trigger}
import scala.collection.mutable.ArrayBuffer

require(spark.version == "4.0.1","Prepared Spark4.0.1 required")
spark.conf.set("spark.sql.streaming.stopTimeout","5000")
ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-038-")
val input=ownedRoot.resolve("input");val checkpoint=ownedRoot.resolve("checkpoint");val output=ownedRoot.resolve("output")
publishFile(ownedRoot,input,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
import json
import uuid

if spark.version!="4.0.1":raise ValueError("Prepared Spark4.0.1 required")
spark.conf.set("spark.sql.streaming.stopTimeout","5000")
owned_root=Path(tempfile.mkdtemp(prefix="spark-038-",dir=Path.cwd()))
input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";output=owned_root/"output"
publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":1,"cents":100}','{"id":2,"cents":200}'])
```

## Worked example / walkthrough

### Worked example 1

```scala
val result=observe(spark,input,ownedRoot.resolve("demo-checkpoint"),ownedRoot.resolve("demo-output"))
assert(result.inputRows==3L && result.stateRows.contains(2L))
assert(bag(spark,ownedRoot.resolve("demo-output"))==Seq("1:100","2:200"))
```

```python
result=observe(spark,input_path,owned_root/"demo-checkpoint",owned_root/"demo-output")
assert result["input_rows"]==3 and result["state_rows"]==2
assert bag(spark,owned_root/"demo-output")==["1:100","2:200"]
```

The progress state count and committed row bag agree for this actual bounded deduplication query. The observations still have distinct meanings and are checked separately.

### Worked example 2

```scala
val milliseconds=Seq(100L,100L,10000L)
val ratio=milliseconds.max.toDouble/milliseconds.sorted.apply(1)
assert(ratio==100.0)
```

```python
milliseconds=[100,100,10000]
ratio=max(milliseconds)/sorted(milliseconds)[1]
assert ratio==100
```

This synthetic task-duration ratio identifies a long tail. It does not prove the cause or measure a task from the preceding live query.

## Exercises

### Exercise 1: Capture actual finite streaming progress

Run the supplied three-occurrence stream with ID deduplication and return a bounded observation record.

**Expected result/shape:** Input count 3, state rows 2 and exact committed bag 1:100,2:200.

**Verify:** Join the progress record with actual readback and inactive-query evidence.

**Progressive hint:** A progress counter is not an application-value assertion.

### Exercise 2: Interpret state and sink metrics with units

Require a state operator and a nonnegative memory-used measurement;preserve unknown or negative sink-row sentinel values as unavailable.

**Expected result/shape:** State memory is reported in bytes. A missing or negative sink output count is not converted into zero.

**Verify:** Check the real state record and explicit None/-1 normalization controls.

**Progressive hint:** Metric absence is not the numeric value zero.

### Exercise 3: Observe bounded state growth across restart

Add a new ID 3:300 and restart the same compatible checkpoint.

**Expected result/shape:** One new input row, state rows grow 2 to 3, and output gains 3:300.

**Verify:** Compare actual state totals, query identity and exact committed rows.

**Progressive hint:** New retained keys explain growth here;growth alone is not evidence of a leak.

### Exercise 4: Distinguish empty input from a stuck query

Run a separate AvailableNow query over an empty owned input directory.

**Expected result/shape:** Zero admitted rows and a terminated query;state/sink metrics may be absent.

**Verify:** Assert zero input and termination without fabricating an output Parquet schema.

**Progressive hint:** No-data completion is different from an active query making no progress.

### Exercise 5: Diagnose three seeded incident records

For the explicitly synthetic incident fixtures, choose one reversible check for skew, growing state and zero admitted input.

**Expected result/shape:** Inspect key/partition distribution;inspect watermark/key-retention policy;inspect source discovery respectively.

**Verify:** Compare the three exact recommendations and state one success observation for each.

**Progressive hint:** Separate the recorded metric from the causal hypothesis.

### Exercise 6: Sanitize evidence with an allowlist

Keep only stage_id, task_id, run_ms and input_records from a supplied task-event dictionary containing fake credential fields.

**Expected result/shape:** Exact four-field record, with fake token/password absent.

**Verify:** Assert field set and values;do not print the unfiltered input.

**Progressive hint:** Allowlisting is safer than trying to guess every sensitive field name.

## Common pitfalls

Do not call zero input a compute bottleneck without checking source progress. Do not equate state-store bytes with total memory or missing sink metrics with zero output. Do not infer a leak from key growth without its retention policy. Keep synthetic incident inputs separate from measured local evidence, and never export full unreviewed event logs or credentials. Correct outputs remain required after every proposed performance repair.

## Self-check

Explain the contract of `capture` / `capture` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 streaming monitoring](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#monitoring-streaming-queries)

- [Spark4.0.1 monitoring and event logs](https://spark.apache.org/docs/4.0.1/monitoring.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-038: Observability: plans, progress, event logs and incidents.
Read courses/scala-spark/guides/spark-038.md and courses/scala-spark/lessons/spark-038.py;the paired sources are courses/scala-spark/lessons/spark-038.scala and courses/scala-spark/lessons/spark-038.py.
Direct prerequisites: spark-037. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
