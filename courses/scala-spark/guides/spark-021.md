# spark-021: Read logical and physical plans

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-020`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-021` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-021.scala) and [PySpark learner](../lessons/spark-021.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-021_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-021_solution.scala) and [PySpark reference](../solutions/spark-021_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Use explain output to connect filters, projections and exchanges to the written query.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Parsed logical plan:** A tree describing the written query before names and types have been fully resolved.

- **Analyzed plan:** A logical tree whose table and column references have resolved against schemas and whose expressions have types.

- **Optimized plan:** A logically equivalent tree after transformations such as filter movement and unused-column elimination.

- **Physical plan:** The chosen execution operators, including scans, local processing and exchanges; it is a plan, not measured completion evidence.

- **Exchange:** A redistribution boundary in a physical plan, such as hash partitioning for a grouped aggregate.

- **Read schema:** The fields requested from a file scan, which can be narrower than the stored schema when unused columns are pruned.

A query has both a meaning and a proposed execution. The meaning is a relation: which rows and fields should be returned. The plan describes how Spark intends to produce it in the current environment. This lesson checks the logical output independently before interpreting any operator text. An attractive plan cannot justify incorrect totals, and a correct total does not prove that a proposed optimization reduced actual resource use.

The local fixture writes 12 generated rows to a fresh owned Parquet directory inside the current job scratch. Its schema has id, group_id, amount and unused_payload. The projection query keeps IDs 3 through 11 and doubles amount. It needs id and amount from the scan, but does not need group_id or unused_payload. The grouped query also needs group_id and yields three groups with counts 3 and totals 180,210,240. These literal results provide a small oracle against which query rewrites can be compared.

EXPLAIN EXTENDED exposes parsed, analyzed, optimized and physical stages. The parsed tree can contain unresolved references. The analyzed tree binds names to known columns and determines expression types. The optimizer may collapse projections or move filters while preserving relational semantics. The physical tree selects concrete execution operators. These stages help locate whether a problem concerns a missing column, a mistaken query transformation, or a costly execution strategy.

EXPLAIN FORMATTED presents a physical outline and node details. The scan detail can reveal its ReadSchema and pushed filters. A pushed predicate indicates that filtering information was passed to the data source; it does not by itself measure how many bytes or row groups were skipped. A residual Filter can remain above the scan even when a predicate was pushed. This is compatible with correctness checks at multiple layers and should not automatically be called a failed optimization.

Column pruning is visible when the scan ReadSchema contains only id and amount for the projection query. The fixture's unused_payload is deliberately stored but unneeded. The reference extracts the ReadSchema line and checks the needed and excluded fields there, rather than searching the entire extended plan, where the original table schema legitimately still appears. That scope matters: testing the wrong portion of plan text can produce a false claim that pruning failed.

The grouped aggregate uses local partial aggregation and a redistribution so equal group keys can meet for final aggregation in this setup. An Exchange is expected under the fixed two-partition, AQE-disabled file scan. Its presence explains a data-movement boundary; it does not report how many network bytes were sent or how long tasks took. A local[2] shuffle is still a logical redistribution, but it is not a measurement of a remote cluster network.

Plan text contains identifiers and local paths that vary across runs. This lesson normalizes expression IDs and the owned scratch-root path for readability. It deliberately avoids an exact whole-plan snapshot assertion. Relevant operator names, query fields and independent outputs are checked instead. Stable normalization should not erase semantics such as partitioning keys, predicates or required columns merely to make a test pass.

The sixth task compares a nested projection/filter query with the direct expression. Both return the same literal rows, and their optimized stages can be inspected to understand how Catalyst simplifies them. The lesson does not assert every Spark version must render byte-identical trees or choose the same operator arrangement. Runtime version, ANSI mode, AQE setting and shuffle partition count accompany the evidence so future differences can be investigated rather than misreported as a semantic regression.

All file creation is under a fresh lesson-owned root, and cleanup removes only that root in finally before the session is stopped. The generated data and plan output are bounded. A plan can be inspected before executing its final result, but producing this Parquet fixture is itself a small write action. No external storage, metastore or production table is involved.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files,Path,Paths}
import scala.jdk.CollectionConverters._

ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-021-")
val fixture = spark.range(0L,12L,1L,2).withColumn("group_id",col("id") % 3L).withColumn("amount",col("id") * 10L).withColumn("unused_payload",lit("xxxxxxxxxxxxxxxx"))
val dataPath = ownedRoot.resolve("data").toString
fixture.write.mode("errorifexists").parquet(dataPath)
val input = spark.read.parquet(dataPath)
input.createOrReplaceTempView("ds60_spark_021_input")
val projectionQuery = "SELECT id,amount*2 AS doubled FROM ds60_spark_021_input WHERE amount>=30"
val aggregateQuery = "SELECT group_id,COUNT(*) AS n,SUM(amount) AS total FROM ds60_spark_021_input WHERE amount>=30 GROUP BY group_id"
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
import re

owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-021-",dir=".")).resolve()
fixture = spark.range(0,12,1,2).withColumn("group_id",F.col("id")%3).withColumn("amount",F.col("id")*10).withColumn("unused_payload",F.lit("xxxxxxxxxxxxxxxx"))
data_path = str(owned_root/"data")
fixture.write.mode("errorifexists").parquet(data_path)
input_frame = spark.read.parquet(data_path)
input_frame.createOrReplaceTempView("ds60_spark_021_input")
projection_query = "SELECT id,amount*2 AS doubled FROM ds60_spark_021_input WHERE amount>=30"
aggregate_query = "SELECT group_id,COUNT(*) AS n,SUM(amount) AS total FROM ds60_spark_021_input WHERE amount>=30 GROUP BY group_id"
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(input.count() == 12L)
assert(input.columns.toSeq == Seq("id","group_id","amount","unused_payload"))
println("Owned Parquet fixture has four stored columns and12 rows")
```

```python
assert input_frame.count() == 12
assert input_frame.columns == ["id","group_id","amount","unused_payload"]
print("Owned Parquet fixture has four stored columns and12 rows")
```

The stored schema and population establish the baseline for later pruning and filtering claims. Parquet reads may mark fields nullable for compatibility, so the lesson checks field names and logical values without asserting writer-side nullability must be preserved exactly.

### Worked example 2

```scala
val rows = spark.sql(projectionQuery).orderBy("id").collect()
assert(rows.length == 9 && rows.head.getLong(0) == 3L && rows.last.getLong(0) == 11L)
spark.sql("EXPLAIN FORMATTED " + projectionQuery).show(false)
```

```python
rows = spark.sql(projection_query).orderBy("id").collect()
assert len(rows) == 9 and rows[0][0] == 3 and rows[-1][0] == 11
spark.sql("EXPLAIN FORMATTED " + projection_query).show(truncate=False)
```

The output check and plan display answer different questions. The first establishes a bounded observable result; the second reveals proposed operators. The exercises strengthen the output oracle and capture plan text as named evidence rather than inferring execution success from EXPLAIN.

## Exercises

### Exercise 1: Check the query meaning before its execution plan

Execute the projection query and return ordered(id, doubled) tuples. Compare all nine rows with the literal rule id 3..11, doubled=20*id.

**Expected result/shape:** Nine tuples from(3,60) through(11,220), with no missing or extra identities.

**Verify:** Assert the complete tuple list, not only the first/last rows or a printed plan.

**Progressive hint:** Use an explicit order only for the tiny comparison; the SELECT relation itself has no promised display order.

### Exercise 2: Capture each extended planning stage

Return EXPLAIN EXTENDED text for the supplied query. Permit only EXTENDED or FORMATTED as the mode and reject another mode.

**Expected result/shape:** Text includes Parsed Logical Plan, Analyzed Logical Plan, Optimized Logical Plan and Physical Plan sections. An invalid mode is rejected.

**Verify:** Assert all four section labels and an explicit invalid-mode exception.

**Progressive hint:** EXPLAIN is a SQL statement returning a plan column; join its returned lines into one bounded string.

### Exercise 3: Inspect the scan scope for column pruning

Capture FORMATTED output and extract lines containing ReadSchema. Verify that the projection scan requests id and amount but not group_id or unused_payload. Also locate Filter and Project operators.

**Expected result/shape:** ReadSchema includes id: bigint and amount: bigint only among the four stored fields. Filter and Project evidence are present.

**Verify:** Assert needed/excluded fields in the extracted scan lines rather than in the entire extended plan.

**Progressive hint:** Original relation schemas may remain visible in earlier planning stages even after physical pruning.

### Exercise 4: Connect grouped output to a redistribution boundary

Execute the grouped aggregate and capture its FORMATTED plan. Return group_id, n, total and locate aggregate plus Exchange operators under the fixed AQE-disabled configuration.

**Expected result/shape:** Groups 0,1,2 each have n3 with totals 180,210,240. The plan shows aggregation and an Exchange.

**Verify:** Assert all group tuples independently, then assert the relevant operator markers and recorded AQE setting.

**Progressive hint:** A local partial aggregate can reduce data before equal keys meet at a later aggregate.

### Exercise 5: Normalize incidental identifiers without erasing semantics

Replace expression-number suffixes such as#123 with#ID and the exact owned root path with<owned-root> in plan text. Preserve operators, field names, predicates and partitioning descriptions.

**Expected result/shape:** A synthetic Project id#123L becomes Project id#IDL; the current temporary root is absent from normalized actual plan text.

**Verify:** Assert the synthetic replacement and required semantic tokens after normalizing the actual plan.

**Progressive hint:** Normalize only explicitly identified unstable fragments; do not remove whole lines to satisfy a snapshot.

### Exercise 6: Compare equivalent query forms with separate semantic and plan evidence

Execute a nested projection/filter form of the direct query and compare its exact rows. Capture its extended plan and return a bounded receipt containing Spark version, ANSI, AQE and shuffle partition settings.

**Expected result/shape:** The nested query has the same nine tuples. Receipt shows Spark 4.0.1, ANSItrue, AQEfalse, shuffle partitions 2. Both extended plans expose an optimized stage.

**Verify:** Assert full output parity with the literal oracle and exact controlled settings; do not assert whole-plan byte equality or faster execution.

**Progressive hint:** Catalyst may collapse adjacent projections; record observed stages rather than requiring one textual tree.

## Common pitfalls

Do not treat EXPLAIN as a benchmark or proof that the final action completed. Do not search the entire extended plan for a field name when checking the scan's ReadSchema. A pushed filter can coexist with a residual Filter. An Exchange denotes redistribution but does not report actual shuffle volume. Keep Spark version and configuration with observations. Delete only the fresh owned fixture root, and never point the cleanup helper at an existing dataset or checkpoint.

## Self-check

Explain the contract of `projectionResult` / `projection_result` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 EXPLAIN stages and modes](https://spark.apache.org/docs/4.0.1/sql-ref-syntax-qry-explain.html)

- [Spark 4.0.1 Parquet schema and scans](https://spark.apache.org/docs/4.0.1/sql-data-sources-parquet.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-021: Read logical and physical plans.
Read courses/scala-spark/guides/spark-021.md and courses/scala-spark/lessons/spark-021.scala;the paired sources are courses/scala-spark/lessons/spark-021.scala and courses/scala-spark/lessons/spark-021.py.
Direct prerequisites: spark-020. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
