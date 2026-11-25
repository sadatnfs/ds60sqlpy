# spark-034: Stream-stream joins and bounded state

Three impressions and four clicks test a stream-stream join. A click counts only when its key matches and it lands in the ten minutes after the impression, so `c1` and `c2` match while `c3` (exactly ten minutes late) and `c4` (an unknown key) do not. The unmatched impression `i2` appears in the outer join only after both watermarks move.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `spark-033`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-034.scala) and [PySpark](../lessons/spark-034.py).

Open the [explained solutions](../solutions/spark-034_solutions.md) after an attempt.

The first worked example checks the half-open interval for an impression at minute 0 and prints `Minute 3 matches; minute 10 is outside the half-open window`. The second joins the literal impressions and clicks in plain code and prints `Independent business pair oracle=` with `[('i1', 'c1'), ('i3', 'c2')]`, the pairs both Spark joins must reproduce.

## Learning objectives

- Express a time-bounded streaming join and explain which unmatched rows can be finalized.
- Put five-minute watermarks on both inputs with the `min` multiple-watermark policy, and join on key equality plus the half-open interval from `impression_time` up to ten minutes later.
- Show that the left outer sink holds only the two matches until advancer rows on both sides push the watermark to at least 00:25, at which point `(i2, NULL)` is emitted, and show that an outer join with no time bound raises `AnalysisException`.

## Vocabulary and concepts

- **Stream-stream join state:** Retained records from both inputs that may still find a future match under the join condition.

- **Time-range predicate:** An explicit relationship between left and right event times that limits which pairs can match.

- **Outer finalization:** Emitting an unmatched row only after progress establishes that no eligible future match is expected under the policy.

- **Multiple-watermark policy:** The rule combining progress from multiple streaming inputs; the conservative minimum can be held back by a slower or idle side.

- **Boundary event:** An event exactly at an interval edge, used to distinguish inclusive from exclusive matching semantics.

- **Retention bound:** A time-based eligibility limit whose actual state size also depends on input rates, key skew and progress; it is not a fixed byte budget.

A stream-stream join cannot decide every match when the first row arrives. It retains records that might match data arriving later on the other side. This lesson joins impression and click streams using both key equality and an explicit interval: click_time is at or after impression_time and strictly before impression_time plus ten minutes. Watermarks on both event-time columns constrain the retained history under the stated late-data policy.

The first impression file has i1/A at 00:00, i2/B at 00:00 and i3/C at 00:05. The click file has c1/A at 00:03, c2/C at 00:10, c3/A at 00:10 and c4/Z at 00:04. The valid pairs are `(i1, c1)` and `(i3, c2)`. Click c3 is exactly at i1's exclusive upper boundary and must not match. Click c4 has no matching identity key. Impression i2 is unmatched, but a streaming left outer join cannot immediately conclude that no B click will arrive within its ten-minute interval.

Both streams use a five-minute watermark. The application explicitly keeps the conservative minimum multiple-watermark policy. At the end of the first finite run, matched pairs can be emitted, but the unmatched i2 result is not yet final. Finishing the currently available files is not evidence that all future event-time possibilities have been ruled out. This is why AvailableNow termination and outer-result finalization are different concepts.

The second phase publishes one 00:30 administrative record on each side, using different keys so the advancers cannot match each other. Advancing both sides matters: under the minimum policy, a stalled input can hold back global progress even if the other side races ahead. After the second finite run and its no-data state-cleanup batch, the actual watermark reaches the required boundary and i2 can be emitted with a NULL click ID. The advancer impression itself is still too recent to be finalized as unmatched.

The final inner sink contains the same two matched pairs. The final left outer sink contains those pairs plus `(i2, NULL)`. The reference inspects actual progress watermarks and state-removal metrics alongside the output. It does not infer an outer NULL row from the mere absence of a click in one input file or from a wall-clock sleep. The two queries use separate checkpoints and sinks so their source progress and state cannot interfere.

The join condition remains part of the business contract. Inclusive BETWEEN would incorrectly include c3 at the ten-minute boundary. Removing the key equality would create unrelated pairs. Removing the temporal bound would leave a left row eligible for an arbitrarily late right match and prevent the same finite outer-finalization reasoning. The final negative control requests a stream-stream left outer join with key equality alone and requires an analysis rejection under this setup.

A time-bounded condition plus watermarks supplies an eviction policy, not a universal fixed-memory guarantee. A high event rate, hot key, large payload or watermark stalled by an idle side can still produce substantial state. Increasing the delay retains more potential matches and state; reducing it changes late-data tolerance. A production design must connect the chosen delay to business lateness requirements and observed state/memory/task metrics.

Changing the multiple-watermark policy to a faster-progress rule can cause the slow stream older data to be treated as late earlier. That is a semantic and operational decision, not just a latency knob. The lesson records the policy and keeps it unchanged across compatible checkpoint restarts. It makes no claim that an input watermark configuration automatically proves all expected outer results are already emitted.

The literal batch pair oracle is evaluated independently from the streaming implementation. It includes key equality and the half-open interval, then separately identifies unmatched business impressions. Administrative advancers are accounted for as source records but excluded from the business oracle by explicit identity. The complete input population is nine records across both sides after the advancers; each query reads that population independently.

