# spark-016: Join cardinality, fanout, semi joins and NULL-safe keys

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-015`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-016` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-016.scala) and [PySpark learner](../lessons/spark-016.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-016_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-016_solution.scala) and [PySpark reference](../solutions/spark-016_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Predict join output counts from key multiplicities before running a join.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Join grain:** The meaning of one output row, such as one matched fact/dimension pair or one original fact retained by membership.

- **Key multiplicity:** The number of rows carrying a key on each side; an equality join emits their product for a matching nonnull key.

- **Semi join:** A membership join returning left rows that have at least one right match without multiplying them by right-side matches.

- **Anti join:** A membership join returning left rows with no right match under the chosen equality rule.

- **NULL-safe equality:** An explicit comparison treating two NULL values as equal; it is a value rule, not proof that unknown entity IDs refer to the same entity.

Before running a join, predict the output grain and row count. Key A appears in two facts and three dimension rows, so an ordinary inner equality join emits six A pairs. Key B contributes one more pair. Keys C and D have no dimension match, and the NULL fact key does not equal the NULL dimension key under ordinary SQL equality. The expected inner count is therefore seven.

The fact amount belongs to a fact, not automatically to every joined pair as an independently additive measure. Joining A to three dimension versions repeats each A amount three times. The joined-pair sum becomes 120 cents even though the matched facts originally total 60. This is not an arithmetic error in SUM; it is a grain error if the result is presented as unduplicated fact revenue.

A left join retains unmatched facts through one NULL-extended row each. Its count is ten: seven matched pairs plus C, D and the NULL-key fact. COUNT(*) counts all ten output rows, while COUNT(dimension_row) counts only seven actual matches. Inspect the nonnull right identity rather than assuming the left-join placeholder represents a dimension record.

Semi and anti joins answer membership questions at fact grain. The semi result is IDs 1,2,3 and the anti result is 4,5,6. The three A dimension rows do not triple the semi result. Their complementary ID sets reconcile to all six facts under the same equality rule. Adding NULL-safe equality changes that membership policy, not merely an optimization detail.

The diagnostic multiplicity ledger deliberately merges the NULL buckets with NULL-safe equality so their counts can be shown on one row, then predicts zero ordinary-equality matches for that bucket. This use of NULL-safe comparison in a diagnostic is separate from changing the actual fact join. In a real identity relationship, unknown keys are usually quarantined rather than assumed to refer to one common entity.

The final enrichment gate requires a nonnull unique dimension key. The original dimension is rejected because A repeats and a NULL key exists. A supplied reviewed subset of rows 103,104,106 is then accepted. Selecting those rows is an explicit fixture decision, not a general instruction to choose the largest ingestion ID or dropDuplicates arbitrarily. The resulting left enrichment preserves all six facts and their 210-cent total.

Both DataFrame and SQL forms are checked against literal pair identities. Matching aggregate counts alone would not reveal swapped dimension labels or a wrong NULL policy. The lesson is about relational correctness; broadcasting or repartitioning cannot repair an ambiguous dimension contract.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val factSchema = StructType(Seq(StructField("fact_id",LongType,false),StructField("key",StringType,true),StructField("amount_cents",LongType,false)))
val dimensionSchema = StructType(Seq(StructField("dimension_row",LongType,false),StructField("key",StringType,true),StructField("label",StringType,false)))
val facts = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"A",10L),Row(2L,"A",20L),Row(3L,"B",30L),Row(4L,"C",40L),Row(5L,null,50L),Row(6L,"D",60L)),2),factSchema)
val dimension = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(101L,"A","alpha1"),Row(102L,"A","alpha2"),Row(103L,"A","alpha3"),Row(104L,"B","beta"),Row(105L,null,"unknown"),Row(106L,"E","epsilon")),2),dimensionSchema)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

