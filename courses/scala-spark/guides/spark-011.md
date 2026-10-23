# spark-011: PySpark bridge: Python values versus Spark Columns

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct design prerequisites: `spark-001`, `python-10`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-011` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-011.scala) and [PySpark learner](../lessons/spark-011.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-011_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-011_solution.scala) and [PySpark reference](../solutions/spark-011_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Translate known Python collections and tests into explicit Spark expressions while keeping Python and engine execution distinct.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Driver value:** A value already present in the Python or Scala process, such as a Boolean or a small local list.

- **Column expression:** A description of an engine calculation over DataFrame rows, not a single driver-side value.

- **Transformation:** An operation constructing another DataFrame plan, such as filter or select.

- **Action:** An operation requesting execution and results, such as count or a bounded collect.

- **SQL NULL:** An unknown value whose comparisons generally produce unknown rather than ordinary false or true.

A Python Boolean and a Spark Column are different kinds of objects. `3 > 1` is already true on the driver. `F.col("amount_cents") > F.lit(10)` describes a comparison that Spark will evaluate for each row. Calling Python bool on that Column asks for one truth value from a distributed expression and is rejected. Python and/or/not have scalar short-circuit semantics, so they are not the operators for combining Spark predicates.

In PySpark, use parenthesized &,| and ~ expressions or Column methods. In Scala, Column overloads such as &&,|| and ! construct engine expressions; they are distinct from applying ordinary driver Boolean logic to collected rows. Parentheses matter in Python because operator precedence can otherwise combine constants and Columns in an unintended order. Write each comparison as a complete unit before combining it.

The four-row fixture has unique event IDs and amounts 0,20, NULL,20. The two 20-cent values are different events. Filtering amount>10 should retain IDs 2 and 4, while the NULL comparison is unknown and does not pass WHERE/filter. Observed zero is not missing. Use isNull to find the missing amount and equality to 0 to find the observed zero; Python `is None` tests the Column object's identity rather than the row values.

select constructs output columns and can preserve or change which identity is visible. Adding one to amount propagates NULL under SQL arithmetic. Replacing it with zero would be a separate imputation policy, not ordinary addition. The exercise retains event_id beside every derived amount so equal output values do not invite accidental deduplication.

The helper `ids` collects only this four-row fixture after ordering by event_id. This bounded demonstration is not a pattern for collecting a large table into driver memory. A real large-data operation should retain distributed outputs or apply an explicit admission and result-size policy. The ordering is part of the output contract because DataFrame row order is not implied by construction or partition arrival.

SQL and DataFrame expressions use the same Spark engine but offer different syntax. The final exercise registers an owned session-local temporary view and writes SELECT, FROM, WHERE and ORDER BY explicitly. Both language implementations compare against the literal IDs[2,4]. Agreement between SQL and Columns alone would not rule out a shared wrong threshold or missingness policy.

This bridge assumes the existing Python testing lesson and does not require completing every Scala foundation first. The paired Scala code is a syntax comparison and optional second implementation. The common SparkSession lesson next makes the schema, action and lifecycle contracts explicit for both entry routes.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val schema = StructType(Seq(
  StructField("event_id",LongType,false),
  StructField("amount_cents",LongType,true)))
val rows = Seq(Row(1L,0L),Row(2L,20L),Row(3L,null),Row(4L,20L))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

schema = StructType([
    StructField("event_id", LongType(), False),
    StructField("amount_cents", LongType(), True),
])
raw = spark.createDataFrame([(1, 0), (2, 20), (3, None), (4, 20)], schema=schema)
```

## Worked example / walkthrough

### Worked example 1

```scala
val driverValue: Boolean = 3 > 1
val predicate: Column = col("amount_cents") > lit(10L)
assert(driverValue)
assert(raw.filter(predicate).select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq == Seq(2L,4L))
println("A Column describes row-wise engine work")
```

```python
driver_value = 3 > 1
predicate = F.col("amount_cents") > F.lit(10)
assert driver_value is True
assert [row.event_id for row in raw.filter(predicate).select("event_id").orderBy("event_id").collect()] == [2, 4]
print("A Column describes row-wise engine work")
```

The driver Boolean is immediately available, while the Column is passed into filter as an expression. The action collects a known four-row fixture and verifies exact retained identities. NULL does not pass the comparison, and duplicate equal amounts remain separate events.

### Worked example 2

```scala
val missing = raw.filter(col("amount_cents").isNull).select("event_id").collect().map(_.getLong(0)).toSeq
val zero = raw.filter(col("amount_cents") === lit(0L)).select("event_id").collect().map(_.getLong(0)).toSeq
assert(missing == Seq(3L) && zero == Seq(1L))
println("Missing amount and observed zero are different rows")
```

