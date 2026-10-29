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


def series_nll(values, phi, sigma):
    if abs(phi) >= 1 or sigma <= 0:
        raise ValueError("Stationary AR(1) needs abs(phi)<1 and sigma>0")
    v = sigma * sigma / (1 - phi * phi)
    loss = 0.5 * (math.log(2 * math.pi * v) + values[0] * values[0] / v)
    for prior, current in zip(values, values[1:], strict=False):
        loss += 0.5 * (
            math.log(2 * math.pi * sigma * sigma) + (current - phi * prior) ** 2 / (sigma * sigma)
        )
    return loss


def run(spark):
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    sequences = {"a": [1.0, 0.9, 0.6, 0.5], "b": [-1.0, -0.7, -0.2, 0.1]}
    phi, sigma = 0.7, 0.5
    rows = [(key, t, value) for key, values in sequences.items() for t, value in enumerate(values)]
    df = spark.createDataFrame(rows, "series string,t long,y double")
    oracle = math.fsum(series_nll(values, phi, sigma) for values in sequences.values())
    evidence = []
    for partitions in (1, 3):
        ordered = df.repartition(partitions).withColumn(
            "prior", F.lag("y").over(Window.partitionBy("series").orderBy("t"))
        )
        v = sigma * sigma / (1 - phi * phi)
        initial = 0.5 * (math.log(2 * math.pi * v) + F.col("y") ** 2 / v)
        transition = 0.5 * (
            math.log(2 * math.pi * sigma * sigma)
            + (F.col("y") - phi * F.col("prior")) ** 2 / (sigma * sigma)
        )
        actual = (
            ordered.agg(
                F.sum(F.when(F.col("prior").isNull(), initial).otherwise(transition)).alias("loss")
            )
            .first()
            .loss
        )
        assert math.isclose(actual, oracle, abs_tol=1e-12)
        evidence.append({"partitions": partitions, "loss": actual})
    reset = math.fsum(
        series_nll(v[:2], phi, sigma) + series_nll(v[2:], phi, sigma) for v in sequences.values()
    )
    assert abs(reset - oracle) > 0.01
    print(
        json.dumps(
            {
                "complete_series_loss": oracle,
                "wrong_chunk_reset": reset,
                "cases": evidence,
                "fixture_times_unique_and_contiguous": True,
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-012")
    try:
        run(spark)
    finally:
        spark.stop()
