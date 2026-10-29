import org.apache.spark.sql.{SparkSession, DataFrame, Dataset, Encoder, Encoders}
import org.apache.spark.sql.functions._

import org.apache.spark.ml.{Estimator, Model, Transformer}
import org.apache.spark.ml.param.{ParamMap, DoubleParam}
import org.apache.spark.ml.param.shared.{HasInputCol, HasOutputCol}
import org.apache.spark.ml.util.{DefaultParamsWritable, DefaultParamsReadable, Identifiable}
import org.apache.spark.sql.types.{StructType, StructField, DoubleType}

class Shift(override val uid: String)
    extends Transformer
    with HasInputCol
    with HasOutputCol
    with DefaultParamsWritable {
  def this() = this(Identifiable.randomUID("shift"))
  val amount = new DoubleParam(this, "amount", "finite offset", (x: Double) => x.isFinite)
  setDefault(amount -> 0.0)
  def setInputCol(value: String): this.type = set(inputCol, value)
  def setOutputCol(value: String): this.type = set(outputCol, value)
  def setAmount(value: Double): this.type = set(amount, value)
  override def transformSchema(schema: StructType): StructType = {
    require(schema($(inputCol)).dataType == DoubleType, "input must be double")
    require(!schema.fieldNames.contains($(outputCol)), "output already exists")
    schema.add(StructField($(outputCol), DoubleType, schema($(inputCol)).nullable))
  }
  override def transform(data: Dataset[_]): DataFrame = {
    transformSchema(data.schema); data.withColumn($(outputCol), col($(inputCol)) + lit($(amount)))
  }
  override def copy(extra: ParamMap): Shift = defaultCopy(extra)
}
object Shift extends DefaultParamsReadable[Shift]
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
      val input = Seq[java.lang.Double](1.0, 2.0, null).toDF("x")
      val transform = new Shift().setInputCol("x").setOutputCol("shifted").setAmount(3.0)
      val directory =
        java.nio.file.Files.createTempDirectory("asm-shift-").resolve("model").toString
      transform.write.save(directory)
      val restored = Shift.load(directory)
      val expected = transform.transform(input).collect().toSeq
      require(restored.transform(input).collect().toSeq == expected)
      require(restored.uid == transform.uid)
      require(expected.head.getDouble(1) == 4.0 && expected.last.isNullAt(1))
      val invalid = try { restored.transform(input.withColumn("shifted", lit(0.0))); false }
      catch { case _: IllegalArgumentException => true }
      require(invalid)
      println("Saved/restored offset, UID, null preservation and collision rejection passed")
    } finally { spark.stop() }
  }
}
