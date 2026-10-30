package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.ds60.spark.tmbad.examples.ModelGallery
import java.nio.file.{Files, Path}
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.lit
import scala.jdk.CollectionConverters._

/** Real precision-limited native trials, never synthetic objective values for rejected points. */
object CandidateChecks {
  def main(args: Array[String]): Unit = {
    require(args.length == 3, "Usage: artifact.json fixtures.json report.json")
    val encoded = Files.readString(Path.of(args(0)))
    val artifact = PreparedArtifact.parse(encoded)
    val fixtureBytes = Files.readAllBytes(Path.of(args(1)))
    val fixtures = Json.read(fixtureBytes).get("cases")
    val recipe = fixtures.get("gaussian_random_intercept_laplace")
    val spark = SparkSession
      .builder()
      .appName("Native scientific candidate rejection contracts")
      .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    try {
      val shared = ModelGallery.run(spark, encoded, recipe)
      val exact = ModelGallery.run(spark, encoded, fixtures.get("gaussian_random_intercept"))
      require(
        Json.integer(shared.get("fit"), "rejected_candidates", 1, 10000) >= 1,
        "Precision-limited trial was not actually exercised"
      )
      val observed = Json.numbers(shared.get("parameters"), 64, "parameters")
      val reference = Json.numbers(exact.get("parameters"), 64, "exact parameters")
      require(
        observed.zip(reference).forall { case (a, b) => math.abs(a - b) < 1e-4 },
        "Recovered Laplace MLE differs from its exact Gaussian marginal oracle"
      )
      require(
        math.abs(
          Json.fieldNumber(shared.get("fit"), "loss") - Json.fieldNumber(exact.get("fit"), "loss")
        ) < 1e-5
      )
      val trainingRows = recipe.get("training_rows")
      val training = ModelGallery.frame(
        spark,
        trainingRows,
        trainingRows.get(0).fieldNames().asScala.toVector,
        false
      )
      val spec =
        """{"model_id":"gaussian_random_intercept_laplace","columns":{"y":"y"},"id_columns":["row_id"],"group_columns":["series"],"order_columns":[],"weight_column":null}"""
      val model = artifact.model("gaussian_random_intercept_laplace")
      val options = recipe.get("fit_options").deepCopy[ObjectNode]()
      options.set[JsonNode]("initial_parameters", recipe.get("initial_parameters"))
      val parsedOptions = FitOptions.parse(Json.write(options), model)
      val distributed = ArtifactFiles.prepare(spark.sparkContext, artifact, PythonBridge.getClass)
      val objective = SharedObjective.open(
        training.repartition(3),
        FitSpecification.parse(spec, model),
        model,
        distributed,
        parsedOptions
      )
      var invalid = Vector.empty[Double]
      try {
        val before = objective.evaluate(parsedOptions.initial)
        val accounting = objective.accounting
        invalid = model.bounds.project(
          parsedOptions.initial.indices
            .map(i => parsedOptions.initial(i) - before.gradient(i))
            .toVector
        )
        val mixed = model.bounds.project(
          parsedOptions.initial.indices
            .map(i => parsedOptions.initial(i) - 0.25 * before.gradient(i))
            .toVector
        )
        var rejected = false
        try objective.evaluate(mixed)
        catch { case _: Optimizer.DomainFailure => rejected = true }
        require(
          rejected && objective.accounting == accounting,
          "Rejected trial replaced accepted accounting/value"
        )
        val recoverable = model.bounds.project(
          parsedOptions.initial.indices
            .map(i => parsedOptions.initial(i) - before.gradient(i) / 64.0)
            .toVector
        )
        require(
          objective.evaluate(recoverable).value < before.value,
          "Certifiable 1/64 step did not recover a decreasing objective"
        )
        val after = objective.evaluate(parsedOptions.initial)
        require(
          math
            .abs(before.value - after.value) < 1e-10 && before.gradient.zip(after.gradient).forall {
            case (a, b) => math.abs(a - b) < 1e-10
          }
        )
      } finally objective.close()
      val invalidOptions = options.deepCopy[ObjectNode]()
      Json.putNumbers(invalidOptions, "initial_parameters", invalid)
      var refusedInitial = false
      try PythonBridge.fitShared(training, spec, encoded, Json.write(invalidOptions))
      catch { case _: Optimizer.DomainFailure => refusedInitial = true }
      require(refusedInitial, "Invalid initial evaluation must remain fatal")
      val independentSpec = spec.replace("\"weight_column\":null", "\"weight_column\":\"weight\"")
      val single =
        training.filter(Data.literal("series") === lit("s0")).withColumn("weight", lit(10.0))
      val groupRows =
        PythonBridge.fitGroups(single, independentSpec, encoded, Json.write(options)).collect()
      require(groupRows.length == 1)
      val independent = Json.read(groupRows.head.getAs[String]("tmbad_model_json"))
      val fit = independent.get("fit")
      require(
        Json.boolean(fit, "converged") && Json.integer(fit, "rejected_candidates", 1, 10000) >= 1
      )
      val estimates = Json.numbers(independent.get("parameters"), 64, "group parameters")
      require(math.abs(estimates.head - 0.6417418047591362) < 1e-4)
      require(math.abs(math.exp(2 * estimates(1)) - 0.19880159310765158) < 1e-4)
      require(math.exp(estimates(2)) < 1e-3)
      val result = Json.obj();
      result.put("kind", "spark-tmbad-real-candidate-recovery").put("passed", true)
      result
        .put("fixture_sha256", Json.sha(fixtureBytes))
        .put("mixed_trial_discarded", true)
        .put("recovering_step", 1.0 / 64.0)
      result.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
      result.set[JsonNode]("shared_laplace", shared); result.set[JsonNode]("shared_exact", exact)
      result.set[JsonNode]("independent_fit", fit)
      result.put(
        "scope",
        "real shared MLE recovery and fresh independent objective sessions; one-group variance component is a boundary estimate, not identified interior random-effect inference"
      )
      Files.writeString(Path.of(args(2)), Json.write(result) + "\n")
      println("DS60_TMBAD_CANDIDATE_RESULT " + Json.write(result))
    } finally spark.stop()
  }
}
