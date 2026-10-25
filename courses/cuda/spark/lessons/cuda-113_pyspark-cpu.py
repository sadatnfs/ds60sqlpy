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
    schema = T.StructType(
        [T.StructField("team", T.StringType(), False), T.StructField("amount", T.LongType(), False)]
    )
    raw = spark.createDataFrame([("A", 2), ("A", 4), ("B", 6), ("B", 8)], schema)
    query = raw.groupBy("team").agg(F.sum("amount").alias("total")).orderBy("team")
    actual = [(row.team, row.total) for row in query.collect()]
    assert actual == [("A", 6), ("B", 14)]
    query.explain("formatted")
    print("CPU PySpark grouped totals:", actual)
finally:
    spark.stop()
