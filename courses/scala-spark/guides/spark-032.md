# spark-032: Event time, watermarks and late-data policy

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-031`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-032` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-032.scala) and [PySpark learner](../lessons/spark-032.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-032_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-032_solution.scala) and [PySpark reference](../solutions/spark-032_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- State what a watermark does and test a declared late-event policy with controlled event-time progression.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Event time:** The timestamp attached to the event being analyzed, which can differ from when a process receives or handles it.

- **Watermark:** A progress threshold derived from observed event-time information and a configured delay, used by eligible stateful operations.

- **State eviction:** Removing state that is no longer retained under the operator watermark and window rules.

- **Late-data guarantee:** A one-sided guarantee protecting sufficiently recent event-time data; older data is not universally guaranteed to be dropped or accepted.

- **Append finalization:** Emitting a window result only when its state is considered complete under the declared watermark policy.

- **Event-time advancer:** A controlled fixture record that advances observed event time so pending windows can be finalized in a finite test.

A five-minute watermark delay is not a wall-clock timer that drops every event arriving five minutes after a machine received another record. It is an event-time policy used by a particular stateful operator. The watermark is derived from observed event times and can lag the latest input through microbatch progression. Pausing the program without new event-time evidence does not establish that a window has become final.

This fixture uses five-minute tumbling windows and a five-minute watermark on event_time. Four phases publish one complete input file each, then run the same compatible AvailableNow query against the same owned checkpoint and Parquet append sink. The phases are deliberately sequenced by query termination rather than file modification-time guesses or sleeps. Each phase therefore has a controlled prior state and watermark history.

Phase 1 containsA events at 00:01 with amount 10 and 00:04 with amount 20. They belong to the 00:00-00:05 window. That window is not final merely because the source temporarily has no more files. Phase 2 adds an out-of-orderA event at 00:03 with amount 5 and anA event at 00:12 with amount 30. The 00:03 event is still within retained state and contributes, so the first window final total is 35 from three events.

The 00:12 event advances event-time progress. AvailableNow can execute a no-data batch after a watermark advance, allowing eligible state cleanup and append finalization before termination. After phase 2, the 00:00-00:05 result is in the append sink. The program verifies the actual progress watermark rather than assuming that the configured delay alone proves this happened.

Phase 3 then sends anA event at 00:02 with amount 999, after the first window has been finalized under the observed progress. That far-late event is dropped by the tested stateful policy, and its amount must not change the already emitted 35. Another event, B at 00:13 with amount 7, belongs to the still-open 00:10-00:15 window. The reference records the actual dropped-by-watermark counter, not merely a guessed decision based on event text.

Phase 4 adds an explicit administrative advancer at 00:30 with amount 0. It is a fixture device to move the watermark far enough to finalize the 00:10 windows. The final append product hasA at 00:00 with records 3, total 35; A at 00:10 with records 1, total 30; and B at 00:10 with records 1, total 7. The advancer own 00:30 window remains unfinalized because the final watermark is around 00:25. The test does not pretend that every input row must already appear in an append result.

The event ledger distinguishes five accepted business events, one observed far-late dropped event and one administrative advancer whose window is pending. All seven records were consumed by the source, while only five business events contribute to the three final result rows. Source input counts, late-drop counters, state retention and sink rows are therefore different metrics. None should be substituted for another.

Spark watermark guarantee is intentionally one-sided: events within the supported delay bound are protected from dropping by that watermark policy, while older events may or may not be processed depending on operator state and progress. This lesson demonstrates one controlled older-event drop after finalization. It does not generalize that observation into an exact universal wall-clock deadline or claim that every older event will always be discarded.

Output mode and sink support also matter. Append mode can write finalized window aggregates to a file sink when the watermark is defined on the aggregated event-time column before aggregation. Update mode represents changing results and is not supported by this Parquet file sink. An unwatermarked arbitrary aggregate cannot simply use append mode and declare itself final. The final task executes these invalid configurations in separate owned namespaces and requires their analysis errors.

All queries have bounded awaits and stop in finally. Checkpoint schema, source path, stateful expression and shuffle configuration remain stable across the four phases. Cleanup preserves scratch if any query is unexpectedly active, then the owned session is stopped. The finite test establishes the stated event ledger and progress observations, not a production policy for every possible late arrival.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery,StreamingQueryProgress,Trigger}
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.time.Instant
import scala.jdk.CollectionConverters._

