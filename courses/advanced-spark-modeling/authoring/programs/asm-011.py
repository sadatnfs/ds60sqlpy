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


def pair_nll(y1, y2, rho):
    if abs(rho) >= 1:
        raise ValueError("Correlation must lie strictly between -1 and 1")
    return (
        math.log(2 * math.pi)
        + 0.5 * math.log1p(-rho * rho)
        + (y1 * y1 - 2 * rho * y1 * y2 + y2 * y2) / (2 * (1 - rho * rho))
    )


def run(spark):
    from pyspark.sql import functions as F

    pairs = [(1.0, 1.0), (-1.0, -0.5), (0.2, -0.3)]
    df = spark.createDataFrame(pairs, "a double,b double")
    evidence = []
    for rho in (0.0, 0.8):
        loss = (
            math.log(2 * math.pi)
            + 0.5 * math.log1p(-rho * rho)
            + (F.col("a") ** 2 - 2 * rho * F.col("a") * F.col("b") + F.col("b") ** 2)
            / (2 * (1 - rho * rho))
        )
        actual = df.agg(F.sum(loss).alias("loss")).first().loss
        oracle = math.fsum(pair_nll(a, b, rho) for a, b in pairs)
        assert math.isclose(actual, oracle, abs_tol=1e-12)
        independent = math.fsum(pair_nll(a, b, 0) for a, b in pairs)
        assert rho != 0 or math.isclose(actual, independent, abs_tol=1e-12)
        assert rho == 0 or abs(actual - independent) > 0.1
        evidence.append(
            {"rho": rho, "joint_loss": actual, "incorrect_independent_loss": independent}
        )
    print(json.dumps({"independent_units": "complete pairs", "cases": evidence}))


if __name__ == "__main__":
    spark = session("asm-011")
    try:
        run(spark)
    finally:
        spark.stop()
