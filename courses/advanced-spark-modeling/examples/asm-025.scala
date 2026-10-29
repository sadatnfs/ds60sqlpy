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
      val data = Seq(1.0, 2.0, 4.0).toDF("x")
      val theta = 0.5
      val terms = data.select((lit(theta) * col("x") - lit(1.0)).as("r"), col("x"))
      val row = terms
        .agg(sum(col("r") * col("r") / 2).as("loss"), sum(col("r") * col("x")).as("gradient"))
        .head()
      val local = Seq(1.0, 2.0, 4.0)
      def loss(t: Double) = local.map(x => math.pow(t * x - 1, 2) / 2).sum
      val finiteDifference = (loss(theta + 1e-5) - loss(theta - 1e-5)) / (2e-5)
      require(math.abs(row.getDouble(1) - finiteDifference) < 1e-9)
      val frozen = row.getDouble(0)
      val different = loss(theta + 0.1)
      require(frozen != different)
      println(s"loss=$frozen gradient=${row.getDouble(1)} finiteDifference=$finiteDifference")
      println("collect materializes numbers; it does not retain a global autodiff tape")
    } finally { spark.stop() }
  }
}
