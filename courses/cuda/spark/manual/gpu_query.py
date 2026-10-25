"""Explicitly acknowledged, local-only external GPU Spark semantic smoke lab."""

from __future__ import annotations

import os

if os.environ.get("DS60_GPU_SPARK_CONFIRMED") != "yes":
    raise SystemExit(
        "Read external-gpu-lab.md and acknowledge your owned prepared GPU environment first"
    )

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

spark = (
    SparkSession.builder.master("local[2]")
    .appName("ds60-owned-local-gpu-spark")
    .config("spark.ui.enabled", "false")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
try:
    if spark.sparkContext.master != "local[2]":
        raise RuntimeError("This teaching script accepts only the explicit local[2] master")
    plugins = spark.sparkContext.getConf().get("spark.plugins", "").split(",")
    if "com.nvidia.spark.SQLPlugin" not in plugins:
        raise RuntimeError("The external GPU lab requires the explicitly prepared Spark plugin")
    if spark.conf.get("spark.rapids.sql.enabled", "false").lower() != "true":
        raise RuntimeError("The GPU lab must explicitly enable the prepared plugin")
    sales_schema = T.StructType(
        [
            T.StructField("product", T.StringType(), False),
            T.StructField("quantity", T.LongType(), False),
        ]
    )
    price_schema = T.StructType(
        [
            T.StructField("product", T.StringType(), False),
            T.StructField("price_cents", T.LongType(), False),
        ]
    )
    sales = spark.createDataFrame([("A", 2), ("A", 4), ("B", 3)], sales_schema)
    prices = spark.createDataFrame([("A", 10), ("B", 20)], price_schema)
    assert prices.count() == prices.select("product").distinct().count()
    query = (
        sales.join(prices, "product")
        .withColumn("revenue_cents", F.col("quantity") * F.col("price_cents"))
        .groupBy("product")
        .agg(F.sum("revenue_cents").alias("revenue_cents"))
        .orderBy("product")
    )
    actual = [(row.product, row.revenue_cents) for row in query.collect()]
    assert actual == [("A", 60), ("B", 60)]
    query.explain("formatted")
    print("Semantic smoke passed:", actual)
    print(
        "Inspect executed operators, fallback reasons and device metrics; this is not a GPU speedup claim."
    )
finally:
    spark.stop()
