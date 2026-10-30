# spark-031: Structured Streaming with finite microbatches

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-030`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-031` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-031.scala) and [PySpark learner](../lessons/spark-031.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-031_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-031_solution.scala) and [PySpark reference](../solutions/spark-031_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Model an unbounded relation while running a finite, reproducible local streaming exercise.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Streaming DataFrame:** A logical relation representing data that can continue arriving; ordinary construction does not itself start a running query.

- **Microbatch:** A finite unit of source offsets processed by a streaming query; its input count differs from the size of a cumulative result table.

- **AvailableNow trigger:** A trigger that processes the data available to its supported source at the start, possibly over several microbatches, then terminates.

- **Complete output mode:** An output mode that writes the full current aggregate result after each update; successive snapshots are not independent appended facts.

- **Checkpoint:** Owned recovery metadata recording source progress and relevant query state, whose compatibility belongs to a specific query contract.

- **Atomic file arrival:** Making a complete new file visible to a file source in one publication step instead of exposing a file while it is still being written.

A streaming relation models arrivals that could continue indefinitely, but a learning run can still be finite and reproducible. This lesson provides exactly three files with three records each and usesAvailableNow. The source can divide that available data into microbatches because maxFilesPerTrigger is one. After processing the finite available files, the query terminates. It does not keep a socket open or depend on a wall-clock producer.

The files are written completely in a sibling staging directory under a fresh owned root, then moved atomically into input. Every destination filename is new. The file source expects arrivals to be complete and does not treat editing an already processed file as a safe update protocol. This local same-filesystem move is a controlled fixture mechanism; remote storage systems require their own supported publication semantics.

The input schema is declared before readStream.json. IDs and amounts are longs, team is a string, and the schema permits unknown amounts. File parsing does not establish identity or domain correctness by itself; the exact fixture is reviewed separately. There are nine records, seven known amounts and a known-amount total of 80. An ordinary batch read of the same input directory provides a comparison path, while the final three-group literal oracle is independent of both implementations.

The aggregate keeps one state row per team with record count, known-amount count and sum. Team A has four records, three known amounts and total 15. Team B has three records, two known amounts and total 35. Team C has two records, two known amounts and total 30. Unknown amounts remain unknown inputs; COUNT(amount) reports completeness separately from COUNT(*). Zero amounts are observed values and remain part of the known count.

Complete mode writes the current full aggregate table after each microbatch. The in-memory sink is a temporary inspection tool in this owned session, not a durable production sink. Summing every complete snapshot would count prior records repeatedly. The correct final product is the final table, while query progress reports how many new input rows each microbatch processed. These are two different count ledgers.

The source limit produces three positive-input batches of three rows for the declared files. Progress can also contain zero-input entries depending on the query and trigger behavior, so the reference sums input counts and inspects positive-input batches rather than pretending every progress entry is a new file. The total observed input must be nine. Batch IDs identify this query execution progress entries and are not global business event identities.

The query has a unique name and a fresh checkpoint path. Construction of readStream and groupBy creates plans; writeStream.start starts the query. The helper awaits termination with a 30-second deadline and always calls stop in finally. The session has a bounded stop timeout. If a query somehow remains active after cleanup, the outer cleanup preserves its scratch root rather than deleting files underneath active work, and session shutdown still runs.

The final batch comparison checks exactly the same three summary tuples and then checks the independent literal values. Matching streaming and batch code alone would be weaker because both might share a wrong aggregation rule. No arbitrary sleep is used to guess when records arrived or when a result became ready. File publication and the query termination condition provide the sequencing.

This finite example does not establish an indefinitely bounded aggregate state. Without a watermark or another retention rule, an unbounded stream with ever-new team keys can grow state. It also does not establish end-to-end exactly-once behavior for arbitrary external sinks. Later lessons introduce event-time policies, deduplication, checkpoint restart and idempotent side effects with their own explicit limits.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery, Trigger}
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import com.fasterxml.jackson.databind.ObjectMapper

spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-031-")
Files.createDirectory(ownedRoot.resolve("input"));
Files.createDirectory(ownedRoot.resolve("staging"))
ownedTable = "ds60_s031_" + UUID.randomUUID().toString.replace("-", "")
val batches = Seq(
  Seq(
    """{"id":1,"team":"A","amount":10}""",
    """{"id":2,"team":"B","amount":20}""",
    """{"id":3,"team":"A","amount":0}"""
  ),
  Seq(
    """{"id":4,"team":"B","amount":null}""",
    """{"id":5,"team":"C","amount":30}""",
    """{"id":6,"team":"A","amount":5}"""
  ),
  Seq(
    """{"id":7,"team":"C","amount":0}""",
    """{"id":8,"team":"B","amount":15}""",
    """{"id":9,"team":"A","amount":null}"""
  )
)
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
import re
import os
import uuid

spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-031-", dir=".")).resolve()
(owned_root / "input").mkdir()
(owned_root / "staging").mkdir()
owned_table = "ds60_s031_" + uuid.uuid4().hex
batches = [
    [
        '{"id":1,"team":"A","amount":10}',
        '{"id":2,"team":"B","amount":20}',
        '{"id":3,"team":"A","amount":0}',
    ],
    [
        '{"id":4,"team":"B","amount":null}',
        '{"id":5,"team":"C","amount":30}',
        '{"id":6,"team":"A","amount":5}',
    ],
    [
        '{"id":7,"team":"C","amount":0}',
        '{"id":8,"team":"B","amount":15}',
        '{"id":9,"team":"A","amount":null}',
    ],
]
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(batches.map(_.size) == Seq(3, 3, 3) && batches.flatten.size == 9)
println("Three complete fixture files will contain exactly nine records")
```

```python
assert [len(batch) for batch in batches] == [3, 3, 3] and sum(map(len, batches)) == 9
print("Three complete fixture files will contain exactly nine records")
```

The fixture population is known before the query starts. This is an input declaration, not a processed-row receipt. The streaming progress test later verifies that the running query actually consumed the declared population.

### Worked example 2

```scala
val mapper = new ObjectMapper()
val amounts = batches.flatten
  .map(line => mapper.readTree(line).get("amount"))
  .filterNot(_.isNull)
  .map(_.asLong())
assert(amounts.size == 7 && amounts.sum == 80L)
println("Independent known-count/amount oracle=7/80")
```

```python
amounts = [json.loads(line)["amount"] for batch in batches for line in batch]
known = [amount for amount in amounts if amount is not None]
assert len(known) == 7 and sum(known) == 80
print("Independent known-count/amount oracle=7/80")
```

The driver-only parse of nine fixed strings supplies an independent completeness and sum oracle. It preserves unknown values instead of replacing them with zero, and is small enough that its bounded nature is explicit.

## Exercises

### Exercise 1: Publish complete input files atomically

Write each declared file in the owned staging directory, then atomically move it into input under a new batch-N.json name. Reject invalid names or an existing destination.

**Expected result/shape:** Three input files, each with 3 completeJSON records; no staging temporary file remains. Reusing batch-0.json is rejected.

**Verify:** Assert the file count and explicit existing-name rejection before starting any query.

**Progressive hint:** The watched input directory must not expose partially written files.

### Exercise 2: Construct an explicit streaming relation without starting it

Read the owned JSON input through readStream with the declared schema and maxFilesPerTrigger 1. Return the streamingDataFrame; do not call an ordinary batch collect on it.

**Expected result/shape:** isStreaming is true, columns are id, team, amount and their types are bigint, string, bigint. No query is started by construction alone.

**Verify:** Assert streaming status and exact type mapping while the active query list remains empty.

**Progressive hint:** A streaming plan needs a sink and trigger before it becomes a running query.

### Exercise 3: Define a cumulative aggregate with separate completeness counts

Group by team and compute row_count, known_amounts and total_amount. Use the same expression for streaming and batch relations without filling unknown amounts.

**Expected result/shape:** The streaming result remains streaming and has one state/result row per team. Its eventual literal result isA(4,3,15), B(3,2,35), C(2,2,30).

**Verify:** Assert output columns and streaming status now; verify the exact final tuples after bounded execution.

**Progressive hint:** COUNT(*) and COUNT(amount) differ because two amounts are unknown.

### Exercise 4: Run AvailableNow with a deadline and owned cleanup

Start the aggregate in a uniquely named memory sink with complete mode, a fresh checkpoint and AvailableNow. Await at most 30 seconds, require termination and always stop the query in finally.

**Expected result/shape:** The query terminates and isActive is false. The memory table holds the final finite aggregate; the checkpoint belongs only to this run.

**Verify:** Assert bounded await success, no query exception and inactive state. No sleep or external producer is used.

**Progressive hint:** Keep the query handle inside a try/finally scope even when awaitTermination raises.

### Exercise 5: Reconcile processed input through progress evidence

Return(batch_id, num_input_rows) from retained query progress. Sum input rows and inspect positive-input batches without confusing cumulative sink snapshots with new input.

**Expected result/shape:** Three positive-input batches of 3 records and total input 9. Any zero-input progress entry contributes zero to that total.

**Verify:** Assert total 9, three positive batches of 3 and unique recorded batch IDs; print the actual ledger.

**Progressive hint:** Complete-mode output rows are snapshots, so summing their sizes does not count source records.

### Exercise 6: Compare final streaming output with batch and literal oracles

Read the final memory table, compare its ordered summary tuples with a batch read of the same nine source records, and compare both with the literalA/B/C oracle.

**Expected result/shape:** ExactlyA(4,3,15), B(3,2,35), C(2,2,30), whose record counts sum 9, known counts 7 and amounts 80.

**Verify:** Assert both path comparisons and the independent literal tuple list; confirm no active query remains before cleanup.

**Progressive hint:** Agreement between two paths is insufficient if both share the same incorrect expression.

## Common pitfalls

Do not write partially completed files into the watched input directory or reuse processed filenames. Do not call readStream construction a running query. Do not sum complete-mode snapshots as if each were new input. A memory sink is not a durable production sink, and AvailableNow termination does not prove indefinite state is bounded. Always await and stop owned queries before session cleanup, and preserve scratch if a query is still active rather than deleting its checkpoint underneath it.

## Self-check

Explain the contract of `publishFile` / `publish_file` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 file sources,triggers,output modes and query lifecycle](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html)

- [Spark 4.0.1 checkpoint configuration limits](https://spark.apache.org/docs/4.0.1/streaming/additional-information.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-031: Structured Streaming with finite microbatches.
Read courses/scala-spark/guides/spark-031.md and courses/scala-spark/lessons/spark-031.scala;the paired sources are courses/scala-spark/lessons/spark-031.scala and courses/scala-spark/lessons/spark-031.py.
Direct prerequisites: spark-030. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
