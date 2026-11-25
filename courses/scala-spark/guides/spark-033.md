# spark-033: Stateful deduplication and event identity

Six deliveries describe four business events. One event is delivered twice, two different events carry the same amount, and one delivery has no event ID at all. Deduplication must keep `e1`, `e2` and `e3`, drop the replay of `e1`, send the missing identity to quarantine, and state how long Spark remembers which IDs it has seen.

## Level and prerequisites

Advanced; approximately 105 minutes. Direct prerequisites: `spark-032`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-033.scala) and [PySpark](../lessons/spark-033.py).

Open the [explained solutions](../solutions/spark-033_solutions.md) after an attempt.

The first worked example lists four occurrences with three distinct IDs and a single amount value, and prints `Equal amounts are not equal event identities`. The second checks the planned files, three, two and one deliveries for six in total, and prints `Six source deliveries feed two independently checkpointed branches`.

## Learning objectives

- Bound deduplication state while distinguishing duplicate delivery from legitimate equal-valued events.
- Classify rows with a NULL `event_id` as `missing_event_id` before deduplication, and write the accepted and quarantine branches to separate Parquet sinks with separate checkpoints.
- Deduplicate on `event_id` with `dropDuplicatesWithinWatermark` and a five-minute watermark, keep three distinct events that all have amount 10, and use `numRowsRemoved` to show that old ID state is eventually discarded.

## Vocabulary and concepts

- **Delivery identity:** The identifier of one arrival occurrence, which can differ for two deliveries of the same business event.

- **Business event identity:** The key stating which logical event a delivery represents; equal measured values do not establish equal identity.

- **Watermarked deduplication:** Stateful suppression of repeated keys within a declared event-time retention policy rather than an unlimited historical uniqueness index.

- **NULL-key quarantine:** A separate result retaining records whose missing identity prevents trustworthy attribution or deduplication.

- **State removal evidence:** Observed state-operator counters showing that entries were evicted; this limits any claim of perpetual duplicate memory.

- **Branch input accounting:** The distinction between source deliveries and processing counts from multiple queries reading the same input.

The fixture distinguishes deliveries from events. Delivery 1 represents event e1, delivery 2 represents e2, and delivery 4 is a replay of e1 with the same amount and event time. Delivery 5 represents e3. All three business events happen to have amount 10. A correct event-ID deduplication keeps e1, e2, e3, for a business total of 30; deduplicating only by amount would collapse distinct events and produce an incorrect total 10.

Delivery 3 has a NULL event ID and amount 99. It cannot be confidently attributed to a business event, so it enters a quarantine output with reason missing_event_id. Treating every NULL ID as one shared entity would merge unrelated unknown records. Generating a new arbitrary ID would hide the missing-identity defect. The original delivery ID remains available so the quarantine row can be reconciled with the source occurrence.

The accepted branch applies a five-minute watermark to event_time and dropDuplicatesWithinWatermark on event_id. The replay arrives in a second controlled phase while the first event state is still retained. That sequencing makes the expected retained delivery explicit: the first phase has already committed e1 before the second delivers its replay. The lesson does not claim an arbitrary duplicate survivor policy when conflicting rows with the same ID arrive together in one unordered batch.

Deduplication by ID also does not decide which conflicting payload is authoritative. This fixture replays the same amount and timestamp. A real event ID reused with a different amount or meaning requires a conflict/version policy, not an assumption that whichever record survives is correct. Stable identity and idempotency are data contracts in addition to the stateful operator choice.

Two finite file queries read the same source. The accepted query writes watermarked deduplicated records to one Parquet sink and checkpoint. The quarantine query writes missing-ID records to its own sink and checkpoint. In the prepared Spark 4.3.0 execution, their progress input metrics count records after the respective branch filters: the first phase reports 2 for accepted identities and 1 for quarantine, not 3 for each raw file scan. The accepted metric still includes an in-horizon replay before deduplication removes it. The final ledger therefore reads the source once as a bounded batch to establish six delivery identities independently of engine metric placement. Adding metrics from arbitrary queries is not a general source-population rule; this fixture has disjoint exhaustive branches and explicit reconciliation.

The third phase publishes an administrative event at 00:20. It remains in the accepted sink with amount 0 so it can advance event-time progress through the stateful operator. Filtering it out before watermarking would remove the evidence needed for that advancement. After the finite run, the business view excludes the explicit administrative ID, but the source and accepted-output ledgers continue to account for it.

