# spark-020: Partitions, repartition, coalesce and output order

Twenty-four generated rows move through `repartition`, `coalesce` and `sortWithinPartitions` while their content stays fixed. The skill is to separate what changed (how rows are split across tasks) from what must not change (which rows exist and what they sum to), and to know that only a final `orderBy` with a full tie-breaker promises a display order.

## Level and prerequisites

Intermediate; approximately 90 minutes. Direct prerequisites: `spark-019`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-020.scala) and [PySpark](../lessons/spark-020.py).

Open the [explained solutions](../solutions/spark-020_solutions.md) after an attempt.

The first worked example builds the 24 rows with `range` over four partitions, confirms 24 rows, 4 partitions and 4 keys, and prints `24 rows,4 key values,4 initial execution partitions`. The second calls `repartition(6)`, confirms six partitions and still 24 rows, and prints `Repartition changes layout while preserving the row population`.

## Learning objectives

- Separate logical rows, physical partitions and a presentation order.
- Check content independently of layout with the metrics `(24, 24, 276, 2760)` for rows, distinct IDs, ID total and value total, and confirm they hold after every redistribution.
- Explain why `coalesce(2)` reduces four partitions to two but `coalesce(6)` leaves four, and why `sortWithinPartitions` sorts each partition without ordering the whole result.

## Vocabulary and concepts

- **Execution partition:** A subdivision of a dataset processed by a task at a stage; it is not a business group or necessarily a persisted file.

- **Repartition:** A transformation requesting a new distribution, usually through a shuffle; hash columns specify which equal keys must be colocated.

- **Coalesce:** A transformation that can reduce partitions without a full redistribution; increasing its requested count does not generally create additional partitions.

- **Partition-local order:** An ordering guaranteed within each output partition, without promising a globally ordered concatenation.

- **Canonical content:** A stable representation of the logical rows used to compare results independently of execution layout or incidental arrival order.

The fixture has 24 rows with identities 0 through 23, four logical key values and a value equal to ten times the identity. Those facts are logical properties. The initial four execution partitions are a physical layout choice. Changing the layout should not add, remove or alter an occurrence. The first task records both the full tiny identity bag and aggregate checks so a layout experiment has a correctness baseline.

Repartitioning to six partitions requests a new distribution. Repartitioning by key additionally requires equal key values to share a destination partition within that result. Four distinct keys do not imply four occupied partitions, and six requested partitions do not imply six nonempty ones. Hash collisions can place different keys together. A partition index is an execution observation, not a durable business identifier to store in a progress table or use as an entity key.

The worker uses `local[2]`. That permits two local execution threads, not two total partitions. A stage with six partitions can execute its tasks in waves. Conversely, a one-partition result offers only one partition of work for that stage. Partition count influences scheduling and potential parallelism, but row counts, record sizes, key skew and operators also matter. A 24-row fixture cannot justify a production tuning recommendation or establish meaningful speed differences.

Coalesce can combine existing partitions while avoiding a full redistribution. This may be useful when a filtered result has become much smaller, but it can also preserve imbalance and concentrate work. Coalescing the six-partition relation to two returns two partitions here, while asking a four-partition source to coalesce to ten leaves its partition count at four. The lesson checks this behavior with AQE disabled to make the observed boundary clear. Adaptive execution can alter partitioning in other workloads and must be recorded when making comparisons.

The partition ledger deliberately records only occupied partitions because a grouped spark_partition_id expression has no row from which to represent an empty partition. The total partition count is recorded separately using the classic DataFrame RDD metadata boundary. Summing the ledger row counts must recover 24; summing its identity totals must recover 276. The ledger does not require a particular hash bucket number for a key, which could bind a semantic test unnecessarily to an implementation detail.

Sorting inside partitions and sorting globally are different contracts. sortWithinPartitions(key ascending, id ascending) makes each partition's sequence ordered. It does not promise that a raw concatenation from all partitions is globally sorted. The reference checks each observed partition sequence separately and does not demand that a locally sorted result always look unsorted globally. Small data can coincidentally satisfy a stronger property without that property being guaranteed.

