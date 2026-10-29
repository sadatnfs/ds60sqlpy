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


def softplus(z):
    return max(z, 0.0) + math.log1p(math.exp(-abs(z)))


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z)) if z >= 0 else math.exp(z) / (1.0 + math.exp(z))


def run(spark):
    from pyspark.sql import functions as F

    rows = [
        (-1000.0, 0.0, 1.0),
        (1000.0, 1.0, 1.0),
        (-2.0, 1.0, 2.0),
        (0.0, 0.0, 0.5),
        (2.0, 1.0, 3.0),
    ]
    frame = spark.createDataFrame(rows, "z double, y double, w double")
    loss = F.col("w") * (
        F.greatest(F.col("z"), F.lit(0.0)) + F.log1p(F.exp(-F.abs("z"))) - F.col("y") * F.col("z")
    )
    expected = math.fsum(w * (softplus(z) - y * z) for z, y, w in rows)
    actual = frame.agg(F.sum(loss).alias("loss"), F.sum("w").alias("weight")).first()
    assert math.isfinite(actual.loss) and math.isclose(actual.loss, expected, rel_tol=1e-13)
    assert actual.weight == 7.5
    wrong = math.fsum(softplus(z) - y * z for z, y, w in rows)
    assert not math.isclose(wrong, expected)
    assert softplus(1000.0) == 1000.0 and softplus(-1000.0) == 0.0
    print(
        json.dumps(
            {
                "weighted_loss": actual.loss,
                "weight_sum": actual.weight,
                "unweighted_loss": wrong,
                "serial_error": abs(actual.loss - expected),
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-005")
    try:
        run(spark)
    finally:
        spark.stop()
