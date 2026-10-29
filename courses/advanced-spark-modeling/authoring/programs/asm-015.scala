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
      val data = Seq[java.lang.Double](-2.0, 0.0, 2.0, null).toDF("x")
      val safeSquare = udf((x: java.lang.Double) =>
        if (x == null) null else java.lang.Double.valueOf(x.doubleValue * x.doubleValue)
      )
      val output =
        data.select(col("x"), (col("x") * col("x")).as("native"), safeSquare(col("x")).as("custom"))
      output
        .collect()
        .foreach(r => require((r.isNullAt(1) && r.isNullAt(2)) || r.getDouble(1) == r.getDouble(2)))
      output.explain("extended")
      val finite = Seq(-1000.0, 0.0, 1000.0).toDF("z")
      val stable = greatest(col("z"), lit(0.0)) + log1p(exp(-abs(col("z"))))
      val values = finite.select(stable.as("loss")).as[Double].collect()
      require(values.forall(_.isFinite) && values.head == 0.0 && values.last == 1000.0)
      println("Native/UDF null parity and finite stable logits passed")
    } finally { spark.stop() }
  }
}
