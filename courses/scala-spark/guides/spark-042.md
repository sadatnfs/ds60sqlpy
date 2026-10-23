# spark-042: Capstone: a recoverable late-event data product

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 180 minutes. Direct design prerequisites: `spark-041`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-042` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-042.scala) and [PySpark learner](../lessons/spark-042.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-042_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-042_solution.scala) and [PySpark reference](../solutions/spark-042_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Deliver a bounded streaming product with credible correctness, recovery and operational evidence.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Delivery identity:** A unique occurrence number for source accounting, distinct from the business event ID used for duplicate detection.

- **Frozen cutoff:** An admission threshold derived from the previously committed maximum and held fixed throughout one microbatch.

- **Conflicting duplicate:** A repeated business ID with different event time or amount, classified invalid under this product contract.

- **Commit chain:** A bounded sequence of published batch records linking prior bytes, input identity and derived product state.

- **Uncertain outcome:** A failure after an external effect became visible but before the caller recorded successful completion.

- **Recovery packet:** Exact data, state, attempt, version, resource and cleanup evidence supporting a narrowly stated recovery claim.

This capstone delivers a bounded data product with actual Spark file streaming, an application-managed event policy, a local idempotent sink and a real injected restart. It combines late and duplicate events without using exactly once as a shortcut for explaining the protocol. The data product has one accepted value per business ID, while every raw source occurrence receives one accounting category.

The source schema is delivery:bigint, id:string, event_second:bigint, cents:bigint, all nullable at the read boundary. A delivery number identifies a source occurrence and must be present, unique in its batch and within 1..12. The business fields can be invalid and are retained for classification. Each microbatch contains at most 8 rows and the complete product at most 12 occurrences. Only those checked tiny batches are collected to the driver for this teaching sink.

## State the policy before running the stream

Accepted IDs are single uppercase letters, event seconds are integers 0..1000 and cents are integers 0..1000. Zero cents is valid. Domain-invalid rows are counted invalid and never advance event time. For a domain-valid row, an existing ID with the same event time and amount is a duplicate;an existing ID with different payload is invalid conflict. A new ID older than the frozen cutoff is late. All remaining new IDs are accepted.

The cutoff for a batch is previous committed maximum accepted event_second minus 10. It is inclusive:an event exactly at the cutoff is accepted. The cutoff does not move after each row in the current batch. This prevents the processing order of one batch from deciding whether another row in the same batch is late. Accepted events update the maximum for the next committed batch.

This is an explicit application policy implemented in the bounded sink state. It is not Spark's native watermark or a demonstration of state-store eviction. The accepted-ID map retains all keys for the finite product. An unbounded deployment would need a different bounded state store, retention/conflict policy and transactional sink implementation. The course keeps that limitation visible instead of disguising a driver dictionary as a distributed state service.

## Work the three immutable input batches

BatchA containsA(100,10), B(105,20), an equalA duplicate and a NULL business ID. It yields accepted 2, duplicate 1, invalid 1, late 0, total 30, max 105. The next cutoff is 95. BatchB deliberately presentsE(120,40) beforeD(95,0), thenC(94,7) and an equalB duplicate. D is accepted at the frozen 95 boundary even though E raises the next maximum to 120. C is late. The cumulative product becomes accepted 4, duplicate 2, late 1, invalid 1, total 70.

BatchC uses cutoff 110. A changed B amount 999 is an invalid conflict, and F(110,5) is accepted exactly at the boundary. The final accepted IDs areA, B, D, E, F, total 75, with duplicate 2, late 1, invalid 2. The conservation equation is 5+2+1+2=10 raw occurrences. A total-only check would miss dropping the valid zero-valuedD, so the oracle includes every accepted identity and timestamp as well as counts and total.

## Publish input and state together

Each callback canonicalizes all input occurrences into deterministic JSON, including invalid business fields. The commit file stores query identity, batch ID, input JSON and SHA256, previous commit digest and canonical derived state. The predecessor chain is bounded and validated when read. State is recomputed from the committed input ledger and compared with the recorded state, so a reader does not trust an unexplained summary counter.

The file is staged beside its final batch-key path and atomically renamed under a single-writer local-filesystem assumption. Input, state and commit metadata share one visibility point. A repeated batch key must carry identical input and a valid existing chain;it returns the already committed logical state rather than applying the rows again. JSON integer fields are validated by numeric value and integral type, avoiding the JVM node-width round-trip mistake discussed in the sink lesson.

This protocol provides the tested local visibility and replay behavior. It does not fsync a power-loss-durable transaction log, coordinate multiple distributed writers or prove object-store atomicity. Hashes identify bytes but do not authenticate an attacker-controlled publisher. Every file here is created inside the owned local job root;the example does not open a database or remote service.

## Fail after the effect exists

The first actual foreachBatch callback publishesBatchA, then raises injected_after_publication before Spark records normal batch completion. The query fails, but the committed product is readable. That is an uncertain outcome from the caller's perspective:the effect happened even though the call did not return success.

Restarting the same compatible checkpoint deliversBatch 0 again. The sink validates the existing content and leaves its bytes and counters unchanged. Query identity persists while run identity changes. The attempt ledger is[0,0], but there is only one committed first-batch effect. This is replay-safe publication, not exactly-once callback computation.

After the restart, the program publishesBatchB and BatchC in turn and waits for each finite query to finish. The final attempt IDs are[0,0,1,2], and callback row counts are[4,4,4,2]. Physical callback work therefore examines 14 row occurrences while the committed source ledger accounts for 10 logical occurrences. Keeping these numbers separate prevents a retry from being mistaken for extra business events or a cost-free recovery.

## Review the handoff and cleanup

The final packet contains the literal full-state oracle, source batch definitions, query/run identities, attempt IDs, callback row work, three committed batch files and the declared bounds. A sink binding connects the application namespace to its source, checkpoint and policy version. An attempt to point that sink at another checkpoint is refused before a query starts.

Every query has a 45-second await bound and a five-second stop timeout. Only queries created by this program are stopped. The owned root is removed only after those queries are inactive, and the session is stopped in finally. No existing checkpoint or learner directory is reset. Resource counts are local work evidence, not a cloud invoice or a throughput forecast.

A reviewer should be able to explain the cutoff boundary, zero retention, conflicting-ID policy, after-publication failure and replay no-op without reading the implementation first. The two languages must independently match the literal product oracle. Their agreement alone would not rule out a shared policy error.

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
ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-042-")
val input=ownedRoot.resolve("input");val checkpoint=ownedRoot.resolve("checkpoint");val sink=Files.createDirectory(ownedRoot.resolve("sink"))
publishFile(ownedRoot,input,"batch-01.json",Seq("""{"delivery":1,"id":"A","event_second":100,"cents":10}""","""{"delivery":2,"id":"B","event_second":105,"cents":20}""","""{"delivery":3,"id":"A","event_second":100,"cents":10}""","""{"delivery":4,"id":null,"event_second":106,"cents":30}"""))
val staticA=spark.read.schema(productSchema).json(input.toString)
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
owned_root=Path(tempfile.mkdtemp(prefix="spark-042-",dir=Path.cwd()))
input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";sink=owned_root/"sink";sink.mkdir()
publish_file(owned_root,input_path,"batch-01.json",['{"delivery":1,"id":"A","event_second":100,"cents":10}', '{"delivery":2,"id":"B","event_second":105,"cents":20}', '{"delivery":3,"id":"A","event_second":100,"cents":10}', '{"delivery":4,"id":null,"event_second":106,"cents":30}'])
static_a=spark.read.schema(PRODUCT_SCHEMA).json(str(input_path))
```

