# spark-038: Observability: plans, progress, event logs and incidents

When a streaming job is reported as slow or stuck, the first task is to collect evidence, not to change settings. This lesson reads the progress report of a deduplicating query, covering input rows, state rows, state memory and operators, then classifies three seeded incidents (a skewed task, growing state and a stalled source) and strips secrets from the evidence before it is shared.

## Level and prerequisites

Advanced; approximately 105 minutes. Direct prerequisites: `spark-037`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-038.scala) and [PySpark](../lessons/spark-038.py).

Open the [explained solutions](../solutions/spark-038_solutions.md) after an attempt.

The first worked example runs `observe` on the fixture into `demo-checkpoint` and `demo-output` and requires 3 input rows, 2 state rows and the bag `1:100, 2:200`. The second computes the skew ratio for task times of 100, 100 and 10,000 milliseconds as the largest time divided by the median, which is exactly 100.

## Learning objectives

- Turn a slow or stalled job report into a bounded evidence-based diagnosis.
- Collect `numInputRows`, the state operator's `numRowsTotal` and `memoryUsedBytes`, the sink row count and the query and run IDs from `lastProgress`, and treat a missing or negative metric as unknown rather than zero.
- Map each seeded symptom to the next check (skew to partition keys, state growth to the watermark and key growth, an idle input to source discovery) and keep only the allowlisted fields `stage_id`, `task_id`, `run_ms` and `input_records` in a shared report.

## Vocabulary and concepts

- **Query progress:** A structured observation of a completed streaming trigger, including input, rate, duration and state information when available.

- **State rows:** Retained entries reported by a stateful operator, not necessarily the number of source events or final output rows.

- **State memory:** An operator metric measured in bytes, distinct from total process memory.

- **Skew:** Uneven work among partitions or tasks, which needs key/work distribution evidence rather than one slow duration.

- **Event log:** Persisted execution events that can support later diagnosis when explicitly enabled and retained.

- **Hypothesis:** A proposed cause that should be distinguished from the metric already observed.

A slow-job report is not a diagnosis. It may refer to source starvation, one expensive partition, state growth, storage delay, driver work or an application correctness failure. Observability is useful when each measurement is connected to a specific question and a bounded next check. This lesson combines actual local streaming progress with three clearly labeled synthetic incident records.

The actual query reads three occurrences: `1:100`, `1:100`, `2:200`. Native streaming deduplication retains two keys. The program waits for finite completion, records input/state/sink metrics and reads the committed two-row product. It then adds 3:300, restarts the same checkpoint and observes state growth from two to three entries. That growth has a known explanation: new keys are retained with no eviction policy in this tiny fixture.

## Read progress without inventing unavailable values

numInputRows describes admitted input work for the reported trigger. State operators report their own row counts and memoryUsedBytes. A sink's numOutputRows can be unavailable or represented by a negative sentinel, depending on its implementation. Missing is not zero. The reference preserves that distinction and uses a separate data readback for the exact application result.

State memory is not driver RSS, executor heap size, total container memory or a cloud charge. It is one implementation-specific operator observation. Compare it with state rows, keys, watermark progress and the actual configured retention policy before deciding that growth is abnormal. An increasing state-row count can be expected when new keys arrive and no eviction exists; deleting checkpoints is not an acceptable response to an unexplained graph.

A separate empty AvailableNow run admits no source rows and terminates. That is a valid finite no-work result. It may have no progress records or no readable Parquet product. The code does not manufacture a schema by reading an empty output path. An active long-running query with zero input is a different operational situation: inspect upstream supply, source discovery, permissions and offsets before blaming compute capacity.

## Three seeded incident records

The skew fixture has task runtimes `[100, 100, 10000]` milliseconds in one stage. The max-to-median ratio is 100, but the observation alone does not establish the cause. One partition may contain a hot key, or the task may be slowed by storage or another resource. A reversible check is to inspect key/partition work distribution and compare the heavy task's input/shuffle work. Success means a changed plan or partition policy preserves the output oracle while reducing the documented imbalance, not merely hiding the slow task from the chart.

The state fixture reports retained rows 10, 100, 1000 while the recorded watermark remains unchanged. This motivates checking event-time parsing, the watermark column, new-key rate and retention semantics. It is not proof of a memory leak. The success condition should name expected eviction or bounded key growth under a defined late-event policy, with exact output consequences reviewed.

