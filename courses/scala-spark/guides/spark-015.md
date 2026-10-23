# spark-015: SQL and DataFrame expressions with ANSI boundaries

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-014`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-015` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-015.scala) and [PySpark learner](../lessons/spark-015.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-015_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-015_solution.scala) and [PySpark reference](../solutions/spark-015_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Express the same relational result with SQL and Columns and make casting/error policy explicit.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **ANSI mode:** A Spark SQL policy that makes invalid casts and selected arithmetic failures raise errors rather than silently returning fallback values.

- **Tolerant cast:** An explicit try_cast expression returning NULL when conversion fails, which still needs provenance to distinguish failure from source NULL.

- **Lexical versus domain validity:** Whether text can be converted to a type is separate from whether the converted value is meaningful for the business rule.

- **Temporary view:** A session-local name for a DataFrame plan used by SQL without creating an external database table.

Spark 4.0.1 enables ANSI behavior by default, and the complete source sets it explicitly. A strict cast of malformed text to BIGINT is expected to fail when evaluated. That is different from a parser that returns a rejected-record result. Choose the behavior deliberately: fail the job for an unexpected broken contract, or use an explicit tolerant parse branch and retain an error ledger for expected dirty data.

The source contains eight event IDs and text amounts 100,0, whitespace-padded 25, NULL, bad, an integer above Long.MaxValue,-5 and 50. The two unconvertible nonnull tokens are IDs 5 and 6. Source NULL at ID 4 is an allowed unknown value in this lesson and must not be mislabeled as a malformed token. Negative 5 is a valid signed BIGINT but can violate a later nonnegative-amount domain rule.

try_cast(trim(amount_text) AS BIGINT) produces a nullable Long column. To classify it, inspect the original token first: source NULL means missing; nonnull source with NULL parse result means rejected; otherwise conversion succeeded. Filling all parse NULLs with zero would hide both source missingness and malformed input while leaving some aggregate totals deceptively plausible.

The accepted parse relation includes six IDs 1,2,3,4,7,8. It contains five known amounts totaling 170 cents. The SQL and DataFrame implementations must agree with those independent values. Their shared engine does not exempt either from the contract: an incorrect WHERE clause can silently drop the allowed missing record or an alias can replace the wrong field.

The strict-cast exercise intentionally evaluates a bad token under ANSI mode and checks the CAST_INVALID_INPUT diagnostic. The program catches only evidence matching that failure code and reports it as expected; an unrelated exception must not count as a successful negative test. Spark may emit an error log for this deliberate case even though the reference later completes all assertions.

Finally, the domain filter retains unknown amounts but rejects negative known amounts. Its accepted IDs become 1,2,3,4,8, with five rows, four observed values and 175 cents. That result differs from the parse-valid relation because domain validity is an additional decision. The complete ledger is five domain-accepted rows, two parse failures and one domain-negative row, not an unexplained change in row count.

All data remain in a local explicit-schema fixture. No external SQL service is opened. This lesson focuses on expression equivalence, error policy and honest rejection accounting; it does not claim that a cast validates every possible source format or that tolerant parsing makes an unknown value safe to use.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val schema = StructType(Seq(StructField("event_id",LongType,false),StructField("amount_text",StringType,true)))
val rows = Seq(Row(1L,"100"),Row(2L,"0"),Row(3L," 25 "),Row(4L,null),Row(5L,"bad"),Row(6L,"9223372036854775808"),Row(7L,"-5"),Row(8L,"50"))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

schema = StructType([StructField("event_id", LongType(), False), StructField("amount_text", StringType(), True)])
raw = spark.createDataFrame([(1,"100"),(2,"0"),(3," 25 "),(4,None),(5,"bad"),(6,"9223372036854775808"),(7,"-5"),(8,"50")], schema=schema)
```

## Worked example / walkthrough

### Worked example 1

```scala
val tolerant = raw.select(col("event_id"),expr("try_cast(trim(amount_text) AS BIGINT)").as("parsed_amount"))
assert(tolerant.filter(col("parsed_amount").isNull).select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq == Seq(4L,5L,6L))
println("Parse NULLs include both source missingness and rejected text")
```

```python
tolerant = raw.select("event_id", F.expr("try_cast(trim(amount_text) AS BIGINT)").alias("parsed_amount"))
assert [row.event_id for row in tolerant.filter(F.col("parsed_amount").isNull()).select("event_id").orderBy("event_id").collect()] == [4, 5, 6]
print("Parse NULLs include both source missingness and rejected text")
```

The parsed column alone cannot distinguish allowed source absence from conversion failure. IDs 4,5,6 all appear as NULL, so the ledger must retain amount_text or a source-missing flag. The result is a typed parsing observation, not yet an accepted-event table.

### Worked example 2

```scala
val signed = raw.filter(col("event_id") === lit(7L)).select(expr("try_cast(amount_text AS BIGINT)").as("amount"))
assert(signed.first().getLong(0) == -5L)
assert(spark.conf.get("spark.sql.ansi.enabled") == "true")
println("A signed integer can be cast-valid while domain-invalid")
```

```python
signed = raw.filter(F.col("event_id") == F.lit(7)).select(F.expr("try_cast(amount_text AS BIGINT)").alias("amount"))
assert signed.first()[0] == -5
assert spark.conf.get("spark.sql.ansi.enabled") == "true"
print("A signed integer can be cast-valid while domain-invalid")
```

The type system permits a negative Long. Rejecting it requires a separate business predicate rather than assuming conversion success establishes a nonnegative monetary domain. ANSI readback confirms the declared error policy independently of this valid signed conversion.

## Exercises

### Exercise 1: Add an explicit tolerant parse column

Return all source columns plus parsed_amount from try_cast(trim(amount_text) AS BIGINT). Preserve eight rows and distinguish this nullable parse result from a final validity decision.

**Expected result/shape:** Ordered parsed values are 100,0,25, NULL, NULL, NULL,-5,50. The output parsed type is bigint.

**Verify:** Compare all eight(event_id, parsed_amount) pairs and the field type with literals.

**Progressive hint:** Use expr for the same SQL try_cast expression in both languages.

### Exercise 2: Classify missing versus rejected tokens

Add parse_status with missing for source NULL, rejected for a nonnull source that parsed to NULL, and valid otherwise. Keep all original rows and parsed values.

**Expected result/shape:** IDs 1,2,3,7,8 are valid, ID 4 missing, and IDs 5,6 rejected. Counts are 5,1,2 and sum to 8.

**Verify:** Assert the ordered status list and the exact two rejected IDs.

**Progressive hint:** Test original missingness before testing parsed missingness.

### Exercise 3: Project the six parse-accepted events

Retain valid and missing statuses, then return event_id and parsed_amount aliased as amount_cents. Reject only malformed/overflowing nonnull tokens at this stage.

**Expected result/shape:** IDs[1,2,3,4,7,8] remain with amounts[100,0,25, NULL,-5,50]. There are 6 rows,5 known values and total 170.

**Verify:** Assert the exact rows and independent count/known/sum metrics.

**Progressive hint:** Filter parse_status!=rejected before projecting the renamed numeric field.

### Exercise 4: Express the same parse contract in SQL

Register the raw frame as a session-local view and produce the same six event_id, amount_cents rows using a SQL parse CTE and explicit missing-or-success filter. Compare with literals rather than only with the DataFrame result.

**Expected result/shape:** The SQL ordered rows are exactly the six rows from Exercise 3, including the NULL amount and signed-5.

**Verify:** Assert the SQL result against the full literal row list and separately compare the DataFrame path to that list.

**Progressive hint:** Keep original amount_text in the CTE long enough to distinguish source NULL from failed conversion.

### Exercise 5: Observe strict ANSI failure at evaluation

Return a strict trimmed BIGINT cast projection. Evaluate a valid subset successfully, then intentionally evaluate the bad token at ID 5 under ANSI mode and require a CAST_INVALID_INPUT diagnostic. Do not count an unrelated exception as success.

**Expected result/shape:** The valid subset has the same six rows. ID 5 fails when collected, and the reference records the expected failure code before continuing.

**Verify:** Assert ANSI readback true, valid-row results, and a caught diagnostic containing CAST_INVALID_INPUT.

**Progressive hint:** Constructing the cast plan is not the same as evaluating it; the negative test needs an action.

### Exercise 6: Apply a separate nonnegative domain policy

From parse-accepted rows, retain unknown amounts and known nonnegative amounts. Return event_id, amount_cents and report the separate negative-domain rejection at ID 7 in the checks.

**Expected result/shape:** Final IDs[1,2,3,4,8] have 5 rows,4 known values, total 175. The full source reconciles as 5 final accepted+2 parse rejected+1 negative-domain rejected.

**Verify:** Assert final rows/metrics, negative ID 7 and the 8-row conservation equation.

**Progressive hint:** Use amount is NULL OR amount>=0 on the parsed relation; do not rewrite parsing status.

## Common pitfalls

If try_cast produces NULL, inspect the original token before deciding whether the row was missing or malformed. If strict casting unexpectedly succeeds on bad text, read back ANSI mode instead of assuming the default. If a negative value survives conversion, remember that BIGINT permits signed values and add the intended domain predicate. If SQL and DataFrames agree on the wrong population, compare each against literal IDs and counts. Expected cast errors must be identified by their diagnostic, not swallowed as any exception.

## Self-check

Explain the contract of `withParsed` / `with_parsed` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 ANSI and tolerant cast behavior](https://spark.apache.org/docs/4.0.1/sql-ref-ansi-compliance.html).

- [Spark 4.0.1 built-in functions](https://spark.apache.org/docs/4.0.1/sql-ref-functions-builtin.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-015: SQL and DataFrame expressions with ANSI boundaries.
Read courses/scala-spark/guides/spark-015.md and courses/scala-spark/lessons/spark-015.scala;the paired sources are courses/scala-spark/lessons/spark-015.scala and courses/scala-spark/lessons/spark-015.py.
Direct prerequisites: spark-014. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
