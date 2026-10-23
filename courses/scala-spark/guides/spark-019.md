# spark-019: Windows, ties and deterministic deduplication

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-018`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-019` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-019.scala) and [PySpark learner](../lessons/spark-019.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-019_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-019_solution.scala) and [PySpark reference](../solutions/spark-019_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Choose a stable winner per key without relying on partition arrival order.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Window partition:** The logical group within which a window function evaluates; it is separate from an execution partition on a worker.

- **Complete ordering:** A sequence of ordering fields and NULL rules that uniquely orders the candidate rows relevant to the decision.

- **Winner policy:** The explicit rule selecting one row per entity, such as latest known event_time then largest unique event_id.

- **Peer group:** Rows equal on the window ordering expressions; a RANGE frame can include all peers together.

- **Row-relative frame:** A ROWS frame defined by positions in the specified ordering, not elapsed time or a guarantee of causal availability.

Deduplication is often a business selection problem disguised as a storage cleanup. The fixture has eight distinct event identities for three entities. We want the latest known event for each entity and, when timestamps tie, the largest event_id. This rule produces 3,6,8. The event ID is a declared deterministic tie-breaker, not evidence that it represents a later physical occurrence than a lower ID with the same timestamp.

A window specification separates grouping from ordering. partitionBy(entity) defines which rows compete with each other. orderBy(event_time descending with NULL last, event_id descending) determines their priority. row_number assigns unique positions within that order, and filtering rank 1 selects one winner. The operation does not remove legitimate input events from the original dataset; it creates a new selected-state relation at entity grain.

Uniqueness is a prerequisite for the final ordering to be complete. If the same event_id were repeated with conflicting fields, ordering by event_time and event_id could still tie on every sort expression. Choosing one would then require a further source-version policy or rejecting the conflict. The first task rejects duplicate identities before ranking. It also requires known positive IDs and known entity keys. Missing timestamps are allowed under the explicit last-priority policy, so entity C keeps its known-time event 8 over missing-time event 7.

A deterministic result is not demonstrated by hoping one execution changes when repartitioned. An incomplete order can happen to produce the same answer many times. The diagnostic task therefore identifies the set of top-time candidates without an ID tie-breaker: entity A has 2 and 3, entity B has 5 and 6, and C has 8. The multiple admissible candidates prove the policy is under-specified even if a particular engine run repeatedly chooses the same row. The reference never asserts that a nondeterministic output must change on demand.

The complete winner implementation is checked under several partition counts and against an equivalent SQL row_number expression. Literal winners remain the primary oracle. DataFrame/SQL agreement alone could hide the same mistaken descending/ascending policy. No performance conclusion is drawn from the tiny repartition checks; they exercise robustness of the logical selection rule.

Window frames answer a different question from rank ordering. A cumulative ROWS frame with a complete chronological order adds one occurrence at a time. A RANGE frame ordered only by event_time reaches all peers with that timestamp at once. EntityA therefore has cumulative ROWS totals 10,30,60 but time-peer RANGE totals 10,60,60. Neither is wrong in isolation. One reports progress through an occurrence ordering; the other reports all events through a clock value.

A final event-ID sort for display is separate from the window order. The learner sees a stable table by event_id, even though a chronological window for entity C places event 8 before the missing-time event 7. Confusing those two orderings makes lag and running totals appear inconsistent. Retain the ordering specification beside any window-derived measure.

Lag uses the prior row in the declared sequence. Two tied-time events can therefore have a zero-second gap, and a null event time can have a known prior event ID but no computable elapsed-time difference. A complete ordering makes these features reproducible; it does not make them causally available at a historical prediction cutoff. Strictly prior-time features and availability-time filters require additional contracts. This chapter keeps deterministic selection, frame semantics and temporal identification distinct while showing how they interact in one small dataset.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.expressions.Window

val schema = StructType(Seq(StructField("event_id",LongType,false),StructField("entity",StringType,false),StructField("time_text",StringType,true),StructField("amount",LongType,false)))
val events = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"A","2024-01-01 00:00:00",10L),Row(2L,"A","2024-01-01 00:01:00",20L),Row(3L,"A","2024-01-01 00:01:00",30L),Row(4L,"B","2024-01-01 00:00:00",40L),Row(5L,"B","2024-01-01 00:02:00",50L),Row(6L,"B","2024-01-01 00:02:00",60L),Row(7L,"C",null,70L),Row(8L,"C","2024-01-01 00:01:00",80L)),2),schema).withColumn("event_time",to_timestamp(col("time_text")))
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pyspark.sql import Window