The input fixture reports an active query, zero admitted rows and no advancing source offset. The next check is source discovery and upstream publication, including whether files are complete and eligible. Adding executors cannot create missing source data. A successful repair should show the intended bounded input admitted and the correct output, not just a higher processing-rate number.

These three records are stored in the case ledger as synthetic diagnostic inputs. They are never mixed into the actual query's measured counters. A useful incident report labels observation, provenance, hypothesis, next check and success condition separately so a reviewer can reject unsupported causal leaps.

## Plans, event logs and data handling

A logical plan explains the requested operators; an executed plan and metrics describe a particular run. Neither is a substitute for output correctness. Classic JVM plan APIs used elsewhere in this track are version-pinned diagnostics and are not assumed available through Spark Connect. The UI is disabled in the course profile, so the lesson does not require a screenshot or expose a new listener.

Event logs can preserve execution history when explicitly enabled before application startup. They can also contain paths, SQL text and configuration. This lesson reviews sanitized supplied task-event fields rather than enabling a history server or exporting complete logs. The allowlist exercise keeps only declared IDs, timing and row-count fields from a fake credential-bearing record. It does not pretend to be a general enterprise redaction policy.

The final packet connects actual input/state/output observations to their query identity and keeps synthetic incident reasoning separate. Every query has a deadline and is stopped before its fresh root is removed. The next chapter adds controlled resource-work comparisons while preserving the same distinction between measured work and a cost estimate.

## Supplied local fixture

`batch-01.json` holds ID 1 twice with 100 cents and ID 2 once with 200, so the deduplicating query reads three rows but keeps two keys in state. Each `observe` call runs an `AvailableNow` Parquet append query and returns its measurements as a dictionary. The incident fixtures are plain data: the skew case has task times of 100, 100 and 10,000 ms, the state case retains 10, 100 and then 1,000 rows under a watermark that never moves, and the input case is an active query that reads zero rows and never advances its offset.

```scala prelude=../solutions/spark-038_solution.scala
import org.apache.spark.sql.functions._
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import org.apache.spark.sql.streaming.{StreamingQuery, Trigger}
import scala.collection.mutable.ArrayBuffer

require(spark.version == "4.3.0", "Prepared Spark 4.3.0 required")
spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), "spark-038-")
val input = ownedRoot.resolve("input"); val checkpoint = ownedRoot.resolve("checkpoint");
val output = ownedRoot.resolve("output")
publishFile(
  ownedRoot,
  input,
  "batch-01.json",
  Seq("""{"id":1,"cents":100}""", """{"id":1,"cents":100}""", """{"id":2,"cents":200}""")
)
```

```python prelude=../solutions/spark-038_solution.py
from pyspark.sql import functions as F
from pathlib import Path
import tempfile
import shutil
import json
import uuid

if spark.version != "4.3.0":
    raise ValueError("Prepared Spark 4.3.0 required")
spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
owned_root = Path(tempfile.mkdtemp(prefix="spark-038-", dir=Path.cwd()))
input_path = owned_root / "input"
checkpoint = owned_root / "checkpoint"
output = owned_root / "output"
publish_file(
    owned_root,
    input_path,
    "batch-01.json",
    ['{"id":1,"cents":100}', '{"id":1,"cents":100}', '{"id":2,"cents":200}'],
)
```

## Worked example / walkthrough

### Worked example 1

```scala
val result =
  observe(spark, input, ownedRoot.resolve("demo-checkpoint"), ownedRoot.resolve("demo-output"))
assert(result.inputRows == 3L && result.stateRows.contains(2L))
assert(bag(spark, ownedRoot.resolve("demo-output")) == Seq("1:100", "2:200"))
```

```python
result = observe(spark, input_path, owned_root / "demo-checkpoint", owned_root / "demo-output")
assert result["input_rows"] == 3 and result["state_rows"] == 2
assert bag(spark, owned_root / "demo-output") == ["1:100", "2:200"]
```

The progress state count and committed row bag agree for this actual bounded deduplication query. The observations still have distinct meanings and are checked separately.

### Worked example 2

```scala
val milliseconds = Seq(100L, 100L, 10000L)
val ratio = milliseconds.max.toDouble / milliseconds.sorted.apply(1)
assert(ratio == 100.0)
```

