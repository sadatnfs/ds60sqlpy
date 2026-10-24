import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  def paidEvents(raw: org.apache.spark.sql.DataFrame): org.apache.spark.sql.DataFrame =
    throw new UnsupportedOperationException("Complete paid event filter")
  def summarize(paid: org.apache.spark.sql.DataFrame): org.apache.spark.sql.DataFrame =
    throw new UnsupportedOperationException("Complete team summary")
  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-013-attempt")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]")
      val schema = StructType(
        Seq(
          StructField("event_id", LongType, false),
          StructField("team", StringType, true),
          StructField("amount_cents", LongType, true),
          StructField("status", StringType, false)
        )
      )
      val rows = Seq(
        Row(1L, "A", 100L, "paid"),
        Row(2L, "A", null, "paid"),
        Row(3L, "B", 0L, "paid"),
        Row(4L, null, 50L, "paid"),
        Row(5L, "B", 150L, "void"),
        Row(6L, "A", 100L, "paid"),
        Row(7L, "C", null, "paid")
      )
      val raw = spark.createDataFrame(
        spark.sparkContext.parallelize(rows, 2),
        schema
      )
      println(raw.schema.simpleString)
      // Exercise 1: retain event identity and filter status.
      // Exercise 2: inspect row count, observed count and sum.
      // Exercise 3: aggregate by team and order NULL keys last.
      // Exercise 4: distinguish NULL predicates and observed zero.
      // Exercise 5: expose projected-distinct loss; repartition safely.
      // Exercise 6: compare both APIs and SQL to the golden fixture.
    } finally {
      spark.stop()
    }
  }
}
