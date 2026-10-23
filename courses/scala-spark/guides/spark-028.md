# spark-028: Capstone: a skewed join with correctness and cost evidence

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 150 minutes. Direct design prerequisites: `spark-027`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-028` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-028.scala) and [PySpark learner](../lessons/spark-028.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-028_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-028_solution.scala) and [PySpark reference](../solutions/spark-028_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Deliver a defensible batch-optimization change backed by a reference result and bounded measurements.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Acceptance ledger:** A row-preserving classification of source records into accepted data and explicit rejection reasons.

- **Approved dimension contract:** A reviewed subset with one known row per key, selected by an explicit business field rather than arbitrary deduplication.

- **Optimization baseline:** A correct reference implementation whose output is fixed before experimenting with physical strategy.

- **Evidence packet:** A bounded record of configuration, logical totals, key frequencies, plans and observed resource metrics tied to the compared runs.

- **Rollback switch:** A controlled choice that restores the prior correct strategy while preserving the same input and output contract.

This capstone starts with a product that is not ready to optimize. The source contains 2002 records:2000 valid fact identities, a missing fact identity and a negative amount. Two hundred accepted facts have unknown amounts. The raw dimension contains two versions for hot key 0, only one marked approved. Joining the raw dimension would multiply 1600 hot facts and make a fast query compute the wrong business relation.

The first responsibility is to define accepted and rejected populations. Missing identity has precedence over the amount rule, and a negative known amount is rejected. An unknown amount is allowed and retained as NULL. The ledger must keep every source_id so accepted 2000 plus rejected 2 equals raw 2002. Accepted fact IDs are unique, and known amounts number 1800. No fill-with-zero operation is permitted to make completeness look better.

The dimension is repaired by an explicit approved flag supplied in the fixture. Key 0 factor 2 is approved; its older factor 1 row is not. This is a business input contract, not a recommendation to choose an arbitrary maximum version or call dropDuplicates. After filtering approved rows, the code requires known unique keys. A negative control adds another approved row for key 0 and must fail before any optimization path runs.

The accepted key-frequency ledger has 1600 rows for key 0 and 100 for each key 1 through 4. Key 5 exists only on the reviewed dimension and does not create a fact. The 80-percent hot-key fraction explains why a shuffle join might concentrate work, but it does not justify skipping the dimension gate. Data correctness and physical skew are distinct issues that happen to appear in the same workload.

The baseline is an ordinary inner equality join with automatic broadcasting and AQE disabled. The candidate strategy broadcasts the reviewed six-row dimension. Broadcasting is a deliberate choice here because the build side is finite and tiny; the prior salting lesson provides an alternative when that condition does not hold. The candidate is not accepted on a timing comparison. It must preserve every projected fact occurrence and the exact per-key summary, including known-amount counts and nullable measures.

The independent golden summary is derived from the fixture formula rather than from one of the Spark join implementations. Key 0 has 1600 rows,1440 known amounts, total 5755 and weighted total 11510. Keys 1 through 4 have 100 rows each and the listed known-count/measure totals. Across all keys, the product has 2000 unique fact IDs,1800 known amounts, total 7196 and weighted total 17913. These exact quantities are checked before interpreting the physical plans.

A duplicate-sensitive distributed comparison then checks both directions of the full projected relation. It avoids collecting the whole fact product on the driver. Only the five-row key summary and one-row metric summary are collected, with fixed schemas and bounded output. This preserves a realistic discipline even though the generated input itself is small enough to fit locally.

The resource observation helper executes a summary query and then reads the actual executed exchange metric maps from that same query tree. This intentionally uses classic Spark 4.0.1 internals, as in the earlier shuffle lesson. Its records include operator names because a broadcast exchange's data-size metric and a shuffle exchange's data-size metric must not be casually added together and called remote network bytes. Missing metrics remain absent rather than becoming fabricated zeros.

The evidence packet recordsSpark version, local master, AQE state, automatic threshold, key-frequency ledger, the two observed join plans and their separate exchange maps. It does not claim measured peak memory, spill or cluster throughput when those were not collected. A lower exchange count or smaller serialized data amount can motivate a representative benchmark, but it is not by itself a complete production cost result.

Finally, the strategy switch is set back to the baseline. The rolled-back product must still satisfy the same exact oracle and bag comparison. Rollback changes execution policy, not the approved dimension or acceptance rules. If the candidate path fails at scale, the team should be able to return to a known correct implementation without undoing the data-quality contract that made either implementation trustworthy.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
val factSchema = StructType(Seq(StructField("source_id",LongType,false),StructField("fact_id",LongType,true),StructField("key",LongType,false),StructField("amount",LongType,true)))
val generated = (1L to 2000L).map { id => Row(id,id,if(id<=1600L) 0L else (id-1601L)%4L+1L,if(id%10L==0L) null else java.lang.Long.valueOf(id%7L+1L)) }
val rawFacts = spark.createDataFrame(spark.sparkContext.parallelize(generated ++ Seq(Row(2001L,null,0L,10L),Row(2002L,2001L,99L,-3L)),4),factSchema)
val dimSchema = StructType(Seq(StructField("key",LongType,false),StructField("factor",LongType,false),StructField("approved",BooleanType,false)))
val rawDimension = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(0L,1L,false),Row(0L,2L,true)) ++ (1L to 5L).map(k => Row(k,k+2L,true)),2),dimSchema)
val expectedMetrics = Map("rows"->2000L,"unique_facts"->2000L,"known_amounts"->1800L,"amount_total"->7196L,"weighted_total"->17913L)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
fact_schema = StructType([StructField("source_id",LongType(),False),StructField("fact_id",LongType(),True),StructField("key",LongType(),False),StructField("amount",LongType(),True)])
generated = [(i,i,0 if i<=1600 else (i-1601)%4+1,None if i%10==0 else i%7+1) for i in range(1,2001)]
raw_facts = spark.createDataFrame(generated+[(2001,None,0,10),(2002,2001,99,-3)],schema=fact_schema)
dim_schema = StructType([StructField("key",LongType(),False),StructField("factor",LongType(),False),StructField("approved",BooleanType(),False)])
raw_dimension = spark.createDataFrame([(0,1,False),(0,2,True)]+[(k,k+2,True) for k in range(1,6)],schema=dim_schema)
expected_metrics = {"rows":2000,"unique_facts":2000,"known_amounts":1800,"amount_total":7196,"weighted_total":17913}
```