```python
milliseconds = [100, 100, 10000]
ratio = max(milliseconds) / sorted(milliseconds)[1]
assert ratio == 100
```

This synthetic task-duration ratio identifies a long tail. It does not prove the cause or measure a task from the preceding live query.

## Exercises

### Exercise 1: Capture actual finite streaming progress

Run the supplied three-occurrence stream with ID deduplication and return a bounded observation record.

**Expected result/shape:** Input count 3, state rows 2 and exact committed bag `1:100, 2:200`.

**Verify:** Join the progress record with actual readback and inactive-query evidence.

**Progressive hint:** A progress counter is not an application-value assertion.

### Exercise 2: Interpret state and sink metrics with units

Require a state operator and a nonnegative memory-used measurement; preserve unknown or negative sink-row sentinel values as unavailable.

**Expected result/shape:** State memory is reported in bytes. A missing or negative sink output count is not converted into zero.

**Verify:** Check the real state record and explicit None/-1 normalization controls.

**Progressive hint:** Metric absence is not the numeric value zero.

### Exercise 3: Observe bounded state growth across restart

Add a new ID 3:300 and restart the same compatible checkpoint.

**Expected result/shape:** One new input row, state rows grow 2 to 3, and output gains 3:300.

**Verify:** Compare actual state totals, query identity and exact committed rows.

**Progressive hint:** New retained keys explain growth here; growth alone is not evidence of a leak.

### Exercise 4: Distinguish empty input from a stuck query

Run a separate AvailableNow query over an empty owned input directory.

**Expected result/shape:** Zero admitted rows and a terminated query; state/sink metrics may be absent.

**Verify:** Assert zero input and termination without fabricating an output Parquet schema.

**Progressive hint:** No-data completion is different from an active query making no progress.

### Exercise 5: Diagnose three seeded incident records

For the explicitly synthetic incident fixtures, choose one reversible check for skew, growing state and zero admitted input.

**Expected result/shape:** Inspect key/partition distribution; inspect watermark/key-retention policy; inspect source discovery respectively.

**Verify:** Compare the three exact recommendations and state one success observation for each.

**Progressive hint:** Separate the recorded metric from the causal hypothesis.

### Exercise 6: Sanitize evidence with an allowlist

Keep only stage_id, task_id, run_ms and input_records from a supplied task-event dictionary containing fake credential fields.

**Expected result/shape:** Exact four-field record, with fake token/password absent.

**Verify:** Assert field set and values; do not print the unfiltered input.

**Progressive hint:** Allowlisting is safer than trying to guess every sensitive field name.

## Common pitfalls

Do not call zero input a compute bottleneck without checking source progress. Do not equate state-store bytes with total memory or missing sink metrics with zero output. Do not infer a leak from key growth without its retention policy. Keep synthetic incident inputs separate from measured local evidence, and never export full unreviewed event logs or credentials. Correct outputs remain required after every proposed performance repair.

## Self-check

- The first run reads 3 rows but stores 2 state rows. Which row has no state entry of its own, and why is the input count still 3?
- `known_metric` returns None for `-1` but 0 for `0`. Why must an unknown value never be reported as zero in an incident note?
- After `batch-02.json`, input is 1 and state is 3 with the same query ID. What would a changed query ID suggest about the checkpoint?
- A raw report contains `password` and `token` fields. Why keep an allowlist of four fields rather than deleting the names you already know are secret?

## Next step

Go on to [spark-039: Resource budgets, spill and cost tradeoffs](spark-039.md). This lesson diagnosed a query from its metrics; the next one measures the same keyed work at two partition counts and turns the numbers into a cost estimate inside a fixed budget.

## Primary sources and official APIs

- [Spark 4.3.0 streaming monitoring](https://spark.apache.org/docs/4.3.0/streaming/apis-on-dataframes-and-datasets.html#monitoring-streaming-queries)

- [Spark 4.3.0 monitoring and event logs](https://spark.apache.org/docs/4.3.0/monitoring.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-038: Observability: plans, progress, event logs and incidents.
Read courses/scala-spark/guides/spark-038.md and courses/scala-spark/lessons/spark-038.py; the paired sources are courses/scala-spark/lessons/spark-038.scala and courses/scala-spark/lessons/spark-038.py.
Direct prerequisites: spark-037. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
