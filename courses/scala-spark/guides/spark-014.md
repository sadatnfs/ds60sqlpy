# spark-014: Capstone: a reconciled local revenue report

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Beginner; approximately 120 minutes. Direct design prerequisites: `spark-013`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-014` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-014.scala) and [PySpark learner](../lessons/spark-014.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-014_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-014_solution.scala) and [PySpark reference](../solutions/spark-014_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Build and explain a small revenue product whose input, rejected and reported rows reconcile.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Ingestion occurrence:** One source record identified by source_row, which remains identifiable even when its business event_id is missing.

- **Quarantine:** A separate retained relation containing invalid records and explicit rejection reasons.

- **Accepted versus reportable:** Accepted records satisfy the source contract; reportable records additionally satisfy the chosen business eligibility rule, such as paid status.

- **Reconciliation:** Comparing identities, counts and measures across pipeline stages to detect hidden loss, multiplication or changed meaning.

This capstone builds a small data product rather than only one aggregate. The source has 12 occurrences identified by source_row. Ten have valid positive event IDs and supported paid/void statuses. One record has an unknown status and one has a missing event ID. The source-row identity lets both rejected records remain traceable even though one lacks a valid business key.

Validation precedes business filtering. A valid void record belongs in accepted data but does not contribute to paid revenue. An unknown status belongs in quarantine rather than being silently treated as void. Unknown amounts are permitted by this source contract and remain NULL; negative observed amounts are rejected. A real source could choose another policy, but it must be explicit and tested.

Reason precedence is deterministic: missing ID, invalid nonpositive ID, unknown status, then negative amount. A row with several defects receives the first reason. This is a fail-fast ledger, not an assertion that only one defect exists. If all reasons are operationally important, the classifier should produce an accumulating error structure rather than hiding them behind one label.

The accepted population has 10 events, including one void. Paid reporting therefore contains 9 events,7 observed amounts and 475 cents. Group C has one unknown amount and a NULL total; group E has one observed zero and a zero total. The NULL team is retained as an explicit group rather than dropped. These distinctions are part of the product contract, not formatting choices.

Two different A events both contain 100 cents. Projecting only team and amount then calling distinct removes one real event and changes paid totals to 8 rows,6 observed amounts and 375 cents. A report can therefore be numerically plausible while wrong by 100 cents. Preserving event_id through the row-level product prevents that shortcut from masquerading as duplicate handling.

The final publication gate checks the bounded source occurrence count, unique nonmissing source_row identities, unique positive accepted event IDs, and accepted-plus-quarantined conservation. Duplicate accepted event identity rejects the batch instead of choosing an arbitrary winner. It then produces the SQL summary and compares it with the same independent literal groups used for the DataFrame implementation.

The reference does not write a durable table or claim a transactional publication mechanism. It delivers a validated local report and its evidence. Later lessons add owned file output, restart and commit boundaries. This separation prevents a successful aggregate from being overclaimed as a production-ready pipeline or an exactly-once system.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val schema = StructType(Seq(
  StructField("source_row",LongType,false),StructField("event_id",LongType,true),
  StructField("team",StringType,true),StructField("amount_cents",LongType,true),
  StructField("status",StringType,true)))
val rows = Seq(
 Row(1L,1L,"A",100L,"paid"),Row(2L,2L,"A",null,"paid"),
 Row(3L,3L,"B",0L,"paid"),Row(4L,4L,null,50L,"paid"),
 Row(5L,5L,"B",150L,"void"),Row(6L,6L,"A",100L,"paid"),
 Row(7L,7L,"C",null,"paid"),Row(8L,8L,"B",25L,"paid"),
 Row(9L,9L,"E",0L,"paid"),Row(10L,10L,"D",200L,"paid"),
 Row(11L,11L,"A",10L,"mystery"),Row(12L,null,"A",5L,"paid"))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

schema = StructType([
    StructField("source_row", LongType(), False),StructField("event_id", LongType(), True),
    StructField("team", StringType(), True),StructField("amount_cents", LongType(), True),
    StructField("status", StringType(), True),
])
rows = [
    (1,1,"A",100,"paid"),(2,2,"A",None,"paid"),(3,3,"B",0,"paid"),(4,4,None,50,"paid"),
    (5,5,"B",150,"void"),(6,6,"A",100,"paid"),(7,7,"C",None,"paid"),(8,8,"B",25,"paid"),
    (9,9,"E",0,"paid"),(10,10,"D",200,"paid"),(11,11,"A",10,"mystery"),(12,None,"A",5,"paid"),
]
raw = spark.createDataFrame(rows, schema=schema)
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(raw.count() == 12L)
assert(raw.select("source_row").distinct().count() == 12L)
assert(raw.filter(col("event_id").isNull).select("source_row").first().getLong(0) == 12L)
println("Source occurrence identity survives a missing business ID")
```

```python
assert raw.count() == 12
assert raw.select("source_row").distinct().count() == 12
assert raw.filter(F.col("event_id").isNull()).select("source_row").first()[0] == 12
print("Source occurrence identity survives a missing business ID")
```

The source grain is an ingestion occurrence, not yet a validated event. source_row12 remains reportable in a rejection ledger even though its event_id is unknown. Counting only nonnull event IDs would incorrectly describe the source as 11 rows and conceal the missing-ID defect.

### Worked example 2