fact_schema = StructType([StructField("fact_id",LongType(),False),StructField("key",StringType(),True),StructField("amount_cents",LongType(),False)])
dimension_schema = StructType([StructField("dimension_row",LongType(),False),StructField("key",StringType(),True),StructField("label",StringType(),False)])
facts = spark.createDataFrame([(1,"A",10),(2,"A",20),(3,"B",30),(4,"C",40),(5,None,50),(6,"D",60)],schema=fact_schema)
dimension = spark.createDataFrame([(101,"A","alpha1"),(102,"A","alpha2"),(103,"A","alpha3"),(104,"B","beta"),(105,None,"unknown"),(106,"E","epsilon")],schema=dimension_schema)
```

## Worked example / walkthrough

### Worked example 1

```scala
val aFacts = facts.filter(col("key") === lit("A")).count()
val aDimensions = dimension.filter(col("key") === lit("A")).count()
assert(aFacts == 2L && aDimensions == 3L && aFacts * aDimensions == 6L)
println(s"A predicts ${aFacts * aDimensions} joined pairs")
```

```python
a_facts = facts.filter(F.col("key") == F.lit("A")).count()
a_dimensions = dimension.filter(F.col("key") == F.lit("A")).count()
assert (a_facts, a_dimensions, a_facts*a_dimensions) == (2,3,6)
print("A predicts", a_facts*a_dimensions, "joined pairs")
```

The multiplication follows from every matching left occurrence pairing with every matching right occurrence. It predicts the six A rows before the join executes. A right-side duplicate is therefore a correctness consideration even if a physical join strategy handles it quickly.

### Worked example 2

```scala
val comparison = spark.sql("SELECT CAST(NULL AS STRING) = CAST(NULL AS STRING) AS ordinary, CAST(NULL AS STRING) <=> CAST(NULL AS STRING) AS null_safe").first()
assert(comparison.isNullAt(0) && comparison.getBoolean(1))
println("Ordinary equality is unknown;explicit NULL-safe equality is true")
```

```python
comparison = spark.sql("SELECT CAST(NULL AS STRING) = CAST(NULL AS STRING) AS ordinary, CAST(NULL AS STRING) <=> CAST(NULL AS STRING) AS null_safe").first()
assert tuple(comparison) == (None, True)
print("Ordinary equality is unknown;explicit NULL-safe equality is true")
```

The comparison rules are visibly different. Choosing NULL-safe equality can intentionally match missing-value buckets, but it does not establish that two missing customer IDs denote the same customer. That semantic decision must precede the join implementation.

## Exercises

### Exercise 1: Build a multiplicity ledger before joining facts

Return key, fact_rows, dimension_rows, predicted_inner for the union of key buckets. Merge NULL diagnostic buckets explicitly, but predict zero ordinary-equality pairs for NULL. Order keys with NULL last.

**Expected result/shape:** A:(2,3,6), B:(1,1,1), C:(1,0,0), D:(1,0,0), E:(0,1,0), NULL:(1,1,0). Predicted inner rows sum to 7.

**Verify:** Assert the full ledger and its summed predicted count, including unmatched right-only E and the NULL bucket.

**Progressive hint:** Aggregate each side first, full-join the small count tables with NULL-safe equality, and apply the ordinary-match rule separately.

### Exercise 2: Verify equality pairs and quantify fanout

Return fact_id, dimension_row, amount_cents from an ordinary inner equality join. Compare both DataFrame and SQL pair identities with the seven literal expected pairs.

**Expected result/shape:** Facts 1 and 2 each match dimension rows 101,102,103; fact 3 matches 104. There are 7 pairs and the repeated joined amount totals 120, while matched fact amounts total 60.

**Verify:** Assert every pair, count 7 and pair-grain sum 120; compare a SQL join to the same pair list.

**Progressive hint:** Alias both sides to make the equality and projected identities unambiguous.

### Exercise 3: Count actual matches in a left join

Return fact_id, dimension_row from an ordinary left equality join. Preserve unmatched facts with a NULL right identity and inspect rows ordered by fact_id, dimension_row.

**Expected result/shape:** There are 10 output rows but 7 nonnull dimension_row values. Facts 4,5,6 each have one NULL-extended row; all six fact IDs remain represented.

**Verify:** Assert the complete ordered pair/NULL list and distinguish COUNT(*)10 from COUNT(dimension_row)7.

**Progressive hint:** Use the right-side identity to count real matches instead of counting the left-join placeholder.

### Exercise 4: Use semi and anti joins for membership

Return a pair of DataFrames containing matched and unmatched facts under ordinary equality, using left_semi and left_anti. Preserve fact rows without right-side fanout.

**Expected result/shape:** Semi IDs are[1,2,3], anti IDs[4,5,6]. Key A contributes two semi rows despite three dimension matches. Their bags reconcile to all six facts.

**Verify:** Assert both exact ID lists and their combined count 6; do not use distinct to repair an inner join.

**Progressive hint:** Membership operators retain left grain directly.

### Exercise 5: Make NULL-safe matching an explicit alternative

Return fact_id, dimension_row from an inner join using NULL-safe key equality. Compare with ordinary equality and explain why the extra pair is a policy change.

**Expected result/shape:** The ordinary seven pairs plus(5,105) produce eight pairs. No C or D match is invented.

**Verify:** Assert all eight ordered pairs and isolate the extra NULL-key pair.

**Progressive hint:** Scala uses <=> and PySpark uses eqNullSafe for the explicit comparison.

### Exercise 6: Gate enrichment on a reviewed unique dimension

Reject a dimension unless key is nonnull and unique, then left-enrich facts with label while retaining fact_id and amount_cents. The supplied reviewed dimension rows 103,104,106 are the explicit accepted fixture; do not invent an arbitrary duplicate winner.

**Expected result/shape:** The raw dimension fails. The reviewed subset yields six facts, total 210, and labels alpha 3, alpha 3, beta, NULL, NULL, NULL for IDs 1..6.

**Verify:** Catch raw-dimension rejection, assert every enriched row and reconcile count 6, total 210.

**Progressive hint:** Compare total dimension count with countDistinct(key) before the join; NULL keys also break equality.

## Common pitfalls

If a joined amount doubles, calculate key multiplicities before adding distinct. If COUNT(*) suggests a right match for every left row, inspect the right identity and NULL-extended placeholders. If semi/anti results disagree with an inner-join-derived membership set, check the NULL equality policy. If a NULL-safe join merges unknown entities, review whether NULL denotes a category or missing identity. If a duplicate dimension has conflicting labels, obtain a valid business/version rule or reject it; broadcasting the ambiguity only makes the wrong join faster.

## Self-check

Explain the contract of `multiplicity` / `multiplicity` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 join types](https://spark.apache.org/docs/4.0.1/sql-ref-syntax-qry-select-join.html).

- [Spark 4.0.1 NULL semantics](https://spark.apache.org/docs/4.0.1/sql-ref-null-semantics.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-016: Join cardinality, fanout, semi joins and NULL-safe keys.
Read courses/scala-spark/guides/spark-016.md and courses/scala-spark/lessons/spark-016.scala;the paired sources are courses/scala-spark/lessons/spark-016.scala and courses/scala-spark/lessons/spark-016.py.
Direct prerequisites: spark-015. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
