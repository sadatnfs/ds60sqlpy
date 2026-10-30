# spark-012: SparkSession, explicit schemas, and bounded actions

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct design prerequisites: `spark-001`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-012` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-012.scala) and [PySpark learner](../lessons/spark-012.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-012_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-012_solution.scala) and [PySpark reference](../solutions/spark-012_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Create an owned local session and a typed schema, then distinguish transformations from actions in either API.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **SparkSession:** The application entry point for DataFrame and SQL work, with configuration and a lifecycle that the creating program must own.

- **Explicit schema:** A declared list of field names, data types and nullability, preventing small-sample inference from silently choosing the data contract.

- **Bounded action:** An action whose driver-side result is constrained by a stated admission limit; it does not necessarily bound all distributed source work.

- **Canonical result:** A deterministic representation with declared field order, types, NULL handling and row ordering used for comparison.

Readiness for this lesson has two routes: complete the Scala foundation through spark-010, or complete the Python bridge spark-011 after the existing Python testing prerequisite. The plan's structural prerequisite lists spark-001 because the framework currently expresses AND prerequisites rather than this OR gate. The learner should demonstrate one route's language skills before treating both APIs as familiar.

SparkSession creates access to the engine and owns session-local views and configuration. The complete source runs in a fresh prepared worker process, requests local[2], disables the UI, binds driver communication to loopback and sets UTC. It reads back the actual master and version rather than assuming the builder text was accepted. The finally block stops the session even when an assertion fails. This is an owned local demonstration, not a request to reuse or stop an unrelated notebook session.

The schema names event_id, team and amount_cents. event_id is Long and nonnullable; team is nullable String; amount_cents is nullable Long. SQL's simpleString representation for Long is bigint. A field's nullable flag describes its contract, not whether the current four-row sample happens to contain NULL. Exact integer cents are preserved rather than inferred as floating point because one amount is missing.

A transformation such as filter returns another DataFrame plan. count or collect requests execution. The lesson demonstrates that separation through small source functions and explicit action sites; it does not infer a measured zero-job history from a wall-clock delay or a printed plan. Planning and metadata operations can also perform work in other contexts, especially when schemas are inferred from files.

Driver result size must be controlled deliberately. The bounded ID reader selects only event_id, orders it, requests at most limit+1 rows and rejects an oversized result. The extra row distinguishes exactly-at-limit from too-many. This bounds the collected payload, but an orderBy or source scan may still examine far more data in a real job. The fixture remains four rows so both driver and engine work are small.

Canonical comparison includes field meaning and row identity. NULL is represented as Option in Scala and None in Python; observed zero remains a value. Repartitioning changes physical placement but must not change the canonical row bag. A final complete order is used only for comparison and display, not as an assumption about raw collect order.

The final settings report distinguishes an actual Spark version from a target declaration. The prepared worker is 4.0.1 with the specified local policies. A matching version string alone is not proof of correct results, cleanup or cluster compatibility. The reference combines settings readback with schema, identity, missingness and bounded-result assertions, then leaves process-level cleanup qualification to the worker receipt.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val schema = StructType(
  Seq(
    StructField("event_id", LongType, false),
    StructField("team", StringType, true),
    StructField("amount_cents", LongType, true)
  )
)
val rows = Seq(Row(1L, "A", 0L), Row(2L, "B", null), Row(3L, "A", 25L), Row(4L, "B", 40L))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows, 2), schema)
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

schema = StructType(
    [
        StructField("event_id", LongType(), False),
        StructField("team", StringType(), True),
        StructField("amount_cents", LongType(), True),
    ]
)
raw = spark.createDataFrame(
    [(1, "A", 0), (2, "B", None), (3, "A", 25), (4, "B", 40)], schema=schema
)
```

## Worked example / walkthrough

### Worked example 1

```scala
val names = raw.schema.fields.map(_.name).toSeq
assert(names == Seq("event_id", "team", "amount_cents"))
assert(raw.schema("event_id").dataType == LongType)
assert(!raw.schema("event_id").nullable && raw.schema("amount_cents").nullable)
println(raw.schema.simpleString)
```

```python
assert raw.columns == ["event_id", "team", "amount_cents"]
assert isinstance(raw.schema["event_id"].dataType, LongType)
assert raw.schema["event_id"].nullable is False
assert raw.schema["amount_cents"].nullable is True
print(raw.schema.simpleString())
```

The schema is checked independently from the row values. Nullable amount permits the second record's unknown value without converting the entire field to a floating or string type. Field names and order are part of the interface used by later transformations.

### Worked example 2

```scala
val planned = raw.filter(col("team") === lit("A"))
val observedCount = planned.count()
assert(observedCount == 2L)
assert(
  planned.select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq == Seq(1L, 3L)
)
println(s"team A rows=$observedCount")
```

