package ds60.spark

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object Probe {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder
      .master("local[2]")
      .appName("teaching-catalyst-exact-version")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.adaptive.enabled", "false")
      .withExtensions(new TeachingExtensions)
      .getOrCreate()
    require(spark.version == "4.0.1")
    spark.sparkContext.setLogLevel("ERROR")
    import spark.implicits._
    try {
      val data = spark
        .range(0, 4)
        .select(
          when(col("id") === 0, lit(-1000.0))
            .when(col("id") === 1, lit(0.0))
            .when(col("id") === 2, lit(1000.0))
            .otherwise(lit(null).cast("double"))
            .as("z")
        )
      val outputs = Seq(true, false).map { enabled =>
        spark.conf.set("spark.sql.codegen.wholeStage", enabled.toString)
        val query = data.selectExpr("teaching_softplus(z) AS value")
        if (enabled) query.explain("codegen")
        query.collect().toSeq
      }
      require(outputs.head == outputs.last)
      require(outputs.head(0).getDouble(0) == 0.0)
      require(math.abs(outputs.head(1).getDouble(0) - math.log(2)) < 1e-14)
      require(outputs.head(2).getDouble(0) == 1000.0 && outputs.head(3).isNullAt(0))
      val counts = spark
        .range(0, 6)
        .select(
          when(col("id") === 0, lit(Long.MinValue))
            .when(col("id") === 1, lit(-1L))
            .when(col("id") === 2, lit(0L))
            .when(col("id") === 3, lit(1L))
            .when(col("id") === 4, lit(Long.MaxValue))
            .otherwise(lit(null).cast("long"))
            .as("count")
        )
      val nested = counts.selectExpr("teaching_clip_count(teaching_clip_count(count)) AS value")
      val analyzed = nested.queryExecution.analyzed.expressions
        .flatMap(_.collect { case _: ClipCount => 1 })
        .size
      val optimized = nested.queryExecution.optimizedPlan.expressions
        .flatMap(_.collect { case _: ClipCount => 1 })
        .size
      require(analyzed == 2 && optimized == 1, s"unexpected rewrite counts $analyzed -> $optimized")
      val rows = nested.collect()
      require(
        rows.take(3).forall(_.getLong(0) == 0L) && rows(3).getLong(0) == 1L && rows(4).getLong(
          0
        ) == Long.MaxValue && rows(5).isNullAt(0)
      )
      val badType = try { spark.sql("SELECT teaching_softplus(1)").collect(); false }
      catch { case _: org.apache.spark.sql.AnalysisException => true }
      val badArity = try { spark.sql("SELECT teaching_softplus(1D, 2D)").collect(); false }
      catch { case _: Exception => true }
      require(badType && badArity)
      println(
        s"CATALYST_CHECK spark=${spark.version} evaluated_codegen_parity=true rewrite=$analyzed->$optimized nulls=true types=true arity=true"
      )
    } finally { spark.stop() }
  }
}
