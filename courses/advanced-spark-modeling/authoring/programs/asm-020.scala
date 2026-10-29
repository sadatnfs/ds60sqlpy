import org.apache.spark.sql.{SparkSession, DataFrame, Dataset, Encoder, Encoders}
import org.apache.spark.sql.functions._

object Main {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder
      .master("local[2]")
      .appName("advanced-spark-modeling")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.sql.ansi.enabled", "true")
      .getOrCreate()
    require(spark.version == "4.0.1", "This example targets Spark 4.0.1")
    spark.sparkContext.setLogLevel("ERROR")
    import spark.implicits._
    try {
      val input = spark.range(0, 10, 1, 2)
      def query = input.select((col("id") * col("id") + lit(1L)).as("value"))
      spark.conf.set("spark.sql.codegen.wholeStage", "true")
      val generated = query
      generated.explain("codegen")
      val expected = generated.as[Long].collect().toSeq
      spark.conf.set("spark.sql.codegen.wholeStage", "false")
      val interpreted = query
      interpreted.explain("formatted")
      require(interpreted.as[Long].collect().toSeq == expected)
      require(expected == (0L until 10L).map(x => x * x + 1L))
      println(
        "Whole-stage on/off parity passed; codegen output is compiler evidence, not a timing benchmark"
      )
    } finally { spark.stop() }
  }
}
