# spark-036: foreachBatch, idempotent sinks and failure injection

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 135 minutes. Direct design prerequisites: `spark-035`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-036` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-036.scala) and [PySpark learner](../lessons/spark-036.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-036_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-036_solution.scala) and [PySpark reference](../solutions/spark-036_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Design an idempotent microbatch sink instead of assuming foreachBatch is exactly once.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **foreachBatch:** A callback receiving a static microbatch DataFrame and its batch ID, with at-least-once execution by default.

- **Idempotency key:** A stable identity used to recognize repeated logical work;here query namespace plus batch ID.

- **Staging:** Writing a candidate result that readers do not yet consider committed.

- **Publication:** The explicit visibility point after which readers include a result.

- **Content collision:** The same logical key paired with different canonical data, a condition to reject rather than overwrite.

- **Single writer:** The local protocol assumption that one query owns its sink namespace at a time.

foreachBatch connects streaming execution to a user-defined sink, but it does not make that sink transactional automatically. Spark can invoke a batch again after a failure. A callback that inserts rows or sends messages without an idempotency rule can repeat its side effects even if the source and checkpoint work correctly. This lesson deliberately observes that replay through a real failed streaming query.

The tiny sink stores each microbatch's canonical data and receipt together in one JSON file. Its key is an application-defined query identity such as stream-v1 plus batchId. This identity is bound to one explicit source path, checkpoint path and schema contract in a sibling binding record. It is not the ephemeral Spark runId. Creating a new checkpoint under the same sink namespace is rejected by that binding rather than silently restarting batch numbers against old output.

## Choose one visible commit boundary

The callback validates the static DataFrame, schema, NULL policy and eight-row bound. It orders the two bigint fields and collects only that tiny checked result into exact newline-delimited text. It computes a SHA256 over those bytes. This is intentionally a small teaching sink, not a scalable recommendation to collect arbitrary streaming batches on the driver.

For a new key, the sink writes a uniquely named staged file in the same owned directory. Readers ignore pending files. Publication atomically renames the complete file to its batch-key name. The file contains both payload and identity/digest metadata, so there is no separate data-file/commit-marker gap in this small protocol. An existing key is accepted only when every recorded value agrees with the candidate. Different content under the same key is a failure.

JSON stores a number without preserving the original JVM integer-node width. The Scala reader therefore validates an integral batch_id and compares its Long value, while comparing identity, digest and payload exactly and rejecting unexpected fields. Comparing Jackson tree objects directly can falsely reject batch 7 after a round trip because an in-memory LongNode can decode as an IntNode. Normalizing that representation does not permit different batch content or a nonintegral ID.

The filesystem assumptions are explicit:one writer, prepared local storage and same-directory atomic rename. The program does not fsync a durable transaction log or coordinate distributed writers. A rename that is atomic for local visibility is not automatically an object-store transaction or a power-loss guarantee. A production database sink would need its own transaction and uniqueness constraints, with data and deduplication record committed together.

## Inject failure at a precise point

The first actual streaming callback writes staging bytes, then raises injected_before_publication before rename. The exception escapes the callback and reaches awaitTermination as a streaming query failure. The temporary file is removed in finally, while no committed stream-v1 batch exists. The attempted batch ID is recorded as 0. This is a failed query with an expected diagnostic, not a swallowed error reported as success.

Restarting the compatible source/checkpoint repeats batch 0. The query ID persists and run ID changes. This time publication completes and the sink exposes exactly two rows. The attempt ledger is[0,0], while the committed logical batch count is one. Delivery count and committed effect count are different measurements. A direct replay of an already committed manual batch separately tests the no-op branch that would be needed after an uncertain post-publication response.

The callback persists the batch while performing multiple validation and collection actions, then unpersists in finally. Without this choice, multiple actions can recompute input and distort work metrics. Persistence is not the idempotency mechanism;it only controls repeated execution within the callback. The durable key/content comparison controls repeated callback deliveries.

## Use a deliberately unsafe control

A separate unsafe-demo file appends the same canonical text twice and therefore contains four occurrences. It never shares a path with the real sink. This deterministic counterexample shows exactly what a naive external append can do under repeated delivery. The repaired sink retains two rows for that logical batch and then accepts a genuinely new batch containing 3:300.

Every path is inside a fresh current-job scratch root. The reference waits with a deadline, stops only queries it created, then removes only that root before stopping its session. The checkpoint remains intact during the failure/restart experiment. No existing learner checkpoint or external database is touched. The final evidence states the precise local protocol, observed failure point, attempt IDs, committed rows and limitations rather than claiming universal end-to-end exactly-once execution.

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
ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-036-")
val input=ownedRoot.resolve("input");val checkpoint=ownedRoot.resolve("checkpoint");val sink=Files.createDirectory(ownedRoot.resolve("sink"))
publishFile(ownedRoot,input,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
val staticFrame=spark.read.schema(eventSchema).json(input.toString)
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
owned_root=Path(tempfile.mkdtemp(prefix="spark-036-",dir=Path.cwd()))
input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";sink=owned_root/"sink";sink.mkdir()
publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
static_frame=spark.read.schema(EVENT_SCHEMA).json(str(input_path))
```

## Worked example / walkthrough

