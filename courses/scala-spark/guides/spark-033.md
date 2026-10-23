# spark-033: Stateful deduplication and event identity

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-032`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-033` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-033.scala) and [PySpark learner](../lessons/spark-033.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-033_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-033_solution.scala) and [PySpark reference](../solutions/spark-033_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Bound deduplication state while distinguishing duplicate delivery from legitimate equal-valued events.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Delivery identity:** The identifier of one arrival occurrence, which can differ for two deliveries of the same business event.

- **Business event identity:** The key stating which logical event a delivery represents; equal measured values do not establish equal identity.

- **Watermarked deduplication:** Stateful suppression of repeated keys within a declared event-time retention policy rather than an unlimited historical uniqueness index.

- **NULL-key quarantine:** A separate result retaining records whose missing identity prevents trustworthy attribution or deduplication.

- **State removal evidence:** Observed state-operator counters showing that entries were evicted; this limits any claim of perpetual duplicate memory.

- **Branch input accounting:** The distinction between source deliveries and processing counts from multiple queries reading the same input.

The fixture distinguishes deliveries from events. Delivery 1 represents evente 1, delivery 2 represents e2, and delivery 4 is a replay ofe 1 with the same amount and event time. Delivery 5 representse 3. All three business events happen to have amount 10. A correct event-ID deduplication keeps e1, e2, e3, for a business total of 30; deduplicating only by amount would collapse distinct events and produce an incorrect total 10.

Delivery 3 has a NULL event ID and amount 99. It cannot be confidently attributed to a business event, so it enters a quarantine output with reason missing_event_id. Treating every NULL ID as one shared entity would merge unrelated unknown records. Generating a new arbitrary ID would hide the missing-identity defect. The original delivery ID remains available so the quarantine row can be reconciled with the source occurrence.

The accepted branch applies a five-minute watermark to event_time and dropDuplicatesWithinWatermark on event_id. The replay arrives in a second controlled phase while the first event state is still retained. That sequencing makes the expected retained delivery explicit: the first phase has already committed e1 before the second delivers its replay. The lesson does not claim an arbitrary duplicate survivor policy when conflicting rows with the same ID arrive together in one unordered batch.

Deduplication by ID also does not decide which conflicting payload is authoritative. This fixture replays the same amount and timestamp. A real event ID reused with a different amount ormeaning requires a conflict/version policy, not an assumption that whichever record survives is correct. Stable identity and idempotency are data contracts in addition to the stateful operator choice.

Two finite file queries read the same source. The accepted query writes watermarked deduplicated records to one Parquet sink and checkpoint. The quarantine query writes missing-ID records to its own sink and checkpoint. In the preparedSpark 4.0.1 execution, their progress input metrics count records after the respective branch filters: the first phase reports 2 for accepted identities and 1 for quarantine, not 3 for each raw file scan. The accepted metric still includes an in-horizon replay before deduplication removes it. The final ledger therefore reads the source once as a bounded batch to establish six delivery identities independently of engine metric placement. Adding metrics from arbitrary queries is not a general source-population rule; this fixture has disjoint exhaustive branches and explicit reconciliation.

The third phase publishes an administrative event at 00:20. It remains in the accepted sink with amount 0 so it can advance event-time progress through the stateful operator. Filtering it out before watermarking would remove the evidence needed for that advancement. After the finite run, the business view excludes the explicit administrative ID, but the source and accepted-output ledgers continue to account for it.

Actual state-operator progress must show removal of the older e1, e2, e3 entries after the watermark advances. This makes the retention boundary observable. The system no longer promises to remember every historical event ID forever. Repeated keys outside the retained horizon require a separate durable identity policy if the business needs perpetual uniqueness. The lesson deliberately does not fabricate such a guarantee from the word deduplication.

The final source has six deliveries: four known-ID business deliveries including one replay, oneNULL-ID quarantine delivery, and one advancer. The accepted sink has four rows: three business events plus the advancer. The quarantine sink has one row. The difference of one known-ID delivery is explained by the in-horizon replay. The business sum is 30, while the rejected 99 never contributes. These counts make the decision ledger auditable.

All source files are atomically published under fresh owned scratch, each phase finishes before the next file appears, and both queries stop in finally. The query definitions and checkpoint paths remain stable across phases. No sleeps, sockets or Kafka service are used. The output and state evidence describe this bounded retention policy and fixture, not an unlimited exactly-once guarantee for every possible source or sink.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQueryProgress,Trigger}
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import scala.jdk.CollectionConverters._

