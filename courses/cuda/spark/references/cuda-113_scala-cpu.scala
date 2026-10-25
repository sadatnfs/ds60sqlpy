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
        Seq(StructField("team", StringType, false), StructField("amount", LongType, false))
      )
      val raw = spark.createDataFrame(
        spark.sparkContext
          .parallelize(Seq(Row("A", 2L), Row("A", 4L), Row("B", 6L), Row("B", 8L)), 2),
        schema
      )
      val query = raw.groupBy("team").agg(sum("amount").as("total")).orderBy("team")
      val actual = query.collect().map(r => (r.getString(0), r.getLong(1))).toSeq
      assert(actual == Seq(("A", 6L), ("B", 14L)))
      query.explain("formatted")
      println("CPU Scala grouped totals: " + actual)
    } finally {
      spark.stop()
    }
  }
}
