# spark-023: Explained paired reference solutions

Read the [guide](../guides/spark-023.md) and attempt one language first. The [Scala reference](spark-023_solution.scala) and [PySpark reference](spark-023_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Inspect statistics and the automatic threshold separately

Return the optimized-plan size estimate for dimension as a nonnegative integer, and record the configured automatic broadcast threshold and actual dimension row count.

**Expected:** A positive finite estimate below 10485760 bytes, threshold 10485760 and actual row count 20. The estimate is not a peak-memory measurement.

```scala
def estimatedBytes(frame: DataFrame): BigInt = {
  frame.queryExecution.optimizedPlan.stats.sizeInBytes
}
```

```python
def estimated_bytes(frame):
    return int(str(frame._jdf.queryExecution().optimizedPlan().stats().sizeInBytes()))
```

The optimizer estimate, the configuration threshold and the observed row count answer different questions. Keeping all three fields makes a planning discussion auditable. An unknown or huge estimate should not be coerced into a small integer by overflow, and even an accurate serialized estimate does not include all hash-table and concurrent-execution memory overhead.

**Verification evidence:** Assert the finite estimate range and print estimate, threshold, rows and Spark version as separate fields.

### Exercise 2: Observe the automatic plan and verify its relational output

Build an ordinary inner equality join on key, projecting fact_id, key, amount, factor. Execute logical metrics and record the physical plan chosen with the declared threshold.

**Expected:** Metrics(20000,20000,79997,839916). The observed plan identifies a join strategy and is printed with current threshold.

```scala
def ordinaryJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.join(dimension, Seq("key"), "inner").select("fact_id", "key", "amount", "factor")
}
```

```python
def ordinary_join(facts, dimension):
    return facts.join(dimension, on="key", how="inner").select("fact_id", "key", "amount", "factor")
```

The projected grain remains one fact because the dimension is unique and covers every fact key. The physical strategy is observed rather than inferred solely from the dimension count. A future optimizer or statistics change may alter the automatic operator while preserving the same correct relation, which is why the semantic metrics are checked independently.

**Verification evidence:** Assert all metrics and a join operator marker. Report the observed automatic strategy without treating a default as a universal guarantee.

### Exercise 3: Disable automatic broadcasting for a fresh comparison

Set automatic broadcast threshold to-1, build a fresh ordinary join and record its plan with AQE disabled. Keep the logical result contract.

**Expected:** Same metrics as automatic. No BroadcastHashJoin in this fresh query underAQEfalse and threshold-1.

```scala
def withoutAutomaticBroadcast(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.sparkSession.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
  ordinaryJoin(facts, dimension)
}
```

```python
def without_automatic_broadcast(facts, dimension):
    facts.sparkSession.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    return ordinary_join(facts, dimension)
```

A fresh query is built after the configuration change so the observation belongs to the intended controlled setup. Disabling automatic broadcast does not make the query incorrect; it changes the physical strategy space. AQE is kept off here because adaptive strategy conversion would introduce another decision mechanism covered in the next lesson.

**Verification evidence:** Assert all four metrics, the disabled setting and observed absence of BroadcastHashJoin.

### Exercise 4: Request an eligible explicit broadcast and reconcile bags

Apply broadcast to the dimension for an inner equality join while automatic threshold remains-1. Project the same columns and compare duplicate-sensitive output with the ordinary join in both directions.

**Expected:** BroadcastHashJoin and BroadcastExchange appear. Both exceptAll differences are empty and logical metrics remain exact.

```scala
def hintedJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.join(broadcast(dimension), Seq("key"), "inner").select("fact_id", "key", "amount", "factor")
}
```

```python
def hinted_join(facts, dimension):
    return facts.join(F.broadcast(dimension), on="key", how="inner").select(
        "fact_id", "key", "amount", "factor"
    )
```

The supported inner equijoin honors the requested broadcast strategy despite the automatic threshold being disabled. Duplicate-sensitive reconciliation verifies the entire projected relation without a large driver collect. A hint remains a physical request: if the dimension duplicated a key, the join would still multiply facts, and broadcasting would only execute that incorrect enrichment grain differently.

**Verification evidence:** Assert the two operator markers, all metrics and both bag differences.

### Exercise 5: Observe an unsupported hint without changing the business result

Request a broadcast dimension in a full outer equality join and inspect the chosen plan. Explain why this fixture still has the same output rows as the inner join.

**Expected:** No BroadcastHashJoin for this unsupported full-outer hash strategy. Metrics remain(20000,20000,79997,839916) because both key domains are fully covered.

```scala
def unsupportedHint(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts
    .join(broadcast(dimension), Seq("key"), "full_outer")
    .select("fact_id", "key", "amount", "factor")
}
```

```python
def unsupported_hint(facts, dimension):
    return facts.join(F.broadcast(dimension), on="key", how="full_outer").select(
        "fact_id", "key", "amount", "factor"
    )
```

A physical hash strategy that cannot represent the required outer semantics must be replaced by another valid strategy. The query result remains correct. Its equality with the inner result is a fixture-specific coverage fact: adding any unmatched key would invalidate that equivalence. The example teaches eligibility and evidence, not a recommendation to rewrite outer joins as inner joins.

**Verification evidence:** Assert the observed absence of BroadcastHashJoin and exact output metrics; report a hint warning if emitted rather than hiding it.

### Exercise 6: Gate a broadcast candidate on explicit bounded evidence

Reject streaming inputs, more than 100 rows, missing/duplicate keys, or an estimated size outside(0,1 MiB]. Return the bounded dimension with a broadcast hint only after those checks.

**Expected:** The 20-row dimension passes; the same dimension with a duplicate key and a 101-row candidate fail. No unbounded input is collected or materialized by the gate.

```scala
def boundedBroadcast(dimension: DataFrame): DataFrame = {
  require(!dimension.isStreaming, "Streaming input is not a bounded build table")
  val rows = dimension.limit(101).count()
  require(rows <= 100L, "Broadcast row budget exceeded")
  require(
    dimension.select("key").distinct().count() == rows && dimension
      .filter(col("key").isNull)
      .count() == 0L,
    "Build keys must be unique and known"
  )
  val estimate = estimatedBytes(dimension)
  require(estimate > 0 && estimate <= BigInt(1048576), "Broadcast estimate outside declared budget")
  broadcast(dimension)
}
```

```python
def bounded_broadcast(dimension):
    if dimension.isStreaming:
        raise ValueError("Streaming input is not a bounded build table")
    rows = dimension.limit(101).count()
    if rows > 100:
        raise ValueError("Broadcast row budget exceeded")
    if (
        dimension.select("key").distinct().count() != rows
        or dimension.filter(F.col("key").isNull()).count()
    ):
        raise ValueError("Build keys must be unique and known")
    if not 0 < estimated_bytes(dimension) <= 1048576:
        raise ValueError("Broadcast estimate outside declared budget")
    return F.broadcast(dimension)
```

The gate turns a casual hint into a declared finite input contract. Limit-plus-one detects a row-budget violation without collecting the whole relation to Python or Scala. Unique known keys protect enrichment grain, while the size estimate adds a separate planning bound. None of these checks certifies production peak memory or concurrency capacity; those require actual workload evidence and budgets.

**Verification evidence:** Assert accepted logical join metrics and explicit rejection for duplicate and row-budget cases.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
