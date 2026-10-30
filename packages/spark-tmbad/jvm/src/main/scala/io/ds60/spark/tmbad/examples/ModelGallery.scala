package io.ds60.spark.tmbad.examples

import com.fasterxml.jackson.databind.JsonNode
import io.ds60.spark.tmbad._
import java.nio.file.{Files, Path}
import org.apache.spark.sql.{DataFrame, SparkSession}
import scala.jdk.CollectionConverters._

/** Prepared, bounded SQL fixtures shared with the Python gallery. No Python executor functions. */
object ModelGallery {
  def frame(
      spark: SparkSession,
      rows: JsonNode,
      names: Vector[String],
      ordered: Boolean
  ): DataFrame = {
    def quoted(value: String): String = "`" + value.replace("`", "``") + "`"
    def dataType(name: String): String =
      if (name == "series") "STRING"
      else if (name == "row_id" || (ordered && name == "time")) "BIGINT"
      else "DOUBLE"
    def literal(value: JsonNode): String = {
      if (value.isTextual) {
        val text = value.textValue()
        require(
          text.matches("[A-Za-z0-9_-]{1,128}"),
          "Prepared SQL gallery IDs must be simple identifiers; general DataFrame API keys are unrestricted bounded UTF-8"
        )
        "'" + text + "'"
      } else {
        Json.number(value, "fixture value")
        value.toString
      }
    }
    val values = Json.elements(rows, 8192, "fixture rows")
    if (values.isEmpty)
      spark.sql(
        "SELECT " + names
          .map(name => "CAST(NULL AS " + dataType(name) + ") AS " + quoted(name))
          .mkString(",") + " WHERE FALSE"
      )
    else {
      values.foreach(value => Json.fields(value, names.toSet))
      val projection = names
        .map(name => "CAST(" + quoted(name) + " AS " + dataType(name) + ") AS " + quoted(name))
        .mkString(",")
      val source = values
        .map(row => names.map(name => literal(row.get(name))).mkString("(", ",", ")"))
        .mkString(",")
      spark.sql(
        "SELECT " + projection + " FROM VALUES " + source + " AS fixture(" + names
          .map(quoted)
          .mkString(",") + ")"
      )
    }
  }
  private def names(row: JsonNode): Vector[String] = row.fieldNames().asScala.toVector
  private def mapping(fields: JsonNode): JsonNode = {
    val result = Json.obj();
    Json.strings(fields, 256, "fields").foreach(name => result.put(name, name)); result
  }
  def run(spark: SparkSession, artifactJson: String, recipe: JsonNode): JsonNode = {
    val modelId = Json.text(recipe, "model_id")
    val artifact = PreparedArtifact.parse(artifactJson)
    val descriptor = artifact.model(modelId)
    val ordered = Json.strings(recipe.get("order_columns"), 64, "order").nonEmpty
    val trainingRows = recipe.get("training_rows")
    val training = frame(spark, trainingRows, names(trainingRows.get(0)), ordered).repartition(2)
    val spec = Json.obj(); spec.put("model_id", modelId)
    spec.set[JsonNode]("columns", mapping(recipe.get("fit_fields")))
    Vector("id_columns", "group_columns", "order_columns").foreach(name =>
      spec.set[JsonNode](name, recipe.get(name))
    )
    spec.putNull("weight_column")
    val options =
      recipe.get("fit_options").deepCopy[com.fasterxml.jackson.databind.node.ObjectNode]()
    options.set[JsonNode]("initial_parameters", recipe.get("initial_parameters"))
    val fitted =
      PythonBridge.fitShared(training, Json.write(spec), artifactJson, Json.write(options))
    val saved = ModelDocument.parse(fitted, artifact)
    require(saved.converged, "Gallery fit did not converge; outputs withheld for " + modelId)
    val output = Json.obj(); output.put("model_id", modelId).put("model_digest", descriptor.digest)
    output.set[JsonNode]("fit", Json.read(fitted).get("fit"))
    Json.putNumbers(output, "parameters", saved.parameters)
    val observations = output.putArray("operations")
    for ((operation, forecast) <- Vector("prediction_cases" -> false, "forecast_cases" -> true)) {
      val declared = if (forecast) descriptor.forecasting else descriptor.prediction
      val cases = Json.elements(recipe.get(operation), 64, "gallery operations")
      require(
        cases.map(Json.text(_, "target")).toSet == declared.keySet,
        "Gallery does not cover every declared target for " + modelId
      )
      cases.foreach { test =>
        val targets = frame(spark, test.get("rows"), names(test.get("rows").get(0)), ordered)
        val historyRows = test.get("history_rows")
        val history = frame(spark, historyRows, names(trainingRows.get(0)), ordered)
        val target = Json.text(test, "target")
        val settings = Json.obj(); settings.put("target", target).put("output_prefix", "example_")
        settings
          .set[JsonNode](if (forecast) "future_columns" else "columns", mapping(test.get("fields")))
        settings.set[JsonNode](
          if (forecast) "future_order_columns" else "order_columns",
          test.get("order_columns")
        )
        if (forecast || declared(target).needsHistory)
          settings.set[JsonNode]("history_columns", mapping(recipe.get("fit_fields")))
        val result =
          if (forecast)
            PythonBridge.forecast(history, targets, fitted, artifactJson, Json.write(settings))
          else if (declared(target).needsHistory)
            PythonBridge.predictConditional(
              history,
              targets,
              fitted,
              artifactJson,
              Json.write(settings)
            )
          else PythonBridge.predict(targets, fitted, artifactJson, Json.write(settings))
        val records = result.orderBy("row_id").collect()
        val expectedIds = Json
          .elements(test.get("rows"), 8192, "target rows")
          .map(row => row.get("row_id").longValue())
          .sorted
        require(
          records.map(_.getAs[Long]("row_id")).toVector == expectedIds,
          "Gallery lost target identities"
        )
        records.foreach(row =>
          declared(target).columns.foreach(name =>
            require(row.getAs[Double]("example_" + name).isFinite, "Nonfinite gallery prediction")
          )
        )
        val record = Json.obj();
        record
          .put("operation", if (forecast) "forecast" else "predict")
          .put("target", target)
          .put("rows", records.length)
          .put("passed", true)
          .put("conditioning", declared(target).conditioning)
          .put("uncertainty", declared(target).uncertainty)
        observations.add(record)
      }
    }
    output.put("passed", true)
    output
  }
  def main(args: Array[String]): Unit = {
    require(
      args.length >= 2 && args.length <= 4,
      "Usage: artifact.json fixtures.json [model-id|all] [report.json]"
    )
    val artifactJson = Files.readString(Path.of(args(0)))
    val fixtureBytes = Files.readAllBytes(Path.of(args(1)))
    val fixtures = Json.read(fixtureBytes).get("cases")
    val selected =
      if (args.length >= 3 && args(2) != "all") Vector(args(2))
      else fixtures.fieldNames().asScala.toVector.sorted
    val spark = SparkSession.builder().appName("Spark TMBad Scala model gallery").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    try {
      val result = Json.obj(); result.put("kind", "spark-tmbad-scala-gallery")
      result.set[JsonNode](
        "artifact_identity",
        Json.read(PreparedArtifact.parse(artifactJson).identityJson)
      )
      result.put("fixture_sha256", Json.sha(fixtureBytes)).put("spark_version", spark.version)
      result.put(
        "scope",
        "bounded prepared fixtures; native task execution, not a scale or global-optimum claim"
      )
      val cases = result.putArray("cases")
      selected.foreach { name =>
        require(fixtures.has(name), "Unknown fixture model");
        cases.add(run(spark, artifactJson, fixtures.get(name)))
      }
      result.put("passed", true)
      val encoded = Json.write(result)
      if (args.length == 4) Files.writeString(Path.of(args(3)), encoded + "\n")
      println("DS60_TMBAD_SCALA_GALLERY " + encoded)
    } finally spark.stop()
  }
}
