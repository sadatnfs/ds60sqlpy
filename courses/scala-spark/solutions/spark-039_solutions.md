# spark-039: Explained paired reference solutions

Read the [guide](../guides/spark-039.md) and attempt one language first. The [Scala reference](spark-039_solution.scala) and [PySpark reference](spark-039_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Validate the generated skewed fixture

Require 20000 rows, IDs 0..19999,100 keys and total ID sum 199990000. Explain key 0 occurs 16040 times.

**Expected:** Exact population tuple 20000,20000,100,199990000;key 0 count 16040, other keys 40.

```scala
def fixtureMetrics(source: DataFrame): Seq[Long] = {
  val r = source.agg(count(lit(1)), countDistinct("id"), countDistinct("key"), sum("id")).first()
  Seq(r.getLong(0), r.getLong(1), r.getLong(2), r.getLong(3))
}
```

```python
def fixture_metrics(source):
    return tuple(
        source.agg(
            F.count(F.lit(1)), F.countDistinct("id"), F.countDistinct("key"), F.sum("id")
        ).first()
    )
```

The source formula supplies an independent expected distribution before any configuration comparison. A hot key is deliberate, so the experiment can show why adding partitions does not divide one unsalted key arbitrarily. Schema and population are fixed;no external large table is collected.

**Verification evidence:** Compare aggregate counts and the independent formula 16000+4000/100.

### Exercise 2: Measure the two-partition configuration

Execute the bounded grouped query under a unique job group, read actual executed metrics, measure partition row counts and persist/read back the product.

**Expected:** 100 exact key/count pairs, total 20000;nonempty retained stage evidence;one or two data files.

```scala
def measureTwo(spark: SparkSession, source: DataFrame, root: Path): BudgetReport = {
  measured(spark, source, 2, root)
}
```

```python
def measure_two(spark, source, root):
    return measured(spark, source, 2, root)
```

The report combines actual query metrics, retained scheduler stage counters and a separate physical partition-row observation. Timing covers the grouped collect only;the extra diagnostic scan and file write are outside that interval and are stated explicitly. The persisted readback ensures the measured transformation still produces the intended product.

**Verification evidence:** Compare all rows with the literal formula before accepting any work/time report.

### Exercise 3: Compare four partitions without assuming a speedup

Repeat with 4 partitions and a separate output directory.

**Expected:** All 100 result tuples match the same oracle;four buckets sum 20000 and one to four files are observed.

```scala
def measureFour(spark: SparkSession, source: DataFrame, root: Path): BudgetReport = {
  measured(spark, source, 4, root)
}
```

```python
def measure_four(spark, source, root):
    return measured(spark, source, 4, root)
```

Increasing partitions changes task granularity and output-file opportunities, not the configured local CPU thread count. It may add scheduling overhead while leaving the dominant key together. A valid comparison preserves the full row contract and reports measurements rather than asserting that more partitions must be faster.

**Verification evidence:** Assert parity and print actual elapsed time/file/metric values without an ordering claim.

### Exercise 4: Interpret work imbalance and spill honestly

Compute maximum bucket rows divided by mean bucket rows;report available dataSize, shuffleBytesWritten and spillSize metrics without inventing missing values.

**Expected:** Both observed work ratios exceed 1;unavailable metrics remain None/None-equivalent.

```scala
def imbalance(counts: Seq[Long]): Double = {
  require(counts.nonEmpty && counts.forall(_ >= 0L) && counts.sum > 0L)
  counts.max.toDouble / (counts.sum.toDouble / counts.size)
}
```

```python
def imbalance(counts):
    if not counts or any(value < 0 for value in counts) or sum(counts) <= 0:
        raise ValueError("Positive bounded work counts required")
    return max(counts) / (sum(counts) / len(counts))
```

SQL metric names are retained because serialized dataSize is not automatically remote-network bytes. spillSize is the reported operator metric, not invented disk I/O when absent. A tiny run may legitimately spill zero. Partition row counts reveal the work distribution, but per-task timing would require additional actual task metrics;the ratio is labeled accordingly.

**Verification evidence:** Assert row conservation and positive ratio, then print exact available metric maps and stage receipts.

### Exercise 5: Compute a separate hypothetical cost model

Use a hypothetical rate 0.05 currency units per vCPU-hour and 0.02 per GiB-month. Evaluate 2 vCPUs for 1 hour plus 2 GiB retained for 30 days under a30-day month.

**Expected:** Estimated 0.14 currency units, not an actual cloud bill or a price recommendation.

```scala
def estimatedCost(vcpu: Double, seconds: Double, gib: Double, days: Double): Double = {
  require(Seq(vcpu, seconds, gib, days).forall(x => x >= 0.0 && x.isFinite))
  vcpu * (seconds / 3600.0) * 0.05 + gib * (days / 30.0) * 0.02
}
```

```python
def estimated_cost(vcpu, seconds, gib, days):
    import math

    if any(not math.isfinite(value) or value < 0 for value in (vcpu, seconds, gib, days)):
        raise ValueError("Finite nonnegative model inputs required")
    return vcpu * (seconds / 3600) * 0.05 + gib * (days / 30) * 0.02
```

The model exposes its units and intentionally hypothetical prices. It omits billing minimums, network, requests, replication and operational overhead. Feeding a small local elapsed time into it would not turn the estimate into a measured production bill. Correct unit arithmetic is necessary but not sufficient for a real cost forecast.

**Verification evidence:** Check each unit conversion and reject negative durations/resources.

### Exercise 6: Enforce the stop budget before scaling data

Accept only row counts 1..20000 and partition counts 1..8 for this local exercise. Reject an attempted larger fixture before constructing it.

**Expected:** 20000/4 accepted;20001/4 and 20000/9 rejected.

```scala
def withinBudget(rows: Long, partitions: Int): Boolean = {
  rows >= 1L && rows <= 20000L && partitions >= 1 && partitions <= 8
}
```

```python
def within_budget(rows, partitions):
    return (
        type(rows) is int
        and type(partitions) is int
        and 1 <= rows <= 20000
        and 1 <= partitions <= 8
    )
```

The limit is a declared teaching workload budget, not a universal safe size for Spark. Requiring an explicit review before expanding it prevents a casual performance experiment from becoming an unbounded resource request. Temporary SQL configuration is restored in finally and only the newly created product root is removed.

**Verification evidence:** Assert both refusals and confirm the session shuffle setting restored to 2.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