## Worked example / walkthrough

### Worked example 1

```scala
val previousMax=105L;val cutoff=previousMax-10L
val orderedSeconds=Seq(120L,95L,94L)
assert(orderedSeconds.filter(_ >= cutoff)==Seq(120L,95L))
```

```python
previous_max=105;cutoff=previous_max-10
ordered_seconds=[120,95,94]
assert [second for second in ordered_seconds if second>=cutoff]==[120,95]
```

The cutoff remains 95 for the whole microbatch. Advancing it immediately after 120 would incorrectly reject 95. This independent arithmetic trace fixes the intended policy before streaming execution.

### Worked example 2

```scala
val counts=Seq(5L,2L,1L,2L)
val acceptedCents=Seq(10L,20L,0L,40L,5L)
assert(counts.sum==10L && acceptedCents.size==5 && acceptedCents.sum==75L)
```

```python
counts=[5,2,1,2];accepted_cents=[10,20,0,40,5]
assert sum(counts)==10 and len(accepted_cents)==5 and sum(accepted_cents)==75
```

The independent final oracle checks both conservation and zero retention. The total alone cannot establish that all five accepted identities survived.

## Exercises

### Exercise 1: Validate and canonicalize each raw microbatch

Require the explicit four-field schema, at most 8 rows and unique delivery IDs 1..12. Preserve NULL/business-invalid fields for classification and emit deterministic JSON.

