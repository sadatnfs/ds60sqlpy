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


def summary(values):
    return {"count": len(values), "sum": math.fsum(values)}


def reconcile(attempts):
    accepted = {}
    for identity, value in attempts:
        if identity in accepted and accepted[identity] != value:
            raise ValueError("Attempt content disagrees for the same immutable evaluation identity")
        accepted[identity] = value
    return accepted


def run(spark):
    data = [1.0, 2.0, 3.0, 4.0]
    rdd = spark.sparkContext.parallelize(data, 2)

    def evaluate(index, iterator):
        yield str(index), summary(list(iterator))

    first = sorted(rdd.mapPartitionsWithIndex(evaluate).collect())
    second = sorted(rdd.mapPartitionsWithIndex(evaluate).collect())
    assert first == second
    attempts = [(("fixture-v1", "beta-zero", key), value) for key, value in first + second]
    accepted = reconcile(attempts)
    assert sum(value["count"] for value in accepted.values()) == 4
    assert sum(value["count"] for _, value in attempts) == 8
    try:
        reconcile(attempts + [(attempts[0][0], {"count": 999, "sum": 0.0})])
    except ValueError:
        rejected = True
    else:
        rejected = False
    assert rejected
    print(
        json.dumps(
            {
                "two_actual_evaluations": 2,
                "accepted_rows": 4,
                "naive_attempt_rows": 8,
                "conflict_rejected": rejected,
                "fault_injection": False,
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-009")
    try:
        run(spark)
    finally:
        spark.stop()
