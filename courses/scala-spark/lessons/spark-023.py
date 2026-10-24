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


def logical_metrics(frame):
    return tuple(
        frame.agg(
            F.count(F.lit(1)),
            F.countDistinct("fact_id"),
            F.sum("amount"),
            F.sum(F.col("amount") * F.col("factor")),
        ).first()
    )


def join_plan(frame):
    return frame._jdf.queryExecution().executedPlan().toString()


def estimated_bytes(frame):
    raise NotImplementedError("Complete estimated_bytes")


def ordinary_join(facts, dimension):
    raise NotImplementedError("Complete ordinary_join")


def without_automatic_broadcast(facts, dimension):
    raise NotImplementedError("Complete without_automatic_broadcast")


def hinted_join(facts, dimension):
    raise NotImplementedError("Complete hinted_join")


def unsupported_hint(facts, dimension):
    raise NotImplementedError("Complete unsupported_hint")


def bounded_broadcast(dimension):
    raise NotImplementedError("Complete bounded_broadcast")


def main():

    spark = (
        SparkSession.builder.appName("ds60-spark-023")
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
            spark.range(0, 20000, 1, 4)
            .withColumnRenamed("id", "fact_id")
            .withColumn("key", F.col("fact_id") % 20)
            .withColumn("amount", F.col("fact_id") % 7 + 1)
        )
        dimension = (
            spark.range(0, 20, 1, 2)
            .withColumnRenamed("id", "key")
            .withColumn("factor", F.col("key") + 1)
        )
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
        spark.conf.set("spark.sql.join.preferSortMergeJoin", "true")
        assert facts.count() == 20000 and dimension.count() == 20
        assert dimension.select("key").distinct().count() == 20
        print("Known finite build side:20 unique keys")
        total = sum((i % 7 + 1) * (i % 20 + 1) for i in range(20000))
        assert total == 839916
        print("Independent weighted-total oracle=", total)
        print("spark-023: worked examples passed; six task implementations remain")
    finally:
        try:
            pass
        finally:
            spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Inspect statistics and the automatic threshold separately. Inputs/task: Return the optimized-plan size estimate for dimension as a nonnegative integer, and record the configured automatic broadcast threshold and actual dimension row count. Expected: A positive finite estimate below 10485760 bytes, threshold 10485760 and actual row count 20. The estimate is not a peak-memory measurement. Verify: Assert the finite estimate range and print estimate, threshold, rows andSpark version as separate fields.
# Exercise 2: Observe the automatic plan and verify its relational output. Inputs/task: Build an ordinary inner equality join on key, projecting fact_id, key, amount, factor. Execute logical metrics and record the physical plan chosen with the declared threshold. Expected: Metrics(20000,20000,79997,839916). The observed plan identifies a join strategy and is printed with current threshold. Verify: Assert all metrics and a join operator marker. Report the observed automatic strategy without treating a default as a universal guarantee.
# Exercise 3: Disable automatic broadcasting for a fresh comparison. Inputs/task: Set automatic broadcast threshold to-1, build a fresh ordinary join and record its plan withAQE disabled. Keep the logical result contract. Expected: Same metrics as automatic. No BroadcastHashJoin in this fresh query underAQEfalse and threshold-1. Verify: Assert all four metrics, the disabled setting and observed absence of BroadcastHashJoin.
# Exercise 4: Request an eligible explicit broadcast and reconcile bags. Inputs/task: Apply broadcast to the dimension for an inner equality join while automatic threshold remains-1. Project the same columns and compare duplicate-sensitive output with the ordinary join in both directions. Expected: BroadcastHashJoin and BroadcastExchange appear. Both exceptAll differences are empty and logical metrics remain exact. Verify: Assert the two operator markers, all metrics and both bag differences.
# Exercise 5: Observe an unsupported hint without changing the business result. Inputs/task: Request a broadcast dimension in a full outer equality join and inspect the chosen plan. Explain why this fixture still has the same output rows as the inner join. Expected: No BroadcastHashJoin for this unsupported full-outer hash strategy. Metrics remain(20000,20000,79997,839916) because both key domains are fully covered. Verify: Assert the observed absence of BroadcastHashJoin and exact output metrics;report a hint warning if emitted rather than hiding it.
# Exercise 6: Gate a broadcast candidate on explicit bounded evidence. Inputs/task: Reject streaming inputs, more than 100 rows, missing/duplicate keys, or an estimated size outside(0,1MiB]. Return the bounded dimension with a broadcast hint only after those checks. Expected: The 20-row dimension passes;the same dimension with a duplicate key and a101-row candidate fail. No unbounded input is collected or materialized by the gate. Verify: Assert accepted logical join metrics and explicit rejection for duplicate and row-budget cases.
