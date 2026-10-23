# spark-041: Compatibility and recovery change rehearsal

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct design prerequisites: `spark-040`. The prepared baseline is Spark4.0.1,Scala binary2.13,JDK17 and Python3.12. Read the [execution baseline](../execution-baseline.md);a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-041` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`;Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-041.scala) and [PySpark learner](../lessons/spark-041.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-041_solutions.md) only after an attempt or an explicit worked comparison;the [Scala reference](../solutions/spark-041_solution.scala) and [PySpark reference](../solutions/spark-041_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture;do not copy it onto an unbounded or large production table.

## Learning objectives

- Assess a Spark/runtime change without reusing incompatible state or trusting a version string alone.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Compatibility tuple:** The actual Spark, Scala, JDK, Python and optional dependency versions relevant to a runtime boundary.

- **Golden suite:** Small independent fixtures checking values, types, NULLs, multiplicity and other semantic contracts.

- **State-key schema:** The representation of keys retained by a stateful streaming operator, which is part of checkpoint compatibility.

- **Candidate namespace:** Separate source/checkpoint/output ownership for a proposed change, preventing accidental mutation of the baseline.

- **Rollback:** Returning to a preserved tested contract and state path, with explicit post-rollback checks.

- **Qualification:** Actual execution evidence for the named stack and behavior, not the presence of a version string in configuration.

A runtime change can affect binary loading, SQL semantics, Python dependencies, state schemas and sink behavior. A successful version print proves only which runtime answered that request. A credible change review joins the actual version tuple with independent golden results and a recovery plan. This lesson executes the current prepared Spark 4.0.1 stack and rehearses a query-shape change without pretending a second runtime has been provisioned.

The receipt records Scala binary family and actual patch, JDK major and runtime patch, Python version and optional PyArrow distribution presence. Scala invokes only the bundled python 3 with a fixed five-second metadata probe;it does not install or import Arrow. PySpark records its own interpreter and JVM. An absent optional dependency is recorded as not-installed rather than silently fetched. These values matter at different boundaries:Scala binary compatibility is not the same as Python wheel compatibility or a valid persisted state schema.

## Test semantics before considering promotion

The golden suite has four rows:two equal 100-cent occurrences under one ID, a NULL amount under another, and a zero under a third. Expected rows 4, known amounts 3, total 200 and distinct IDs 3 catch different defects. Dropping duplicate occurrences can preserve some aggregates while changing the population;replacing NULL with zero changes known-value counts. The suite also checks exact decimal 12345678.90 and a timezone-offset instant rendered 19:00UTC under the baseline.

The tests are deliberately tiny so their expected results are independently inspectable. They are not a complete compatibility certification. A production workload adds its own UDFs, connectors, data formats, optimizer-sensitive expectations and performance bounds. The important discipline is to run the same semantic contract in both actual environments and preserve failures, rather than comparing only two version labels.

## Separate state compatibility from source compatibility

The baseline streaming query deduplicates by id and writes to its own Parquet sink. Its checkpoint contains state whose keys represent that operator contract. Changing the keys to id, cents changes both stored state representation and business semantics. The program refuses that same-checkpoint request before launching it. This refusal is an application policy check;the guide does not fabricate a particular Spark engine error.

A rejected incompatible reuse must not be repaired by deleting checkpoint internals, changing schema checks or silently migrating state. The documented Spark recovery rules constrain what query changes can reuse a checkpoint. Some stateless changes may be supported under conditions, while stateful schema/operator changes require a separately designed recovery path. Review the exact operation instead of assuming every source edit is safe because the main function still compiles.

## Run a candidate without modifying the baseline

The fixture first processes 1:100 and 2:200 under ID-only deduplication. It then publishes a new occurrence 1:999. The candidate uses id, cents keys with a new checkpoint and output namespace, so replay produces 1:100,1:999,2:200. That is a real observed product difference, not a checkpoint corruption. It fails the existing one-row-per-ID product gate and is not promoted.

The baseline checkpoint and sink remain available. Resuming the original ID-only query processes the new source occurrence under its existing policy and does not append another ID 1 row. Its query identity persists and its output remains 1:100,2:200. This is an explicit rollback rehearsal within one runtime. It does not establish cross-version state migration or decide how a real application should resolve conflicting event payloads.

A production first-seen policy may itself be insufficient when conflicting updates matter. This fixture uses the difference to expose a changed contract. A real migration review must state whether it preserves append events, latest updates, corrections or one canonical record per ID, including tie-breaking and late-data rules. The next capstone defines those decisions more explicitly in a bounded application ledger.

## Keep the target-profile row honest

The proposal gate requires actual target qualification, golden pass, recovery review and product acceptance. A missing target profile remains unavailable even if the proposed Spark/Scala/JDK strings look plausible. The lesson never downloads a second runtime or resets an existing learner checkpoint. All files are created inside one fresh root and removed only after owned queries terminate.

The final packet records source and target claims separately. For this run, the source runtime and query-shape rehearsal have actual evidence;the hypothetical target runtime does not. That distinction makes a migration review actionable:it says exactly which acceptance work remains instead of giving an unsupported compatibility approval.

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
ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-041-")
val input=ownedRoot.resolve("input");val oldCheckpoint=ownedRoot.resolve("baseline-checkpoint");val oldOutput=ownedRoot.resolve("baseline-output")
publishFile(ownedRoot,input,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
val golden=spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,100L),Row(1L,100L),Row(2L,null),Row(3L,0L))),eventSchema)
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
owned_root=Path(tempfile.mkdtemp(prefix="spark-041-",dir=Path.cwd()))
input_path=owned_root/"input";old_checkpoint=owned_root/"baseline-checkpoint";old_output=owned_root/"baseline-output"
publish_file(owned_root,input_path,"batch-01.json",['{"id":1,"cents":100}','{"id":2,"cents":200}'])
golden=spark.createDataFrame([(1,100),(1,100),(2,None),(3,0)],EVENT_SCHEMA)
```

## Worked example / walkthrough

### Worked example 1

```scala
val keys=Seq("id")
val changed=Seq("id","cents")
assert(keys!=changed)
```

```python
keys=["id"];changed=["id","cents"]
assert keys!=changed
```

The state-key change is visible before any query launch. This pure comparison motivates a separate recovery namespace;it does not claim to inspect or rewrite Spark checkpoint internals.

### Worked example 2

```scala
val sameInstant=spark.sql("SELECT CAST(to_timestamp('2026-10-23T12:00:00-07:00') AS STRING)").first().getString(0)
assert(sameInstant=="2026-10-23 19:00:00")
```

```python
same_instant=spark.sql("SELECT CAST(to_timestamp('2026-10-23T12:00:00-07:00') AS STRING)").first()[0]
assert same_instant=="2026-10-23 19:00:00"
```

The actual SQL expression checks the instant under the UTC session. Preserving displayed local clock text instead would change meaning and fail the golden expectation.

## Exercises

### Exercise 1: Capture the actual runtime tuple

Record Spark, Scala binary and patch, JDK major and patch, Python version and optional PyArrow distribution version without installing anything.

**Expected result/shape:** Spark 4.0.1, Scala 2.13 family, JDK 17;actual patch strings and explicit not-installed Arrow when absent.

**Verify:** Inspect actual values and reject a claimed target qualification based only on a proposed version string.

**Progressive hint:** Optional dependency absence is a valid recorded state.

### Exercise 2: Run a type, NULL and multiplicity golden suite

Evaluate the supplied four-row bag plus exact decimal and timezone expressions.

**Expected result/shape:** 4 rows,3 known amounts, total 200,3 distinct IDs;decimal 12345678.90;instant 19:00UTC.

**Verify:** Compare exact metrics and rendered values under the UTC baseline.

**Progressive hint:** Agreement between languages is useful only after matching an independent oracle.

### Exercise 3: Preserve baseline state and reject incompatible reuse

Run the baseline ID-only deduplication query, then reject a request to change its state keys to id, cents while retaining that checkpoint.

**Expected result/shape:** Baseline output 1:100,2:200;preflight rejects changed keys before starting a new query.

**Verify:** Compare owned-query count before/after the refusal and confirm the old checkpoint/output remain present and unchanged.

**Progressive hint:** A state-key schema change needs a new recovery plan, not a renamed version label.

### Exercise 4: Run the changed query in a separate candidate namespace

Add a new occurrence 1:999 and run id, cents deduplication using a new checkpoint/output.

**Expected result/shape:** Candidate bag 1:100,1:999,2:200, which fails the baseline one-row-per-ID product gate.

**Verify:** Compare candidate and baseline exact bags and preserve old checkpoint/output.

**Progressive hint:** Separate execution avoids corruption but does not make a changed product automatically acceptable.

### Exercise 5: Rehearse rollback to the preserved compatible query

Resume the original ID-only query with its original checkpoint after the candidate is rejected.

**Expected result/shape:** The same baseline query ID resumes;the new occurrence of already-seen ID 1 does not add a row;baseline output stays 1:100,2:200.

**Verify:** Check query identity and exact sink bag without deleting either checkpoint.

**Progressive hint:** Rollback restores the tested contract;it does not erase input history.

### Exercise 6: Gate a proposed runtime change on actual evidence

Require a qualified target profile, golden-suite pass, compatible recovery design and product acceptance before promotion.

**Expected result/shape:** The supplied unqualified target or failed candidate is rejected;all four true permits a proposal in this pure decision model.

**Verify:** Check missing-profile and wrong-product negatives, then record that no second runtime was provisioned.

**Progressive hint:** A version string is an input to qualification, not the qualification itself.

## Common pitfalls

Do not compare only version strings, assume Scala binary compatibility implies checkpoint compatibility, or reuse a candidate checkpoint/output accidentally. Do not delete state to turn an incompatible change into a fresh run without labeling that data-recovery choice. Keep optional Arrow absence explicit. The preflight refusal is application policy and the candidate is same-runtime query-shape rehearsal;neither is a claimed cross-version engine migration test.

## Self-check

Explain the contract of `versionReceipt` / `version_receipt` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark4.0.1 recovery after query changes](https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html#recovery-semantics-after-changes-in-a-streaming-query)

- [Spark4.0.1 SQL migration guide](https://spark.apache.org/docs/4.0.1/sql-migration-guide.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-041: Compatibility and recovery change rehearsal.
Read courses/scala-spark/guides/spark-041.md and courses/scala-spark/lessons/spark-041.scala;the paired sources are courses/scala-spark/lessons/spark-041.scala and courses/scala-spark/lessons/spark-041.py.
Direct prerequisites: spark-040. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