For a stable learner-facing preview, the final task uses orderBy(key descending, id ascending), then limit 5. The complete tie-breaker makes the preview IDs 3,7,11,15,19 regardless of earlier layout. A limit without an ordering would produce an arbitrary subset of the relation; a sort by key alone would leave six peer identities unordered. If the user needs pagination, the same complete ordering and a suitable continuation key belong in the interface contract.

Canonical collection is intentionally limited to 24 rows. Production correctness comparisons should use distributed reconciliation suited to duplicate occurrences, or carefully designed fingerprints with stated collision limitations. A count and sum alone are insufficient: a missing ID and duplicated ID can sometimes preserve those aggregates. The literal identity bag in this tiny lesson makes those failure cases impossible to hide while partition evidence explains the execution layout separately.

## Supplied local fixture

The data is generated, not typed: IDs 0 to 23 in four initial partitions, `key` equal to the ID modulo 4 and `value` equal to ten times the ID. The fixture asserts that adaptive query execution is off, because AQE could otherwise merge shuffle partitions and make the partition counts in Exercises 2 and 3 differ from run to run.

```scala
import org.apache.spark.sql.functions._

val facts =
  spark.range(0L, 24L, 1L, 4).withColumn("key", col("id") % 4L).withColumn("value", col("id") * 10L)
assert(spark.conf.get("spark.sql.adaptive.enabled") == "false")
```

```python
from pyspark.sql import functions as F

facts = (
    spark.range(0, 24, 1, 4)
    .withColumn("key", F.col("id") % 4)
    .withColumn("value", F.col("id") * 10)
)
assert spark.conf.get("spark.sql.adaptive.enabled") == "false"
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(facts.count() == 24L && facts.rdd.getNumPartitions == 4)
assert(facts.select("key").distinct().count() == 4L)
println("24 rows,4 key values,4 initial execution partitions")
```

```python
assert facts.count() == 24 and facts.rdd.getNumPartitions() == 4
assert facts.select("key").distinct().count() == 4
print("24 rows,4 key values,4 initial execution partitions")
```

The counts happen to include two fours, but they measure different things. Distinct keys describe the data model; execution partitions describe work placement. The local worker thread count is another separate setting and is two in this profile.

### Worked example 2

```scala
val changed = facts.repartition(6)
assert(changed.rdd.getNumPartitions == 6 && changed.count() == 24L)
println("Repartition changes layout while preserving the row population")
```

```python
changed = facts.repartition(6)
assert changed.rdd.getNumPartitions() == 6 and changed.count() == 24
print("Repartition changes layout while preserving the row population")
```

This is a bounded layout observation, not a benchmark. The stronger exercises compare the full canonical content and per-partition evidence. A count-only check here is a first observation rather than the final correctness oracle.

## Exercises

### Exercise 1: Establish logical content independently of layout

Return the ordered list of (id, key, value) tuples for the declared 24-row fixture. Compare its full bag with the literal arithmetic rule and compute count, distinct IDs, sum(id), sum(value).

**Expected result/shape:** IDs 0..23 appear once, key=id%4, value=10*id. Metrics are 24,24,276,2760.

**Verify:** Assert every canonical tuple and all four aggregate values.

**Progressive hint:** An aggregate fingerprint supplements the complete tiny bag; it does not replace it.

### Exercise 2: Request keyed redistribution and test colocation

Return facts repartitioned to 6 partitions by key. Record its partition count and check that each logical key is observed in exactly one execution partition.

**Expected result/shape:** Six partitions requested; all 24 rows unchanged. Each of four keys has one observed partition ID; different keys may share one.

**Verify:** Assert partition metadata 6, canonical equality and per-key countDistinct(partition_id)=1.

**Progressive hint:** Project spark_partition_id after the redistribution; do not assume a key maps to its numeric value.

