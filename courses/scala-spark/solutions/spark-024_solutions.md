# spark-024: Explained paired reference solutions

Read the [guide](../guides/spark-024.md) and attempt one language first. The [Scala reference](spark-024_solution.scala) and [PySpark reference](spark-024_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Measure the key-frequency imbalance

Return ordered(key, n) counts for the fact relation. Derive total population and the hot-key fraction from this ledger.

**Expected:** Key 0 has 9000; keys 1..10 each 100. Total 10000 and hot fraction 0.9.

```scala
def keyFrequencies(facts: DataFrame): Seq[(Long,Long)] = {
  facts.groupBy("key").count().collect().toSeq.map(r => (r.getLong(0),r.getLong(1))).sortBy(_._1)
}
```

```python
def key_frequencies(facts):
    return sorted(tuple(r) for r in facts.groupBy("key").count().collect())
```

The full ledger distinguishes one hot key from a large but evenly distributed relation. Its reconciliation provides a baseline for both adaptive observations and explicit salting. A high fraction is a useful diagnosis of potential key concentration, not a complete measurement of task memory or elapsed time.

**Verification evidence:** Assert all 11 ledger rows and the exact population/fraction.

### Exercise 2: Establish a baseline join with exact identity conservation

Build an inner join with AQE disabled and broadcasting thresholds disabled, returning fact_id, key, amount, factor. Materialize the bounded result and compare every tuple with the generation formula.

**Expected:** 10000 unique fact identities, amount total 10000 and weighted total 15500. The baseline plan contains a join and is printed.

```scala
def baselineJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.sparkSession.conf.set("spark.sql.adaptive.enabled","false")
  facts.join(dimension,Seq("key"),"inner").select("fact_id","key","amount","factor")
}
```

```python
def baseline_join(facts, dimension):
    facts.sparkSession.conf.set("spark.sql.adaptive.enabled","false")
    return facts.join(dimension,on="key",how="inner").select("fact_id","key","amount","factor")
```

The complete relation establishes identity and measure conservation before physical changes. Broadcasting is disabled to expose the shuffle-skew mechanism for teaching; this is not a claim that disabling broadcast is best for this small dimension. The same projection must be retained in every comparison so helper fields cannot conceal a changed output grain.

**Verification evidence:** Assert all 10000 literal formula tuples and both totals before examining any optimization.

### Exercise 3: Observe an adaptive plan before and after execution

Build a freshAQE-enabled join with skew handling enabled, coalescing disabled, skew factor 2, threshold 1024 bytes and advisory size 16384 bytes. Capture the initial plan, materialize the same DataFrame and capture the final plan.

**Expected:** Initial/final text identifies AdaptiveSparkPlan; after materialization isFinalPlan=true. Every result tuple matches the baseline. Actual skew splitting is reported only if visible.

```scala
def adaptiveJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  val conf = facts.sparkSession.conf
  conf.set("spark.sql.adaptive.enabled","true")
  conf.set("spark.sql.adaptive.skewJoin.enabled","true")
  conf.set("spark.sql.adaptive.coalescePartitions.enabled","false")
  conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor","2")
  conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes","1024")
  conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes","16384")
  facts.join(dimension,Seq("key"),"inner").select("fact_id","key","amount","factor")
}
```

```python
def adaptive_join(facts, dimension):
    conf = facts.sparkSession.conf
    for key,value in {"spark.sql.adaptive.enabled":"true","spark.sql.adaptive.skewJoin.enabled":"true","spark.sql.adaptive.coalescePartitions.enabled":"false","spark.sql.adaptive.skewJoin.skewedPartitionFactor":"2","spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes":"1024","spark.sql.adaptive.advisoryPartitionSizeInBytes":"16384"}.items():
        conf.set(key,value)
    return facts.join(dimension,on="key",how="inner").select("fact_id","key","amount","factor")
```

Materializing the same DataFrame lets the reader inspect the final adaptive decision rather than a fresh initial plan from another query. Small thresholds make this a bounded experiment but do not guarantee a particular split. Full-result parity remains mandatory whether the adaptive mechanism changes the physical shape or leaves it unchanged.

**Verification evidence:** Assert adaptive finalization and full row parity; print both plans and the small demonstration thresholds.

### Exercise 4: Split the hot logical key with a deterministic helper

Add salt=fact_id modulo 4 only for key 0 and salt 0 otherwise. WithAQE disabled, compare eight-partition row-load ledgers by key and by(key, salt).

**Expected:** Hot salt buckets 0..3 each have 2250 rows; cold facts all have salt 0. Both physical ledgers reconcile to 10000, and the unsalted maximum is at least 9000.

```scala
def saltFacts(facts: DataFrame): DataFrame = {
  facts.withColumn("salt",when(col("key") === 0L,pmod(col("fact_id"),lit(4L))).otherwise(lit(0L)))
}
```

```python
def salt_facts(facts):
    return facts.withColumn("salt",F.when(F.col("key")==0,F.pmod("fact_id",F.lit(4))).otherwise(F.lit(0)).cast("long"))
```

The helper divides logical hot-key membership without duplicating facts. Exact bucket counts follow from consecutive fixture identities and a fixed modulo rule. Physical partition loads are observed separately because hash placement can merge multiple salted buckets. Row counts are a useful skew proxy here, but not a substitute for bytes, memory or duration metrics.

**Verification evidence:** Assert all four hot bucket counts and both reconciled ledgers; print actual salted loads without inventing perfect hash balance.

### Exercise 5: Replicate only the matching small-side hot row

Expand dimension key 0 to salts 0,1,2,3 and every other dimension key to salt 0. Retain factor and verify uniqueness on the composite key.

**Expected:** 14 dimension rows, with four key 0 variants and ten cold rows. Every(key, salt) pair is unique.

```scala
def expandDimension(dimension: DataFrame): DataFrame = {
  dimension.withColumn("salts",when(col("key") === 0L,array(lit(0L),lit(1L),lit(2L),lit(3L))).otherwise(array(lit(0L)))).withColumn("salt",explode(col("salts"))).drop("salts")
}
```

```python
def expand_dimension(dimension):
    return dimension.withColumn("salts",F.when(F.col("key")==0,F.array(*[F.lit(i).cast("long") for i in range(4)])).otherwise(F.array(F.lit(0).cast("long")))).withColumn("salt",F.explode("salts")).drop("salts")
```

Replication creates a match for every hot fact salt while preserving one dimension record per composite key. The original key is intentionally no longer unique on the expanded relation, so validating only that old key would misunderstand the new join contract. Replicating the small side is a cost of salting and must be budgeted rather than treated as free.

**Verification evidence:** Assert row count 14, distinct composite keys 14 and exact hot/cold salt populations.

### Exercise 6: Remove the physical helper and reconcile the business relation

Join salted facts to the expanded dimension on key and salt, then project only fact_id, key, amount, factor. Compare the complete result with baseline and adaptive variants.

**Expected:** All 10000 fact tuples remain exactly equal, with amount 10000 and weighted total 15500. Salt is absent from the final schema.

```scala
def saltedJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.join(dimension,Seq("key","salt"),"inner").select("fact_id","key","amount","factor")
}
```

```python
def salted_join(facts, dimension):
    return facts.join(dimension,on=["key","salt"],how="inner").select("fact_id","key","amount","factor")
```

Projecting away salt restores the declared business schema while the full bag comparison proves the helper strategy did not alter any fact occurrence or factor. The final plan explains how the salted relation is executed. Performance remains a separate question: dimension replication, additional expressions and hash collisions can offset the potential benefit of splitting a hot key.

**Verification evidence:** Assert exact canonical bag equality and final column names; report the salted plan and row-load evidence separately from any speed claim.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
