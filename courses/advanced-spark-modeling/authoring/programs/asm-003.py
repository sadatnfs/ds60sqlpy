from __future__ import annotations

import json
import math


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


def run(spark):
    from pyspark.sql import functions as F

    a = [1.0, 3.0]
    b = [8.0, 10.0, 10.0, 12.0, 9.0, 11.0]
    rows = [("A", x) for x in a] + [("B", x) for x in b]
    frame = spark.createDataFrame(rows, "group string, y double").repartition(3)
    groups = (
        frame.groupBy("group")
        .agg(F.count("*").alias("n"), F.sum("y").alias("total"), F.avg("y").alias("mean"))
        .orderBy("group")
        .collect()
    )
    assert [(r.group, r.n, r.total, r.mean) for r in groups] == [
        ("A", 2, 4.0, 2.0),
        ("B", 6, 60.0, 10.0),
    ]
    pooled = math.fsum(r.total for r in groups) / sum(r.n for r in groups)
    average_models = math.fsum(r.mean for r in groups) / len(groups)
    assert pooled == 8.0 and average_models == 6.0
    assert sum((y - pooled) ** 2 for _, y in rows) < sum((y - average_models) ** 2 for _, y in rows)
    duplicated_b = (sum(a) + 2 * sum(b)) / (len(a) + 2 * len(b))
    equal_sized = (sum(a) + sum([9.0, 11.0])) / 4
    assert math.isclose(duplicated_b, 124 / 14) and equal_sized == 6.0
    print(
        json.dumps(
            {
                "independent_means": {r.group: r.mean for r in groups},
                "shared_mean_mle": pooled,
                "unweighted_model_mean": average_models,
                "shared_mean_after_B_replication": duplicated_b,
                "equal_group_sizes_coincide": equal_sized,
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-003")
    try:
        run(spark)
    finally:
        spark.stop()
