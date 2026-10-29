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

    cases = []
    for labels in ([0.0, 0.0, 1.0, 1.0, 1.0], [0.0, 0.0, 0.0, 0.0, 1.0]):
        df = spark.createDataFrame([(y,) for y in labels], "y double").repartition(2).cache()
        beta = 0.0
        history = []
        try:
            for iteration in range(8):
                p = 1 / (1 + math.exp(-beta))
                row = df.agg(
                    F.count("*").alias("n"),
                    F.sum(
                        F.lit(max(beta, 0) + math.log1p(math.exp(-abs(beta)))) - F.col("y") * beta
                    ).alias("loss"),
                    F.sum(F.lit(p) - F.col("y")).alias("g"),
                    F.sum(F.lit(p * (1 - p))).alias("h"),
                ).first()
                history.append(
                    {"iteration": iteration, "beta": beta, "loss": row.loss, "gradient": row.g}
                )
                if abs(row.g) < 1e-10:
                    break
                if row.h <= 0:
                    raise ValueError("Nonpositive curvature")
                beta -= row.g / row.h
            empirical = sum(labels) / len(labels)
            target = math.log(empirical / (1 - empirical))
            assert abs(beta - target) < 1e-8 and abs(history[-1]["gradient"]) < 1e-10
            assert all(
                b["loss"] <= a["loss"] + 1e-12 for a, b in zip(history, history[1:], strict=False)
            )
            cases.append(
                {
                    "positive_fraction": empirical,
                    "beta": beta,
                    "closed_form": target,
                    "history": history,
                }
            )
        finally:
            df.unpersist()
    print(json.dumps({"cases": cases, "objective": "sum Bernoulli negative log likelihood"}))


if __name__ == "__main__":
    spark = session("asm-007")
    try:
        run(spark)
    finally:
        spark.stop()
