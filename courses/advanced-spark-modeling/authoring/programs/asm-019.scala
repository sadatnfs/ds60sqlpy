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
      val source = spark.range(0, 12, 1, 2).withColumn("x", col("id").cast("double"))
      val query = source.filter(col("id") < 4).select((col("x") + lit(1.0)).as("value"))
      println("ANALYZED\n" + query.queryExecution.analyzed.treeString)
      println("OPTIMIZED\n" + query.queryExecution.optimizedPlan.treeString)
      query.explain("formatted")
      require(query.as[Double].collect().toSeq == Seq(1.0, 2.0, 3.0, 4.0))
      val opaque = udf((x: Double) => x + 1.0)
      val alternative = source.filter(col("id") < 4).select(opaque(col("x")).as("value"))
      require(alternative.as[Double].collect().toSeq == query.as[Double].collect().toSeq)
      println("CUSTOM EXPRESSION PLAN\n" + alternative.queryExecution.optimizedPlan.treeString)
      println("Equal outputs do not imply identical optimizer visibility or measured performance")
    } finally { spark.stop() }
  }
}