### Exercise 3: Reduce partitions without assuming balanced redistribution

Coalesce a six-partition input to 2 and return it. Separately request coalesce 10 on the original four-partition relation. Preserve canonical content in both cases.

**Expected result/shape:** The first has 2 partitions; the attempted increase remains 4. Both retain the 24-row bag and sum 2760.

**Verify:** Assert both partition counts and complete canonical equality.

**Progressive hint:** Coalesce is useful for reduction; repartition is the explicit redistribution mechanism when increasing parallelism.

### Exercise 4: Reconcile an occupied-partition ledger

Return partition_id, row_count, id_total for occupied partitions of the supplied relation. Record total partition metadata separately and do not manufacture empty-partition rows.

**Expected result/shape:** Ledger row_count sums 24 and id_total sums 276; each recorded partition ID lies in [0, total_partitions). Occupied count may be lower than total.

**Verify:** Assert reconciliation and partition-ID bounds for both keyed 6 and coalesced 2 layouts.

**Progressive hint:** A groupBy on projected spark_partition_id can only report partitions that supplied rows.

### Exercise 5: Verify ordering only within its promised scope

Return a relation sorted within each partition by key ascending, id ascending. Inspect the sequence of (key, id) pairs within each recorded partition and preserve the logical bag.

**Expected result/shape:** Every occupied partition sequence is sorted; the complete canonical relation is unchanged. No raw global collect sequence is required.

**Verify:** Assert per-partition sorted sequences and canonical equality without asserting that raw concatenation must be sorted or unsorted.

**Progressive hint:** Collect the tiny rows with spark_partition_id, group them preserving observed sequence, and check each group separately.

### Exercise 6: Create a globally ordered bounded preview

Order key descending then event identity id ascending and return the first 5 rows. Repeat after several input layouts.

**Expected result/shape:** IDs `[3, 7, 11, 15, 19]`, all with key 3, and values `[30, 70, 110, 150, 190]`. The sixth key 3 row is outside the limit.

**Verify:** Assert all five ordered tuples from original, keyed and coalesced inputs.

**Progressive hint:** Apply the complete global order before the limit, not a partition-local sort after choosing arbitrary rows.

## Common pitfalls

Do not equate partitions with executors, worker threads, business groups or output files without inspecting the relevant stage and write path. Do not claim that six partitions means six occupied partitions. Do not use spark_partition_id as stable data identity. Coalesce can reduce parallelism and retain skew; repartition incurs redistribution. Neither operation guarantees a globally ordered presentation. The 24-row fixture demonstrates semantics only; production tuning requires recorded size, skew, task and shuffle metrics under a controlled workload.

## Self-check

- After `repartition(6, col("key"))`, each key sits in exactly one partition. Why might two different keys still share a partition, and why is that acceptable?
- `coalesce(6)` on a four-partition frame still has four partitions. What would you call instead if you really needed six, and what does it cost?
- The partition ledger may list fewer occupied partitions than the total. Why is an empty partition not an error?
- Exercise 6 returns IDs 3, 7, 11, 15 and 19. Which two calls make that answer deterministic, and what goes wrong if you use `limit` before `orderBy`?

## Next step

Go on to [spark-021: Read logical and physical plans](spark-021.md). You have watched partitions change from the outside; next you read the plan Spark builds and find where those exchanges and sorts actually appear.

## Primary sources and official APIs

- [Spark 4.3.0 repartition](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.repartition.html)

- [Spark 4.3.0 coalesce](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.coalesce.html)

- [Spark 4.3.0 sortWithinPartitions](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.sortWithinPartitions.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-020: Partitions, repartition, coalesce and output order.
Read courses/scala-spark/guides/spark-020.md and courses/scala-spark/lessons/spark-020.scala; the paired sources are courses/scala-spark/lessons/spark-020.scala and courses/scala-spark/lessons/spark-020.py.
Direct prerequisites: spark-019. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
