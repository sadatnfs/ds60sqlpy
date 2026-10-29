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


def profile_fit(n, su, suu, sy, suy, syy):
    determinant = n * suu - su * su
    if determinant <= 1e-12:
        raise ValueError("The exponential column and intercept are not identifiable")
    a = (n * suy - su * sy) / determinant
    c = (sy - a * su) / n
    sse = syy + a * a * suu + n * c * c - 2 * a * suy - 2 * c * sy + 2 * a * c * su
    if sse <= 0:
        raise ValueError("A finite Gaussian scale MLE requires positive residual variation")
    scale2 = sse / n
    loss = n / 2 * (math.log(2 * math.pi * scale2) + 1)
    return a, c, scale2, loss


def run(spark):
    from pyspark.sql import functions as F

    rows = [
        (float(i), 2 * math.exp(-0.4 * i) + 0.5 + e)
        for i, e in enumerate([0.02, -0.01, 0.01, -0.02, 0.02, -0.01, 0.01, -0.02])
    ]
    rates = [0.2, 0.3, 0.4, 0.5, 0.6]
    data = spark.createDataFrame(rows, "t double,y double")
    grid = spark.createDataFrame([(b,) for b in rates], "b double")
    pairs = data.crossJoin(grid).withColumn("u", F.exp(-F.col("b") * F.col("t")))
    stats = (
        pairs.groupBy("b")
        .agg(
            F.count("*").alias("n"),
            F.sum("u").alias("su"),
            F.sum(F.col("u") ** 2).alias("suu"),
            F.sum("y").alias("sy"),
            F.sum(F.col("u") * F.col("y")).alias("suy"),
            F.sum(F.col("y") ** 2).alias("syy"),
        )
        .collect()
    )
    fits = []
    for r in stats:
        fit = profile_fit(r.n, r.su, r.suu, r.sy, r.suy, r.syy)
        u = [math.exp(-r.b * t) for t, _ in rows]
        y = [y for _, y in rows]
        oracle = profile_fit(
            len(rows),
            math.fsum(u),
            math.fsum(v * v for v in u),
            math.fsum(y),
            math.fsum(a * b for a, b in zip(u, y, strict=True)),
            math.fsum(v * v for v in y),
        )
        assert max(abs(a - b) for a, b in zip(fit, oracle, strict=True)) < 1e-7
        fits.append((r.b,) + fit)
    best = min(fits, key=lambda x: x[-1])
    assert best[0] == 0.4
    try:
        profile_fit(3, 3, 3, 6, 6, 14)
    except ValueError:
        rejected = True
    else:
        rejected = False
    assert rejected
    print(
        json.dumps(
            {
                "finite_grid_fits": sorted(fits),
                "best": best,
                "rank_deficiency_rejected": rejected,
                "continuous_optimizer": False,
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-010")
    try:
        run(spark)
    finally:
        spark.stop()
