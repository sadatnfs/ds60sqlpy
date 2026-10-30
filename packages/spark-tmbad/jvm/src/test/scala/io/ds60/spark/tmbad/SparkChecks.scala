package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.nio.file.{Files, Path}
import org.apache.spark.sql.SparkSession

/** Numerical and lifecycle acceptance against an actual prepared worker, not a mock. */
object SparkChecks {
  private def near(actual: Double, expected: Double, tolerance: Double = 1e-5): Unit =
    require(
      math.abs(actual - expected) <= tolerance * math.max(1.0, math.abs(expected)),
      s"Expected $expected, got $actual"
    )
  private def refused(body: => Unit): Unit = {
    var rejected = false
    try body
    catch { case _: Exception => rejected = true }
    require(rejected, "Invalid input was not rejected")
  }
  def main(args: Array[String]): Unit = {
    require(args.length == 2, "Usage: artifact.json report.json")
    val artifactJson = Files.readString(Path.of(args(0)))
    val artifact = PreparedArtifact.parse(artifactJson)
    val spark = SparkSession.builder().appName("Spark TMBad native JVM contracts").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    val result = Json.obj(); result.put("kind", "spark-tmbad-native-spark-checks")
    result.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
    result.put("spark_master", spark.sparkContext.master)
    val checks = result.putArray("checks")
    def passed(name: String): Unit = { checks.add(name); println("PASSED " + name) }
    try {
      result.set[JsonNode]("probe", Json.read(PythonBridge.probe(spark, artifactJson, "normal")))
      passed("prepared-native-executor-handshake")
      val spec =
        """{"model_id":"normal","columns":{"y":"y"},"id_columns":["id"],"group_columns":[],"order_columns":[],"weight_column":null}"""
      val options =
        """{"initial_parameters":[3.0,0.8],"gradient_tolerance":0.00001,"function_tolerance":0,"batch_rows":2}"""
      val training = spark
        .sql("SELECT * FROM VALUES (0L,1D),(1L,3D),(2L,5D),(3L,7D) AS sample(id,y)")
        .repartition(3)
        .cache()
      training.count()
      val beforeCache = spark.sparkContext.getPersistentRDDs.keySet
      val fitted = PythonBridge.fitShared(training, spec, artifactJson, options)
      val parsed = ModelDocument.parse(fitted, artifact)
      require(parsed.converged, "Normal fit did not converge")
      near(parsed.parameters(0), 4); near(math.exp(2 * parsed.parameters(1)), 5)
      require(
        spark.sparkContext.getPersistentRDDs.keySet == beforeCache,
        "Fit changed caller cache ownership"
      )
      passed("shared-mle-oracle-unequal-partitions-and-owned-cache")
      val repartitioned = ModelDocument.parse(
        PythonBridge.fitShared(training.repartition(6), spec, artifactJson, options),
        artifact
      )
      parsed.parameters.zip(repartitioned.parameters).foreach { case (a, b) => near(a, b) }
      passed("partition-and-empty-partition-invariance")
      val targets = spark.sql("SELECT * FROM VALUES (10L),(11L),(12L) AS future(id)")
      val predictionOptions = """{"target":"response","columns":{},"batch_rows":1}"""
      val predictions = PythonBridge
        .predict(targets, fitted, artifactJson, predictionOptions)
        .orderBy("id")
        .collect()
      require(predictions.map(_.getLong(0)).toVector == Vector(10L, 11L, 12L))
      predictions.foreach(row => {
        near(row.getAs[Double]("tmbad_mean"), 4); near(row.getAs[Double]("tmbad_sd"), math.sqrt(5))
      })
      passed("response-free-prediction-preserves-identities")
      val collision = targets.withColumnRenamed("id", "TMBAD_MEAN")
      refused {
        PythonBridge.predict(
          collision,
          fitted,
          artifactJson,
          """{"target":"response","columns":{},"id_columns":["TMBAD_MEAN"]}"""
        );
        ()
      }
      require(
        PythonBridge
          .predict(
            collision,
            fitted,
            artifactJson,
            """{"target":"response","columns":{},"id_columns":["TMBAD_MEAN"],"output_prefix":"prediction_"}"""
          )
          .count() == 3
      )
      passed("case-insensitive-output-collision-and-explicit-prefix-control")
      val unicode = targets.withColumnRenamed("id", "TMBAD_ſD")
      require(
        !unicode.drop("tmbad_sd").columns.contains("TMBAD_ſD"),
        "Exact Spark resolver did not exercise the Unicode alias"
      )
      refused {
        PythonBridge.predict(
          unicode,
          fitted,
          artifactJson,
          """{"target":"response","columns":{},"id_columns":["TMBAD_ſD"]}"""
        );
        ()
      }
      val safeUnicode = PythonBridge.predict(
        unicode,
        fitted,
        artifactJson,
        """{"target":"response","columns":{},"id_columns":["TMBAD_ſD"],"output_prefix":"prediction_"}"""
      )
      require(
        safeUnicode.drop("prediction_sd").columns.contains("TMBAD_ſD") && safeUnicode.count() == 3
      )
      val ambiguousUnicode = spark.sql("SELECT 0L AS id, 1D AS y, 1 AS i, 2 AS `İ`")
      refused { PythonBridge.fitShared(ambiguousUnicode, spec, artifactJson, options); () }
      passed("actual-spark-unicode-resolver-collision-and-safe-prefix")
      val forecastOptions = """{"target":"response","future_columns":{},"history_columns":{}}"""
      val forecast = PythonBridge
        .forecast(training.limit(0), targets, fitted, artifactJson, forecastOptions)
        .collect()
      require(forecast.length == 3);
      forecast.foreach(row => near(row.getAs[Double]("tmbad_mean"), 4))
      refused {
        PythonBridge.forecast(training, targets, fitted, artifactJson, forecastOptions).count(); ()
      }
      refused {
        PythonBridge
          .forecast(training.limit(0), targets.limit(0), fitted, artifactJson, forecastOptions)
          .count();
        ()
      }
      passed("unconditional-forecast-empty-history-and-nonempty-future")
      val broken = Json.read(fitted).deepCopy[ObjectNode]()
      broken.get("fit").asInstanceOf[ObjectNode].put("converged", false)
      refused {
        PythonBridge.predict(targets, Json.write(broken), artifactJson, predictionOptions); ()
      }
      require(
        PythonBridge
          .predict(
            targets,
            Json.write(broken),
            artifactJson,
            """{"target":"response","columns":{},"allow_unconverged":true}"""
          )
          .count() == 3
      )
      passed("unconverged-output-refusal-and-explicit-diagnostic-override")
      for (field <- Vector("active_bounds", "trace", "data_ledger")) {
        val invalid = Json.read(fitted).deepCopy[ObjectNode]()
        invalid.get("fit").asInstanceOf[ObjectNode].put(field, "invalid")
        refused { ModelDocument.parse(Json.write(invalid), artifact); () }
      }
      val invalidCounts = Json.read(fitted).deepCopy[ObjectNode]()
      invalidCounts.get("fit").asInstanceOf[ObjectNode].put("unit_count", 5)
      refused { ModelDocument.parse(Json.write(invalidCounts), artifact); () }
      passed("persisted-diagnostic-type-and-count-refusals")
      val weighted =
        spark.sql("SELECT * FROM VALUES (0L,1D,1D),(1L,3D,2D),(2L,5D,3D) AS sample(id,y,w)")
      val weightedSpec = spec.replace("\"weight_column\":null", "\"weight_column\":\"w\"")
      val model = artifact.model("normal")
      val distribution = ArtifactFiles.prepare(spark.sparkContext, artifact, PythonBridge.getClass)
      val selectedOptions = FitOptions.parse(
        """{"initial_parameters":[2.0,0.0],"reduction":"weighted_mean","l2_strength":0.3,"batch_rows":1}""",
        model
      )
      val objective = SharedObjective.open(
        weighted.repartition(3),
        FitSpecification.parse(weightedSpec, model),
        model,
        distribution,
        selectedOptions
      )
      try {
        val actual = objective.evaluate(Vector(2, 0))
        val rows = Vector((1.0, 1.0), (3.0, 2.0), (5.0, 3.0))
        val expectedLoss = rows.map { case (y, w) =>
          w * (0.5 * math.log(2 * math.Pi) + 0.5 * math.pow(y - 2, 2))
        }.sum / 6 + 0.6
        near(actual.value, expectedLoss)
        near(actual.gradient(0), rows.map { case (y, w) => w * (2 - y) }.sum / 6 + 0.6)
        near(actual.gradient(1), rows.map { case (y, w) => w * (1 - math.pow(y - 2, 2)) }.sum / 6)
      } finally objective.close()
      passed("weighted-mean-and-global-penalty-once-oracle")
      val large = spark.sql("SELECT * FROM VALUES (0L,1E200D),(1L,1E200D) AS sample(id,y)")
      val unpenalized = SharedObjective.open(
        large,
        FitSpecification.parse(spec, model),
        model,
        distribution,
        FitOptions.parse("""{"initial_parameters":[1e200,0],"l2_strength":0}""", model)
      )
      try {
        val actual = unpenalized.evaluate(Vector(1e200, 0))
        near(actual.value, math.log(2 * math.Pi)); near(actual.gradient(0), 0);
        near(actual.gradient(1), 2)
      } finally unpenalized.close()
      passed("disabled-penalty-does-not-overflow-large-valid-parameters")
      val unitModel = artifact.model("gaussian_random_intercept")
      val unitSpec =
        """{"model_id":"gaussian_random_intercept","columns":{"y":"y"},"id_columns":["id"],"group_columns":["g"],"order_columns":[],"weight_column":"w"}"""
      val units = spark.sql(
        "SELECT * FROM VALUES (0L,'a',1D,2D),(1L,'a',2D,2D),(2L,'b',4D,1D),(3L,'b',6D,1D) AS t(id,g,y,w)"
      )
      val theta = Vector(1.0, math.log(0.8), math.log(0.5))
      val unitOptions = FitOptions.parse(
        """{"initial_parameters":[1,-0.2231435513142097,-0.6931471805599453],"reduction":"weighted_mean"}""",
        unitModel
      )
      val marginal = SharedObjective.open(
        units.repartition(3),
        FitSpecification.parse(unitSpec, unitModel),
        unitModel,
        distribution,
        unitOptions
      )
      def marginalOracle(point: Vector[Double]): Double = {
        def contribution(values: Vector[Double]): Double = {
          val variance = math.exp(2 * point(1)); val latent = math.exp(2 * point(2));
          val n = values.size
          val residual = values.map(_ - point.head)
          val quadratic = residual.map(x => x * x).sum / variance -
            latent * math.pow(residual.sum, 2) / (variance * (variance + n * latent))
          0.5 * (n * math.log(2 * math.Pi) + (n - 1) * math.log(variance) + math.log(
            variance + n * latent
          ) + quadratic)
        }
        (2 * contribution(Vector(1, 2)) + contribution(Vector(4, 6))) / 3
      }
      try {
        val actual = marginal.evaluate(theta)
        near(actual.value, marginalOracle(theta))
        theta.indices.foreach { index =>
          val step = 1e-6
          val high = theta.updated(index, theta(index) + step);
          val low = theta.updated(index, theta(index) - step)
          near(actual.gradient(index), (marginalOracle(high) - marginalOracle(low)) / (2 * step))
        }
        require(
          marginal.accounting.rows == 4 && marginal.accounting.units == 2 && marginal.accounting.weight == 3,
          "Complete-unit weights were counted per row"
        )
      } finally marginal.close()
      passed("complete-unit-weight-once-and-marginal-score-oracle")
      val groups = spark
        .sql(
          "SELECT * FROM VALUES (0L,'a',1D),(1L,'a',3D),(2L,'a',5D),(3L,'b',7D),(4L,'b',9D),(5L,'b',11D) AS sample(id,g,y)"
        )
        .repartition(2)
      val groupSpec = spec.replace("\"group_columns\":[]", "\"group_columns\":[\"g\"]")
      refused {
        PythonBridge.fitGroups(
          groups.withColumnRenamed("g", "TMBAD_MODEL_JSON"),
          groupSpec.replace("\"g\"", "\"TMBAD_MODEL_JSON\""),
          artifactJson,
          options
        );
        ()
      }
      refused {
        PythonBridge.fitGroups(
          groups.withColumnRenamed("g", "TMBAD_WEİGHT_SUM"),
          groupSpec.replace("\"g\"", "\"TMBAD_WEİGHT_SUM\""),
          artifactJson,
          options
        );
        ()
      }
      passed("case-insensitive-independent-model-column-collision")
      val models = PythonBridge.fitGroups(groups, groupSpec, artifactJson, options)
      val directory = Files.createTempDirectory("tmbad-group-models-")
      val modelPath = directory.resolve("models").toString
      models.write.parquet(modelPath)
      val restored = spark.read.parquet(modelPath)
      val groupTargets =
        spark.sql("SELECT * FROM VALUES (10L,'a'),(11L,'b'),(12L,'a') AS future(id,g)")
      val groupPredictions = PythonBridge
        .predictGroups(groupTargets, restored, artifactJson, predictionOptions)
        .orderBy("id")
        .collect()
      require(groupPredictions.length == 3)
      groupPredictions.foreach(row =>
        near(row.getAs[Double]("tmbad_mean"), if (row.getAs[String]("g") == "a") 3 else 9)
      )
      passed("independent-fits-parquet-roundtrip-and-keyed-predictions")
      training.unpersist()
      result.put("passed", true)
      result.put(
        "scope",
        "actual prepared native worker and Spark; bounded fixtures, no global-optimum or multi-node claim"
      )
      Files.writeString(Path.of(args(1)), Json.write(result) + "\n")
      println("DS60_TMBAD_SPARK_RESULT " + Json.write(result))
    } finally spark.stop()
  }
}