## Worked example / walkthrough

### Worked example 1

```scala
val predictedRawJoinRows = 1600L*2L + 400L
assert(predictedRawJoinRows == 3600L)
println("Raw dimension multiplicity predicts3600 pairs for2000 accepted facts")
```

```python
predicted_raw_join_rows = 1600*2+400
assert predicted_raw_join_rows == 3600
print("Raw dimension multiplicity predicts3600 pairs for2000 accepted facts")
```

The multiplication is a grain diagnosis before execution strategy enters the discussion. Broadcasting the raw dimension could make these 3600 pairs arrive faster, but it would not turn them into the intended 2000-fact product.

### Worked example 2

```scala
val known = (1L to 2000L).filter(_%10L!=0L)
val amountTotal = known.map(_%7L+1L).sum
val weighted = known.map { i => val key = if(i<=1600L) 0L else (i-1601L)%4L+1L;(i%7L+1L)*(key+2L) }.sum
assert(known.size == 1800 && amountTotal == 7196L && weighted == 17913L)
println("Independent formula totals=" + amountTotal + "," + weighted)
```

```python
known = [i for i in range(1,2001) if i%10 != 0]
amount_total = sum(i%7+1 for i in known)
weighted = sum((i%7+1)*((0 if i<=1600 else (i-1601)%4+1)+2) for i in known)
assert len(known) == 1800 and amount_total == 7196 and weighted == 17913
print("Independent formula totals=",amount_total,weighted)
```

The oracle follows the input-generation and approved-factor rules without calling the Spark join or aggregate under review. Unknown amounts are excluded from known totals while remaining part of the accepted population, so completeness and value cannot be conflated.

## Exercises

### Exercise 1: Classify facts and reconcile the whole source population

Add reason using missing fact identity, negative known amount, then accepted precedence. Retain all source records; acceptedNULL amounts remain unknown.

**Expected result/shape:** Accepted 2000, rejected 2 with source 2001 missing_identity and 2002 negative_amount. Accepted unique fact IDs 2000 and known amounts 1800.

