"""Run these cells in the prepared notebook container, not on the host."""

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("ds60-notebook-session")
    .master("spark://master:7077")
    .config("spark.driver.host", "notebook")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.driver.port", "39000")
    .config("spark.driver.blockManager.port", "39001")
    .config("spark.driver.maxResultSize", "1m")
    .getOrCreate()
)
try:
    result = spark.range(100_000, numPartitions=8).selectExpr("sum(id) AS sum_id").first()
    assert result.sum_id == 4_999_950_000
    print({"application_id": spark.sparkContext.applicationId, "sum_id": result.sum_id})
finally:
    spark.stop()
