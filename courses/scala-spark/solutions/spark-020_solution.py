from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    IntegerType,
    StringType,
    DoubleType,
    BooleanType,
    ArrayType,
    MapType,
    TimestampType,
    DecimalType,
)


def canonical(frame):
    return [tuple(r) for r in frame.select("id", "key", "value").orderBy("id").collect()]


def keyed_layout(facts):
    return facts.repartition(6, "key")


def reduce_layout(frame):
    return frame.coalesce(2)


def partition_ledger(frame):
    return (
        frame.select("id", F.spark_partition_id().alias("partition_id"))
        .groupBy("partition_id")
        .agg(F.count(F.lit(1)).alias("row_count"), F.sum("id").alias("id_total"))
    )


def local_order(frame):
    return frame.sortWithinPartitions("key", "id")


def preview(frame):
    return [
        tuple(r)
        for r in frame.orderBy(F.col("key").desc(), F.col("id").asc())
        .limit(5)
        .select("id", "key", "value")
        .collect()
    ]


def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-020")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        facts = (
            spark.range(0, 24, 1, 4)
            .withColumn("key", F.col("id") % 4)
            .withColumn("value", F.col("id") * 10)
        )
        assert spark.conf.get("spark.sql.adaptive.enabled") == "false"
        # Exercise 1: Establish logical content independently of layout
        expected = [(i, i % 4, i * 10) for i in range(24)]
        assert canonical(facts) == expected
        assert tuple(
            facts.agg(F.count(F.lit(1)), F.countDistinct("id"), F.sum("id"), F.sum("value")).first()
        ) == (24, 24, 276, 2760)
        # Exercise 2: Request keyed redistribution and test colocation
        keyed = keyed_layout(facts)
        assert keyed.rdd.getNumPartitions() == 6 and canonical(keyed) == expected
        colocated = (
            keyed.withColumn("partition_id", F.spark_partition_id())
            .groupBy("key")
            .agg(F.countDistinct("partition_id").alias("partitions"))
            .collect()
        )
        assert len(colocated) == 4 and all(r[1] == 1 for r in colocated)
        # Exercise 3: Reduce partitions without assuming balanced redistribution
        reduced = reduce_layout(keyed)
        assert reduced.rdd.getNumPartitions() == 2 and canonical(reduced) == expected
        not_increased = facts.coalesce(10)
        assert not_increased.rdd.getNumPartitions() == 4 and canonical(not_increased) == expected
        # Exercise 4: Reconcile an occupied-partition ledger
        for frame in [keyed, reduced]:
            total = frame.rdd.getNumPartitions()
            ledger = partition_ledger(frame).collect()
            assert sum(r[1] for r in ledger) == 24 and sum(r[2] for r in ledger) == 276
            assert len(ledger) <= total and all(0 <= r[0] < total for r in ledger)
            print(
                "partition_count=",
                total,
                "occupied=",
                len(ledger),
                "ledger=",
                [tuple(r) for r in ledger],
            )
        # Exercise 5: Verify ordering only within its promised scope
        locally_sorted = local_order(facts.repartition(6))
        observed = locally_sorted.select(F.spark_partition_id().alias("pid"), "key", "id").collect()
        by_partition = {}
        for pid, key, ident in observed:
            by_partition.setdefault(pid, []).append((key, ident))
        assert all(pairs == sorted(pairs) for pairs in by_partition.values())
        assert canonical(locally_sorted) == expected
        # Exercise 6: Create a globally ordered bounded preview
        expected_preview = [(i, 3, i * 10) for i in [3, 7, 11, 15, 19]]
        for frame in [facts, keyed, reduced]:
            assert preview(frame) == expected_preview
        print("spark-020: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Establish logical content independently of layout. Inputs/task: Return the ordered list of(id, key, value) tuples for the declared 24-row fixture. Compare its full bag with the literal arithmetic rule and compute count, distinct IDs, sum(id), sum(value). Expected: IDs 0..23 appear once, key=id%4, value=10*id. Metrics are 24,24,276,2760. Verify: Assert every canonical tuple and all four aggregate values.
# Exercise 2: Request keyed redistribution and test colocation. Inputs/task: Return facts repartitioned to 6 partitions by key. Record its partition count and check that each logical key is observed in exactly one execution partition. Expected: Six partitions requested;all 24 rows unchanged. Each of four keys has one observed partition ID;different keys may share one. Verify: Assert partition metadata 6, canonical equality and per-key countDistinct(partition_id)=1.
# Exercise 3: Reduce partitions without assuming balanced redistribution. Inputs/task: Coalesce a six-partition input to 2 and return it. Separately request coalesce 10 on the original four-partition relation. Preserve canonical content in both cases. Expected: The first has 2 partitions;the attempted increase remains 4. Both retain the 24-row bag and sum 2760. Verify: Assert both partition counts and complete canonical equality.
# Exercise 4: Reconcile an occupied-partition ledger. Inputs/task: Return partition_id, row_count, id_total for occupied partitions of the supplied relation. Record total partition metadata separately and do not manufacture empty-partition rows. Expected: Ledger row_count sums 24 and id_total sums 276;each recorded partition ID lies in[0, total_partitions). Occupied count may be lower than total. Verify: Assert reconciliation and partition-ID bounds for both keyed 6 and coalesced 2 layouts.
# Exercise 5: Verify ordering only within its promised scope. Inputs/task: Return a relation sorted within each partition by key ascending, id ascending. Inspect the sequence of(key, id) pairs within each recorded partition and preserve the logical bag. Expected: Every occupied partition sequence is sorted;the complete canonical relation is unchanged. No raw global collect sequence is required. Verify: Assert per-partition sorted sequences and canonical equality without asserting that raw concatenation must be sorted or unsorted.
# Exercise 6: Create a globally ordered bounded preview. Inputs/task: Order key descending then event identity id ascending and return the first 5 rows. Repeat after several input layouts. Expected: IDs[3,7,11,15,19], allkey 3 and values[30,70,110,150,190]. The final sixthkey 3 row is outside the limit. Verify: Assert all five ordered tuples from original, keyed and coalesced inputs.
