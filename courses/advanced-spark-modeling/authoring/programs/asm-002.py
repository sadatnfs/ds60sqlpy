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


def normal_nll(values, mean, scale):
    if not scale > 0:
        raise ValueError("positive Gaussian scale required")
    constant = 0.5 * math.log(2 * math.pi * scale * scale)
    return math.fsum(constant + (y - mean) ** 2 / (2 * scale * scale) for y in values)


def shared_intercept_nll(first, second, noise_variance, intercept_variance):
    diagonal = noise_variance + intercept_variance
    covariance = intercept_variance
    determinant = diagonal * diagonal - covariance * covariance
    if noise_variance <= 0 or intercept_variance < 0 or determinant <= 0:
        raise ValueError("positive-definite covariance required")
    quadratic = (
        diagonal * (first * first + second * second) - 2 * covariance * first * second
    ) / determinant
    return math.log(2 * math.pi) + 0.5 * math.log(determinant) + 0.5 * quadratic


def run(spark):
    from pyspark.sql import functions as F

    values = [-1.0, 0.5, 2.0, 4.0]
    mean, scale = 1.5, 2.0
    oracle = normal_nll(values, mean, scale)
    frame = spark.createDataFrame([(y,) for y in values], "y double")
    reports = []
    for partitions in (1, 2, 3):
        contribution = F.lit(0.5 * math.log(2 * math.pi * scale * scale)) + (
            (F.col("y") - mean) ** 2 / (2 * scale * scale)
        )
        row = (
            frame.repartition(partitions)
            .agg(F.count("*").alias("n"), F.sum(contribution).alias("loss"))
            .first()
        )
        assert row.n == len(values) and math.isclose(row.loss, oracle, abs_tol=1e-10)
        reports.append({"partitions": partitions, "n": row.n, "loss": row.loss})
    shared = shared_intercept_nll(1.0, 1.0, 1.0, 1.0)
    false_independent = normal_nll([1.0, 1.0], 0.0, math.sqrt(2.0))
    independent = shared_intercept_nll(1.0, 1.0, 1.0, 0.0)
    assert not math.isclose(shared, false_independent, abs_tol=1e-6)
    assert math.isclose(independent, normal_nll([1.0, 1.0], 0.0, 1.0), abs_tol=1e-12)
    print(
        json.dumps(
            {
                "additive": reports,
                "shared_latent_joint": shared,
                "wrong_product_of_marginals": false_independent,
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-002")
    try:
        run(spark)
    finally:
        spark.stop()
