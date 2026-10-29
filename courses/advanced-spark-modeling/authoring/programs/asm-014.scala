import org.apache.spark.sql.{SparkSession, DataFrame, Dataset, Encoder, Encoders}
import org.apache.spark.sql.functions._

import org.apache.spark.sql.expressions.Aggregator
case class WeightedInput(value: Option[Double], weight: Option[Double])
case class WeightedSummary(seen: Long, accepted: Long, totalWeight: Double, weightedSum: Double)
class WeightedMeanSummary extends Aggregator[WeightedInput, WeightedSummary, WeightedSummary] {
  def zero = WeightedSummary(0L, 0L, 0.0, 0.0)
  def reduce(b: WeightedSummary, x: WeightedInput): WeightedSummary = (x.value, x.weight) match {
    case (Some(v), Some(w)) if v.isFinite && w.isFinite && w >= 0 =>
      WeightedSummary(b.seen + 1, b.accepted + 1, b.totalWeight + w, b.weightedSum + v * w)
    case _ => b.copy(seen = b.seen + 1)
  }
  def merge(a: WeightedSummary, b: WeightedSummary) = WeightedSummary(
    a.seen + b.seen,
    a.accepted + b.accepted,
    a.totalWeight + b.totalWeight,
    a.weightedSum + b.weightedSum
  )
  def finish(b: WeightedSummary) = b
  def bufferEncoder: Encoder[WeightedSummary] = Encoders.product[WeightedSummary]
  def outputEncoder: Encoder[WeightedSummary] = Encoders.product[WeightedSummary]
}
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
      val input = Seq(
        WeightedInput(Some(2), Some(1)),
        WeightedInput(Some(10), Some(3)),
        WeightedInput(None, Some(2)),
        WeightedInput(Some(9), Some(-1))
      ).toDS()
      spark.udf.register("weighted_summary", udaf(new WeightedMeanSummary))
      input.createOrReplaceTempView("measurements")
      val r = spark
        .sql("SELECT weighted_summary(value,weight) AS summary FROM measurements")
        .select("summary.*")
        .as[WeightedSummary]
        .head()
      require(r == WeightedSummary(4, 2, 4, 32))
      require(r.weightedSum / r.totalWeight == 8.0)
      val rejected =
        Seq(WeightedInput(None, None)).toDS().select(new WeightedMeanSummary().toColumn).head()
      require(rejected.accepted == 0 && rejected.totalWeight == 0)
      println(
        s"$r mean=8.0 rejected=${r.seen - r.accepted}; all-invalid denominator=${rejected.totalWeight}"
      )
    } finally { spark.stop() }
  }
}
