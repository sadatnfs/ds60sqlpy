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
    keyed = [(0, 1.0), (1, 3.0), (1, 3.0), (1, 3.0)]
    rdd = spark.sparkContext.parallelize(keyed, 2).partitionBy(2)

    def summary(iterator):
        values = [value for _, value in iterator]
        yield (len(values), math.fsum(values))

    summaries = rdd.mapPartitions(summary).collect()
    n = sum(x[0] for x in summaries)
    total = math.fsum(x[1] for x in summaries)
    mean = total / n
    bad = math.fsum(loss / count for count, loss in summaries if count) / len(
        [1 for count, _ in summaries if count]
    )
    assert sorted(count for count, _ in summaries) == [1, 3]
    assert mean == 2.5 and bad == 2.0
    beta, lam = 2.0, 0.5
    once = total + lam * beta * beta / 2
    repeated = math.fsum(loss + lam * beta * beta / 2 for _, loss in summaries)
    assert once == 11.0 and repeated == 12.0
    terms = [1e16, 1.0, -1e16]
    naive = 0.0
    for term in terms:
        naive += term
    assert naive == 0.0 and math.fsum(terms) == 1.0
    print(
        json.dumps(
            {
                "summaries": summaries,
                "global_mean": mean,
                "wrong_mean_of_means": bad,
                "penalty_once": once,
                "penalty_per_partition": repeated,
                "naive_sum": naive,
                "accurate_sum": math.fsum(terms),
            }
        )
    )


if __name__ == "__main__":
    spark = session("asm-008")
    try:
        run(spark)
    finally:
        spark.stop()
