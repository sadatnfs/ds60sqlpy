from __future__ import annotations

import json


def session(name):
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[2]")
        .appName(name)
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    if spark.version != "4.0.1":
        spark.stop()
        raise RuntimeError("This worked reference is qualified for Spark 4.0.1")
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def dense_numeric_lower_bound(rows, columns):
    if not isinstance(rows, int) or not isinstance(columns, int) or rows < 0 or columns < 1:
        raise ValueError("nonnegative rows and positive numeric width required")
    return 8 * rows * columns


def run(spark):
    from pyspark.sql import functions as F

    rows = [("hot", float(i)) for i in range(16)]
    rows += [(f"small-{g}", float(i)) for g in range(3) for i in (1, 3)]
    frame = spark.createDataFrame(rows, "group string, y double")
    observed = []
    for partitions in (1, 4):
        result = (
            frame.repartition(partitions)
            .groupBy("group")
            .agg(F.count("*").alias("n"), F.sum("y").alias("total"))
        )
        summaries = result.orderBy("group").collect()
        assert max(r.n for r in summaries) == 16
        for row in summaries:
            original = [value for group, value in rows if group == row.group]
            assert row.n == len(original)
            assert row.total / row.n == sum(original) / len(original)
        observed.append({"physical_partitions": partitions, "largest_group": 16})
        if partitions == 4:
            result.explain("formatted")
    estimate = dense_numeric_lower_bound(2_000_000, 50)
    budget = 512 * 1024 * 1024
    assert estimate == 800_000_000 and estimate > budget
    print(
        json.dumps(
            {
                "group_ownership": observed,
                "raw_float64_bytes": estimate,
                "illustrative_budget_bytes": budget,
                "admit_whole_group": False,
                "note": "memory lower bound, not an observed OOM",
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-004")
    try:
        run(spark)
    finally:
        spark.stop()
