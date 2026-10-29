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


def run(spark):
    from pyspark.sql import functions as F

    frame = spark.range(0, 12, 1, 3).withColumn("square", F.col("id") * F.col("id"))
    expected = sum(x * x for x in range(12))
    assert expected == 506
    spark.sparkContext.setJobGroup("asm-001-objective", "One bounded objective evaluation")
    result = frame.agg(F.count("*").alias("n"), F.sum("square").alias("loss")).first()
    jobs = spark.sparkContext.statusTracker().getJobIdsForGroup("asm-001-objective")
    assert result.n == 12 and result.loss == expected and len(jobs) >= 1
    frame.explain("formatted")
    evidence = []
    for partitions in (1, 2, 3):
        row = (
            frame.repartition(partitions)
            .agg(F.count("*").alias("n"), F.sum("square").alias("loss"))
            .first()
        )
        assert (row.n, row.loss) == (12, expected)
        evidence.append({"requested_partitions": partitions, "n": row.n, "loss": row.loss})
    print(json.dumps({"case_1_jobs_observed": len(jobs), "case_2_partition_parity": evidence}))


if __name__ == "__main__":
    spark = session("asm-001")
    try:
        run(spark)
    finally:
        spark.stop()