spark.conf.set("spark.sql.streaming.stopTimeout","10000")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-033-")
Files.createDirectory(ownedRoot.resolve("input"));Files.createDirectory(ownedRoot.resolve("staging"))
val batches = Seq(
 Seq("""{"delivery_id":1,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}""","""{"delivery_id":2,"event_id":"e2","amount":10,"event_time":"2024-01-01T00:02:00Z"}""","""{"delivery_id":3,"event_id":null,"amount":99,"event_time":"2024-01-01T00:02:00Z"}"""),
 Seq("""{"delivery_id":4,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}""","""{"delivery_id":5,"event_id":"e3","amount":10,"event_time":"2024-01-01T00:03:00Z"}"""),
 Seq("""{"delivery_id":6,"event_id":"__advance__","amount":0,"event_time":"2024-01-01T00:20:00Z"}"""))
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
import os
import uuid

spark.conf.set("spark.sql.streaming.stopTimeout","10000")
owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-033-",dir=".")).resolve()
(owned_root/"input").mkdir();(owned_root/"staging").mkdir()
batches = [
 ['{"delivery_id":1,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}','{"delivery_id":2,"event_id":"e2","amount":10,"event_time":"2024-01-01T00:02:00Z"}','{"delivery_id":3,"event_id":null,"amount":99,"event_time":"2024-01-01T00:02:00Z"}'],
 ['{"delivery_id":4,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}','{"delivery_id":5,"event_id":"e3","amount":10,"event_time":"2024-01-01T00:03:00Z"}'],
 ['{"delivery_id":6,"event_id":"__advance__","amount":0,"event_time":"2024-01-01T00:20:00Z"}']]
