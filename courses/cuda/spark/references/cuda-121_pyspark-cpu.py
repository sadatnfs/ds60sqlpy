"""Bounded CPU Spark parity lab; no GPU plugin, downloads or external cluster."""

from pyspark.sql import SparkSession
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
        [T.StructField("key", T.StringType(), False), T.StructField("value", T.LongType(), False)]
    )
    left = spark.createDataFrame([("A", 1), ("A", 2), ("B", 3)], schema).withColumnRenamed(
        "value", "left_value"
    )
    right = spark.createDataFrame([("A", 10), ("A", 20), ("C", 30)], schema).withColumnRenamed(
        "value", "right_value"
    )
    query = left.join(right, "key", "inner").orderBy("key", "left_value", "right_value")
    actual = [(r.key, r.left_value, r.right_value) for r in query.collect()]
    assert actual == [("A", 1, 10), ("A", 1, 20), ("A", 2, 10), ("A", 2, 20)]
    query.explain("formatted")
    print("CPU PySpark duplicate-key join:", actual)
finally:
    spark.stop()
