import org.apache.spark.sql.{SparkSession, DataFrame, Dataset, Encoder, Encoders}
import org.apache.spark.sql.functions._

import org.apache.spark.sql.expressions.Aggregator

case class Summary(n: Long, total: Double)
class SumCount extends Aggregator[Double, Summary, Summary] {
  def zero: Summary = Summary(0L, 0.0)
  def reduce(b: Summary, x: Double): Summary = Summary(b.n + 1L, b.total + x)
  def merge(a: Summary, b: Summary): Summary = Summary(a.n + b.n, a.total + b.total)
  def finish(b: Summary): Summary = b
  def bufferEncoder: Encoder[Summary] = Encoders.product[Summary]
  def outputEncoder: Encoder[Summary] = Encoders.product[Summary]
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
      val aggregate = new SumCount
      val values = Seq(1.0, 3.0, 3.0, 3.0).toDS()
      for (partitions <- Seq(1, 3)) {
        val result = values.repartition(partitions).select(aggregate.toColumn).head()
        require(result == Summary(4L, 10.0))
        println(
          s"partitions=$partitions count=${result.n} sum=${result.total} mean=${result.total / result.n}"
        )
      }
      val a = Summary(1L, 1.0); val b = Summary(2L, 6.0); val c = Summary(1L, 3.0)
      require(aggregate.merge(aggregate.zero, a) == a)
      require(
        aggregate.merge(aggregate.merge(a, b), c) == aggregate.merge(a, aggregate.merge(b, c))
      )
      val empty = Seq.empty[Double].toDS().select(aggregate.toColumn).head()
      require(empty == aggregate.zero)
      println("identity, associative fixture and empty input passed; arbitrary doubles still round")
    } finally { spark.stop() }
  }
}
