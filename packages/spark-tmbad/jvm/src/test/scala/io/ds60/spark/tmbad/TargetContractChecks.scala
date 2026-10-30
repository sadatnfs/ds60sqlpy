// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.nio.file.{Files, Path}

/** Actual pure-JVM target/parser tests when executed; no native worker or Spark session is
  * involved.
  */
object TargetContractChecks {
  private def close(actual: Double, expected: Double, tolerance: Double = 1e-6): Unit =
    require(
      math.abs(actual - expected) <= tolerance * math.max(1.0, math.abs(expected)),
      s"Expected $expected, received $actual"
    )
  private def refused(body: => Unit): Unit = {
    var failed = false
    try body
    catch { case _: IllegalArgumentException => failed = true }
    require(failed, "Invalid target/parameter document was accepted")
  }
  def main(args: Array[String]): Unit = {
    require(args.length <= 1, "Optional argument: fresh synthetic serialization fixture directory")
    val exports = scala.collection.mutable.LinkedHashMap.empty[String, String]
    val response = NativeTarget(
      Vector.empty,
      Vector("mean", "sd"),
      false,
      "declared population parameters",
      "observation only"
    )
    val model = NativeModel(
      "normal",
      "1",
      "a" * 64,
      "rows",
      Vector("y"),
      Vector("mu", "log_sigma"),
      Optimizer
        .Bounds(Vector(Double.NegativeInfinity, -20.0), Vector(Double.PositiveInfinity, 20.0)),
      "none",
      0,
      false,
      256,
      Vector(1, 2),
      Map("response" -> response),
      Map("response" -> response),
      "{}"
    )
    val identity = Json.obj().put("build_id", "b" * 64).put("binary_sha256", "c" * 64)
    identity.putObject("platform").put("os", "linux").put("arch", "arm64")
    identity
      .putObject("engine")
      .put("name", "TMBad")
      .put("version", "1.9.25")
      .put("source_sha256", "d" * 64)
    identity.putNull("jvm_sha256")
    val artifact = PreparedArtifact(
      "b" * 64,
      "/fixture/worker",
      "c" * 64,
      "arm64",
      "{}",
      Map(model.id -> model),
      None,
      None,
      Json.write(identity)
    )
    val specJson =
      """{"model_id":"normal","columns":{"y":"y"},"id_columns":["id"],"group_columns":[],"order_columns":[],"weight_column":null}"""
    val spec = FitSpecification.parse(specJson, model)
    val observations = Vector(-1.0, 1.0, 3.0, 5.0)
    val ledger = observations.zipWithIndex.foldLeft(Ledger.empty) { case (previous, (y, index)) =>
      val key = Vector(KeyAtom("long", index.toString))
      previous + Ledger.row(NativeRow(key, Vector.empty, Vector.empty, key, Vector(y), 1.0))
    }
    def raw(theta: Vector[Double]): GlobalEvaluation = {
      val variance = math.exp(2 * theta(1))
      val residuals = observations.map(y => theta(0) - y)
      val squares = residuals.map(x => x * x).sum
      val loss = 4 * theta(1) + 2 * math.log(2 * math.Pi) + 0.5 * squares / variance
      GlobalEvaluation(
        loss,
        Vector(residuals.sum / variance, 4 - squares / variance),
        4,
        0,
        4,
        ledger,
        3
      )
    }
    def options(reduction: String, l1: Boolean): FitOptions = {
      val value = Json
        .read(
          """{"initial_parameters":[0,0.2],"max_iterations":1000,"gradient_tolerance":1e-8,"function_tolerance":0,"fixed_parameters":{"log_sigma":0},"regularization":{"schema_version":1,"coordinate_system":"native_optimizer_parameters","normalization":"summed_likelihood_target","gaussian":{"mu":{"mean":1,"precision":2}},"l1":{}}}"""
        )
        .asInstanceOf[ObjectNode]
      value.put("reduction", reduction)
      if (l1) value.get("regularization").get("l1").asInstanceOf[ObjectNode].put("mu", 1.0)
      FitOptions.parse(Json.write(value), model)
    }
    var example: String = ""
    for (reduction <- Vector("sum", "weighted_mean"); l1 <- Vector(false, true)) {
      val selected = options(reduction, l1)
      val (fit, data, target) = FitTarget.solve(raw, selected.extension.get)
      require(
        fit.converged,
        s"Synthetic Gaussian target did not converge: reduction=$reduction, l1=$l1, status=${fit.status}, parameters=${fit.parameters}, projected=${fit.projectedGradientInfinityNorm}, calls=${fit.evaluations}"
      )
      close(fit.parameters(0), if (l1) 1.5 else 5.0 / 3.0)
      require(fit.parameters(1) == 0.0, "Fixed nuisance coordinate changed")
      val encoded = ModelDocument.create(model, artifact, spec, selected, fit, data, Some(target))
      require(ModelDocument.parse(encoded, artifact).converged, "Schema2 round trip failed")
      exports.put(s"schema2-${if (l1) "proximal" else "bfgs"}-$reduction.json", encoded)
      val node = Json.read(encoded)
      require(Json.integer(node, "schema_version", 2, 2) == 2, "Named fit was not schema2")
      if (l1) {
        require(
          fit.projectedGradientInfinityNorm > 0.1,
          "L1 optimum incorrectly claimed zero smooth gradient"
        )
        require(
          Json.fieldNumber(node.get("target").get("stationarity"), "summed_inf") <= 1e-8,
          "L1 stationarity did not use its subgradient"
        )
        example = encoded
      }
      val parameters = fit.parameters
      val evaluation = selected.extension.get.evaluate(
        raw(parameters),
        parameters,
        NamedRegularization.Scaling(selected.extension.get.reduction, 4)
      )
      val evaluated = Json.read(
        EvaluationDocument.create(
          model,
          artifact,
          parameters,
          selected,
          selected.extension.get,
          evaluation
        )
      )
      exports.put(
        s"evaluation-${if (l1) "proximal" else "bfgs"}-$reduction.json",
        Json.write(evaluated)
      )
      require(
        Json.text(evaluated, "weight_kind") == "observation" && Json
          .integer(evaluated, "partition_count", 1, 4096) == 3,
        "Evaluation data accounting changed"
      )
    }
    val tampered = Json.read(example).asInstanceOf[ObjectNode]
    tampered
      .get("target")
      .get("regularization")
      .get("gaussian")
      .get("mu")
      .asInstanceOf[ObjectNode]
      .put("mean", 9.0)
    refused { ModelDocument.parse(Json.write(tampered), artifact); () }
    val fakeConvergence = Json.read(example).asInstanceOf[ObjectNode]
    fakeConvergence.get("fit").asInstanceOf[ObjectNode].put("status", "maximum_iterations")
    refused { ModelDocument.parse(Json.write(fakeConvergence), artifact); () }
    val wrongFixed = Json.read(example).asInstanceOf[ObjectNode]
    wrongFixed.get("target").get("fixed_parameters").asInstanceOf[ObjectNode].put("log_sigma", 0.1)
    refused { ModelDocument.parse(Json.write(wrongFixed), artifact); () }

    for (reduction <- Vector("sum", "weighted_mean")) {
      val value = Json
        .read(
          """{"initial_parameters":[0,0.2],"l2_strength":0.2,"fixed_parameters":{"log_sigma":0},"function_tolerance":0,"gradient_tolerance":1e-8}"""
        )
        .asInstanceOf[ObjectNode]
      value.put("reduction", reduction)
      val selected = FitOptions.parse(Json.write(value), model)
      val (fit, data, target) = FitTarget.solve(raw, selected.extension.get)
      close(fit.parameters(0), if (reduction == "sum") 40.0 / 21.0 else 5.0 / 3.0)
      val document = ModelDocument.create(model, artifact, spec, selected, fit, data, Some(target))
      ModelDocument.parse(document, artifact)
      exports.put(s"schema2-legacy-fixed-$reduction.json", document)
    }
    val allFixed = FitOptions.parse(
      """{"initial_parameters":[0,0],"fixed_parameters":{"mu":2,"log_sigma":0}}""",
      model
    )
    val (fixedFit, fixedData, fixedTarget) = FitTarget.solve(raw, allFixed.extension.get)
    require(
      fixedFit.status == "all_parameters_fixed" && fixedFit.evaluations == 1,
      "All-fixed fit invented iterations"
    )
    val fixedDocument =
      ModelDocument.create(model, artifact, spec, allFixed, fixedFit, fixedData, Some(fixedTarget))
    ModelDocument.parse(fixedDocument, artifact)
    exports.put("schema2-all-fixed.json", fixedDocument)

    val declared = Json
      .obj()
      .put("schema_version", 1)
      .put("kind", "spark-tmbad-parameter-set")
      .put("package_version", "0.1.0")
      .put("model_id", "normal")
      .put("model_digest", model.digest)
      .put("parameter_set_id", "truth-1")
      .put("purpose", "simulation_truth")
    declared.set[JsonNode]("artifact_identity", identity)
    Json.putStrings(declared, "parameter_names", model.parameterNames)
    Json.putNumbers(declared, "parameters", Vector(2.0, 0.0))
    val layout = declared.putObject("layout")
    Json.putStrings(layout, "id_columns", Vector("id"));
    Json.putStrings(layout, "group_columns", Vector.empty)
    Json.putStrings(layout, "order_columns", Vector.empty)
    declared
      .putObject("provenance")
      .put("kind", "simulation_truth")
      .put("generator_source_sha256", "f" * 64)
      .put("seed", 7)
    exports.put("parameter-set-truth-input.json", Json.write(declared))
    val binding = ParameterDocument.parse(Json.write(declared), artifact)
    require(
      binding.converged.isEmpty && binding.fittedSpec.isEmpty && binding.declared.get.purpose == "simulation_truth",
      "Parameter set fabricated fitted provenance"
    )
    PredictionOptions.parse("""{"target":"response","columns":{}}""", binding, false, false)
    refused {
      PredictionOptions.parse(
        """{"target":"response","columns":{},"allow_unconverged":false}""",
        binding,
        false,
        false
      );
      ()
    }
    refused { ModelDocument.parse(Json.write(declared), artifact); () }
    declared.put("converged", true)
    refused { ParameterDocument.parse(Json.write(declared), artifact); () }
    if (args.nonEmpty) {
      val directory = Path.of(args(0))
      require(!Files.exists(directory), "Preserve prior fixture exports; choose a fresh directory")
      Files.createDirectories(directory)
      val descriptor = Json
        .obj()
        .put("id", model.id)
        .put("version", model.version)
        .put("digest", model.digest)
        .put("fit_kind", model.fitKind)
        .put("marginalization", model.marginalization)
        .put("random_dimension", model.randomDimension)
        .put("ordered", model.ordered)
        .put("max_unit_rows", model.maxUnitRows)
      Json.putStrings(descriptor, "fit_fields", model.fitFields)
      Json.putStrings(descriptor, "parameter_names", model.parameterNames)
      val bounds = descriptor.putArray("parameter_bounds")
      model.parameterNames.indices.foreach { i =>
        val pair = Json.array()
        if (model.bounds.lower(i).isFinite) pair.add(model.bounds.lower(i)) else pair.addNull()
        if (model.bounds.upper(i).isFinite) pair.add(model.bounds.upper(i)) else pair.addNull()
        bounds.add(pair)
      }
      val orders = descriptor.putArray("derivative_orders");
      model.derivativeOrders.foreach(orders.add)
      for (
        (role, targets) <- Vector("predict" -> model.prediction, "forecast" -> model.forecasting)
      ) {
        val mapping = descriptor.putObject(role)
        targets.foreach { case (name, target) =>
          val node = mapping
            .putObject(name)
            .put("needs_history", target.needsHistory)
            .put("conditioning", target.conditioning)
            .put("uncertainty", target.uncertainty)
          Json.putStrings(node, "fields", target.fields);
          Json.putStrings(node, "columns", target.columns)
        }
      }
      val manifest = Json
        .obj()
        .put("schema_version", 1)
        .put("kind", "spark-tmbad-artifact")
        .put("package_version", artifact.packageVersion)
        .put("protocol", 1)
        .put("build_id", artifact.buildId)
      manifest.set[JsonNode]("platform", identity.get("platform"));
      manifest.set[JsonNode]("engine", identity.get("engine"))
      manifest
        .putObject("binary")
        .put("path", artifact.binaryPath)
        .put("sha256", artifact.binarySha256)
      manifest.putArray("models").add(descriptor)
      require(
        Json.read(PreparedArtifact.parse(Json.write(manifest)).identityJson) == identity,
        "Exported fixture identity differs"
      )
      exports.put("synthetic-manifest.json", Json.write(manifest))
      exports.foreach { case (name, value) =>
        Files.writeString(directory.resolve(name), value + "\n")
      }
      val receipt = Json
        .obj()
        .put("kind", "synthetic-jvm-serialization-fixtures")
        .put(
          "scope",
          "Real JVM analytic-objective fits with synthetic artifact metadata; no native/Spark execution or posterior inference"
        )
        .put("binary_available", false)
        .put("native_executed", false)
        .put("spark_executed", false)
      val hashes = receipt.putObject("files")
      exports.keys.foreach(name =>
        hashes.put(name, Json.fileHash(directory.resolve(name).toAbsolutePath))
      )
      Files.writeString(directory.resolve("SCOPE.json"), Json.write(receipt) + "\n")
    }
    println(
      "{\"kind\":\"spark-tmbad-target-contracts\",\"passed\":true,\"scope\":\"pure JVM target mathematics and serialization; no native/Spark execution\"}"
    )
  }
}
