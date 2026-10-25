import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder()
      .master("local[2]")
      .appName("cuda-spark-cpu-parity")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC")
      .config("spark.rapids.sql.enabled", "false")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]")
      val schema = StructType(
        Seq(StructField("key", StringType, false), StructField("value", LongType, false))
      )
      val left = spark
        .createDataFrame(
          spark.sparkContext.parallelize(Seq(Row("A", 1L), Row("A", 2L), Row("B", 3L)), 2),
          schema
        )
        .withColumnRenamed("value", "left_value")
      val right = spark
        .createDataFrame(
          spark.sparkContext.parallelize(Seq(Row("A", 10L), Row("A", 20L), Row("C", 30L)), 2),
          schema
        )
        .withColumnRenamed("value", "right_value")
      val query = left.join(right, Seq("key"), "inner").orderBy("key", "left_value", "right_value")
      val actual = query.collect().map(r => (r.getString(0), r.getLong(1), r.getLong(2))).toSeq
      assert(actual == Seq(("A", 1L, 10L), ("A", 1L, 20L), ("A", 2L, 10L), ("A", 2L, 20L)))
      query.explain("formatted")
      println("CPU Scala duplicate-key join: " + actual)
    } finally {
      spark.stop()
    }
  }
}