Actual state-operator progress must show removal of the older e1, e2, e3 entries after the watermark advances. This makes the retention boundary observable. The system no longer promises to remember every historical event ID forever. Repeated keys outside the retained horizon require a separate durable identity policy if the business needs perpetual uniqueness. The lesson deliberately does not fabricate such a guarantee from the word deduplication.

The final source has six deliveries: four known-ID business deliveries including one replay, one NULL-ID quarantine delivery, and one advancer. The accepted sink has four rows: three business events plus the advancer. The quarantine sink has one row. The difference of one known-ID delivery is explained by the in-horizon replay. The business sum is 30, while the rejected 99 never contributes. These counts make the decision ledger auditable.

All source files are atomically published under fresh owned scratch, each phase finishes before the next file appears, and both queries stop in finally. The query definitions and checkpoint paths remain stable across phases. No sleeps, sockets or Kafka service are used. The output and state evidence describe this bounded retention policy and fixture, not an unlimited exactly-once guarantee for every possible source or sink.

## Supplied local fixture

File 0 holds delivery 1 (`e1`, 10, 00:01), delivery 2 (`e2`, 10, 00:02) and delivery 3 (NULL ID, 99, 00:02). File 1 holds delivery 4, a replay of `e1` at 00:01, and delivery 5 (`e3`, 10, 00:03). File 2 holds delivery 6, an `__advance__` event at 00:20 whose only job is to move the watermark. The source is read with `FAILFAST`, so malformed JSON stops the run instead of turning into NULL rows.

```scala
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.{StreamingQueryProgress, Trigger}
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import scala.jdk.CollectionConverters._

spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-033-")
Files.createDirectory(ownedRoot.resolve("input"));
Files.createDirectory(ownedRoot.resolve("staging"))
val batches = Seq(
  Seq(
    """{"delivery_id":1,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}""",
    """{"delivery_id":2,"event_id":"e2","amount":10,"event_time":"2024-01-01T00:02:00Z"}""",
    """{"delivery_id":3,"event_id":null,"amount":99,"event_time":"2024-01-01T00:02:00Z"}"""
  ),
  Seq(
    """{"delivery_id":4,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}""",
    """{"delivery_id":5,"event_id":"e3","amount":10,"event_time":"2024-01-01T00:03:00Z"}"""
  ),
  Seq(
    """{"delivery_id":6,"event_id":"__advance__","amount":0,"event_time":"2024-01-01T00:20:00Z"}"""
  )
)
```

```python
from pyspark.sql import functions as F
from pathlib import Path
import tempfile
import shutil
import os
import uuid

spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-033-", dir=".")).resolve()
(owned_root / "input").mkdir()
(owned_root / "staging").mkdir()
batches = [
    [
        '{"delivery_id":1,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}',
        '{"delivery_id":2,"event_id":"e2","amount":10,"event_time":"2024-01-01T00:02:00Z"}',
        '{"delivery_id":3,"event_id":null,"amount":99,"event_time":"2024-01-01T00:02:00Z"}',
    ],
    [
        '{"delivery_id":4,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}',
        '{"delivery_id":5,"event_id":"e3","amount":10,"event_time":"2024-01-01T00:03:00Z"}',
    ],
    ['{"delivery_id":6,"event_id":"__advance__","amount":0,"event_time":"2024-01-01T00:20:00Z"}'],
]
```

## Worked example / walkthrough

### Worked example 1

```scala
val occurrences = Seq(("e1", 10L), ("e2", 10L), ("e1", 10L), ("e3", 10L))
assert(occurrences.map(_._1).distinct.size == 3 && occurrences.map(_._2).distinct.size == 1)
println("Equal amounts are not equal event identities")
```

```python
occurrences = [("e1", 10), ("e2", 10), ("e1", 10), ("e3", 10)]
assert (
    len({event for event, _ in occurrences}) == 3
    and len({amount for _, amount in occurrences}) == 1
)
print("Equal amounts are not equal event identities")
```

The independent collection example isolates the key choice. Event identity yields three logical events, whereas value deduplication would erase legitimate equal-valued events. A total that looks plausible is not enough to validate that identity decision.