### Worked example 1

```scala
val demo=spark.read.schema(eventSchema).json(input.toString)
val text=canonicalBatch(demo)
assert(text=="1,100\n2,200\n")
assert(publishBatch(sink,"demo-v1",0L,text,false))
assert(!publishBatch(sink,"demo-v1",0L,text,false))
```

```python
demo=spark.read.schema(EVENT_SCHEMA).json(str(input_path))
text=canonical_batch(demo)
assert text=="1,100\n2,200\n"
assert publish_batch(sink,"demo-v1",0,text)
assert not publish_batch(sink,"demo-v1",0,text)
```

The same key and canonical content publishes once. This direct helper demonstration isolates the sink rule;the reference exercises the real foreachBatch failure and replay separately.

### Worked example 2

```scala
var failed=false
try publishBatch(sink,"demo-failure",0L,"1,100\n",true) catch { case e: IllegalStateException if e.getMessage=="injected_before_publication" => failed=true }
assert(failed && publishedRows(sink,"demo-failure").isEmpty)
```

```python
try:
    publish_batch(sink,"demo-failure",0,"1,100\n",True)
except RuntimeError as error:
    assert str(error)=="injected_before_publication"
else:
    raise AssertionError("Failure injection disappeared")
assert published_rows(sink,"demo-failure")==[]
```

Failure after staging leaves no published row. The expected exception is inspected explicitly;temporary-file cleanup is not mistaken for a successful commit.

## Exercises

### Exercise 1: Define canonical bounded microbatch content

Validate the explicit bigint schema, nonnegative cents, positive IDs and at most 8 rows;return sorted id, cents newline records preserving multiplicity.

**Expected result/shape:** Exact text 1,100 newline 2,200 newline, with a stable SHA256 after repartitioning.

**Verify:** Compare exact bytes and reject NULL cents before publication.

**Progressive hint:** Content validation precedes the digest;the digest is not itself a business oracle.

### Exercise 2: Publish one logical batch idempotently

Publish the same canonical content twice under identity manual-v1 and batch 7. Compare the existing receipt instead of appending.

**Expected result/shape:** First call publishes true;second returns false;exactly 2 logical rows remain.

**Verify:** Assert return values, unchanged receipt bytes and one batch file.

**Progressive hint:** The identity includes a stable query namespace and batch ID;run ID must not reset it.

### Exercise 3: Inject a real callback failure before publication

Run the actual foreachBatch query with failure after staging and before rename. Retain the wrapped streaming exception and attempted batch ID.

**Expected result/shape:** The query fails with injected_before_publication;no stream-v1 batch is visible and the attempted batch ID is 0.

**Verify:** Check the exception marker, empty published rows and inactive query.

**Progressive hint:** The exception must escape the callback so Spark cannot mark the batch successful.

### Exercise 4: Recover the same checkpoint and observe replay

Restart the same source/checkpoint/query namespace without failure. Compare attempts and logical query/run IDs.

**Expected result/shape:** Batch 0 is attempted again and publishes 2 rows once. Query ID persists;run ID changes.

**Verify:** Assert attempt sequence 0,0, exact rows and corresponding identities.

**Progressive hint:** foreachBatch provides at-least-once callback execution;the sink supplies replay safety.

### Exercise 5: Expose a non-idempotent append counterexample

Append the same canonical batch text twice to a separate unsafe-demo file, then compare it with the idempotent published batch.

**Expected result/shape:** Unsafe append has 4 row occurrences;the committed batch remains 2.

**Verify:** Compare exact repeated lines and preserve the unsafe file as a separate diagnostic until owned cleanup.

**Progressive hint:** A retry after an uncertain response is enough to duplicate append side effects.

### Exercise 6: Reject identity collisions and admit the next batch

Reject different content under an existing batch key, then publish a new source file 3:300 and resume the real query.

**Expected result/shape:** The conflicting key fails without replacing its receipt. Stream batch 1 adds one row, leaving IDs 1,2,3 and total 600 across two batch files.

**Verify:** Assert collision rejection, old receipt equality, attempt sequence 0,0,1 and exact 3-row sink.

**Progressive hint:** A duplicate key is safe only if its content agrees;new work receives a new batch ID.

## Common pitfalls

Do not use runId as the replay key. Do not suppress a repeated batch ID without checking content and query namespace. Do not catch a callback failure and return success to Spark. A local rename protocol is not a distributed transaction or an fsync durability claim. A declared tiny collection bound must be checked before collection, and a missing capability is not permission to download a connector or open a database.

## Self-check

Explain the contract of `encodeBatch` / `encode_batch` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 foreachBatch semantics](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#using-foreach-and-foreachbatch)

- [Java17 atomic file move](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html#move(java.nio.file.Path,java.nio.file.Path,java.nio.file.CopyOption...))

- [Python rename semantics](https://docs.python.org/3/library/os.html#os.rename)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-036: foreachBatch, idempotent sinks and failure injection.
Read courses/scala-spark/guides/spark-036.md and courses/scala-spark/lessons/spark-036.py;the paired sources are courses/scala-spark/lessons/spark-036.scala and courses/scala-spark/lessons/spark-036.py.
Direct prerequisites: spark-035. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
