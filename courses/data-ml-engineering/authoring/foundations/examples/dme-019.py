"""Actual local Spark shuffles and a correctness-preserving salted aggregation."""

from contextlib import contextmanager

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


@contextmanager
def session(existing=None):
    if existing is not None:
        yield existing
        return
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("dme-shuffle-contract")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", ("127.0.0.1"))
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.shuffle.partitions", ("4"))
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        yield spark
    finally:
        spark.stop()


def records():
    return [("hot", number, number + 1) for number in range(20)] + [
        ("cold-a", 20, 5),
        ("cold-b", 21, 7),
    ]


def frame(spark):
    return spark.createDataFrame(records(), "group_name string, event_id long, amount long")


def partition_counts(data):
    return data.rdd.mapPartitions(lambda values: [sum(1 for _ in values)]).collect()


def totals(data):
    return {row["group_name"]: int(row["total"]) for row in data.orderBy("group_name").collect()}


def example_one(existing=None):
    with session(existing) as spark:
        data = frame(spark).repartition(4, "group_name")
        counts = partition_counts(data)
        result = data.groupBy("group_name").agg(F.sum("amount").alias("total"))
        actual = totals(result)
        plan = result._jdf.queryExecution().executedPlan().toString()
        assert actual == {"cold-a": 5, "cold-b": 7, "hot": 20 * 21 // 2}
        assert len(counts) == 4 and sum(counts) == 22 and max(counts) >= 20
        assert "Exchange" in plan
        return {
            "group_totals": actual,
            "observed_partition_rows": counts,
            "executed_plan_has_exchange": True,
            "scope": ("actual local[2] Spark, not a distributed-cluster performance claim"),
        }


def example_two(existing=None):
    with session(existing) as spark:
        salted = (
            frame(spark)
            .withColumn(
                "salt",
                F.when(F.col("group_name") == "hot", F.pmod(F.col("event_id"), F.lit(4))).otherwise(
                    F.lit(0)
                ),
            )
            .repartition(4, ("group_name"), ("salt"))
        )
        first = salted.groupBy("group_name", "salt").agg(
            F.sum("amount").alias("subtotal"), F.count("*").alias("records")
        )
        hot_counts = [
            int(row["records"])
            for row in first.filter(F.col("group_name") == "hot").orderBy("salt").collect()
        ]
        combined = first.groupBy("group_name").agg(F.sum("subtotal").alias("total"))
        actual = totals(combined)
        counts = partition_counts(salted)
        assert hot_counts == [5, 5, 5, 5] and sum(counts) == 22
        assert actual == {"cold-a": 5, "cold-b": 7, "hot": sum(range(1, 21))}
        return {
            "group_totals": actual,
            "hot_records_per_logical_salt": hot_counts,
            "observed_physical_partition_rows": counts,
            "no_timing_speedup_was_claimed": True,
        }


def main():
    with session() as spark:
        print("A real shuffle with a hot key:", example_one(spark))
        print("Two-stage aggregation retains the independent total:", example_two(spark))


if __name__ == "__main__":
    main()
