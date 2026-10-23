# spark-037: Deterministic streaming tests without sleep-based guesses

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-036`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-037` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-037.scala) and [PySpark learner](../lessons/spark-037.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-037_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-037_solution.scala) and [PySpark reference](../solutions/spark-037_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Test finite streaming scenarios with explicit batch progression and bounded cleanup.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Scenario:** A finite input, explicit processing policy and independent expected output designed to exercise one mechanism.

- **Synchronization point:** An API-observed event such as finite query termination, rather than an elapsed sleep.

- **Canonical bag:** An ordered comparison representation that preserves row multiplicity.

- **Negative control:** A deliberately wrong result or implementation that the test must reject.

- **Owned scratch:** A fresh directory created by this invocation and removed only after its queries stop.

- **Admission cutoff:** An explicit business policy for event time, distinct from Spark internal watermark progress.

Streaming tests are hard when they confuse wall-clock waiting with logical progress. A sleep of two seconds may be longer than one machine needs and shorter than another needs. It does not establish that a particular source file was admitted, a batch committed or a stateful operator advanced. This lesson replaces those guesses with finite files, AvailableNow, deadline-based await and exact readback.

The case matrix has four independent scenarios:compatible checkpoint restart, duplicate delivery, late-by-policy input and invalid records. Each has its own input/checkpoint/output paths inside one fresh owned root. Separating cases prevents one scenario's committed offsets, state or output from silently influencing another. The root is created under the current job directory and is never selected by a learner-supplied external path.

## Design the input and oracle together

Every source row has nullable bigint fields id, event_second, cents. Nullable schema is not permission to accept NULL in the business product:the invalid case explicitly checks the boundary. Event seconds are small integers on a declared synthetic timeline. The fixed cutoff 90 is a business admission rule, not a claim that an engine watermark has reached 90. Naming that distinction keeps the test deterministic and avoids pretending an ordinary filter verified state-store eviction.

The restart case has two valid rows. The first finite query writes them;the second uses the same checkpoint and no new files. Its new input sum must be zero, and the old sink bag must remain unchanged. The persistent query ID and changed run ID distinguish logical recovery from a new query history. An empty progress array is a valid no-work shape and should not cause a test to invent a batch.

The duplicate case uses two exactly equal occurrences of one ID. It invokes native streaming dropDuplicates, so the output contains one row. There is no watermark eviction in this isolated case. The fixture has at most two input rows, so the demonstration is bounded, but an unbounded production stream would need a state-retention policy. Different payloads under the same ID would also require an explicit conflict rule rather than accepting an arbitrary retained row.

The late case has event seconds 80,90,110 and uses>=90. It must retain the boundary 90. A total-only check could hide a mistaken row policy if zero-valued data were used, so this case compares identities and amounts as a bag. The invalid case has one NULL identity, one negative amount and one valid row. Input 3=invalid 2+accepted 1 is recorded explicitly. A malformed JSON document would be a source decoding failure under FAILFAST, which is a different test from rejecting a schema-valid row.

## Observe completion and failures precisely

The query object is the lifecycle handle. Each run awaits at most 45 seconds, and active queries are stopped in finally with a bounded stop timeout. The complete program also records every query it created and requires them all inactive before deleting its owned root. A process-level supervisor still supplies an outer budget for a wedged JVM or unexpected failure outside normal query control. The lesson never uses a broad stop-all operation on unrelated sessions.

JSON predicate pushdown can apply the admission filter inside the scan before the numInputRows metric is reported. Therefore the late/invalid cases record a separate unfiltered static count of the immutable source and print the actual query progress count, which can be smaller. They preserve the exact output oracle and check that the reported scan count lies between emitted rows and raw rows. The reference does not overwrite the metric with a desired value or equate it automatically with raw file-line count. The actual configured JSON pushdown flag is recorded beside the observed late-case values.

Progress describes input and execution behavior. Readback describes the committed product. Both are needed:two processed rows do not prove two correct output rows, and one correct output row does not prove which source data was consumed. The expected bags are literal fixtures rather than outputs generated by the same transformation under test. Scala/PySpark agreement is useful only after each matches those independent expectations.

The final negative control submits the unsafe two-copy bag to the one-row duplicate oracle. The mismatch must be rejected with a meaningful diagnostic. This shows that the test can distinguish the intended behavior from dropping the deduplication step or repeating an append. It is stronger than a test that merely asserts the program did not throw.

## Keep recovery evidence portable and bounded

Retain input fixture identity, query/run IDs, batch/input observations, canonical rows and the named failure reason. Avoid copying whole event logs or arbitrary user records when a small field extract explains the case. A test-owned checkpoint exists only during the scenario;cleanup happens after all evidence assertions and query termination. Existing checkpoints are neither reset nor migrated.

These are local classic Spark 4.0.1 tests. They qualify the finite semantics and lifecycle observed in that prepared profile. They do not simulate executor loss, remote storage races or every distributed scheduling interleaving. The next observability chapter uses the same discipline to distinguish actual progress from a diagnosis hypothesis.

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
ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-037-")
val restartPaths=prepareCase(ownedRoot,"restart",Seq("""{"id":1,"event_second":100,"cents":100}""","""{"id":2,"event_second":110,"cents":200}"""))
val duplicatePaths=prepareCase(ownedRoot,"duplicates",Seq("""{"id":1,"event_second":100,"cents":100}""","""{"id":1,"event_second":100,"cents":100}"""))
val latePaths=prepareCase(ownedRoot,"late",Seq("""{"id":1,"event_second":80,"cents":100}""","""{"id":2,"event_second":90,"cents":200}""","""{"id":3,"event_second":110,"cents":300}"""))
val invalidPaths=prepareCase(ownedRoot,"invalid",Seq("""{"id":null,"event_second":100,"cents":100}""","""{"id":2,"event_second":100,"cents":-1}""","""{"id":3,"event_second":100,"cents":300}"""))
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
owned_root=Path(tempfile.mkdtemp(prefix="spark-037-",dir=Path.cwd()))
restart_paths=prepare_case(owned_root,'restart',['{"id":1,"event_second":100,"cents":100}', '{"id":2,"event_second":110,"cents":200}'])
duplicate_paths=prepare_case(owned_root,'duplicates',['{"id":1,"event_second":100,"cents":100}', '{"id":1,"event_second":100,"cents":100}'])
late_paths=prepare_case(owned_root,'late',['{"id":1,"event_second":80,"cents":100}', '{"id":2,"event_second":90,"cents":200}', '{"id":3,"event_second":110,"cents":300}'])
invalid_paths=prepare_case(owned_root,'invalid',['{"id":null,"event_second":100,"cents":100}', '{"id":2,"event_second":100,"cents":-1}', '{"id":3,"event_second":100,"cents":300}'])
```

## Worked example / walkthrough

### Worked example 1

```scala
val demo=prepareCase(ownedRoot,"demo",Seq("""{"id":1,"event_second":100,"cents":100}""","""{"id":1,"event_second":100,"cents":100}"""))
val result=runScenario(spark,demo._1,demo._2,demo._3,"duplicates")
assert(result.inputRows==2L && bag(spark,demo._3)==Seq("1:100"))
```

```python
demo=prepare_case(owned_root,"demo",['{"id":1,"event_second":100,"cents":100}']*2)
result=run_scenario(spark,*demo,"duplicates")
assert result["input_rows"]==2 and bag(spark,demo[2])==["1:100"]
```

Two source occurrences become one committed ID through a real streaming deduplication operator. The assertion checks input and output separately, and query completion comes from the API.

### Worked example 2

```scala
val samples=Seq(80L,90L,110L)
assert(samples.filter(_ >= 90L)==Seq(90L,110L))
```

```python
samples=[80,90,110]
assert [value for value in samples if value>=90]==[90,110]
```

This independent arithmetic oracle fixes the inclusive event-time policy before the actual late-case Spark query runs. It deliberately makes no engine-watermark claim.

## Exercises

### Exercise 1: Establish a finite restart baseline

Run the restart scenario with two supplied records and retain progress plus exact sink values.

**Expected result/shape:** 2 input rows and bag 1:100,2:200.

**Verify:** Assert the literal bag, input count 2 and inactive query.

**Progressive hint:** Progress and sink values are independent checks.

### Exercise 2: Prove no-input recovery without a sleep

Restart the compatible baseline with its existing checkpoint and no new file.

**Expected result/shape:** Same query ID, new run ID, zero new rows and unchanged sink.

**Verify:** Compare identities, input sum and exact bag;allow empty progress entries.

**Progressive hint:** An empty AvailableNow run can terminate without a data batch.

### Exercise 3: Test real streaming duplicate suppression

Use native streaming dropDuplicates on the id key for two identical occurrences of 1:100.

**Expected result/shape:** 2 source rows,1 committed row 1:100.

**Verify:** Compare input count 2 and the one-row bag.

**Progressive hint:** This finite state is bounded by the fixture;no watermark eviction claim is made.

### Exercise 4: Test the exact event-time boundary

Apply the explicitly declared admission cutoff event_second>=90 to rows at 80,90 and 110.

**Expected result/shape:** 3 source rows;accepted IDs 2,3 with cents 200,300.

**Verify:** Compare exact two-row bag and explain why 90 is retained.

**Progressive hint:** This is a business cutoff test, not an assertion about Spark watermark advancement.

### Exercise 5: Keep invalid rows visible in the case ledger

Reject a NULL identity and a negative amount while retaining valid 3:300.

**Expected result/shape:** 3 input occurrences,2 invalid,1 accepted.

**Verify:** Compare raw source count 3, actual progress, sink bag 3:300 and static predicate count 2.

**Progressive hint:** Missingness and domain validation are different from late-event admission.

### Exercise 6: Prove the oracle rejects a plausible regression

Compare the correct duplicate-case bag with an unsafe two-copy append result and reject the mismatch. Confirm every owned query is inactive before cleanup.

**Expected result/shape:** Correct bag passes;duplicated bag raises an assertion-contract error;all owned queries are inactive.

**Verify:** Catch the specific mismatch and compare the exact offending rows.

**Progressive hint:** A test must distinguish the intended behavior from a tempting shortcut.

## Common pitfalls

Do not substitute sleeps for batch completion, compare unordered collections as though order were guaranteed, or remove duplicates from an oracle that is supposed to preserve a bag. Do not reuse checkpoints between independent cases. Keep the fixed event-time cutoff separate from native watermark semantics. A successful local test does not establish executor-loss recovery or production throughput. Cleanup waits for owned queries and never removes a pre-existing learner root.

## Self-check

Explain the contract of `baseline` / `baseline` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 triggers and lifecycle](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#triggers)

- [Spark4.0.1 streaming deduplication](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#streaming-deduplication)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-037: Deterministic streaming tests without sleep-based guesses.
Read courses/scala-spark/guides/spark-037.md and courses/scala-spark/lessons/spark-037.scala;the paired sources are courses/scala-spark/lessons/spark-037.scala and courses/scala-spark/lessons/spark-037.py.
Direct prerequisites: spark-036. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
