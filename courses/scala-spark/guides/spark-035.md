# spark-035: Checkpoints, restart and delivery guarantees

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-034`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-035` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-035.scala) and [PySpark learner](../lessons/spark-035.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-035_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-035_solution.scala) and [PySpark reference](../solutions/spark-035_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Explain how source offsets, state, checkpoints and sink behavior jointly determine recovery semantics.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Checkpoint:** Persistent query metadata including progress and, for stateful operators, state needed for compatible recovery.

- **Source offset:** A source-specific position or processed-input identity;it is not a business event key.

- **Query ID:** The logical streaming query identity preserved when restarting from its checkpoint.

- **Run ID:** A new identity for one start of that logical query.

- **Sink commit:** The output-side decision that makes a batch visible under that sink protocol.

- **Replay:** Reading source occurrences again under a new or recovered processing context.

A streaming query is a long-lived logical computation, even when this lesson uses a finite invocation. Its recovery story spans input identity, query state and output publication. A checkpoint records progress so a compatible restart can continue rather than treating every available input as new. The output sink must also implement a suitable commit protocol. A checkpoint file alone does not make arbitrary HTTP calls, emails or database inserts exactly once.

The fixture has two immutable JSON files with an explicit id:bigint, cents:bigint schema. FileA contains 1:100 and 2:200. FileB contains 2:200 and 3:300. Each row is an input occurrence;ID 2 appears in two occurrences. This deliberately separates replay of an already processed file from repetition of a business identity in a new file. Correct source recovery retains four occurrences and total 800, not three rows and 600.

## Follow the three histories

The source history identifies immutable files admitted to each batch. A producer should publish a complete file atomically into the watched directory, not append to an already consumed file and expect the source to treat it as a new event. The helper writes a bounded staged file outside the input directory and moves it into place under a fresh name. The inputs are written only inside this operation's new scratch root.

The checkpoint history includes the logical query identity, offset/commit information and any stateful-operator data. This example has no stateful aggregation, so it isolates source and sink recovery. State schemas, watermarks and operator topology add compatibility obligations in later lessons. Never edit checkpoint internals or delete a checkpoint to make a test pass. They are implementation-managed state, not a learner-authored JSON configuration.

The sink history records committed Parquet output. Reading through Spark's file sink metadata is different from broadly concatenating every file that happens to be visible on disk. A filesystem listing is useful diagnostic evidence, but the logical product is the committed dataset. The readback uses the schema and exact ordered row bag after the finite query terminates.

## Bound the experiment without guessing arrival time

AvailableNow processes the data available for that invocation and stops. maxFilesPerTrigger 1 bounds source admission per microbatch;it does not mean there will always be exactly one batch, or that a batch takes a fixed number of seconds. The reference awaits completion with 45 seconds per query and a five-second stop timeout. No sleep is used to infer that a file has been processed. Query progress is read only after completion and is joined with actual sink values.

The first run seesFileA. After it finishes, the producer publishesFileB and starts the same query against the same checkpoint and sink. The logical query ID stays the same, the run ID changes, and only the new file contributes to that run's input count. A third run adds no file and must leave the sink unchanged. An empty finite run may have no progress entries, so a sum over available input counts is more appropriate than demanding one progress record.

## New checkpoint means a new processing history

A fourth run uses a new checkpoint and a different output directory. It replays both source files, which is expected because its source history is empty. It must never reuse the original append output casually:that would combine a new history with old side effects and could duplicate data. The separate output lets the learner compare the same four-row product without altering the prior checkpoint.

The complete guarantee ledger names source immutability, checkpoint compatibility, sink protocol, business key policy and the tested failure boundary. This lesson demonstrates compatible restarts within one bounded local program and prepared filesystem. It does not simulate process death, power loss, object-store consistency or arbitrary external transactions. Those claims need their own environment and fault receipts. The important habit is to describe the exact guarantee you observed instead of applying exactly once as an undifferentiated label.

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
ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-035-")
val input=ownedRoot.resolve("input");val checkpoint=ownedRoot.resolve("checkpoint");val output=ownedRoot.resolve("output")
publishFile(ownedRoot,input,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
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
owned_root=Path(tempfile.mkdtemp(prefix="spark-035-",dir=Path.cwd()))
input_path=owned_root/"input";checkpoint=owned_root/"checkpoint";output=owned_root/"output"
publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
```

## Worked example / walkthrough

### Worked example 1

```scala
val demoInput=ownedRoot.resolve("demo-input")
publishFile(ownedRoot,demoInput,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
val demoFirst=runParquet(spark,demoInput,ownedRoot.resolve("demo-checkpoint"),ownedRoot.resolve("demo-output"))
assert(demoFirst.inputRows==2L && bag(spark,ownedRoot.resolve("demo-output"))==Seq("1:100","2:200"))
```

```python
demo_input=owned_root/"demo-input"
publish_file(owned_root,demo_input,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
demo_first=run_parquet(spark,demo_input,owned_root/"demo-checkpoint",owned_root/"demo-output")
assert demo_first["input_rows"]==2 and bag(spark,owned_root/"demo-output")==["1:100","2:200"]
```

The first finite query processes exactly the two supplied occurrences. The expected bag is independent of partition/file order, and completion is established through awaitTermination rather than a delay.

### Worked example 2

```scala
val demoInput=ownedRoot.resolve("demo-input")
publishFile(ownedRoot,demoInput,"batch-02.json",Seq("""{"id":2,"cents":200}""","""{"id":3,"cents":300}"""))
val demoSecond=runParquet(spark,demoInput,ownedRoot.resolve("demo-checkpoint"),ownedRoot.resolve("demo-output"))
assert(demoSecond.inputRows==2L && bag(spark,ownedRoot.resolve("demo-output"))==Seq("1:100","2:200","2:200","3:300"))
```

```python
publish_file(owned_root,demo_input,"batch-02.json",['{"id":2,"cents":200}','{"id":3,"cents":300}'])
demo_second=run_parquet(spark,demo_input,owned_root/"demo-checkpoint",owned_root/"demo-output")
assert demo_second["input_rows"]==2 and bag(spark,owned_root/"demo-output")==["1:100","2:200","2:200","3:300"]
```

The repeated business ID is retained because it arrived in a new source file. Offset recovery prevents rereadingFileA as fresh input;it is not an event-ID deduplication rule.

## Exercises

### Exercise 1: Validate the finite input and output grain

Read a static copy of the two-row schema fixture and require bigint id/cents, known nonnull values and at most 8 rows. Return its canonical ordered bag without removing duplicates.

**Expected result/shape:** The first bag is 1:100,2:200. A NULL identity or cents value is rejected.

**Verify:** Compare the exact two-row bag and reject an explicit null-id DataFrame.

**Progressive hint:** A bag preserves repeated rows;schema and NULL validation occur before bounded collection.

### Exercise 2: Run the first finite file stream

Execute the AvailableNow Parquet query with its owned checkpoint/output and retain query ID, run ID, input count and batch IDs.

**Expected result/shape:** Two input rows and exactly 1:100,2:200 in the committed sink.

**Verify:** Assert the progress input count is 2, query is terminated, and readback bag is exact.

**Progressive hint:** Await the finite query instead of sleeping;the sink read happens after termination.

### Exercise 3: Resume the same checkpoint after a new file

Publish a second file with 2:200 and 3:300, then restart the compatible query with the same checkpoint and sink.

**Expected result/shape:** Only 2 new input rows are processed. The sink bag is 1:100,2:200,2:200,3:300. Query ID persists and run ID changes.

**Verify:** Compare both identities, progress count and all 4 output occurrences.

**Progressive hint:** The duplicate business ID is in a new file;checkpoint offsets do not deduplicate event IDs.

### Exercise 4: Resume with no new source files

Run the same compatible query again without adding input and compare output before/after.

**Expected result/shape:** Zero new input rows and an unchanged 4-row output bag.

**Verify:** Assert zero progress input sum and exact unchanged sink rows.

**Progressive hint:** An empty AvailableNow run may have no progress entries;sum the available entries rather than require one batch.

### Exercise 5: Replay with a separate checkpoint and output

Start from a new checkpoint only when the output namespace is also new. Replay the same source and preserve the old checkpoint/sink.

**Expected result/shape:** The separate output has 4 rows, with a new logical query ID. The old output remains 4 rows.

**Verify:** Assert checkpoint/output paths differ and both independent bags equal the literal 4-row oracle.

**Progressive hint:** A new checkpoint forgets old offsets;do not point it at the old append sink.

### Exercise 6: Write a guarantee ledger from exact counts

Return output row count, distinct business IDs and total cents, then explain why source recovery is not business-ID deduplication or a universal exactly-once guarantee.

**Expected result/shape:** 4 occurrences,3 distinct IDs, total 800.

**Verify:** Compare all three independent values and preserve the duplicate occurrence.

**Progressive hint:** The source/sink protocol and the business key policy answer different questions.

## Common pitfalls

Do not reuse an old output with a new checkpoint without an idempotency plan. Do not infer readiness from a sleep or expect one progress record for an empty run. Do not mutate consumed input files. A correct total can hide a missing duplicate or zero, so compare row bags, identities and sums. The owned root is removed only after every query created by this program is inactive;no existing checkpoint or unrelated session is reset.

## Self-check

Explain the contract of `validatedBag` / `validated_bag` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 checkpoint and recovery semantics](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#recovering-from-failures-with-checkpointing)

- [Spark4.0.1 query identity and lifecycle](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#managing-streaming-queries)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-035: Checkpoints, restart and delivery guarantees.
Read courses/scala-spark/guides/spark-035.md and courses/scala-spark/lessons/spark-035.scala;the paired sources are courses/scala-spark/lessons/spark-035.scala and courses/scala-spark/lessons/spark-035.py.
Direct prerequisites: spark-034. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