spark.conf.set("spark.sql.streaming.stopTimeout","10000")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-032-")
Files.createDirectory(ownedRoot.resolve("input"));Files.createDirectory(ownedRoot.resolve("staging"))
val batches = Seq(
 Seq("""{"id":1,"team":"A","amount":10,"event_time":"2024-01-01T00:01:00Z"}""","""{"id":2,"team":"A","amount":20,"event_time":"2024-01-01T00:04:00Z"}"""),
 Seq("""{"id":3,"team":"A","amount":5,"event_time":"2024-01-01T00:03:00Z"}""","""{"id":4,"team":"A","amount":30,"event_time":"2024-01-01T00:12:00Z"}"""),
 Seq("""{"id":5,"team":"A","amount":999,"event_time":"2024-01-01T00:02:00Z"}""","""{"id":6,"team":"B","amount":7,"event_time":"2024-01-01T00:13:00Z"}"""),
 Seq("""{"id":7,"team":"__advance__","amount":0,"event_time":"2024-01-01T00:30:00Z"}"""))
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
from datetime import datetime,timedelta
import tempfile
import shutil
import os
import uuid
from pyspark.errors import AnalysisException

spark.conf.set("spark.sql.streaming.stopTimeout","10000")
owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-032-",dir=".")).resolve()
(owned_root/"input").mkdir();(owned_root/"staging").mkdir()
batches = [
 ['{"id":1,"team":"A","amount":10,"event_time":"2024-01-01T00:01:00Z"}','{"id":2,"team":"A","amount":20,"event_time":"2024-01-01T00:04:00Z"}'],
 ['{"id":3,"team":"A","amount":5,"event_time":"2024-01-01T00:03:00Z"}','{"id":4,"team":"A","amount":30,"event_time":"2024-01-01T00:12:00Z"}'],
 ['{"id":5,"team":"A","amount":999,"event_time":"2024-01-01T00:02:00Z"}','{"id":6,"team":"B","amount":7,"event_time":"2024-01-01T00:13:00Z"}'],
 ['{"id":7,"team":"__advance__","amount":0,"event_time":"2024-01-01T00:30:00Z"}']]