```scala
val unknown = raw.filter(col("amount_cents").isNull).select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq
val zero = raw.filter(col("amount_cents") === lit(0L)).select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq
assert(unknown == Seq(2L,7L) && zero == Seq(3L,9L))
println("Unknown amounts and observed zeros have different identities")
```

```python
unknown = [row.event_id for row in raw.filter(F.col("amount_cents").isNull()).select("event_id").orderBy("event_id").collect()]
zero = [row.event_id for row in raw.filter(F.col("amount_cents") == F.lit(0)).select("event_id").orderBy("event_id").collect()]
assert unknown == [2, 7] and zero == [3, 9]
print("Unknown amounts and observed zeros have different identities")
```

The two ID lists are disjoint and both meaningful. An unknown amount can remain an accepted event under the declared contract, while an observed zero must contribute to the known-value count. Coalescing both to zero before the report would erase this evidence.

## Exercises

### Exercise 1: Classify defects without dropping source occurrences

Add a nullable rejection_reason Column using the declared precedence: missing_id, invalid_id, unknown_status, negative_amount. Keep every source field and row. Unknown amounts are allowed; unknown statuses are not.

**Expected result/shape:** Source row 11 has unknown_status, row 12 has missing_id, and the other 10 reasons are NULL. All 12 source_row identities remain.

**Verify:** Assert the exact two(source_row, reason) pairs and the unchanged source count 12.

**Progressive hint:** Build a when/otherwise chain and include an explicit isNull status branch because NULL isin results are unknown.

### Exercise 2: Create the accepted event relation

Return source_row, event_id, team, amount_cents, status only for rows with no rejection reason. Preserve the valid void event and all accepted zero/NULL amounts.

**Expected result/shape:** Accepted event IDs are 1 through 10, with 10 rows. Event 5 remains accepted as void; IDs 2 and 7 remain accepted with unknown amounts.

**Verify:** Assert the complete accepted ID list, count 10, one void row and two NULL-amount rows.

**Progressive hint:** Use the validation result first; paid filtering belongs to a later business stage.

### Exercise 3: Retain a complete quarantine row

Return source_row, event_id, team, amount_cents, status, rejection_reason for rejected records, ordered by source_row when inspected. Keep the original values, including the missing event ID.

**Expected result/shape:** Rows are(11,11, A,10, mystery, unknown_status) and (12, NULL, A,5, paid, missing_id). Accepted and quarantined counts sum to 12.

**Verify:** Compare every quarantined field with literal expected rows and check count conservation independently.

**Progressive hint:** Filter the same classification in the complementary direction and preserve source_row as its occurrence identity.

### Exercise 4: Publish a NULL-aware paid summary

From accepted records, filter paid and group by team into team, rows, valued, total_cents. Count every event, only nonnull amounts, and the exact Long sum. Preserve a NULL team group and a NULL-only amount group.

**Expected result/shape:** Groups are A:(3,2,200), B:(2,2,25), C:(1,0, NULL), D:(1,1,200), E:(1,1,0), NULL:(1,1,50). Paid metrics are 9 rows,7 valued,475 cents.

**Verify:** Assert the full typed canonical group list and the global paid metrics against independent literals.

**Progressive hint:** COUNT(*) and COUNT(amount_cents) have different denominators; SUM over all NULL amounts remains NULL.

### Exercise 5: Expose projection-plus-distinct loss

Return a paid row-level projection retaining event_id, team, amount_cents. Compare it with the deliberately wrong team/amount distinct projection and explain the lost 100-cent event.

**Expected result/shape:** The correct projection has metrics(9,7,475); the wrong projection has(8,6,375). IDs 1 and 6 must both remain despite equal team/amount values.

**Verify:** Assert both metric tuples and verify that correct event IDs include 1 and 6 separately.

**Progressive hint:** Identity must survive before any deduplication policy can be evaluated.

### Exercise 6: Gate the SQL report on identity and conservation

Validate at most 100 unique nonmissing source_row occurrences, unique positive accepted event IDs, and accepted-plus-quarantine conservation before returning a SQL paid summary. Reject a duplicate accepted event ID. Compare SQL output to the same literal groups.

**Expected result/shape:** The base 12-row batch passes and matches all six golden groups. Appending source_row13 with a second event_id1 rejects publication instead of choosing a winner.

**Verify:** Assert base SQL parity and a real failure for the duplicate-ID extension; retain the validation failure rather than publishing a partial report.

**Progressive hint:** Use aggregate checks for source and accepted identities before creating the session-local paid view.

## Common pitfalls

If raw count becomes 11, check whether COUNT(event_id) was confused with COUNT(*). If accepted count becomes 9, look for paid filtering before validity accounting. If C and E both show zero totals, inspect premature NULL filling. If revenue drops by 100 after distinct, restore event identity. If a missing-ID row cannot be traced, use source occurrence identity in quarantine. If a duplicate event is silently chosen, define a correction/version policy or reject it; do not use partition arrival order as truth.

## Self-check

Explain the contract of `classified` / `classified` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 NULL-aware aggregates](https://spark.apache.org/docs/4.0.1/sql-ref-null-semantics.html).

- [Spark 4.0.1 DataFrame/SQL programming](https://spark.apache.org/docs/4.0.1/sql-getting-started.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-014: Capstone: a reconciled local revenue report.
Read courses/scala-spark/guides/spark-014.md and courses/scala-spark/lessons/spark-014.scala;the paired sources are courses/scala-spark/lessons/spark-014.scala and courses/scala-spark/lessons/spark-014.py.
Direct prerequisites: spark-013. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
