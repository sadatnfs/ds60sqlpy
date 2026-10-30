// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.types.MetadataBuilder

private[tmbad] final case class PredictionLayout(
    ids: Vector[String],
    groups: Vector[String],
    order: Vector[String]
) extends Serializable
private[tmbad] final case class DeclaredOrigin(id: String, purpose: String, parameterDigest: String)
    extends Serializable
private[tmbad] final case class PredictionBinding(
    model: NativeModel,
    parameters: Vector[Double],
    layout: PredictionLayout,
    fittedSpec: Option[FitSpecification],
    converged: Option[Boolean],
    declared: Option[DeclaredOrigin]
) extends Serializable {
  require(
    converged.isDefined != declared.isDefined,
    "Prediction origin must be fitted or declared parameters"
  )
  def admit(allowUnconverged: Boolean, groupedTemplate: Boolean = false): Unit = {
    if (declared.nonEmpty)
      require(!allowUnconverged, "Declared parameters do not accept allow_unconverged")
    else
      require(
        converged.contains(true) || allowUnconverged || groupedTemplate,
        "Unconverged fit cannot predict/forecast without explicit allow_unconverged=true"
      )
  }
}
private[tmbad] object PredictionBinding {
  def fitted(value: ModelDocument.Loaded): PredictionBinding =
    PredictionBinding(
      value.model,
      value.parameters,
      PredictionLayout(value.spec.idColumns, value.spec.groupColumns, value.spec.orderColumns),
      Some(value.spec),
      Some(value.converged),
      None
    )
}

/** A distinct data-only parameter document. It never fabricates optimizer success or training
  * history.
  */
object ParameterDocument {
  private[tmbad] def parse(text: String, artifact: PreparedArtifact): PredictionBinding = {
    val node = Json.read(text)
    Json.fields(
      node,
      Set(
        "schema_version",
        "kind",
        "package_version",
        "model_id",
        "model_digest",
        "artifact_identity",
        "parameter_names",
        "parameters",
        "parameter_set_id",
        "purpose",
        "layout",
        "provenance"
      )
    )
    require(
      Json.integer(node, "schema_version", 1, 1) == 1 &&
        Json.text(node, "kind") == "spark-tmbad-parameter-set" &&
        Json.text(node, "package_version") == artifact.packageVersion,
      "Unsupported parameter-set document"
    )
    val model = artifact.model(Json.text(node, "model_id", 64))
    require(
      Json.text(node, "model_digest", 64) == model.digest &&
        node.get("artifact_identity") == Json.read(artifact.identityJson),
      "Parameter set differs from prepared artifact/model"
    )
    require(
      Json.strings(
        node.get("parameter_names"),
        64,
        "parameter names",
        allowEmpty = false
      ) == model.parameterNames,
      "Parameter-set name/order differs from prepared model"
    )
    val parameters = Json.numbers(node.get("parameters"), 64, "declared parameters")
    model.validateTheta(parameters)
    val id = Json.text(node, "parameter_set_id", 128)
    val purpose = Json.text(node, "purpose", 32)
    require(
      Set("simulation_truth", "posterior_draw", "sensitivity")(purpose),
      "Unknown parameter-set purpose"
    )
    val layout = node.get("layout")
    Json.fields(layout, Set("id_columns", "group_columns", "order_columns"))
    val keys = PredictionLayout(
      Json.strings(layout.get("id_columns"), 64, "identity columns", allowEmpty = false),
      Json.strings(layout.get("group_columns"), 64, "group columns"),
      Json.strings(layout.get("order_columns"), 64, "order columns")
    )
    require(
      model.fitKind != "unit" || keys.groups.nonEmpty,
      "Complete-unit parameter sets require group columns"
    )
    require(!model.ordered || keys.order.nonEmpty, "Ordered parameter sets require order columns")
    val provenance = node.get("provenance")
    purpose match {
      case "simulation_truth" =>
        Json.fields(
          provenance,
          Set("kind", "generator_source_sha256", "seed"),
          Set("fixture_sha256")
        )
        Json.hash(Json.text(provenance, "generator_source_sha256", 64))
        Json.integer(provenance, "seed", 0, 9007199254740991L)
        if (provenance.has("fixture_sha256")) Json.hash(Json.text(provenance, "fixture_sha256", 64))
      case "posterior_draw" =>
        Json.fields(
          provenance,
          Set("kind", "posterior_target_sha256", "sampler_receipt_sha256", "chain_id", "draw_index")
        )
        Json.hash(Json.text(provenance, "posterior_target_sha256", 64))
        Json.hash(Json.text(provenance, "sampler_receipt_sha256", 64))
        Json.text(provenance, "chain_id", 128)
        Json.integer(provenance, "draw_index", 0, 9007199254740991L)
      case "sensitivity" =>
        Json.fields(provenance, Set("kind", "reference_sha256"))
        Json.hash(Json.text(provenance, "reference_sha256", 64))
      case _ => throw new IllegalArgumentException("Unknown parameter-set purpose")
    }
    require(Json.text(provenance, "kind", 32) == purpose, "Parameter purpose/provenance differ")
    PredictionBinding(
      model,
      parameters,
      keys,
      None,
      None,
      Some(DeclaredOrigin(id, purpose, FitTarget.parameterDigest(model, parameters)))
    )
  }

  private[tmbad] def annotate(
      frame: DataFrame,
      binding: PredictionBinding,
      options: PredictionOptions,
      forecast: Boolean
  ): DataFrame = {
    val origin = binding.declared.getOrElse(
      throw new IllegalArgumentException("Expected declared parameter origin")
    )
    val target =
      (if (forecast) binding.model.forecasting else binding.model.prediction) (options.targetName)
    val columns = target.columns.map(options.prefix + _).toSet
    val metadata = new MetadataBuilder()
      .putString("parameter_set_id", origin.id)
      .putString("purpose", origin.purpose)
      .putString("parameter_digest", origin.parameterDigest)
      .build()
    frame.select(frame.schema.fieldNames.toVector.map { name =>
      if (columns(name)) Data.literal(name).as(name, metadata) else Data.literal(name)
    }: _*)
  }
}