Every file is fully staged before atomic arrival, each query is awaited with a deadline and stopped in finally, and cleanup removes only the fresh owned root after all queries are inactive. No external broker, network producer or sleep-based event timing is required. The evidence establishes the stated finite match/finalization ledger and the tested state policy, not a general exactly-once or production-memory claim.

## Supplied local fixture

Impressions are `i1` (key A, 00:00), `i2` (B, 00:00) and `i3` (C, 00:05). Clicks are `c1` (A, 00:03), `c2` (C, 00:10), `c3` (A, 00:10) and `c4` (Z, 00:04). Each side is a separate input folder read one file per batch with `FAILFAST`, and the session sets `spark.sql.streaming.multipleWatermarkPolicy` to `min`. Later, an advancer row at 00:30 is added to each side.

```scala
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.{StreamingQuery, StreamingQueryProgress, Trigger}
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.time.Instant
import scala.jdk.CollectionConverters._

spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
spark.conf.set("spark.sql.streaming.multipleWatermarkPolicy", "min")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-034-")
Seq("impressions", "clicks", "staging").foreach(name =>
  Files.createDirectory(ownedRoot.resolve(name))
)
val impressionLines = Seq(
  """{"impression_id":"i1","key":"A","impression_time":"2024-01-01T00:00:00Z"}""",
  """{"impression_id":"i2","key":"B","impression_time":"2024-01-01T00:00:00Z"}""",
  """{"impression_id":"i3","key":"C","impression_time":"2024-01-01T00:05:00Z"}"""
)
val clickLines = Seq(
  """{"click_id":"c1","key":"A","click_time":"2024-01-01T00:03:00Z"}""",
  """{"click_id":"c2","key":"C","click_time":"2024-01-01T00:10:00Z"}""",
  """{"click_id":"c3","key":"A","click_time":"2024-01-01T00:10:00Z"}""",
  """{"click_id":"c4","key":"Z","click_time":"2024-01-01T00:04:00Z"}"""
)
```

```python
from pyspark.sql import functions as F
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import os
import uuid
from pyspark.errors import AnalysisException

spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
spark.conf.set("spark.sql.streaming.multipleWatermarkPolicy", "min")
owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-034-", dir=".")).resolve()
for name in ["impressions", "clicks", "staging"]:
    (owned_root / name).mkdir()
impression_lines = [
    '{"impression_id":"i1","key":"A","impression_time":"2024-01-01T00:00:00Z"}',
    '{"impression_id":"i2","key":"B","impression_time":"2024-01-01T00:00:00Z"}',
    '{"impression_id":"i3","key":"C","impression_time":"2024-01-01T00:05:00Z"}',
]
click_lines = [
    '{"click_id":"c1","key":"A","click_time":"2024-01-01T00:03:00Z"}',
    '{"click_id":"c2","key":"C","click_time":"2024-01-01T00:10:00Z"}',
    '{"click_id":"c3","key":"A","click_time":"2024-01-01T00:10:00Z"}',
    '{"click_id":"c4","key":"Z","click_time":"2024-01-01T00:04:00Z"}',
]
```

## Worked example / walkthrough

### Worked example 1

```scala
val impressionMinute = 0
assert(3 >= impressionMinute && 3 < impressionMinute + 10)
assert(!(10 >= impressionMinute && 10 < impressionMinute + 10))
println("Minute 3 matches; minute 10 is outside the half-open window")
```

```python
impression_minute = 0
assert 3 >= impression_minute and 3 < impression_minute + 10
assert not (10 >= impression_minute and 10 < impression_minute + 10)
print("Minute 3 matches; minute 10 is outside the half-open window")
```

This independent boundary calculation distinguishes the required interval from an inclusive BETWEEN. The actual join must reproduce the same rule for timestamps rather than relying on coincidental fixture counts.

### Worked example 2

```scala
val impressions = Seq(("i1", "A", 0), ("i2", "B", 0), ("i3", "C", 5))
val clicks = Seq(("c1", "A", 3), ("c2", "C", 10), ("c3", "A", 10), ("c4", "Z", 4))
val pairs =
  for (i <- impressions; c <- clicks if i._2 == c._2 && c._3 >= i._3 && c._3 < i._3 + 10)
    yield (i._1, c._1)
assert(pairs == Seq(("i1", "c1"), ("i3", "c2")))
println("Independent business pair oracle=" + pairs)
```

```python
impressions = [("i1", "A", 0), ("i2", "B", 0), ("i3", "C", 5)]
clicks = [("c1", "A", 3), ("c2", "C", 10), ("c3", "A", 10), ("c4", "Z", 4)]
pairs = [
    (i[0], c[0]) for i in impressions for c in clicks if i[1] == c[1] and i[2] <= c[2] < i[2] + 10
]
assert pairs == [("i1", "c1"), ("i3", "c2")]
print("Independent business pair oracle=", pairs)
```

The tiny nested-loop oracle checks identity and time predicates without reusing Spark join code. It establishes the matched business pairs, but does not by itself say when a streaming outer result becomes final. That timing requires observed watermark progression.

