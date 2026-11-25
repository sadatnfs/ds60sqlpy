# spark-023: Broadcast joins, statistics and strategy evidence

Joining 20,000 facts to a 20-row dimension is a textbook case for a broadcast join, but this lesson treats the textbook as a hypothesis. You will read the size estimate, watch the plan change when the automatic threshold is disabled or a hint is added, and check that the joined bag, with weighted total 839,916, never changes with the strategy.

## Level and prerequisites

Intermediate; approximately 105 minutes. Direct prerequisites: `spark-022`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-023.scala) and [PySpark](../lessons/spark-023.py).

Open the [explained solutions](../solutions/spark-023_solutions.md) after an attempt.

The first worked example counts the dimension's distinct keys and prints `Known finite build side: 20 unique keys`. The second computes the weighted total independently of any Spark join and prints `Independent weighted-total oracle=` followed by 839916 (the Scala pad prints `oracle=839916`). That number is the target every join strategy in the exercises has to reproduce.

## Learning objectives

- Choose and verify a join strategy without turning a hint into a correctness assumption.
- Compare the dimension's estimated size with the 10,485,760-byte automatic threshold, then produce a shuffled plan with the threshold at -1 and a `BroadcastHashJoin` plan with an explicit hint, proving with `exceptAll` in both directions that the rows are identical.
- Explain why a broadcast hint is not honored for the full outer join in Exercise 5, and gate any broadcast candidate on a key-uniqueness check and a row bound that reject a duplicated key 0 or a 101-row table.

## Vocabulary and concepts

- **Broadcast build side:** The bounded relation distributed so each worker can build local lookup state for eligible joins.

- **Size estimate:** Optimizer metadata about expected relation size; it may be stale, incomplete or different from actual in-memory hash-table size.

- **Automatic threshold:** The configured size limit influencing automatic broadcast selection, subject to strategy eligibility and available statistics.

- **Join hint:** A requested strategy attached to a relation; it cannot make an unsupported join type eligible or repair logical multiplicity.

- **Strategy evidence:** The observed physical join operator in the actual configured plan, checked separately from the relational result.

The fixture joins 20000 fact identities to a 20-row dimension with one row per key. Each fact key is fact_id modulo 20, so every fact has exactly one dimension match. The fact amount cycles from one through seven and the dimension factor is key plus one. The independent arithmetic totals are 79997 for amount and 839916 for amount times factor. These values are the correctness anchor for every strategy experiment.

Broadcasting can avoid shuffling the large side for an eligible equijoin by making the small build relation available to workers. The small relation must still be materialized and distributed, and each worker needs memory for its representation. A 20-row range is safely bounded for this local teaching fixture. A production relation called dimension can still contain millions of rows or wide payloads; its name does not establish that broadcasting is sensible.

The optimizer uses statistics and configuration to choose a strategy. This lesson records the optimized plan estimate of the dimension and a deliberately set 10 MiB automatic threshold. The estimate is inspected through classic Spark plan metadata, which is a version-specific diagnostic boundary. It is not substituted for the measured row-count/uniqueness gate or treated as a precise prediction of hash-table memory. Missing statistics can make an automatic decision unexpectedly conservative or unsafe.

The automatic case records its observed operator with broadcasting enabled. The next case disables automatic broadcasting by setting the threshold to -1 while AQE stays disabled, then builds a fresh query. Under this controlled setup the join should use a shuffle-capable strategy rather than BroadcastHashJoin. Exact result metrics remain unchanged. Reusing an already-planned DataFrame after changing configuration could test an old decision, so every comparison builds a new join after applying its settings.

The explicit broadcast hint is then applied with automatic broadcasting still disabled. For this supported inner equijoin, the plan uses BroadcastHashJoin and BroadcastExchange. The hint requests a strategy; it does not change equality semantics, validate uniqueness or prove enough production memory exists. The reference compares the full identity/measure relation using distributed exceptAll in both directions so duplicate-sensitive parity is checked without collecting 20000 rows onto the driver.

Not every join type supports every physical strategy. A full outer equijoin with a broadcast hint on this dimension cannot use the same broadcast hash join strategy. Spark may warn that the hint is unsupported and choose another valid strategy. The lesson checks the observed absence of BroadcastHashJoin and keeps the relational output oracle. A hint being ignored is not automatically a query correctness failure; it is evidence that strategy eligibility must be considered before assuming a requested plan.

