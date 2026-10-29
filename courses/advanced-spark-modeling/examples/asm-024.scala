import org.apache.spark.sql.{SparkSession, DataFrame, Dataset, Encoder, Encoders}
import org.apache.spark.sql.functions._

case class Dual(value: Double, tangent: Double) {
  def +(b: Dual) = Dual(value + b.value, tangent + b.tangent)
  def *(b: Dual) = Dual(value * b.value, tangent * b.value + value * b.tangent)
  def exp: Dual = { val e = math.exp(value); Dual(e, e * tangent) }
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
      def f(x: Dual): Dual = x * x + x.exp
      val input = Seq(-1.0, 0.0, 1.0).toDS()
      val result = input.map(x => { val d = f(Dual(x, 1.0)); (x, d.value, d.tangent) }).collect()
      result.foreach { case (x, value, derivative) =>
        require(math.abs(value - (x * x + math.exp(x))) < 1e-12)
        require(math.abs(derivative - (2 * x + math.exp(x))) < 1e-12)
      }
      val directional = f(Dual(1.0, 2.0))
      require(math.abs(directional.tangent - 2 * (2 + math.E)) < 1e-12)
      println(result.toSeq.toString)
      println(
        "Original bounded forward-mode implementation; no derivatives through Spark scheduling or arbitrary SQL"
      )
    } finally { spark.stop() }
  }
}