### Worked example 2

```scala
assert(batches.map(_.size) == Seq(3, 2, 1) && batches.flatten.size == 6)
println("Six source deliveries feed two independently checkpointed branches")
```

```python
assert [len(batch) for batch in batches] == [3, 2, 1] and sum(map(len, batches)) == 6
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

**Expected result/shape:** `Accepted(e1, delivery 1, 10)`, `(e2, delivery 2, 10)`; quarantine (delivery 3, NULL, missing_event_id). The raw source has 3 rows; prepared branch input metrics report 2 accepted-eligible rows and 1 quarantine row.

**Verify:** Assert both exact output populations, branch metrics 2/1 and an independent raw batch-source count 3.

**Progressive hint:** Two queries reading one source need separate progress identities and checkpoints.

### Exercise 4: Suppress a replay while retaining distinct equal-valued events

Publish the second file after the first phase terminates and run both compatible branches again. Compare the accepted business identities and their total.

**Expected result/shape:** `Accepted(e1, delivery 1, 10)`, `(e2, delivery 2, 10)`, `(e3, delivery 5, 10)`; delivery 4 replay contributes no additional row. Business total 30.

**Verify:** Assert all retained event/delivery pairs, sum 30, raw source total 5 and prepared branch metrics 2 accepted-eligible inputs versus 0 quarantined inputs for this phase.

**Progressive hint:** The first e1 delivery is already committed before its replay arrives, so survivor identity is controlled in this fixture.

### Exercise 5: Observe state removal and state the retention limit

Publish the 00:20 advancer and run both branches. Sum actual numRowsRemoved state metrics from the accepted branch and inspect remaining state.

**Expected result/shape:** The three old business-key states are removed under the observed watermark progression; accepted output still retains their committed rows plus the advancer.

**Verify:** Assert removed state rows at least 3, unchanged business rows and one advancer output. Print actual state metrics without promising perpetual deduplication.

**Progressive hint:** State eviction removes future duplicate memory, not previously committed sink rows.

### Exercise 6: Reconcile deliveries, quarantine, replay suppression and business totals

Read the six source deliveries once as a bounded batch and compare them with both sinks. Return source deliveries, known-ID deliveries, quarantine rows, accepted rows including advancer, and business total.

**Expected result/shape:** `Ledger(6, 5, 1, 4, 30)`. One known-ID delivery is suppressed as an in-horizon replay; three distinct equal-valued business events remain.

**Verify:** Assert the complete ledger and six unique delivery IDs; confirm no active queries remain before cleanup.

**Progressive hint:** Do not sum the input metrics of two branches into a unique source count.

## Common pitfalls

Do not deduplicate by amount when identity is the contract. Do not merge all NULL IDs into one event or manufacture replacement IDs silently. A conflicting payload under one ID needs an explicit policy. Do not claim that stateful watermarked deduplication remembers every ID forever. Keep source delivery counts separate from per-query branch processing counts, and stop every owned query before removing its checkpoint or sink.

## Self-check

- Delivery 3 has amount 99. Why is it quarantined before deduplication instead of being treated as one more event with an unknown ID?
- Deliveries 2 and 5 both have amount 10. Which column decides that both are kept, and what would deduplicating on `amount` remove?
- Delivery 4 is a replay of `e1`. Why is it suppressed in this run, and under what condition could a much later replay of `e1` be accepted again?
- The ledger is `(6, 5, 1, 4, 30)`. Explain each number and say which one includes the advancer.

## Next step

Go on to [spark-034: Stream-stream joins and bounded state](spark-034.md). Deduplication kept state for one stream; the next lesson joins two streams, where each side must remember the other's rows only for a bounded time.

## Primary sources and official APIs

- [Spark 4.3.0 dropDuplicatesWithinWatermark](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.dropDuplicatesWithinWatermark.html)

- [Spark 4.3.0 streaming deduplication, watermarks and progress](https://spark.apache.org/docs/4.3.0/streaming/apis-on-dataframes-and-datasets.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-033: Stateful deduplication and event identity.
Read courses/scala-spark/guides/spark-033.md and courses/scala-spark/lessons/spark-033.py; the paired sources are courses/scala-spark/lessons/spark-033.scala and courses/scala-spark/lessons/spark-033.py.
Direct prerequisites: spark-032. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