```

## Worked example / walkthrough

### Worked example 1

```scala
val occurrences = Seq(("e1",10L),("e2",10L),("e1",10L),("e3",10L))
assert(occurrences.map(_._1).distinct.size == 3 && occurrences.map(_._2).distinct.size == 1)
println("Equal amounts are not equal event identities")
```

```python
occurrences = [("e1",10),("e2",10),("e1",10),("e3",10)]
assert len({event for event,_ in occurrences}) == 3 and len({amount for _,amount in occurrences}) == 1
print("Equal amounts are not equal event identities")
```

The independent collection example isolates the key choice. Event identity yields three logical events, whereas value deduplication would erase legitimate equal-valued events. A total that looks plausible is not enough to validate that identity decision.

### Worked example 2

```scala
assert(batches.map(_.size) == Seq(3,2,1) && batches.flatten.size == 6)
println("Six source deliveries feed two independently checkpointed branches")
```

```python
assert [len(batch) for batch in batches] == [3,2,1] and sum(map(len,batches)) == 6
print("Six source deliveries feed two independently checkpointed branches")
```

The prepared execution reports branch-filtered scan counts, which differ from the raw source population. Across the three phases the accepted branch reports 5 and quarantine reports 1. Their values are interpreted using the declared filters and checked against an independent six-delivery source ledger, not treated as an automatic generic accounting identity.

## Exercises

### Exercise 1: Classify missing event identity before deduplication

Add reason missing_event_id for NULL event_id and accepted otherwise, retaining delivery_id, amount and event_time.

**Expected result/shape:** Delivery 3 is quarantined; known IDs are eligible for the separate deduplication policy.

**Verify:** Construct the first streaming classification with all declared fields and verify the exact quarantine row after the first phase.

**Progressive hint:** NULL is not a shared business identity and must not be filled with an invented event ID.

### Exercise 2: Define a bounded event-ID stateful operator

Filter accepted identities, drop the reason field, attach a five-minute watermark to event_time, and deduplicate within that watermark on event_id only.

**Expected result/shape:** The result remains streaming and retains delivery_id, event_id, amount, event_time. Equal amounts across distinct IDs remain distinct.

**Verify:** Assert output shape and use the explicit event_id key, then validate all retained identities through later sink checks.

**Progressive hint:** Including delivery_id in the deduplication key would prevent replay suppression.

### Exercise 3: Execute accepted and quarantine branches with separate checkpoints

Run both first-phase branches with AvailableNow: deduplicated records to accepted-output and missing-ID records to quarantine-output. Use distinct checkpoints and bounded await/stop scopes.

**Expected result/shape:** Accepted(e1, delivery 1,10),(e2, delivery 2,10); quarantine(delivery 3, NULL, missing_event_id). The raw source has 3 rows; prepared branch input metrics report 2 accepted-eligible rows and 1 quarantine row.

**Verify:** Assert both exact output populations, branch metrics 2/1 and an independent raw batch-source count 3.

**Progressive hint:** Two queries reading one source need separate progress identities and checkpoints.

### Exercise 4: Suppress a replay while retaining distinct equal-valued events

Publish the second file after the first phase terminates and run both compatible branches again. Compare the accepted business identities and their total.

**Expected result/shape:** Accepted(e1, delivery 1,10),(e2, delivery 2,10),(e3, delivery 5,10); delivery 4 replay contributes no additional row. Business total 30.

**Verify:** Assert all retained event/delivery pairs, sum 30, raw source total 5 and prepared branch metrics 2 accepted-eligible inputs versus 0 quarantined inputs for this phase.

**Progressive hint:** The first e1 delivery is already committed before its replay arrives, so survivor identity is controlled in this fixture.

### Exercise 5: Observe state removal and state the retention limit

Publish the 00:20 advancer and run both branches. Sum actual numRowsRemoved state metrics from the accepted branch and inspect remaining state.

**Expected result/shape:** The three old business-key states are removed under the observed watermark progression; accepted output still retains their committed rows plus the advancer.

**Verify:** Assert removed state rows at least 3, unchanged business rows and one advancer output. Print actual state metrics without promising perpetual deduplication.

**Progressive hint:** State eviction removes future duplicate memory, not previously committed sink rows.

### Exercise 6: Reconcile deliveries, quarantine, replay suppression and business totals

Read the six source deliveries once as a bounded batch and compare them with both sinks. Return source deliveries, known-ID deliveries, quarantine rows, accepted rows including advancer, and business total.

**Expected result/shape:** Ledger(6,5,1,4,30). One known-ID delivery is suppressed as an in-horizon replay; three distinct equal-valued business events remain.

**Verify:** Assert the complete ledger and six unique delivery IDs; confirm no active queries remain before cleanup.

**Progressive hint:** Do not sum the input metrics of two branches into a unique source count.

## Common pitfalls

Do not deduplicate by amount when identity is the contract. Do not merge all NULL IDs into one event or manufacture replacement IDs silently. A conflicting payload under one ID needs an explicit policy. Do not claim that stateful watermarked deduplication remembers every ID forever. Keep source delivery counts separate from per-query branch processing counts, and stop every owned query before removing its checkpoint or sink.

## Self-check

Explain the contract of `classify` / `classify` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 dropDuplicatesWithinWatermark](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.dropDuplicatesWithinWatermark.html)

- [Spark 4.0.1 streaming deduplication,watermarks and progress](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-033: Stateful deduplication and event identity.
Read courses/scala-spark/guides/spark-033.md and courses/scala-spark/lessons/spark-033.py;the paired sources are courses/scala-spark/lessons/spark-033.scala and courses/scala-spark/lessons/spark-033.py.
Direct prerequisites: spark-032. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
