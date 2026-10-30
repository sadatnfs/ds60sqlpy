// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.nio.file.{Files, Path}
import org.apache.spark.sql.SparkSession

/** Execute new target/evaluation/ParameterSet contracts against a real prepared native worker. */
object FeatureSparkChecks {
  private def near(actual: Double, expected: Double, tolerance: Double = 2e-5): Unit =
    require(
      math.abs(actual - expected) <= tolerance * math.max(1.0, math.abs(expected)),
      s"Expected $expected, got $actual"
    )
  private def refused(body: => Unit): Unit = {
    var rejected = false
    try body
    catch { case _: Exception => rejected = true }
    require(rejected, "Invalid feature input was accepted")
  }
  private def declared(fitted: String, id: String): String = {
    val source = Json.read(fitted)
    val value = Json
      .obj()
      .put("schema_version", 1)
      .put("kind", "spark-tmbad-parameter-set")
      .put("package_version", Json.text(source, "package_version"))
      .put("model_id", Json.text(source, "model_id"))
      .put("model_digest", Json.text(source, "model_digest"))
      .put("parameter_set_id", id)
      .put("purpose", "sensitivity")
    Vector("artifact_identity", "parameter_names", "parameters").foreach(name =>
      value.set[JsonNode](name, source.get(name))
    )
    val layout = value.putObject("layout")
    Vector("id_columns", "group_columns", "order_columns").foreach(name =>
      layout.set[JsonNode](name, source.get("spec").get(name))
    )
    value
      .putObject("provenance")
      .put("kind", "sensitivity")
      .put("reference_sha256", Json.sha(fitted.getBytes(java.nio.charset.StandardCharsets.UTF_8)))
    Json.write(value)
  }
  def main(args: Array[String]): Unit = {
    require(args.length == 2, "Usage: artifact.json report.json")
    val artifactJson = Files.readString(Path.of(args(0)))
    val artifact = PreparedArtifact.parse(artifactJson)
    val spark = SparkSession
      .builder()
      .appName("Native named target and declared parameter checks")
      .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    val report =
      Json.obj().put("kind", "spark-tmbad-modeling-target-spark-checks").put("passed", false)
    report.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
    report.put("master", spark.sparkContext.master)
    val checks = report.putArray("checks")
    def passed(name: String): Unit = { checks.add(name); println("PASSED " + name) }
    val spec =
      """{"model_id":"normal","columns":{"y":"y"},"id_columns":["id"],"group_columns":[],"order_columns":[],"weight_column":null}"""
    val normalOptions =
      """{"initial_parameters":[0,0.2],"max_iterations":1000,"gradient_tolerance":0.000001,"function_tolerance":0,"fixed_parameters":{"log_sigma":0},"regularization":{"schema_version":1,"coordinate_system":"native_optimizer_parameters","normalization":"summed_likelihood_target","gaussian":{"mu":{"mean":1,"precision":2}},"l1":{"mu":1}}}"""
    val training = spark
      .sql("SELECT * FROM VALUES (0L,-1D),(1L,1D),(2L,3D),(3L,5D) AS data(id,y)")
      .repartition(3)
      .cache()
    try {
      training.count()
      val caches = spark.sparkContext.getPersistentRDDs.keySet
      val evaluation = Json.read(
        PythonBridge.evaluateShared(training, spec, artifactJson, """{"parameters":[2,0]}""", "{}")
      )
      near(
        Json.fieldNumber(evaluation.get("loss_components"), "data_sum"),
        10 + 2 * math.log(2 * math.Pi)
      )
      val score = Json.numbers(evaluation.get("data_gradient_sum"), 64, "score")
      near(score(0), 0); near(score(1), -16)
      require(
        Json.integer(evaluation, "row_count", 1, 100) == 4 && Json
          .integer(evaluation, "partition_count", 1, 4096) == 3,
        "Fixed evaluation lost data/partition accounting"
      )
      require(
        spark.sparkContext.getPersistentRDDs.keySet == caches,
        "Evaluation changed caller cache ownership"
      )
      passed("bounded-public-fixed-evaluation-and-owned-cache")

      var saved = ""
      for (reduction <- Vector("sum", "weighted_mean")) {
        val options = Json.read(normalOptions).asInstanceOf[ObjectNode];
        options.put("reduction", reduction)
        val fitted = PythonBridge.fitShared(training, spec, artifactJson, Json.write(options))
        val loaded = ModelDocument.parse(fitted, artifact)
        require(loaded.converged, "Named Gaussian/L1 native fit did not converge")
        near(loaded.parameters(0), 1.5);
        require(loaded.parameters(1) == 0.0, "Fixed log scale moved")
        val node = Json.read(fitted)
        require(
          Json.fieldNumber(node.get("target").get("stationarity"), "summed_inf") <= 1e-6,
          "L1 fit did not meet summed KKT"
        )
        require(
          Json.fieldNumber(node.get("fit"), "projected_gradient_inf") > 0.1,
          "L1 stationarity was confused with the smooth gradient"
        )
        saved = fitted
      }
      passed("native-nonzero-gaussian-prior-exact-l1-fixed-scale-and-normalization")
      val zeroOptions = Json.read(normalOptions).asInstanceOf[ObjectNode]
      zeroOptions.get("regularization").get("l1").asInstanceOf[ObjectNode].put("mu", 20.0)
      val zero = ModelDocument.parse(
        PythonBridge.fitShared(training, spec, artifactJson, Json.write(zeroOptions)),
        artifact
      )
      require(
        zero.converged && zero.parameters(0) == 0.0,
        "Exact L1 failed to retain its certified zero"
      )
      passed("native-exact-threshold-zero")

      val weighted = spark.sql(
        "SELECT * FROM VALUES (0L,-1D,1D),(1L,1D,2D),(2L,3D,1D),(3L,5D,3D) AS data(id,y,w)"
      )
      val weightedSpec = Json.read(spec).asInstanceOf[ObjectNode];
      weightedSpec.put("weight_column", "w")
      for (partitions <- Vector(2, 6); reduction <- Vector("sum", "weighted_mean")) {
        val options = Json.read(normalOptions).asInstanceOf[ObjectNode];
        options.put("reduction", reduction)
        val fitted = ModelDocument.parse(
          PythonBridge.fitShared(
            weighted.repartition(partitions),
            Json.write(weightedSpec),
            artifactJson,
            Json.write(options)
          ),
          artifact
        )
        require(fitted.converged, "Weighted target did not converge")
        near(fitted.parameters(0), 20.0 / 9.0)
      }
      passed("unequal-weights-empty-partitions-and-once-global-prior")

      val grouped = spark
        .sql(
          "SELECT id, CASE WHEN id<4 THEN 'A' ELSE 'B' END AS series, CAST((id%4)*2-1-CASE WHEN id<4 THEN 0 ELSE 1 END AS DOUBLE) AS y FROM range(8)"
        )
        .repartition(3)
      val groupedSpec = Json.read(spec).asInstanceOf[ObjectNode]
      Json.putStrings(groupedSpec, "group_columns", Vector("series"))
      val independent = PythonBridge
        .fitGroups(grouped, Json.write(groupedSpec), artifactJson, normalOptions)
        .select("series", "tmbad_model_json")
        .collect()
      require(independent.length == 2, "Expected exactly two bounded fixture models")
      independent.foreach { row =>
        val fitted = ModelDocument.parse(row.getString(1), artifact)
        require(fitted.converged, "Independent named target did not converge")
        near(fitted.parameters(0), if (row.getString(0) == "A") 1.5 else 5.0 / 6.0)
      }
      passed("one-prior-per-independent-vector-and-task-deadline-path")

      val targets = spark.sql("SELECT id+100 AS id FROM range(3)")
      val parameterSet = declared(saved, "normal-sensitivity")
      val prediction = PythonBridge.predictAtParameters(
        targets,
        parameterSet,
        artifactJson,
        """{"target":"response","columns":{}}"""
      )
      require(
        prediction
          .schema("tmbad_mean")
          .metadata
          .getString("parameter_set_id") == "normal-sensitivity" &&
          prediction.schema("tmbad_mean").metadata.getString("purpose") == "sensitivity",
        "Declared parameter identity was not attached"
      )
      prediction
        .orderBy("id")
        .collect()
        .foreach(row => {
          near(row.getAs[Double]("tmbad_mean"), 1.5); near(row.getAs[Double]("tmbad_sd"), 1.0)
        })
      require(
        !Json.read(parameterSet).has("fit") && !Json.read(parameterSet).has("converged"),
        "Declared point fabricated fit metadata"
      )
      refused {
        PythonBridge.predictAtParameters(
          targets,
          parameterSet,
          artifactJson,
          """{"target":"response","columns":{},"allow_unconverged":true}"""
        );
        ()
      }
      passed("source-bound-parameter-set-prediction-without-fit-provenance")

      val history = spark.sql(
        "SELECT CAST(id AS BIGINT) AS id, CAST(time AS BIGINT) AS time, 'A' AS series, CAST(y AS DOUBLE) AS y FROM VALUES (0,0,-1),(1,1,0),(2,2,1) AS sample(id,time,y)"
      )
      val arSpec =
        """{"model_id":"ar1","columns":{"time":"time","y":"y"},"id_columns":["id"],"group_columns":["series"],"order_columns":["time"],"weight_column":null}"""
      val arOptions = Json.obj();
      Json.putNumbers(arOptions, "initial_parameters", Vector(0.0, 0.0, 0.5 * math.log(2.0 / 3.0)))
      val arFit =
        PythonBridge.fitShared(history.repartition(2), arSpec, artifactJson, Json.write(arOptions))
      require(ModelDocument.parse(arFit, artifact).converged, "AR1 control fit did not converge")
      val future = spark.sql("SELECT id+10 AS id, id+3 AS time, 'A' AS series FROM range(2)")
      val forecastOptions =
        """{"target":"conditional_history","history_columns":{"time":"time","y":"y"},"future_columns":{"time":"time"}}"""
      val forecast = PythonBridge
        .forecastAtParameters(
          history,
          future,
          declared(arFit, "ar1-sensitivity"),
          artifactJson,
          forecastOptions
        )
        .orderBy("id")
        .collect()
      require(
        forecast.length == 2 && forecast.map(_.getAs[Long]("id")).toVector == Vector(10L, 11L),
        "Forecast lost declared IDs"
      )
      forecast.foreach(row => {
        near(row.getAs[Double]("tmbad_mean"), 0.0);
        near(row.getAs[Double]("tmbad_variance"), 2.0 / 3.0)
      })
      passed("declared-parameter-conditional-history-forecast")

      refused {
        PythonBridge.evaluateShared(
          training,
          spec,
          artifactJson,
          """{"parameters":[2,0.1]}""",
          """{"fixed_parameters":{"log_sigma":0}}"""
        );
        ()
      }
      val mixed = Json.read(normalOptions).asInstanceOf[ObjectNode]; mixed.put("l2_strength", 0.1)
      refused { PythonBridge.fitShared(training, spec, artifactJson, Json.write(mixed)); () }
      require(
        spark.sparkContext.getPersistentRDDs.keySet == caches,
        "Feature failures changed caller cache ownership"
      )
      passed("fixed-point-mismatch-and-ambiguous-penalties-refused")
      report.put("passed", true)
    } finally {
      training.unpersist()
      Files.writeString(Path.of(args(1)), Json.write(report) + "\n")
      spark.stop()
    }
  }
}
