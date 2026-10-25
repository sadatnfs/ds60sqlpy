import org.apache.spark.sql.{Row, SparkSession}
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
      val schema = StructType(Seq(StructField("amount",LongType,true)))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(2L),Row(null),Row(5L)),2),schema)
      val row = raw.agg(count(lit(1)).as("rows"),count("amount").as("nonnull"),sum("amount").as("total")).first()
      assert((row.getLong(0),row.getLong(1),row.getLong(2)) == ((3L,2L,7L)))
      val emptySum = raw.filter(col("amount").isNull).agg(sum("amount").as("total")).first()
      assert(emptySum.isNullAt(0))
      println("CPU Scala null semantics: " + row + "; all-null sum is null")
    } finally {
      spark.stop()
    }
  }
}
