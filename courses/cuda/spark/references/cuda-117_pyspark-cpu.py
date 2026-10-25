"""Bounded CPU Spark parity lab; no GPU plugin, downloads or external cluster."""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

spark = (
    SparkSession.builder.master("local[2]")
    .appName("cuda-spark-cpu-parity")
    .config("spark.ui.enabled", "false")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.rapids.sql.enabled", "false")
    .getOrCreate()
)
try:
    assert spark.sparkContext.master == "local[2]"
    schema = T.StructType([T.StructField("amount", T.LongType(), True)])
    raw = spark.createDataFrame([(2,), (None,), (5,)], schema)
    query = raw.agg(
        F.count(F.lit(1)).alias("rows"),
        F.count("amount").alias("nonnull"),
        F.sum("amount").alias("total"),
    )
    row = query.first()
    assert (row.rows, row.nonnull, row.total) == (3, 2, 7)
    empty_sum = (
        raw.filter(F.col("amount").isNull()).agg(F.sum("amount").alias("total")).first().total
    )
    assert empty_sum is None
    print("CPU PySpark null semantics:", tuple(row), "all-null sum", empty_sum)
finally:
    spark.stop()
