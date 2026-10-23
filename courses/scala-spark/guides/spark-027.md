# spark-027: Persistence lifecycle and cross-language golden tests

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-026`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-027` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-027.scala) and [PySpark learner](../lessons/spark-027.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-027_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-027_solution.scala) and [PySpark reference](../solutions/spark-027_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Cache only reusable work and test Scala/PySpark results with schema and bag-aware comparisons.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Persistence registration:** Marking a reusable relation for caching under a selected storage policy; this alone does not show its partitions have been computed.

- **Materialization:** An action that actually computes data; for a registered cache, it can populate stored partitions.

- **Cache reuse evidence:** A subsequent physical plan using an in-memory relation or scan, recorded separately from any timing claim.

- **Unpersist:** Releasing a registered cached relation and its stored blocks; blocking cleanup waits for block removal at that boundary.

- **Schema-aware oracle:** A comparison that checks field names and data types before comparing values, preventing coercion from hiding a type regression.

- **Bag-aware oracle:** A comparison preserving duplicate occurrence counts and NULL values rather than reducing a relation to a set.

The input deliberately contains repeated records. Entity 1/segmenta/amount 10 appears twice, and entity 4/segmentb/amount 20 appears twice. They are separate occurrences in this lesson, not accidental duplicates to remove. One amount is unknown, one is zero, one segment is unknown, and one amount is negative. The transformation keeps nonnegative or unknown amounts and doubles known amounts. Its golden result has seven rows and known doubled total 130.

Persistence is useful when several actions reuse expensive work and recomputation costs outweigh storage and management overhead. It is not automatically beneficial for every relation. The eight-row source makes no meaningful speed benchmark, but it supports exact observations of cache registration, materialization, reuse and cleanup. The reference runs two consumers and records a cache scan while keeping the logical result fixed.

Calling persist records a storage policy and makes the relation eligible for reuse. It does not by itself execute the full computation. A count action then materializes this tiny cached relation. A second aggregate reads its values, and a filtered consumer plan exposes InMemoryTableScan. Those observations are different evidence: registration is configuration, materialization is an action, and a cache-scan plan shows the selected reuse mechanism. None alone proves a production speedup or that every partition will remain resident forever.

The storage policy permits memory and disk in the owned local worker. Available memory, eviction and competing queries influence whether cached blocks remain in memory. Persistence also consumes resources that could have been used by another stage. An application should select a useful boundary, materialize only when reuse justifies it, and release it when its consumers are finished. Caching an already cheap result or a relation used once may add overhead rather than remove it.

Cleanup belongs in finally. The successful helper unpersists after its two consumers, and the failure helper injects an error after materialization to prove the same cleanup occurs on an exceptional path. The caller checks that no memory/disk storage policy remains registered afterward. Blocking unpersist is used to make this lifecycle observation explicit in the bounded demonstration. It does not constitute a durable checkpoint or survive application restart.

The cross-language oracle checks ordered field names and simple data types before duplicate-sensitive value comparison. A long entity_id column cast to string can display the same digits, but it violates the contract. Comparing only rendered CSV text or allowing implicit type coercion in a set operation could hide that regression. The schema check deliberately precedes exceptAll.

Value comparison treats the output as a bag. It accepts different row arrival orders and execution partitions, while preserving duplicate counts and NULL positions. A distinct result loses one entity 1 occurrence and one entity 4 occurrence. Its total and population change, but the bag difference explains the exact direction: zero unexpected distinct rows and two missing expected occurrences. A set-based comparator would incorrectly call these relations equal.

The same literal golden schema and seven rows are embedded in both standalone language programs and retained in the shared fixture ledger. Each implementation compares with that oracle independently. Agreement between Scala and Python would be insufficient if both applied an accidental DISTINCT or turned unknown amounts into zero. The negative controls prove that the validator catches both the type and multiplicity mistakes it claims to protect against.

The lesson's cache boundary is limited to one owned SparkSession and no external state. A checkpoint, an idempotent sink or a restartable publication manifest solves different problems. Persist/unpersist manages reusable computation inside the application; it does not promise recovery after process loss or exactly-once external delivery. Later chapters build those contracts separately.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.storage.StorageLevel

val schema = StructType(Seq(StructField("entity_id",LongType,false),StructField("segment",StringType,true),StructField("amount",LongType,true)))
val source = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"a",10L),Row(1L,"a",10L),Row(2L,"a",null),Row(3L,"b",0L),Row(4L,"b",20L),Row(4L,"b",20L),Row(5L,null,5L),Row(6L,"c",-5L)),2),schema)
val goldenSchema = StructType(Seq(StructField("entity_id",LongType,false),StructField("segment",StringType,true),StructField("doubled",LongType,true)))
val golden = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"a",20L),Row(1L,"a",20L),Row(2L,"a",null),Row(3L,"b",0L),Row(4L,"b",40L),Row(4L,"b",40L),Row(5L,null,10L)),2),goldenSchema)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pyspark import StorageLevel

