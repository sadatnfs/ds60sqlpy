package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import org.apache.spark.SparkEnv
import org.apache.spark.sql.{DataFrame, SparkSession}

/** Java/Py4J-friendly facade. Only DataFrames and bounded JSON cross this boundary. */
object PythonBridge {
  def describe(artifactJson: String, modelId: String): String = {
    val artifact = PreparedArtifact.parse(artifactJson)
    val model = artifact.model(modelId)
    val value = Json.obj()
    value.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
    value.set[JsonNode]("model", Json.read(model.json))
    Json.write(value)
  }

  def probe(session: SparkSession, artifactJson: String, modelId: String): String = {
    require(session != null, "An explicit SparkSession is required")
    val artifact = PreparedArtifact.parse(artifactJson)
    val selected = artifact.model(modelId)
    val distributed = ArtifactFiles.prepare(session.sparkContext, artifact, getClass)
    val records = session.sparkContext
      .parallelize(Vector(0), 1)
      .mapPartitions { values =>
        require(values.hasNext, "Missing explicit probe fixture")
        artifact.requireLoadedJvm(classOf[NativeWorker])
        val worker = new NativeWorker(artifact, distributed.executable, 30)
        try {
          worker.handshake(); worker.finish()
          val result = Json.obj()
          result
            .put("executor_id", SparkEnv.get.executorId)
            .put("jvm_pid", ProcessHandle.current().pid())
            .put("binary_sha256", artifact.binarySha256)
            .put("build_id", artifact.buildId)
            .put("model_digest", selected.digest)
            .put("passed", true)
          Iterator(Json.write(result))
        } finally worker.close()
      }
      .collect()
    require(records.length == 1, "Explicit native probe coverage differs")
    val result = Json.obj()
    result
      .put("passed", true)
      .put("scope", "one explicit native executor probe; not multi-node qualification")
    result.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
    result.set[JsonNode]("execution", Json.read(records.head))
    Json.write(result)
  }

  private def fitInputs(
      frame: DataFrame,
      specJson: String,
      artifactJson: String,
      optionsJson: String
  ): (NativeModel, FitSpecification, DistributedArtifact, FitOptions) = {
    require(frame != null, "Fit requires a Spark DataFrame")
    val artifact = PreparedArtifact.parse(artifactJson)
    val model = artifact.model(Json.text(Json.read(specJson), "model_id", 64))
    val specification = FitSpecification.parse(specJson, model)
    val options = FitOptions.parse(optionsJson, model)
    val distributed = ArtifactFiles.prepare(frame.sparkSession.sparkContext, artifact, getClass)
    (model, specification, distributed, options)
  }

  def fitShared(
      frame: DataFrame,
      specJson: String,
      artifactJson: String,
      optionsJson: String
  ): String = {
    val (model, spec, artifact, options) = fitInputs(frame, specJson, artifactJson, optionsJson)
    Fitting.shared(frame, spec, model, artifact, options)
  }

  def fitGroups(
      frame: DataFrame,
      specJson: String,
      artifactJson: String,
      optionsJson: String
  ): DataFrame = {
    val (model, spec, artifact, options) = fitInputs(frame, specJson, artifactJson, optionsJson)
    Fitting.independent(frame, spec, model, artifact, options)
  }

  private def sharedOutput(
      history: Option[DataFrame],
      future: DataFrame,
      modelJson: String,
      artifactJson: String,
      optionsJson: String,
      forecast: Boolean,
      conditional: Boolean
  ): DataFrame = {
    require(future != null, "Prediction/forecast requires a target DataFrame")
    val artifact = PreparedArtifact.parse(artifactJson)
    val loaded = ModelDocument.parse(modelJson, artifact)
    val options = PredictionOptions.parse(optionsJson, loaded, forecast, conditional)
    val distributed = ArtifactFiles.prepare(future.sparkSession.sparkContext, artifact, getClass)
    history.foreach(frame =>
      require(
        frame.sparkSession.sparkContext eq future.sparkSession.sparkContext,
        "History and future must belong to the same SparkContext"
      )
    )
    if (!forecast && !conditional && loaded.model.fitKind == "rows")
      Prediction.rows(future, loaded, distributed, options)
    else Prediction.joined(history, future, loaded, None, distributed, options, forecast)
  }

  def predict(
      frame: DataFrame,
      modelJson: String,
      artifactJson: String,
      optionsJson: String
  ): DataFrame =
    sharedOutput(
      None,
      frame,
      modelJson,
      artifactJson,
      optionsJson,
      forecast = false,
      conditional = false
    )

  def predictConditional(
      history: DataFrame,
      targets: DataFrame,
      modelJson: String,
      artifactJson: String,
      optionsJson: String
  ): DataFrame = {
    require(history != null, "Conditional prediction requires history")
    sharedOutput(
      Some(history),
      targets,
      modelJson,
      artifactJson,
      optionsJson,
      forecast = false,
      conditional = true
    )
  }

  def forecast(
      history: DataFrame,
      future: DataFrame,
      modelJson: String,
      artifactJson: String,
      optionsJson: String
  ): DataFrame =
    sharedOutput(
      Option(history),
      future,
      modelJson,
      artifactJson,
      optionsJson,
      forecast = true,
      conditional = false
    )

  private def independentOutput(
      history: Option[DataFrame],
      future: DataFrame,
      models: DataFrame,
      artifactJson: String,
      optionsJson: String,
      forecast: Boolean,
      conditional: Boolean
  ): DataFrame = {
    require(
      future != null && models != null,
      "Independent prediction needs target and fitted-model DataFrames"
    )
    require(
      models.sparkSession.sparkContext eq future.sparkSession.sparkContext,
      "Models and target data must belong to the same SparkContext"
    )
    history.foreach(frame =>
      require(
        frame.sparkSession.sparkContext eq future.sparkSession.sparkContext,
        "History and future must belong to the same SparkContext"
      )
    )
    val artifact = PreparedArtifact.parse(artifactJson)
    val template = Prediction.groupModelTemplate(models, artifact)
    val options =
      PredictionOptions.parse(optionsJson, template, forecast, conditional, grouped = true)
    val distributed = ArtifactFiles.prepare(future.sparkSession.sparkContext, artifact, getClass)
    Prediction.joined(history, future, template, Some(models), distributed, options, forecast)
  }

  def predictGroups(
      frame: DataFrame,
      models: DataFrame,
      artifactJson: String,
      optionsJson: String
  ): DataFrame =
    independentOutput(
      None,
      frame,
      models,
      artifactJson,
      optionsJson,
      forecast = false,
      conditional = false
    )

  def predictConditionalGroups(
      history: DataFrame,
      targets: DataFrame,
      models: DataFrame,
      artifactJson: String,
      optionsJson: String
  ): DataFrame = {
    require(history != null, "Conditional prediction requires history")
    independentOutput(
      Some(history),
      targets,
      models,
      artifactJson,
      optionsJson,
      forecast = false,
      conditional = true
    )
  }

  def forecastGroups(
      history: DataFrame,
      future: DataFrame,
      models: DataFrame,
      artifactJson: String,
      optionsJson: String
  ): DataFrame =
    independentOutput(
      Option(history),
      future,
      models,
      artifactJson,
      optionsJson,
      forecast = true,
      conditional = false
    )
}
