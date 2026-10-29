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


def oracle(rows, beta):
    loss, g0, g1 = [], [], []
    for x, y in rows:
        z = beta[0] + beta[1] * x
        p = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
        loss.append(max(z, 0) + math.log1p(math.exp(-abs(z))) - y * z)
        g0.append(p - y)
        g1.append((p - y) * x)
    return math.fsum(loss), (math.fsum(g0), math.fsum(g1))


def run(spark):
    from pyspark.sql import functions as F

    rows = [(-2.0, 0.0), (-1.0, 1.0), (0.0, 0.0), (1.0, 1.0), (3.0, 1.0)]
    beta = (0.2, -0.4)
    df = spark.createDataFrame(rows, "x double,y double")
    z = F.lit(beta[0]) + F.lit(beta[1]) * F.col("x")
    p = F.when(z >= 0, 1 / (1 + F.exp(-z))).otherwise(F.exp(z) / (1 + F.exp(z)))
    loss = F.greatest(z, F.lit(0.0)) + F.log1p(F.exp(-F.abs(z))) - F.col("y") * z
    r = p - F.col("y")
    out = df.agg(
        F.count("*").alias("n"),
        F.sum(loss).alias("loss"),
        F.sum(r).alias("g0"),
        F.sum(r * F.col("x")).alias("g1"),
        F.sum(p * (1 - p)).alias("h00"),
    ).first()
    expected, g = oracle(rows, beta)
    assert out.n == 5 and math.isclose(out.loss, expected, rel_tol=1e-13)
    assert all(math.isclose(a, b, abs_tol=1e-13) for a, b in zip((out.g0, out.g1), g, strict=True))
    h = 1e-5
    fd = []
    for j in range(2):
        plus = list(beta)
        minus = list(beta)
        plus[j] += h
        minus[j] -= h
        fd.append((oracle(rows, plus)[0] - oracle(rows, minus)[0]) / (2 * h))
    assert max(abs(a - b) for a, b in zip(fd, g, strict=True)) < 1e-8
    assert abs(g[0] - g[1]) > 0.1
    print(
        json.dumps(
            {
                "rows": out.n,
                "loss": out.loss,
                "gradient": g,
                "central_difference": fd,
                "h00": out.h00,
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-006")
    try:
        run(spark)
    finally:
        spark.stop()