```python
planned = raw.filter(F.col("team") == F.lit("A"))
observed_count = planned.count()
assert observed_count == 2
assert [row.event_id for row in planned.select("event_id").orderBy("event_id").collect()] == [1, 3]
print("team A rows=", observed_count)
```

The filter expression defines the selected relation; count and the bounded fixture collection are action sites. Exact IDs confirm the predicate's meaning beyond the count. The source DataFrame still represents all four rows because a transformation does not mutate it in place.

## Exercises

### Exercise 1: Inspect the complete schema contract

Return ordered field triples(name, simpleString, nullable) for a DataFrame. Check the fixture rather than inferring correctness from a printed schema alone.

**Expected result/shape:** The triples are(event_id, bigint, false),(team, string, true),(amount_cents, bigint, true).

**Verify:** Compare the complete triples with literals in both languages, including all nullability flags.

**Progressive hint:** Iterate schema.fields and read each field's name, dataType.simpleString and nullable property.

### Exercise 2: Keep a transformation separate from its action

Return a DataFrame plan selecting team A without collecting or counting inside the function. At the call site, request a count and verify IDs 1 and 3. Preserve raw.

**Expected result/shape:** The returned frame contains two rows when evaluated; raw still has four. The function body contains only a filter transformation.

**Verify:** Assert returned count 2, ordered IDs[1,3] and raw count 4 at explicit action sites.

**Progressive hint:** Return frame.filter with a Column predicate; put count/collect in the reference checks.

### Exercise 3: Bound the driver result and detect overflow of the budget

Return ordered event IDs while collecting at most limit+1 rows, with 0<=limit<=20. Reject a result larger than limit and invalid limits. Empty data with limit 0 is valid. Do not collect the full frame before checking length.

**Expected result/shape:** The four-row fixture passes limit 4 and rejects limit 3. An empty filter with limit 0 returns empty; limit 21 is rejected before collection.

**Verify:** Assert exact IDs, catch the oversize and invalid-budget errors, and inspect the bounded limit before the action.

**Progressive hint:** Use the extra row as an overflow witness, then require the returned size not to exceed the declared limit.

### Exercise 4: Retain observed zero while isolating unknown amounts

Return rows with nonnull amount_cents, keeping all columns and identities. Do not replace NULL with zero or filter out observed zero.

**Expected result/shape:** IDs 1,3,4 remain with amounts 0,25,40, total 65. Raw still has one NULL amount at ID 2.

**Verify:** Assert exact IDs and sum 65, and independently count the unchanged raw NULL row.

**Progressive hint:** Use isNotNull only; zero is a legitimate observed value.

### Exercise 5: Canonicalize content across physical repartitioning

Return ordered triples(event_id, optional team, optional amount) for this bounded fixture. Compare raw, repartition(1) and repartition(3) against the same literal content, not raw collect order.

**Expected result/shape:** Every version yields (1, A,0),(2, B, NULL),(3, A,25),(4, B,40). Physical placement does not change identity, NULL state or value.

**Verify:** Assert all three canonical outputs and keep the final event_id ordering explicit.

**Progressive hint:** Order by the unique event ID before bounded collection and use explicit nullable Row extraction in Scala.

### Exercise 6: Read back the actual local session contract

Return master, timezone, shuffle-partition, ANSI, AQE, UI, driver-binding and Spark-version settings from the active session. Compare them with this prepared profile and rely on finally for owned stop. Do not substitute a hardcoded target string for version readback.

**Expected result/shape:** Master local[2], UTC, two shuffle partitions, ANSI true, AQE false, UI false, both driver addresses 127.0.0.1, and Spark version 4.0.1.

**Verify:** Assert the complete settings map; record actual version output and distinguish it from worker cleanup evidence.

**Progressive hint:** Read SparkSession.conf and SparkContext.getConf alongside spark.version.

## Common pitfalls

If a schema assertion fails, compare names, types and nullability separately rather than changing all fields to strings. If a bounded result overflows, do not collect first and truncate afterward. If repartitioned results compare unequal only in order, canonicalize by a real unique identity before diagnosing data loss. If NULL extraction throws in Scala, check isNullAt before getLong/getString. If settings differ from the builder, inspect the actual session and prepared profile. Never stop an unrelated session or treat a version string as proof that all cleanup and correctness contracts passed.

## Self-check

Explain the contract of `schemaFields` / `schema_fields` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 SparkSession and explicit schemas](https://spark.apache.org/docs/4.0.1/sql-getting-started.html).

- [Spark 4.0.1 configuration](https://spark.apache.org/docs/4.0.1/configuration.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-012: SparkSession, explicit schemas, and bounded actions.
Read courses/scala-spark/guides/spark-012.md and courses/scala-spark/lessons/spark-012.scala;the paired sources are courses/scala-spark/lessons/spark-012.scala and courses/scala-spark/lessons/spark-012.py.
Direct prerequisites: spark-001. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