## Exercises

### Exercise 1: Declare both streaming schemas and watermark policies

Read the owned impression and click file directories with their explicit schemas, maxFilesPerTrigger 1 and five-minute watermarks on their respective event-time columns.

**Expected result/shape:** Both relations are streaming; the minimum multiple-watermark policy is explicit and no query runs merely from construction.

**Verify:** Assert both streaming flags, the declared timestamp fields and policy min before execution.

**Progressive hint:** Each side has its own event-time column and progress; do not watermark an unrelated timestamp.

### Exercise 2: Express key equality and the exact time range

Build either an inner or left_outer join using key equality, click_time>=impression_time and click_time<impression_time+10 minutes. Project impression_id, click_id and both timestamps.

**Expected result/shape:** A streaming relation with the four declared columns. The condition can match i1/c1 and i3/c2 but not boundary click c3.

**Verify:** Assert output shape and reject an unsupported kind value; later exact pair checks validate both predicates.

**Progressive hint:** Alias both sides so the equality and time expressions refer to the intended stream.

### Exercise 3: Run inner and outer queries with separate owned recovery state

Execute a named join kind with AvailableNow, Parquet append and its own checkpoint/output paths. Await at most 30 seconds and stop in finally. Run both kinds for the first input phase.

**Expected result/shape:** Each query consumes 7 source rows across its two inputs and terminates. The two checkpoints are distinct.

**Verify:** Assert input 7 for each query and inactive state after both bounded runs; do not combine their processing counts into 14 unique source events.

**Progressive hint:** Each query owns independent state even when it reads the same source directories.

### Exercise 4: Distinguish immediate matches from pending unmatched impressions

Read either owned output as ordered (impression_id, click_id) pairs. After phase 1, compare inner and outer sinks with the two-pair literal oracle.

**Expected result/shape:** Both sinks contain `(i1, c1)`, `(i3, c2)`. i2/NULL is absent because its possible match interval is not yet finalized. c3 and c4 produce no pair.

**Verify:** Assert exact pair lists and absence of premature i2/NULL; do not rely only on output count 2.

**Progressive hint:** An outer join preserves a future unmatched result only after its event-time eligibility is closed.

### Exercise 5: Advance both sides and observe delayed outer finalization

Publish distinct-key 00:30 advancers to both sources, rerun both compatible queries and extract actual watermark/state-removal evidence.

**Expected result/shape:** Inner remains two pairs. Outer becomes `(i1, c1)`, `(i2, NULL)`, `(i3, c2)`. Actual watermark reaches at least 00:25 and state removal is positive; the new advancer impression remains pending.

**Verify:** Assert the complete outer ledger, input 2 for each new run, observed progress boundary and removed-state count.

**Progressive hint:** With minimum watermark policy, both sides must progress; the advancers must not match each other.

### Exercise 6: Reject an outer join without an event-time bound

In a separate owned checkpoint/output namespace, attempt a stream-stream left outer join using only key equality despite input watermarks. Require analysis rejection and stop any unexpectedly created query.

**Expected result/shape:** AnalysisException because this design lacks the required bounded match/finalization condition. The valid inner/outer sinks remain unchanged and no query is active.

**Verify:** Assert the named rejection, inactive state and unchanged final valid outer pairs.

**Progressive hint:** Watermarks alone do not define the temporal relationship between left and right records.

## Common pitfalls

Do not infer unmatched outer output from temporary source silence. Keep key equality and the half-open time predicate explicit. Under a minimum policy, an idle source can delay global watermark progress. Time bounds do not guarantee a fixed memory budget independently of rates, payloads and skew. Do not change stateful checkpoint configuration casually. Use separate sinks/checkpoints for comparison queries, and stop them before deleting only the fresh owned scratch root.

## Self-check

- `c3` has the same key as `i1` and arrives at 00:10. Which part of the join condition rejects it, and what would change if the upper bound were inclusive?
- Why does the outer sink not contain `(i2, NULL)` after the first run, even though `i2` has no matching click in the data?
- The session uses the `min` policy for two watermarks. Why is that the safe choice when one input could run ahead of the other?
- The unbounded outer join is rejected at query start. What state would Spark have to keep forever if it allowed that join?

## Next step

Go on to [spark-035: Checkpoints, restart and delivery guarantees](spark-035.md). Every query so far started, finished and stopped cleanly; the next lesson stops one on purpose and restarts it from its checkpoint to see what is replayed and what is not.

## Primary sources and official APIs

- [Spark 4.3.0 stream-stream joins, watermarks and outer semantics](https://spark.apache.org/docs/4.3.0/streaming/apis-on-dataframes-and-datasets.html)

- [Spark 4.3.0 stateful checkpoint configuration limits](https://spark.apache.org/docs/4.3.0/streaming/additional-information.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-034: Stream-stream joins and bounded state.
Read courses/scala-spark/guides/spark-034.md and courses/scala-spark/lessons/spark-034.scala; the paired sources are courses/scala-spark/lessons/spark-034.scala and courses/scala-spark/lessons/spark-034.py.
Direct prerequisites: spark-033. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