**Expected result/shape:** BatchA has four occurrences with IDsA, B, A, NULL;NULL is preserved in canonical input. An oversized batch is rejected before collection.

**Verify:** Compare decoded delivery IDs 1..4 and the NULL marker;reject a 12-row union.

**Progressive hint:** Structural delivery identity is required even when business data is invalid.

### Exercise 2: Implement the explicit state and lateness policy

Freeze cutoff at previous committed max_event_second minus 10. Validate domain, then classify existing equal ID payload as duplicate, conflicting payload as invalid, new old event as late, and remaining event as accepted.

**Expected result/shape:** AfterA:accepted 2, duplicate 1, late 0, invalid 1, total 30, max 105. An invalid far-future row does not advance max time.

**Verify:** Assert exact state and an invalid future control;preserve the original state value.

**Progressive hint:** The cutoff is fixed for the microbatch, not recomputed after each row.

### Exercise 3: Inject failure after publication but before query completion

Run the actual foreachBatch query with one injected exception after the atomic commit file becomes visible.

**Expected result/shape:** The query fails with injected_after_publication;commit 0 is readable and contains the correct first-state ledger.

**Verify:** Inspect the expected streaming exception, attempt 0 and unchanged source/checkpoint ownership.

**Progressive hint:** This failure point deliberately creates an uncertain callback outcome for Spark.

### Exercise 4: Replay the committed batch without applying it twice

Restart the same compatible query and checkpoint. Validate the existing batch input/content/chain and reuse its state.

**Expected result/shape:** Attempts 0,0 and callback rows 4,4;commit 0 bytes and logical state remain unchanged.

**Verify:** Compare query/run identities, exact bytes and all first-state counters.

**Progressive hint:** Repeated computation is allowed;repeated logical publication is not.

### Exercise 5: Process late, boundary, duplicate and conflicting events

PublishBatchB thenBatchC as separate immutable files and run each finite invocation against the same checkpoint.

**Expected result/shape:** Final accepted IDsA, B, D, E, F, total 75;duplicate 2, late 1, invalid 2;10 logical occurrences. Zero-valuedD and cutoff-boundaryF remain accepted.

**Verify:** Compare intermediateB counts and the final literal state;the high-timeE must not make same-batchD late.

**Progressive hint:** Freeze each cutoff from the previously committed state:95 for B and 110 for C.

### Exercise 6: Hand off correctness, recovery and resource evidence

Return the exact final canonical state, record callback work 14 versus logical occurrences 10, and reject binding the existing sink to a different checkpoint.

**Expected result/shape:** Literal golden state matches;attempt IDs 0,0,1,2;callback rows 4,4,4,2;only owned inactive queries are eligible for cleanup.

**Verify:** Compare the complete state JSON and namespace-refusal negative;state the single-writer/local-filesystem limitations.

**Progressive hint:** An evidence packet separates data effects, physical work, source identity and cleanup.

## Common pitfalls

Do not call a repeated callback exactly-once computation, advance the cutoff within one batch, drop valid zero values, or silently choose a winner for conflicting IDs. Do not publish counters separately from their supporting batch state. Do not trust only a digest without the business oracle. The bounded local driver ledger is explicitly not a production distributed state store, power-loss proof or object-store transaction. Preserve the source/checkpoint/sink binding and stop owned queries before cleanup.

## Self-check

Explain the contract of `canonicalProductInput` / `canonical_product_input` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 foreachBatch and recovery](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#using-foreach-and-foreachbatch)

- [Spark4.0.1 event-time concepts](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#handling-late-data-and-watermarking)

- [Java17 atomic file publication](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html#move(java.nio.file.Path,java.nio.file.Path,java.nio.file.CopyOption...))

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-042: Capstone: a recoverable late-event data product.
Read courses/scala-spark/guides/spark-042.md and courses/scala-spark/lessons/spark-042.scala;the paired sources are courses/scala-spark/lessons/spark-042.scala and courses/scala-spark/lessons/spark-042.py.
Direct prerequisites: spark-041. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
