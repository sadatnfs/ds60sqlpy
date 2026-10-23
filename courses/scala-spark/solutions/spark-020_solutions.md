# spark-020: Explained paired reference solutions

Read the [guide](../guides/spark-020.md) and attempt one language first. The [Scala reference](spark-020_solution.scala) and [PySpark reference](spark-020_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Establish logical content independently of layout

Return the ordered list of(id, key, value) tuples for the declared 24-row fixture. Compare its full bag with the literal arithmetic rule and compute count, distinct IDs, sum(id), sum(value).

**Expected:** IDs 0..23 appear once, key=id%4, value=10*id. Metrics are 24,24,276,2760.

```scala
def canonical(frame: DataFrame): Seq[(Long,Long,Long)] = {
  frame.select("id","key","value").orderBy("id").collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2)))
}
```

```python
def canonical(frame):
    return [tuple(r) for r in frame.select("id","key","value").orderBy("id").collect()]
```

The sorted tuple list is a representation for comparison, not a claim that the underlying relation is intrinsically ordered. It retains every declared field and occurrence. The aggregate checks provide readable diagnostics if a future implementation drops or repeats data, but the full bag comparison is what prevents compensating errors from passing accidentally.

**Verification evidence:** Assert every canonical tuple and all four aggregate values.

### Exercise 2: Request keyed redistribution and test colocation

Return facts repartitioned to 6 partitions by key. Record its partition count and check that each logical key is observed in exactly one execution partition.

**Expected:** Six partitions requested; all 24 rows unchanged. Each of four keys has one observed partition ID; different keys may share one.

```scala
def keyedLayout(facts: DataFrame): DataFrame = {
  facts.repartition(6,col("key"))
}
```

```python
def keyed_layout(facts):
    return facts.repartition(6,"key")
```

Hash repartitioning expresses equal-key colocation, not one partition per key. The assertion tolerates collisions between distinct keys and does not attach meaning to a numeric partition index. Logical equality is checked independently so a distribution experiment cannot be judged successful merely because the requested partition count was achieved.

**Verification evidence:** Assert partition metadata 6, canonical equality and per-key countDistinct(partition_id)=1.

### Exercise 3: Reduce partitions without assuming balanced redistribution

Coalesce a six-partition input to 2 and return it. Separately request coalesce 10 on the original four-partition relation. Preserve canonical content in both cases.

**Expected:** The first has 2 partitions; the attempted increase remains 4. Both retain the 24-row bag and sum 2760.

```scala
def reduceLayout(frame: DataFrame): DataFrame = {
  frame.coalesce(2)
}
```

```python
def reduce_layout(frame):
    return frame.coalesce(2)
```

The result demonstrates reduction and the absence of expansion for this classic Spark transformation. It does not prove equal partition sizes or a performance improvement. A skewed source can remain skewed after coalescing, and reducing too far can remove useful parallel work. The reference keeps AQE disabled so adaptive partition changes do not confuse this isolated observation.

**Verification evidence:** Assert both partition counts and complete canonical equality.

### Exercise 4: Reconcile an occupied-partition ledger

Return partition_id, row_count, id_total for occupied partitions of the supplied relation. Record total partition metadata separately and do not manufacture empty-partition rows.

**Expected:** Ledger row_count sums 24 and id_total sums 276; each recorded partition ID lies in[0, total_partitions). Occupied count may be lower than total.

```scala
def partitionLedger(frame: DataFrame): DataFrame = {
  frame.select(col("id"),spark_partition_id().as("partition_id")).groupBy("partition_id").agg(count(lit(1)).as("row_count"),sum("id").as("id_total"))
}
```

```python
def partition_ledger(frame):
    return frame.select("id",F.spark_partition_id().alias("partition_id")).groupBy("partition_id").agg(F.count(F.lit(1)).alias("row_count"),F.sum("id").alias("id_total"))
```

The ledger turns a physical layout into inspectable run evidence while reconciling it to the logical population. Empty partitions lack rows and are absent from the grouped result, so metadata is needed to report the total. Persisting partition IDs as business identities would be a mistake because a later shuffle or different plan can change them.

**Verification evidence:** Assert reconciliation and partition-ID bounds for both keyed 6 and coalesced 2 layouts.

### Exercise 5: Verify ordering only within its promised scope

Return a relation sorted within each partition by key ascending, id ascending. Inspect the sequence of(key, id) pairs within each recorded partition and preserve the logical bag.

**Expected:** Every occupied partition sequence is sorted; the complete canonical relation is unchanged. No raw global collect sequence is required.

```scala
def localOrder(frame: DataFrame): DataFrame = {
  frame.sortWithinPartitions(col("key"),col("id"))
}
```

```python
def local_order(frame):
    return frame.sortWithinPartitions("key","id")
```

The operator promises order inside a partition and the test checks exactly that scope. It avoids the common but fragile test that an inadequately specified global order must visibly change or be unsorted. Coincidental global ordering on a tiny fixture is compatible with a weaker contract. Consumers needing a stable global presentation must request it explicitly.

**Verification evidence:** Assert per-partition sorted sequences and canonical equality without asserting that raw concatenation must be sorted or unsorted.

### Exercise 6: Create a globally ordered bounded preview

Order key descending then event identity id ascending and return the first 5 rows. Repeat after several input layouts.

**Expected:** IDs[3,7,11,15,19], allkey 3 and values[30,70,110,150,190]. The final sixthkey 3 row is outside the limit.

```scala
def preview(frame: DataFrame): Seq[(Long,Long,Long)] = {
  frame.orderBy(col("key").desc,col("id").asc).limit(5).select("id","key","value").collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2)))
}
```

```python
def preview(frame):
    return [tuple(r) for r in frame.orderBy(F.col("key").desc(),F.col("id").asc()).limit(5).select("id","key","value").collect()]
```

The complete ordering converts a relation into a specified display sequence before selecting a bounded prefix. A key-only sort leaves same-key peers unresolved; an unordered limit chooses an arbitrary subset. The reference compares every displayed identity and value across layouts, providing a reusable pattern for deterministic small previews without implying that a full production result should be collected on the driver.

**Verification evidence:** Assert all five ordered tuples from original, keyed and coalesced inputs.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