schema = StructType([StructField("entity_id",LongType(),False),StructField("segment",StringType(),True),StructField("amount",LongType(),True)])
source = spark.createDataFrame([(1,"a",10),(1,"a",10),(2,"a",None),(3,"b",0),(4,"b",20),(4,"b",20),(5,None,5),(6,"c",-5)],schema=schema)
golden_schema = StructType([StructField("entity_id",LongType(),False),StructField("segment",StringType(),True),StructField("doubled",LongType(),True)])
golden = spark.createDataFrame([(1,"a",20),(1,"a",20),(2,"a",None),(3,"b",0),(4,"b",40),(4,"b",40),(5,None,10)],schema=golden_schema)
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(source.count() == 8L && source.select("entity_id","segment","amount").distinct().count() == 6L)
assert(golden.count() == 7L && golden.agg(sum("doubled")).first().getLong(0) == 130L)
println("Golden bag contains duplicates and unknown values deliberately")
```

```python
assert source.count() == 8 and source.select("entity_id","segment","amount").distinct().count() == 6
assert golden.count() == 7 and golden.agg(F.sum("doubled")).first()[0] == 130
print("Golden bag contains duplicates and unknown values deliberately")
```

The row count and distinct count differ because the fixture treats repeated records as meaningful occurrences. Any testing strategy that converts the data to a set before comparison would lose information needed to validate this contract.

### Worked example 2

```scala
val numeric = spark.sql("SELECT CAST(1 AS BIGINT) AS entity_id")
val textual = spark.sql("SELECT CAST('1' AS STRING) AS entity_id")
assert(numeric.schema("entity_id").dataType != textual.schema("entity_id").dataType)
println("Identical displayed digits can have different field types")
```

```python
numeric = spark.sql("SELECT CAST(1 AS BIGINT) AS entity_id")
textual = spark.sql("SELECT CAST('1' AS STRING) AS entity_id")
assert numeric.schema["entity_id"].dataType != textual.schema["entity_id"].dataType
print("Identical displayed digits can have different field types")
```

Schema is part of the product contract. A display representation can hide a type change that affects ordering, arithmetic and joins. The validator therefore checks types before a comparison operation has a chance to coerce values.

## Exercises

### Exercise 1: Transform without collapsing occurrences or unknowns

Keep rows whose amount is nonnegative or NULL, then return entity_id, segment, doubled=amount*2. Preserve duplicate occurrences and unknown values.

**Expected result/shape:** Seven rows, known total 130 and oneNULL doubled value. The negative entity 6 row is excluded.

**Verify:** Assert population, total and unknown count, then compare with the literal golden relation in later tasks.

**Progressive hint:** Ordinary amount>=0 would filter unknowns unless the missingness branch is explicit.

### Exercise 2: Define an ordered field/type contract

Return ordered(name, simple_type) pairs from the result schema. Compare with entity_id bigint, segment string, doubled bigint.

**Expected result/shape:** Exactly those three fields in that order. Casting entity_id to string changes the contract even when printed values look alike.

**Verify:** Assert the correct type list and a different list after the deliberate cast.

**Progressive hint:** Use schema metadata rather than inferring types from formatted output or the first nonNULL row.

### Exercise 3: Compare schemas before duplicate-sensitive values

Reject a schema mismatch first, then require both exceptAll differences to be empty. Accept a repartitioned correct result and reject the deliberate string-ID result.

**Expected result/shape:** Correct result passes in different physical layouts; string-ID candidate fails with a named schema contract error.

**Verify:** Assert acceptance for golden/repartitioned values and explicit schema rejection before a coercing bag comparison.

**Progressive hint:** exceptAll resolves columns by position; check the ordered schema contract before calling it.

### Exercise 4: Register, materialize, reuse and release one cached relation

Persist the supplied transformed relation with MEMORY_AND_DISK, materialize via count, reuse for a total and inspect a filtered consumer plan. Unpersist with blocking cleanup in finally.

**Expected result/shape:** Count 7, total 130, an InMemoryTableScan reuse marker, and no registered storage level after return.

**Verify:** Assert result values, cache-scan evidence and post-returnStorageLevel.NONE. Do not use a timing threshold.

**Progressive hint:** Registration precedes materialization; capture the reuse plan while the cache is still registered.

### Exercise 5: Release persistence when a consumer fails

Persist and materialize the relation, then raise an injected failure before a later consumer. Unpersist in finally and verify the original error reaches the caller.

**Expected result/shape:** The injected_after_materialize error is observed and storage level isNONE afterward. Correct uncached output still passes the golden oracle.

**Verify:** Assert the named failure, post-failure release and full golden equality on a subsequent computation.

**Progressive hint:** Cleanup must run on exceptions as well as the successful return path.

### Exercise 6: Demonstrate why set equality misses duplicate loss

Return directional exceptAll row counts after schema validation. Compare transformed.distinct with golden and require the golden validator to reject it.

**Expected result/shape:** Distinct has 5 rows; unexpected occurrences 0 and missing expected occurrences 2. The bag validator raises a named bag contract mismatch.

**Verify:** Assert(0,2), count 5 and the explicit negative-control rejection.

**Progressive hint:** Both duplicate groups lose one occurrence even though every distinct value still appears.

## Common pitfalls

Do not interpret persist registration as completed materialization or a cache scan as a measured speedup. Unpersist in finally on both success and failure. Do not use cache as a replacement for a checkpoint or publication protocol. Compare ordered schema fields before values, and preserve duplicate occurrence counts. Both languages agreeing is weaker than both languages matching the same independent golden contract and rejecting deliberate type/multiplicity mutations.

## Self-check

Explain the contract of `transform` / `transform` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 DataFrame persistence](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.persist.html)

- [Spark 4.0.1 unpersist lifecycle](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.unpersist.html)

- [Spark 4.0.1 exceptAll preserves duplicates](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.exceptAll.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-027: Persistence lifecycle and cross-language golden tests.
Read courses/scala-spark/guides/spark-027.md and courses/scala-spark/lessons/spark-027.scala;the paired sources are courses/scala-spark/lessons/spark-027.scala and courses/scala-spark/lessons/spark-027.py.
Direct prerequisites: spark-026. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
