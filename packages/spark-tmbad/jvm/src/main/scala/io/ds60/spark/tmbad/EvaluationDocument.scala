// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode

private[tmbad] object EvaluationDocument {
  def create(model: NativeModel, artifact: PreparedArtifact, parameters: Vector[Double],
             options: FitOptions, settings: FitTarget.Settings, evaluated: FitTarget.Evaluated): String = {
    val data = evaluated.data
    val node = Json.obj().put("schema_version", 1).put("kind", "spark-tmbad-evaluation")
      .put("package_version", artifact.packageVersion).put("model_id", model.id)
      .put("model_digest", model.digest).put("parameter_digest", FitTarget.parameterDigest(model, parameters))
      .put("target_spec_digest", settings.targetDigest).put("reduction", options.reduction)
      .put("weight_kind", if (model.fitKind == "unit") "unit" else "observation")
      .put("row_count", data.rows).put("unit_count", data.units).put("weight_sum", data.weight)
      .put("partition_count", data.partitions).put("summed_kkt_inf", evaluated.summedKkt)
      .put("reduced_kkt_inf", evaluated.reducedKkt)
    node.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
    Json.putStrings(node, "parameter_names", model.parameterNames)
    Json.putNumbers(node, "parameters", parameters)
    Json.putNumbers(node, "data_gradient_sum", data.gradient)
    Json.putNumbers(node, "smooth_gradient_sum", evaluated.smooth.rawGradient)
    Json.putNumbers(node, "smooth_gradient_reduced", evaluated.smooth.gradient)
    node.set[JsonNode]("data_ledger", data.ledger.json)
    node.set[JsonNode]("loss_components", evaluated.components)
    node.set[JsonNode]("fixed_parameters", Json.read(settings.fixedJson))
    val intervals = node.putArray("l1_subgradient_sum")
    settings.plan.rawL1Subgradients(parameters).foreach { case (lo, hi) =>
      val pair = Json.array(); pair.add(lo); pair.add(hi); intervals.add(pair)
    }
    Json.write(node)
  }
}