schema = StructType([StructField("event_id",LongType(),False),StructField("entity",StringType(),False),StructField("time_text",StringType(),True),StructField("amount",LongType(),False)])
events = spark.createDataFrame([(1,"A","2024-01-01 00:00:00",10),(2,"A","2024-01-01 00:01:00",20),(3,"A","2024-01-01 00:01:00",30),(4,"B","2024-01-01 00:00:00",40),(5,"B","2024-01-01 00:02:00",50),(6,"B","2024-01-01 00:02:00",60),(7,"C",None,70),(8,"C","2024-01-01 00:01:00",80)],schema=schema).withColumn("event_time",F.to_timestamp("time_text"))
```

## Worked example / walkthrough

### Worked example 1

```scala
val group = events.filter(col("entity") === "A")
assert(group.count() == 3L && group.select("event_time").distinct().count() == 2L)
println("Three event identities share only two timestamp values")
```

```python
group = events.filter(F.col("entity")=="A")
assert group.count() == 3 and group.select("event_time").distinct().count() == 2
print("Three event identities share only two timestamp values")
```

The timestamp cannot uniquely order these occurrences by itself. Counting unique times alongside event count exposes the missing tie-breaker before any row_number is computed. An equal timestamp is not evidence of an identical event payload.

### Worked example 2

```scala
val counts = events.dropDuplicates("entity").count()
assert(counts == 3L)
println("dropDuplicates guarantees entity cardinality here; it does not state a newest-row policy")
```

```python
counts = events.dropDuplicates(["entity"]).count()
assert counts == 3
print("dropDuplicates guarantees entity cardinality here; it does not state a newest-row policy")
```

The example intentionally checks only the cardinality promised by this use of dropDuplicates. It does not print a particular survivor as the correct winner. Selecting newest state requires the explicit ordering and rank policy implemented later.

## Exercises

### Exercise 1: Validate identities before defining a winner

Reject an input unless event_id is known, positive and unique and entity is known. Allow missing event_time under the declared last-priority policy. Return Unit/None on success.

**Expected result/shape:** The eight-event fixture passes; adding another copy of event 1 fails. Missing-time event 7 is allowed.

**Verify:** Assert normal acceptance and explicit rejection after unioning a duplicate identity.

**Progressive hint:** Compare count(*) with countDistinct(event_id), and check domain validity separately.

### Exercise 2: Rank all candidates with an explicit NULL rule

Add candidate_rank using row_number per entity, descending event_time with NULL last, then descending event_id. Keep all eight rows.

**Expected result/shape:** Ranks by event_id are 1:3,2:2,3:1,4:3,5:2,6:1,7:2,8:1.

**Verify:** Assert the full ID/rank table and input count 8.

**Progressive hint:** Use desc_nulls_last for time and a separate descending identity tie-breaker.

### Exercise 3: Select stable winners across physical layouts

Validate candidates, rank them and retain rank 1. Compare winner IDs after repartitioning to 1,3 and 4 partitions, then compare an equivalentSQL row_number query.

**Expected result/shape:** Every case yields event IDs[3,6,8], one per entity. SQL returns the same literal winners.

**Verify:** Assert exact winners in every layout and SQL, not just equal row counts.

**Progressive hint:** Repartition changes execution layout; complete window ordering controls the logical decision.

### Exercise 4: Prove why timestamp-only ordering is incomplete

Use dense_rank ordered only by descending event_time with NULL last, returning all rank 1 candidates. Report the candidate IDs rather than choosing an arbitrary winner.

**Expected result/shape:** Top-time candidates[2,3,5,6,8]. Entities A and B each have two admissible candidates under the incomplete rule.

**Verify:** Assert the five candidate identities and the two ambiguous entity keys. Do not require unstable executions to change output.

**Progressive hint:** dense_rank preserves peers at the highest time, exposing the missing decision criterion.

### Exercise 5: Distinguish occurrence totals from time-peer totals

Return event_id, rows_total, peer_total. ROWS uses ascending time NULL last then ID and an unbounded-preceding/current-row frame. RANGE uses only ascending time NULL last over the same cumulative boundary.

**Expected result/shape:** By ID:1(10,10),2(30,60),3(60,60),4(40,40),5(90,150),6(150,150),7(150,150),8(80,80).

**Verify:** Assert all eight tuples, especially tied IDs 2/3 and the missing-time event 7.

**Progressive hint:** Adding event_id to the RANGE ordering would redefine peers and defeat this comparison.

### Exercise 6: Interpret lag without claiming strict temporal availability

Using ascending time NULL last then event_id, return event_id, previous_id, gap_seconds. Lag the event identity and time, then subtract epoch seconds.

**Expected result/shape:** 1(NULL, NULL),2(1,60),3(2,0),4(NULL, NULL),5(4,120),6(5,0),7(8, NULL),8(NULL, NULL).

**Verify:** Assert the complete identity/gap rows and explain zero gaps and the known previous ID with unknown duration.

**Progressive hint:** Lag refers to a row in the declared sequence. A stable ID tie-breaker does not turn an equal-time event into a strictly earlier observation.

## Common pitfalls

Do not assume sort before dropDuplicates defines its survivor contract. Do not omit an identity tie-breaker and test nondeterminism by requiring a random change. Do not confuse window partitionBy with an executor partition count. Specify ROWS or RANGE when peer behavior matters, and preserve NULL ordering explicitly. An event-ID tie-breaker encodes a choice; if the business requires a different version or source priority, replace the policy and its oracle together.

## Self-check

Explain the contract of `validateCandidates` / `validate_candidates` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 window syntax and frames](https://spark.apache.org/docs/4.0.1/sql-ref-syntax-qry-select-window.html)

- [Spark 4.0.1 dropDuplicates](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.dropDuplicates.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-019: Windows, ties and deterministic deduplication.
Read courses/scala-spark/guides/spark-019.md and courses/scala-spark/lessons/spark-019.py;the paired sources are courses/scala-spark/lessons/spark-019.scala and courses/scala-spark/lessons/spark-019.py.
Direct prerequisites: spark-018. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