```

## Worked example / walkthrough

### Worked example 1

```scala
val firstWindow = Seq((1,10L),(2,20L),(3,5L))
assert(firstWindow.map(_._2).sum == 35L)
println("Retained out-of-order event contributes to35,not30")
```

```python
first_window = [(1,10),(2,20),(3,5)]
assert sum(amount for _,amount in first_window) == 35
print("Retained out-of-order event contributes to35,not30")
```

The expected first-window value explicitly includes the out-of-order event from the second phase. It excludes the later 999 event only because the controlled query history finalizes that window before the third phase arrives, not simply because its timestamp is smaller.

### Worked example 2

```scala
val latest = Instant.parse("2024-01-01T00:30:00Z")
assert(latest.minusSeconds(300L) == Instant.parse("2024-01-01T00:25:00Z"))
println("Five-minute delay is event-time arithmetic;actual watermark still needs a receipt")
```

```python
latest = datetime.fromisoformat("2024-01-01T00:30:00+00:00")
assert latest-timedelta(minutes=5) == datetime.fromisoformat("2024-01-01T00:25:00+00:00")
print("Five-minute delay is event-time arithmetic;actual watermark still needs a receipt")
```

The arithmetic predicts a useful progress boundary but does not replace inspection of the actual query watermark. Microbatch advancement and stateful processing determine when that boundary is applied.

## Exercises

### Exercise 1: Define watermark placement and window state

Apply withWatermark(event_time,5 minutes) before grouping by a 5-minute window and team. Aggregate records and total amount, retaining the window struct in the result.

**Expected result/shape:** A streaming aggregate with window, team, records, total. The watermark is attached to the same event-time column used by the window.

**Verify:** Assert streaming status and the four output fields before starting the first phase.

**Progressive hint:** Placing a watermark after aggregation oron a different timestamp does not establish this append-finalization contract.

### Exercise 2: Record actual watermark progress after the first phase

Run phase 1 and extract nonmissing watermark strings from retained progress. Parse them as instants rather than wall-clock elapsed duration.

**Expected result/shape:** Exactly 2 input rows processed. At least one watermark observation exists; the final observed watermark is no later than 00:00 for this phase.

**Verify:** Assert input count 2 and actual watermark presence/order; do not infer finalization from the file count alone.

**Progressive hint:** Progress can include a no-data batch; collect its watermark evidence as well as positive-input entries.

### Exercise 3: Accept a retained out-of-order event and observe finalization

Publish phase 2, run the compatible query again and read finalized sink rows as(start, team, records, total). Verify the 00:03 event contributed before the first window closed.

**Expected result/shape:** The finalized sink contains only(00:00, A,3,35) at this point. The actual watermark reaches at least 00:07.

**Verify:** Assert the exact first-window tuple and the observed progress boundary.

**Progressive hint:** The 00:12 event advances event time; AvailableNow can run a no-data batch to apply that advance.

### Exercise 4: Observe a far-late drop after the window has closed

Publish phase 3 after phase 2 has terminated. Read the actual state-operator dropped-by-watermark counters and verify the 999 event does not change the finalized first window.

**Expected result/shape:** Two new source rows consumed, one observed watermark drop and unchanged first-window result 35. B at 00:13 remains in pending state.

**Verify:** Assert input 2, drop counter 1 and the unchanged sink tuple. Preserve missing metric evidence as an error rather than guessing zero.

**Progressive hint:** The late event is tested after an observed finalization boundary, not merely against an arithmetic timestamp comparison.

### Exercise 5: Advance event time and distinguish finalized from pending output

Publish the 00:30 administrative advancer, run phase 4 and return a ledger of total source inputs, observed drops and final business-window records.

**Expected result/shape:** Seven total inputs, one observed drop, five finalized business records across three tuples:(00:00, A,3,35),(00:10, A,1,30),(00:10, B,1,7). The advancer window remains pending.

**Verify:** Assert all final tuples, input/drop reconciliation and actual watermark at least 00:25.

**Progressive hint:** The advancer itself is a real source record, but append output need not contain its unfinalized window.

### Exercise 6: Verify output-mode and sink eligibility through explicit failures

Attempt two invalid configurations in separate owned paths: Update mode to Parquet, and Append mode for an unwatermarked team aggregate. Require analysis rejection and stop any unexpectedly created query in finally.

**Expected result/shape:** Both configurations raise AnalysisException; no active query remains. The valid windowed append sink stays intact.

**Verify:** Assert each named analysis failure and the unchanged three-row valid sink after the checks.

**Progressive hint:** An output mode describes result changes; the chosen sink and stateful operation must support that mode.

## Common pitfalls

Do not translate watermark delay into a wall-clock sleep deadline. Do not assume beyond-delay data is always dropped or always accepted. Inspect actual progress and operator counters. Keep a watermark on the same event-time column before window aggregation. Do not count the administrative advancer as finalized business output or mistake pending state for lost data. Check sink/output-mode compatibility and preserve the query/checkpoint contract across the sequential phases.

## Self-check

Explain the contract of `windowed` / `windowed` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 event-time windows,watermarks,guarantees and AvailableNow](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html)

- [Spark 4.0.1 streaming checkpoint configuration boundaries](https://spark.apache.org/docs/4.0.1/streaming/additional-information.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-032: Event time, watermarks and late-data policy.
Read courses/scala-spark/guides/spark-032.md and courses/scala-spark/lessons/spark-032.scala;the paired sources are courses/scala-spark/lessons/spark-032.scala and courses/scala-spark/lessons/spark-032.py.
Direct prerequisites: spark-031. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
