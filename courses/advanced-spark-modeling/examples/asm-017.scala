import org.apache.spark.sql.{SparkSession, DataFrame, Dataset, Encoder, Encoders}
import org.apache.spark.sql.functions._

import org.apache.spark.ml.{Estimator, Model, Transformer}
import org.apache.spark.ml.param.{ParamMap, DoubleParam}
import org.apache.spark.ml.param.shared.{HasInputCol, HasOutputCol}
import org.apache.spark.ml.util.{DefaultParamsWritable, DefaultParamsReadable, Identifiable}
import org.apache.spark.sql.types.{StructType, StructField, DoubleType}

class CenterModel(override val uid: String)
    extends Model[CenterModel]
    with HasInputCol
    with HasOutputCol
    with DefaultParamsWritable {
  def this() = this(Identifiable.randomUID("centerModel"))
  val center =
    new DoubleParam(this, "center", "fitted finite training mean", (x: Double) => x.isFinite)
  def configure(in: String, out: String, value: Double): this.type = {
    set(inputCol, in); set(outputCol, out); set(center, value)
  }
  override def transformSchema(schema: StructType): StructType = {
    require(schema($(inputCol)).dataType == DoubleType);
    require(!schema.fieldNames.contains($(outputCol)));
    schema.add(StructField($(outputCol), DoubleType, schema($(inputCol)).nullable))
  }
  override def transform(data: Dataset[_]): DataFrame = {
    transformSchema(data.schema); data.withColumn($(outputCol), col($(inputCol)) - lit($(center)))
  }
  override def copy(extra: ParamMap): CenterModel = defaultCopy(extra)
}
object CenterModel extends DefaultParamsReadable[CenterModel]
class CenterEstimator(override val uid: String)
    extends Estimator[CenterModel]
    with HasInputCol
    with HasOutputCol
    with DefaultParamsWritable {
  def this() = this(Identifiable.randomUID("centerEstimator"))
  def configure(in: String, out: String): this.type = { set(inputCol, in); set(outputCol, out) }
  override def transformSchema(schema: StructType): StructType = {
    require(schema($(inputCol)).dataType == DoubleType);
    require(!schema.fieldNames.contains($(outputCol)));
    schema.add(StructField($(outputCol), DoubleType, schema($(inputCol)).nullable))
  }
  override def fit(data: Dataset[_]): CenterModel = {
    transformSchema(data.schema)
    val row = data
      .agg(
        count(lit(1)).as("rows"),
        count(col($(inputCol))).as("present"),
        avg(col($(inputCol))).as("mean")
      )
      .head()
    require(
      row.getLong(0) > 0 && row.getLong(0) == row.getLong(1),
      "training input must be nonempty without nulls"
    )
    val value = row.getDouble(2); require(value.isFinite, "training mean must be finite")
    new CenterModel(uid + "_model").configure($(inputCol), $(outputCol), value).setParent(this)
  }
  override def copy(extra: ParamMap): CenterEstimator = defaultCopy(extra)
}
object CenterEstimator extends DefaultParamsReadable[CenterEstimator]
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
      val training = Seq(1.0, 2.0, 3.0).toDF("x")
      val test = Seq(10.0, 12.0).toDF("x")
      val model = new CenterEstimator().configure("x", "centered").fit(training)
      val result = model.transform(test).select("centered").as[Double].collect().toSeq
      require(result == Seq(8.0, 10.0))
      val directory =
        java.nio.file.Files.createTempDirectory("asm-center-").resolve("model").toString
      model.write.save(directory)
      require(
        CenterModel
          .load(directory)
          .transform(test)
          .select("centered")
          .as[Double]
          .collect()
          .toSeq == result
      )
      val leaked = new CenterEstimator()
        .configure("x", "centered")
        .fit(test)
        .transform(test)
        .select("centered")
        .as[Double]
        .collect()
        .toSeq
      require(leaked == Seq(-1.0, 1.0) && leaked != result)
      println("Training-only fit, fitted-model persistence and leakage counterexample passed")
    } finally { spark.stop() }
  }
}