```python
missing = [row.event_id for row in raw.filter(F.col("amount_cents").isNull()).select("event_id").collect()]
zero = [row.event_id for row in raw.filter(F.col("amount_cents") == F.lit(0)).select("event_id").collect()]
assert missing == [3] and zero == [1]
print("Missing amount and observed zero are different rows")
```

isNull asks about row values in the engine. The known-zero comparison selects a different ID. These singleton outputs do not require a tie-breaking order, but larger displayed results should state an explicit final order. A driver-level is-None comparison would ask whether the Column object itself is absent.

## Exercises

### Exercise 1: Construct a predicate without collapsing it to a driver Boolean

Implement aboveTen/above_ten returning a Spark Column for amount_cents>10. Do not collect values or return a Python/Scala scalar Boolean.

**Expected result/shape:** Passing the predicate to raw.filter retains IDs 2 and 4. In Python, bool(predicate) raises ValueError rather than choosing one row's truth value.

**Verify:** Assert the exact filtered IDs and, in the PySpark reference, catch the scalar-Boolean conversion failure.

**Progressive hint:** Use col plus lit and return the expression itself.

### Exercise 2: Apply the predicate and preserve event identity

Return the ordered event IDs selected by aboveTen from this tiny fixture. Preserve both equal-valued 20-cent events and leave raw unchanged.

**Expected result/shape:** The result is[2,4], and raw still contains IDs[1,2,3,4]. Projecting amount and calling distinct is not an acceptable implementation.

**Verify:** Compare the selected IDs with literals and independently check all four raw IDs.

**Progressive hint:** Filter first, select event_id, order it, and collect only the declared small fixture.

### Exercise 3: Select missingness explicitly

Return ordered IDs whose amount_cents is SQL NULL. Do not compare the Column to JVM null/Python None using driver identity logic, and do not treat zero as missing.

**Expected result/shape:** Only ID 3 is returned. The observed-zero ID 1 is absent from the missingness result.

**Verify:** Assert[3] and separately assert that the zero-amount filter returns [1].

**Progressive hint:** Use the Column isNull operation, not a language-level object identity test.

### Exercise 4: Combine conditions with engine operators

Return ordered IDs with a known amount at least 10 and event_id less than 4. Combine parenthesized Column comparisons with engine Boolean operators in each language.

**Expected result/shape:** Only ID 2 qualifies. ID 4 fails the ID bound, ID 3 is missing, and ID 1 is below the amount threshold.

**Verify:** Assert the exact singleton and explain one exclusion reason for each other ID.

**Progressive hint:** PySpark uses & between parenthesized comparisons; Scala Columns support &&.

### Exercise 5: Preserve NULL through a derived column

Return a DataFrame with event_id and amount_plus_one=amount_cents+1, without filling NULL or dropping identity. Keep a Long-compatible integer result.

**Expected result/shape:** Ordered rows are(1,1),(2,21),(3, NULL),(4,21). The two 21 values remain separate events and unknown remains unknown.

**Verify:** Compare every ordered row with literal expected values, including the NULL position.

**Progressive hint:** select the ID and an aliased Column arithmetic expression.

### Exercise 6: Compare SQL and Columns with an independent expectation

Register a session-local temporary view and return ordered IDs from SQL SELECT/WHERE amount_cents>10. Compare SQL and DataFrame paths to the literal expected IDs rather than only to one another.

**Expected result/shape:** Both paths return [2,4]. The temporary view exists only in this owned session and no external database connection is opened.

**Verify:** Assert SQL IDs and selectedIds against [2,4] independently, then let the complete program stop its session in finally.

**Progressive hint:** The SQL query uses the same explicit threshold, NULL behavior and ORDER BY event_id.

## Common pitfalls

If Python reports that a Column cannot be converted to bool, inspect and/or/not or an if statement around a Column. If a missing-row filter returns nothing, distinguish isNull from equality to a null literal. If equal amounts collapse, restore event identity and remove unjustified distinct. If output order varies, add a complete final order before bounded collection. If a schema error appears, inspect the explicit Long/String/nullability contract before relying on inference. A temporary view name is session-local and should not be mistaken for a durable published table.

## Self-check

Explain the contract of `aboveTen` / `above_ten` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 DataFrame and SQL programming](https://spark.apache.org/docs/4.0.1/sql-getting-started.html).

- [Spark 4.0.1 NULL semantics](https://spark.apache.org/docs/4.0.1/sql-ref-null-semantics.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-011: PySpark bridge: Python values versus Spark Columns.
Read courses/scala-spark/guides/spark-011.md and courses/scala-spark/lessons/spark-011.py;the paired sources are courses/scala-spark/lessons/spark-011.scala and courses/scala-spark/lessons/spark-011.py.
Direct prerequisites: spark-001, python-10. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
