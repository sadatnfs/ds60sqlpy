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
      val salesSchema = StructType(Seq(StructField("product",StringType,false),StructField("quantity",LongType,false)))
      val priceSchema = StructType(Seq(StructField("product",StringType,false),StructField("price_cents",LongType,false)))
      val sales = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",2L),Row("A",4L),Row("B",3L)),2),salesSchema)
      val prices = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row("A",10L),Row("B",20L)),2),priceSchema)
      assert(prices.count() == prices.select("product").distinct().count())
      val query = sales.join(prices,Seq("product")).withColumn("revenue_cents",col("quantity")*col("price_cents")).groupBy("product").agg(sum("revenue_cents").as("revenue_cents")).orderBy("product")
      val actual = query.collect().map(r => (r.getString(0),r.getLong(1))).toSeq
      assert(actual == Seq(("A",60L),("B",60L)))
      query.explain("formatted")
      println("CPU Scala ETL capstone: " + actual)
    } finally {
      spark.stop()
    }
  }
}
