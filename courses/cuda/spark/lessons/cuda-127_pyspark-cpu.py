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
    actual = [(r.product, r.revenue_cents) for r in query.collect()]
    assert actual == [("A", 60), ("B", 60)]
    query.explain("formatted")
    print("CPU PySpark ETL capstone:", actual)
finally:
    spark.stop()