The full-outer fixture happens to produce the same rows as the inner join because all 20 dimension keys are represented among the facts and every fact key exists in the dimension. This is a controlled property of the data, not a general equivalence of join types. Add a right-only dimension key or an unmatched fact and the result relationship changes. The explanation preserves that limitation so the strategy example does not teach an incorrect relational rewrite.

The final bounded-broadcast gate requires a batch relation, at most 100 rows, a nonnull unique key and an estimated size within 1 MiB before attaching the hint. Row validation uses a limit-plus-one count to reject an oversized candidate, then validates identities on the bounded population. The estimate remains only one signal. A production gate would also consider actual encoded sizes, peak build memory, concurrent queries and worker memory budgets. A successful 20-row broadcast on `local[2]` does not certify those production conditions.

The lesson deliberately omits elapsed-time superiority claims. Tiny data, compilation and scheduler startup can dominate. Physical strategy evidence explains what was selected; duplicate-sensitive output comparison explains whether the choice preserved semantics. These are useful results even when neither establishes a meaningful speedup.

## Supplied local fixture

Facts come from `spark.range(0, 20000, 1, 4)` renamed to `fact_id`, with `key = fact_id % 20` and `amount = fact_id % 7 + 1`. The dimension has keys 0 to 19 in two partitions with `factor = key + 1`, so every fact matches exactly one dimension row. The session pins the broadcast threshold at 10,485,760 bytes and prefers sort-merge joins, so any change of strategy comes from what an exercise sets.

```scala
import org.apache.spark.sql.functions._

val facts = spark
  .range(0L, 20000L, 1L, 4)
  .withColumnRenamed("id", "fact_id")
  .withColumn("key", col("fact_id") % 20L)
  .withColumn("amount", col("fact_id") % 7L + 1L)
val dimension =
  spark.range(0L, 20L, 1L, 2).withColumnRenamed("id", "key").withColumn("factor", col("key") + 1L)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
spark.conf.set("spark.sql.join.preferSortMergeJoin", "true")
```

```python
from pyspark.sql import functions as F

facts = (
    spark.range(0, 20000, 1, 4)
    .withColumnRenamed("id", "fact_id")
    .withColumn("key", F.col("fact_id") % 20)
    .withColumn("amount", F.col("fact_id") % 7 + 1)
)
dimension = (
    spark.range(0, 20, 1, 2).withColumnRenamed("id", "key").withColumn("factor", F.col("key") + 1)
)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
spark.conf.set("spark.sql.join.preferSortMergeJoin", "true")
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(facts.count() == 20000L && dimension.count() == 20L)
assert(dimension.select("key").distinct().count() == 20L)
println("Known finite build side: 20 unique keys")
```

```python
assert facts.count() == 20000 and dimension.count() == 20
assert dimension.select("key").distinct().count() == 20
print("Known finite build side: 20 unique keys")
```

The small build relation is a measured fixture property. A unique dimension key prevents fanout, but it does not itself choose a join strategy. A production dimension needs a fresh bound and identity check rather than inheriting this fixture assurance.

### Worked example 2

```scala
val total = (0L until 20000L).map(i => (i % 7L + 1L) * (i % 20L + 1L)).sum
assert(total == 839916L)
println("Independent weighted-total oracle=" + total)
```

```python
total = sum((i % 7 + 1) * (i % 20 + 1) for i in range(20000))
assert total == 839916
print("Independent weighted-total oracle=", total)
```

This bounded driver arithmetic uses the declared generation rule and does not call Spark join or aggregation. It supplies an independent measure oracle so two strategies sharing the same faulty join expression cannot pass merely by agreeing with each other.

## Exercises

### Exercise 1: Inspect statistics and the automatic threshold separately

Return the optimized-plan size estimate for dimension as a nonnegative integer, and record the configured automatic broadcast threshold and actual dimension row count.

**Expected result/shape:** A positive finite estimate below 10485760 bytes, threshold 10485760 and actual row count 20. The estimate is not a peak-memory measurement.

**Verify:** Assert the finite estimate range and print estimate, threshold, rows and Spark version as separate fields.

**Progressive hint:** The classic JVM optimized plan exposes stats.sizeInBytes; retain arbitrary integer precision when inspecting it.

### Exercise 2: Observe the automatic plan and verify its relational output

Build an ordinary inner equality join on key, projecting fact_id, key, amount, factor. Execute logical metrics and record the physical plan chosen with the declared threshold.

**Expected result/shape:** `Metrics(20000, 20000, 79997, 839916)`. The observed plan identifies a join strategy and is printed with current threshold.