**Verify:** Assert every rejection identity/reason, source reconciliation and accepted uniqueness/completeness counts.

**Progressive hint:** A NULL amount does not satisfy a negative comparison and is explicitly allowed by this contract.

### Exercise 2: Select an approved unique dimension before tuning

Keep approved dimension rows, require at most 100 rows and known unique keys, then return key, factor. Reject a candidate with a second approved key 0 row.

**Expected result/shape:** Reviewed keys 0..5, factors 2..7, six rows. The conflicting approved candidate fails before joining.

**Verify:** Assert all six key/factor rows and the explicit duplicate-approved rejection.

**Progressive hint:** The approved flag is the supplied decision rule; arbitrary distinct/max selection is not authorized by the contract.

### Exercise 3: Produce the correct baseline and independent key summary

Build the ordinary equality join over accepted facts and reviewed dimension, projecting source_id, fact_id, key, amount, factor. Summarize per key with rows, known amounts, total amount and weighted total.

**Expected result/shape:** Key 0:(1600,1440,5755,11510);1:(100,100,401,1203);2:(100,80,321,1284);3:(100,100,398,1990);4:(100,80,321,1926).

**Verify:** Assert all five summary tuples and aggregate metrics 2000,2000,1800,7196,17913.

**Progressive hint:** COUNT(amount) and COUNT(*) answer different completeness questions.

### Exercise 4: Compare a bounded broadcast strategy with the same business contract

Broadcast the reviewed dimension for the same equality join and projection. Preserve all output occurrences using exceptAll in both directions against baseline.

**Expected result/shape:** Identical metrics and empty directional bag differences. The candidate plan containsBroadcastHashJoin.

**Verify:** Assert the full metric map, both distributed bag differences and the observed strategy marker.

**Progressive hint:** The dimension is already reviewed and bounded; the hint alone supplies neither property.

### Exercise 5: Assemble an honest bounded comparison receipt

Return version, master, AQE and automatic broadcast threshold as named fields. Attach key frequencies, the baseline/candidate plans and each observed summary-query exchange metric map.

**Expected result/shape:** Spark 4.0.1, local[2], AQEfalse, threshold-1; key 0 frequency 1600 and others 100. Both runs expose actual nonempty exchange observations. No peak-memory or throughput value is invented.

**Verify:** Assert controlled settings and frequency ledger, then print plans and separately labeled actual metric maps.

**Progressive hint:** Keep operator names with metrics because broadcast and shuffle data-size counters are not interchangeable network-byte totals.

### Exercise 6: Roll back execution policy without rolling back data quality

Choose baseline or broadcast using an explicit Boolean switch over the same accepted facts and reviewed dimension. Switch back to baseline and revalidate the complete product.

**Expected result/shape:** Both switch positions satisfy the same metric map and bag contract. The disabled position has no BroadcastHashJoin under the controlled configuration.

**Verify:** Assert golden metrics and bag equality after rollback, and inspect the restored baseline plan.

**Progressive hint:** Rollback chooses an execution implementation; it must not restore rejected facts or unapproved dimension versions.

## Common pitfalls

Do not optimize a fanout error or replaceNULL amounts with zero to simplify a checksum. Do not select dimension winners arbitrarily. Keep fact identity, known-value counts and measure totals in the acceptance contract. Do not collect an unbounded result to compare strategies. Internal metric names and plan access are pinned to classicSpark 4.0.1; keep their units and limitations visible. Rollback must preserve the repaired data contract even when it changes the physical implementation.

## Self-check

Explain the contract of `classifyFacts` / `classify_facts` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 join strategies and AQE](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)

- [Spark 4.0.1 monitoring](https://spark.apache.org/docs/4.0.1/monitoring.html)

- [Spark 4.0.1 duplicate-sensitive exceptAll](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.exceptAll.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-028: Capstone: a skewed join with correctness and cost evidence.
Read courses/scala-spark/guides/spark-028.md and courses/scala-spark/lessons/spark-028.scala;the paired sources are courses/scala-spark/lessons/spark-028.scala and courses/scala-spark/lessons/spark-028.py.
Direct prerequisites: spark-027. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
