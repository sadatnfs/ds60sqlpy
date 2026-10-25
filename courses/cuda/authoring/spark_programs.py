"""Bounded ordinary Spark Scala/PySpark parity examples, with no GPU plugin."""

PYSPARK_BODY = {
    49: """schema = T.StructType([T.StructField("team", T.StringType(), False), T.StructField("amount", T.LongType(), False)])
raw = spark.createDataFrame([("A", 2), ("A", 4), ("B", 6), ("B", 8)], schema)
query = raw.groupBy("team").agg(F.sum("amount").alias("total")).orderBy("team")
actual = [(row.team, row.total) for row in query.collect()]
assert actual == [("A", 6), ("B", 14)]
query.explain("formatted")
print("CPU PySpark grouped totals:", actual)""",
    53: """schema = T.StructType([T.StructField("amount", T.LongType(), True)])
raw = spark.createDataFrame([(2,), (None,), (5,)], schema)
query = raw.agg(F.count(F.lit(1)).alias("rows"), F.count("amount").alias("nonnull"), F.sum("amount").alias("total"))
row = query.first()
assert (row.rows, row.nonnull, row.total) == (3, 2, 7)
empty_sum = raw.filter(F.col("amount").isNull()).agg(F.sum("amount").alias("total")).first().total
assert empty_sum is None
print("CPU PySpark null semantics:", tuple(row), "all-null sum", empty_sum)""",
    57: """schema = T.StructType([T.StructField("key", T.StringType(), False), T.StructField("value", T.LongType(), False)])
left = spark.createDataFrame([("A", 1), ("A", 2), ("B", 3)], schema).withColumnRenamed("value", "left_value")
right = spark.createDataFrame([("A", 10), ("A", 20), ("C", 30)], schema).withColumnRenamed("value", "right_value")
query = left.join(right, "key", "inner").orderBy("key", "left_value", "right_value")
actual = [(r.key, r.left_value, r.right_value) for r in query.collect()]
assert actual == [("A", 1, 10), ("A", 1, 20), ("A", 2, 10), ("A", 2, 20)]
query.explain("formatted")
print("CPU PySpark duplicate-key join:", actual)""",
    63: """sales_schema = T.StructType([T.StructField("product", T.StringType(), False), T.StructField("quantity", T.LongType(), False)])
price_schema = T.StructType([T.StructField("product", T.StringType(), False), T.StructField("price_cents", T.LongType(), False)])
sales = spark.createDataFrame([("A", 2), ("A", 4), ("B", 3)], sales_schema)
prices = spark.createDataFrame([("A", 10), ("B", 20)], price_schema)
assert prices.count() == prices.select("product").distinct().count()
query = sales.join(prices, "product").withColumn("revenue_cents", F.col("quantity")*F.col("price_cents")).groupBy("product").agg(F.sum("revenue_cents").alias("revenue_cents")).orderBy("product")
actual = [(r.product, r.revenue_cents) for r in query.collect()]
assert actual == [("A", 60), ("B", 60)]
query.explain("formatted")
print("CPU PySpark ETL capstone:", actual)""",
}
SCALA_BODY = {
    49: """val schema = StructType(Seq(StructField("team", StringType, false), StructField("amount", LongType, false)))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",2L),Row("A",4L),Row("B",6L),Row("B",8L)),2),schema)
val query = raw.groupBy("team").agg(sum("amount").as("total")).orderBy("team")
val actual = query.collect().map(r => (r.getString(0),r.getLong(1))).toSeq
assert(actual == Seq(("A",6L),("B",14L)))
query.explain("formatted")
println("CPU Scala grouped totals: " + actual)""",
    53: """val schema = StructType(Seq(StructField("amount",LongType,true)))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(2L),Row(null),Row(5L)),2),schema)
val row = raw.agg(count(lit(1)).as("rows"),count("amount").as("nonnull"),sum("amount").as("total")).first()
assert((row.getLong(0),row.getLong(1),row.getLong(2)) == ((3L,2L,7L)))
val emptySum = raw.filter(col("amount").isNull).agg(sum("amount").as("total")).first()
assert(emptySum.isNullAt(0))
println("CPU Scala null semantics: " + row + "; all-null sum is null")""",
    57: """val schema = StructType(Seq(StructField("key",StringType,false),StructField("value",LongType,false)))
val left = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",1L),Row("A",2L),Row("B",3L)),2),schema).withColumnRenamed("value","left_value")
val right = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",10L),Row("A",20L),Row("C",30L)),2),schema).withColumnRenamed("value","right_value")
val query = left.join(right,Seq("key"),"inner").orderBy("key","left_value","right_value")
val actual = query.collect().map(r => (r.getString(0),r.getLong(1),r.getLong(2))).toSeq
assert(actual == Seq(("A",1L,10L),("A",1L,20L),("A",2L,10L),("A",2L,20L)))
query.explain("formatted")
println("CPU Scala duplicate-key join: " + actual)""",
    63: """val salesSchema = StructType(Seq(StructField("product",StringType,false),StructField("quantity",LongType,false)))
val priceSchema = StructType(Seq(StructField("product",StringType,false),StructField("price_cents",LongType,false)))
val sales = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",2L),Row("A",4L),Row("B",3L)),2),salesSchema)
val prices = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",10L),Row("B",20L)),2),priceSchema)
assert(prices.count() == prices.select("product").distinct().count())
val query = sales.join(prices,Seq("product")).withColumn("revenue_cents",col("quantity")*col("price_cents")).groupBy("product").agg(sum("revenue_cents").as("revenue_cents")).orderBy("product")
val actual = query.collect().map(r => (r.getString(0),r.getLong(1))).toSeq
assert(actual == Seq(("A",60L),("B",60L)))
query.explain("formatted")
println("CPU Scala ETL capstone: " + actual)""",
}


def pyspark_program(n):
    header = '''"""Bounded CPU Spark parity lab; no GPU plugin, downloads or external cluster."""
from pyspark.sql import SparkSession
from pyspark.sql import types as T

spark = (SparkSession.builder.master("local[2]").appName("cuda-spark-cpu-parity")
    .config("spark.ui.enabled", "false")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.rapids.sql.enabled", "false")
    .getOrCreate())
try:
    assert spark.sparkContext.master == "local[2]"
'''
    if "F." in PYSPARK_BODY[n]:
        header = header.replace(
            "from pyspark.sql import SparkSession\n",
            "from pyspark.sql import SparkSession\nfrom pyspark.sql import functions as F\n",
        )
    return (
        header
        + "\n".join("    " + line for line in PYSPARK_BODY[n].splitlines())
        + "\nfinally:\n    spark.stop()\n"
    )


def scala_program(n):
    header = """import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().master("local[2]").appName("cuda-spark-cpu-parity")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC")
      .config("spark.rapids.sql.enabled", "false")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]")
"""
    return (
        header
        + "\n".join("      " + line for line in SCALA_BODY[n].splitlines())
        + "\n    } finally {\n      spark.stop()\n    }\n  }\n}\n"
    )