**Verify:** Assert all metrics and a join operator marker. Report the observed automatic strategy without treating a default as a universal guarantee.

**Progressive hint:** Use using-key equality to avoid duplicate key columns; keep fact identity in the projection.

### Exercise 3: Disable automatic broadcasting for a fresh comparison

Set automatic broadcast threshold to -1, build a fresh ordinary join and record its plan with AQE disabled. Keep the logical result contract.

**Expected result/shape:** Same metrics as automatic. No BroadcastHashJoin in this fresh query under AQE false and threshold -1.

**Verify:** Assert all four metrics, the disabled setting and observed absence of BroadcastHashJoin.

**Progressive hint:** Changing a setting after a query has already been planned may not create the comparison you intended.

### Exercise 4: Request an eligible explicit broadcast and reconcile bags

Apply broadcast to the dimension for an inner equality join while automatic threshold remains-1. Project the same columns and compare duplicate-sensitive output with the ordinary join in both directions.

**Expected result/shape:** BroadcastHashJoin and BroadcastExchange appear. Both exceptAll differences are empty and logical metrics remain exact.

**Verify:** Assert the two operator markers, all metrics and both bag differences.

**Progressive hint:** A broadcast hint can override the automatic size threshold for an eligible strategy, but cannot prove key uniqueness.

### Exercise 5: Observe an unsupported hint without changing the business result

Request a broadcast dimension in a full outer equality join and inspect the chosen plan. Explain why this fixture still has the same output rows as the inner join.

**Expected result/shape:** No BroadcastHashJoin for this unsupported full-outer hash strategy. Metrics remain `(20000, 20000, 79997, 839916)` because both key domains are fully covered.

**Verify:** Assert the observed absence of BroadcastHashJoin and exact output metrics; report a hint warning if emitted rather than hiding it.

**Progressive hint:** Strategy eligibility depends on join type. Equal results here rely on complete key coverage, not a general inner/full-outer equivalence.

### Exercise 6: Gate a broadcast candidate on explicit bounded evidence

Reject streaming inputs, more than 100 rows, missing/duplicate keys, or an estimated size outside (0, 1 MiB]. Return the bounded dimension with a broadcast hint only after those checks.

**Expected result/shape:** The 20-row dimension passes; the same dimension with a duplicate key and a 101-row candidate fail. No unbounded input is collected or materialized by the gate.

**Verify:** Assert accepted logical join metrics and explicit rejection for duplicate and row-budget cases.

**Progressive hint:** Check isStreaming first, then limit 101/count for the row budget. Validate identity and estimates only after that finite bound.

## Common pitfalls

Do not broadcast a relation just because it is named dimension. Do not treat a hint as a guarantee for every join type or as a uniqueness check. Statistics can be missing or stale, and in-memory build structures may exceed the estimated bytes. Disable or account for AQE when isolating static planning. Keep full-output reconciliation separate from the plan comparison. This local demonstration establishes strategy behavior and logical parity, not a cluster speedup or a safe production memory limit.

## Self-check

- The automatic plan contains a join, but Exercise 2 does not require it to be a broadcast join. Why is the threshold comparison in Exercise 1 not enough to predict the strategy?
- With the threshold at -1, the plan has no `BroadcastHashJoin` and AQE is off. Why does the lesson switch AQE off before making that claim about the plan?
- Exercise 4 checks `exceptAll` in both directions. Describe an incorrect hinted result that a one-directional check would accept.
- The broadcast gate rejects a dimension in which key 0 appears twice. What would that duplicate do to the 20,000-row join and to its 839,916 total?

## Next step

Go on to [spark-024: AQE, skew and bounded salting experiments](spark-024.md). Broadcasting helps when one side is small; the next lesson keeps both sides in a shuffle join and confronts the case where 90 percent of the facts share a single key.

## Primary sources and official APIs

- [Spark 4.3.0 statistics, broadcast thresholds and hint eligibility](https://spark.apache.org/docs/4.3.0/sql-performance-tuning.html)

- [Spark 4.3.0 join syntax](https://spark.apache.org/docs/4.3.0/sql-ref-syntax-qry-select-join.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-023: Broadcast joins, statistics and strategy evidence.
Read courses/scala-spark/guides/spark-023.md and courses/scala-spark/lessons/spark-023.scala; the paired sources are courses/scala-spark/lessons/spark-023.scala and courses/scala-spark/lessons/spark-023.py.
Direct prerequisites: spark-022. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
