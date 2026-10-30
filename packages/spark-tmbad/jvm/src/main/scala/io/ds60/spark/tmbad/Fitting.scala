package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import java.nio.file.Path
import org.apache.spark.TaskContext
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Row}
import org.apache.spark.sql.types._

private[tmbad] object GlobalPenalty {
  def value(theta: Vector[Double], strength: Double): Double = {
    require(strength.isFinite && strength >= 0, "Invalid global penalty")
    if (strength == 0.0) 0.0
    else {
      val sum = new StableSum
      val scale = math.sqrt(strength)
      theta.foreach { value =>
        val scaled = scale * value
        sum.add(0.5 * scaled * scaled)
      }
      sum.value
    }
  }
}

private[tmbad] object NumericalRejection {
  val codes: Set[String] =
    Set("DOMAIN_ERROR", "INNER_MODE_FAILURE", "BAD_CURVATURE", "NONFINITE_EVALUATION")
  def reviewed(error: NativeFailure): Boolean =
    error.verifiedTerminal && error.operation == "evaluate" && codes(error.code)
}

private[tmbad] final case class PartitionSummary(
    partition: Int,
    loss: Double,
    gradient: Vector[Double],
    rows: Long,
    units: Long,
    weight: Double,
    ledger: Ledger,
    modelDigest: String,
    buildId: String,
    rejection: Option[String]
) extends Serializable
private[tmbad] final case class GlobalEvaluation(
    value: Double,
    gradient: Vector[Double],
    rows: Long,
    units: Long,
    weight: Double,
    ledger: Ledger,
    partitions: Int = 1
)
private[tmbad] final class Accumulator(parameters: Int) {
  private val objective = new StableSum
  private val score = Array.fill(parameters)(new StableSum)
  private val weights = new StableSum
  private var rowCount = 0L
  private var unitCount = 0L
  private var fingerprint = Ledger.empty
  def account(rows: Vector[NativeRow], unit: Boolean): Unit = {
    require(rows.nonEmpty, "Cannot account an empty numerical request")
    if (unit) {
      require(
        rows.forall(_.weight == rows.head.weight),
        "A complete unit needs one consistent weight, applied once"
      )
      weights.add(rows.head.weight)
    } else rows.foreach(row => weights.add(row.weight))
    rowCount = Math.addExact(rowCount, rows.size.toLong)
    unitCount = Math.addExact(unitCount, if (unit) 1L else 0L)
    rows.foreach(row => fingerprint = fingerprint + Ledger.row(row))
  }
  def add(result: NativeEvaluation, rows: Vector[NativeRow]): Unit = {
    require(result.rowCount == rows.size, "Local native row coverage differs")
    objective.add(result.loss)
    result.gradient.indices.foreach(i => score(i).add(result.gradient(i)))
    account(rows, result.unitCount == 1)
  }
  def summary(
      partition: Int,
      model: NativeModel,
      artifact: PreparedArtifact,
      rejection: Option[String] = None
  ): PartitionSummary =
    PartitionSummary(
      partition,
      if (rejection.nonEmpty) 0.0 else objective.value,
      if (rejection.nonEmpty) Vector.fill(parameters)(0.0) else score.map(_.value).toVector,
      rowCount,
      unitCount,
      weights.value,
      fingerprint,
      model.digest,
      artifact.buildId,
      rejection
    )

}

/** Owns only a derived RDD cache. Input snapshot immutability remains the caller's contract. */
private[tmbad] final class SharedObjective private (
    val data: RDD[NativeRow],
    model: NativeModel,
    distributed: DistributedArtifact,
    options: FitOptions
) extends AutoCloseable {
  private val partitions = data.getNumPartitions
  private var baseline: Option[(Long, Long, Double, Ledger)] = None
  private var latest: Option[GlobalEvaluation] = None
  private var closed = false
  def evaluateRaw(theta: Vector[Double]): GlobalEvaluation = {
    require(!closed, "Shared objective is closed")
    model.validateTheta(theta)
    val selectedModel = model
    val selectedArtifact = distributed
    val selectedOptions = options
    val reports = data
      .mapPartitionsWithIndex { (index, input) =>
        val rows = input.buffered
        val sums = new Accumulator(theta.size)
        var worker: NativeWorker = null
        var rejection: Option[String] = None
        try {
          if (rows.hasNext) {
            selectedArtifact.artifact.requireLoadedJvm(classOf[NativeWorker])
            worker = new NativeWorker(
              selectedArtifact.artifact,
              selectedArtifact.executable,
              selectedOptions.taskTimeoutSeconds
            )
            worker.handshake()
            val batches =
              if (selectedModel.fitKind == "unit")
                Data.grouped(rows, selectedModel.maxUnitRows, selectedModel.ordered)
              else Data.batches(rows, selectedOptions.batchRows)
            batches.foreach { batch =>
              if (rejection.nonEmpty) sums.account(batch, selectedModel.fitKind == "unit")
              else
                try sums.add(NativeCalls.evaluate(worker, selectedModel, theta, batch), batch)
                catch {
                  case error: NativeFailure if NumericalRejection.reviewed(error) =>
                    rejection = Some(error.code)
                    sums.account(batch, selectedModel.fitKind == "unit")
                }
            }
            if (rejection.isEmpty) worker.finish()
          }
          Iterator(sums.summary(index, selectedModel, selectedArtifact.artifact, rejection))
        } finally if (worker != null) worker.close()
      }
      .collect()
      .toVector
    // The driver receives only one bounded numerical summary for each logical partition.
    require(
      reports.size == partitions && reports
        .map(_.partition)
        .sorted == (0 until partitions).toVector,
      "Logical partition coverage is missing or duplicated"
    )
    val loss = new StableSum
    val gradient = Array.fill(theta.size)(new StableSum)
    val weight = new StableSum
    var count = 0L; var units = 0L; var ledger = Ledger.empty
    reports.sortBy(_.partition).foreach { report =>
      require(
        report.modelDigest == model.digest && report.buildId == distributed.artifact.buildId &&
          report.gradient.size == theta.size && report.rows >= 0 && report.units >= 0 && report.weight >= 0,
        "Partition identity/dimension/count contract differs"
      )
      require(report.ledger.count == report.rows, "Partition data ledger lost row coverage")
      require(report.rejection.forall(NumericalRejection.codes), "Unreviewed partition rejection")
      if (report.rejection.isEmpty) {
        loss.add(report.loss)
        report.gradient.indices.foreach(i => gradient(i).add(report.gradient(i)))
      } else
        require(
          report.loss == 0 && report.gradient.forall(_ == 0),
          "Rejected partition leaked partial sums"
        )
      weight.add(report.weight)
      count = Math.addExact(count, report.rows); units = Math.addExact(units, report.units)
      ledger = ledger + report.ledger
    }
    require(
      count > 0 && count <= 9007199254740991L && units <= 9007199254740991L && weight.value > 0,
      "Fitting requires positive effective data and bounded exact counts"
    )
    baseline match {
      case None => baseline = Some((count, units, weight.value, ledger))
      case Some((oldCount, oldUnits, oldWeight, oldLedger)) =>
        require(
          count == oldCount && units == oldUnits && ledger == oldLedger &&
            math.abs(weight.value - oldWeight) <= 1e-12 * math.max(1.0, oldWeight),
          "Data snapshot/weight ledger changed across objective evaluations"
        )
    }
    val rejected = reports.flatMap(_.rejection).distinct.sorted
    if (rejected.nonEmpty)
      throw new Optimizer.DomainFailure(
        "Native candidate rejected after complete partition/ledger validation: " + rejected
          .mkString(",")
      )
    val result = GlobalEvaluation(loss.value, gradient.map(_.value).toVector, count, units, weight.value, ledger, partitions)
    latest = Some(result)
    result
  }
  def evaluate(theta: Vector[Double]): Optimizer.Evaluation = {
    val raw = evaluateRaw(theta)
    val denominator = if (options.reduction == "weighted_mean") raw.weight else 1.0
    val penalized = raw.value / denominator + GlobalPenalty.value(theta, options.l2Strength)
    val score = theta.indices.map(i => raw.gradient(i) / denominator + options.l2Strength * theta(i)).toVector
    require(penalized.isFinite && score.forall(_.isFinite), "Global reduction/penalty is nonfinite")
    latest = Some(raw.copy(value = penalized, gradient = score))
    Optimizer.Evaluation(penalized, score)
  }
  def accounting: GlobalEvaluation =
    latest.getOrElse(throw new IllegalStateException("Objective has not been evaluated"))
  override def close(): Unit = if (!closed) { closed = true; data.unpersist(blocking = false) }
}
private[tmbad] object SharedObjective {
  def open(
      frame: DataFrame,
      spec: FitSpecification,
      model: NativeModel,
      artifact: DistributedArtifact,
      options: FitOptions
  ): SharedObjective = {
    val projected = Data.project(
      frame,
      model.fitFields,
      spec.columns,
      spec.idColumns,
      spec.groupColumns,
      spec.orderColumns,
      spec.weightColumn
    )
    val partitions = projected.rdd.getNumPartitions
    require(
      partitions > 0 && partitions <= options.maxPartitions,
      "Input partition count exceeds the bounded summary contract"
    )
    val data =
      if (model.fitKind == "unit") Data.sortedGroups(projected.rdd, partitions) else projected.rdd
    Data.ownedCache(data)
    try {
      Data.checkUniqueIds(data)
      new SharedObjective(data, model, artifact, options)
    } catch { case error: Throwable => data.unpersist(blocking = false); throw error }
  }
}

private[tmbad] object ModelDocument {
  def create(
      model: NativeModel,
      artifact: PreparedArtifact,
      spec: FitSpecification,
      options: FitOptions,
      fit: Optimizer.Result,
      accounting: GlobalEvaluation,
    targetJson: Option[String] = None
  ): String = {
    val document = Json.obj()
    document
      .put("schema_version", if (targetJson.nonEmpty) 2 else 1)
      .put("kind", "spark-tmbad-model")
      .put("package_version", artifact.packageVersion)
      .put("model_id", model.id)
      .put("model_digest", model.digest)
    document.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
    Json.putNumbers(document, "parameters", fit.parameters)
    Json.putStrings(document, "parameter_names", model.parameterNames)
    document.set[JsonNode]("spec", Json.read(spec.json))
    val result = document.putObject("fit")
    result
      .put("converged", fit.converged)
      .put("status", fit.status)
      .put(
        "reason",
        if (fit.converged && targetJson.nonEmpty)
          "Declared constrained stationarity criterion only; no global optimum, identification or posterior-sampling claim"
        else if (fit.converged)
          "Projected first-order stationarity only; no global optimum or identifiability claim"
        else "Optimizer stopped without satisfying its stationarity criterion"
      )
      .put("iterations", fit.iterations)
      .put("objective_calls", fit.evaluations)
      .put("rejected_candidates", fit.rejectedCandidates)
      .put("loss", fit.value)
      .put("raw_gradient_inf", fit.rawGradientInfinityNorm)
      .put("projected_gradient_inf", fit.projectedGradientInfinityNorm)
      .put("row_count", accounting.rows)
      .put("unit_count", accounting.units)
      .put("weight_sum", accounting.weight)
      .put("reduction", options.reduction)
      .put("l2_strength", options.l2Strength)
    val active = result.putArray("active_bounds"); fit.activeBounds.foreach(active.add)
    result.set[JsonNode]("data_ledger", accounting.ledger.json)
    val trace = result.putArray("trace")
    fit.trace.foreach { entry =>
      val row = Json.obj()
      row
        .put("iteration", entry.iteration)
        .put("loss", entry.value)
        .put("raw_gradient_inf", entry.rawGradientInfinityNorm)
        .put("projected_gradient_inf", entry.projectedGradientInfinityNorm)
        .put("step_inf", entry.stepInfinityNorm)
        .put("objective_calls", entry.evaluations)
        .put("hessian_reset", entry.hessianReset)
      trace.add(row)
    }
    targetJson.foreach(value => document.set[JsonNode]("target", Json.read(value)))
    Json.write(document)
  }
  final case class Loaded(
      model: NativeModel,
      parameters: Vector[Double],
      spec: FitSpecification,
      converged: Boolean,
      json: String
  ) extends Serializable
  def parse(text: String, artifact: PreparedArtifact): Loaded = {
    val node = Json.read(text)
    val schemaVersion = Json.integer(node, "schema_version", 1, 2)
    Json.fields(
      node,
      Set(
        "schema_version",
        "kind",
        "package_version",
        "model_id",
        "model_digest",
        "artifact_identity",
        "parameters",
        "parameter_names",
        "spec",
        "fit"
      ) ++ (if (schemaVersion == 2) Set("target") else Set.empty[String])
    )
    require(
      Json.text(node, "kind") == "spark-tmbad-model" &&
        Json.text(node, "package_version") == artifact.packageVersion,
      "Unsupported fitted model format"
    )
    val model = artifact.model(Json.text(node, "model_id", 64))
    require(
      Json.text(node, "model_digest", 64) == model.digest && node.get("artifact_identity") == Json
        .read(artifact.identityJson),
      "Fitted model differs from the prepared artifact"
    )
    require(
      Json.strings(
        node.get("parameter_names"),
        64,
        "fitted parameter names",
        allowEmpty = false
      ) == model.parameterNames,
      "Fitted parameter names/order differ"
    )
    val parameters = Json.numbers(node.get("parameters"), 64, "fitted parameters")
    model.validateTheta(parameters)
    val spec = FitSpecification.parse(Json.write(node.get("spec")), model)
    val fit = node.get("fit")
    Json.fields(
      fit,
      Set(
        "converged",
        "status",
        "reason",
        "iterations",
        "objective_calls",
        "loss",
        "raw_gradient_inf",
        "projected_gradient_inf",
        "active_bounds",
        "row_count",
        "unit_count",
        "weight_sum",
        "trace"
      ),
      Set("reduction", "l2_strength", "data_ledger", "rejected_candidates")
    )
    val converged = Json.boolean(fit, "converged")
    Json.text(fit, "status", 128); Json.text(fit, "reason")
    Json.integer(fit, "iterations", 0, 1000); Json.integer(fit, "objective_calls", 1, 10000)
    Json.fieldNumber(fit, "loss")
    require(
      Json.fieldNumber(fit, "raw_gradient_inf") >= 0 && Json
        .fieldNumber(fit, "projected_gradient_inf") >= 0 &&
        Json.fieldNumber(fit, "weight_sum") > 0,
      "Invalid fitted score/weight diagnostics"
    )
    val rowCount = Json.integer(fit, "row_count", 1, 9007199254740991L)
    val unitCount = Json.integer(fit, "unit_count", 0, 9007199254740991L)
    require(
      unitCount <= rowCount && (if (model.fitKind == "rows") unitCount == 0 else unitCount >= 1),
      "Fitted row/unit counts contradict the model factorization"
    )
    val active =
      Json.elements(fit.get("active_bounds"), parameters.size, "active bounds").map { value =>
        require(
          value.isIntegralNumber && value.canConvertToInt && value.intValue() >= 0 && value
            .intValue() < parameters.size,
          "Active bound index is outside the parameter vector"
        )
        value.intValue()
      }
    require(active.distinct.size == active.size, "Repeated active bound index")
    Json.elements(fit.get("trace"), 1000, "fit trace").foreach { row =>
      Json.fields(
        row,
        Set(
          "iteration",
          "loss",
          "raw_gradient_inf",
          "projected_gradient_inf",
          "step_inf",
          "objective_calls",
          "hessian_reset"
        )
      )
      Json.integer(row, "iteration", 1, 1000); Json.integer(row, "objective_calls", 1, 10000)
      Json.fieldNumber(row, "loss")
      Vector("raw_gradient_inf", "projected_gradient_inf", "step_inf").foreach(name =>
        require(Json.fieldNumber(row, name) >= 0, "Negative trace score/step norm")
      )
      Json.boolean(row, "hessian_reset")
    }
    if (fit.has("rejected_candidates"))
      Json.integer(fit, "rejected_candidates", 0, Json.integer(fit, "objective_calls", 1, 10000))
    if (fit.has("reduction"))
      require(Set("sum", "weighted_mean")(Json.text(fit, "reduction")), "Unknown fitted reduction")
    if (fit.has("l2_strength"))
      require(Json.fieldNumber(fit, "l2_strength") >= 0, "Negative fitted penalty")
    if (fit.has("data_ledger")) {
      val ledger = fit.get("data_ledger")
      Json.fields(ledger, Set("count", "xor", "sum"))
      require(
        Json.integer(ledger, "count", 0, 9007199254740991L) == rowCount,
        "Fitted ledger count differs"
      )
      Vector("xor", "sum").foreach(name =>
        require(Json.text(ledger, name, 64).matches("[a-f0-9]{1,64}"), "Invalid ledger hash")
      )
    }
    if (schemaVersion == 2) FitTarget.validateDocument(node.get("target"), model, parameters, fit)
    Loaded(model, parameters, spec, converged, Json.write(node))
  }
}

private[tmbad] object Fitting {
  def shared(
      frame: DataFrame,
      spec: FitSpecification,
      model: NativeModel,
      artifact: DistributedArtifact,
      options: FitOptions
  ): String = {
    val objective = SharedObjective.open(frame, spec, model, artifact, options)
    try {
      options.extension match {
        case None =>
          val result = Optimizer.minimize(objective.evaluate, options.initial, options.optimizer, Some(model.bounds))
          ModelDocument.create(model, artifact.artifact, spec, options, result, objective.accounting)
        case Some(settings) =>
          val (result, accounting, target) = FitTarget.solve(objective.evaluateRaw, settings)
          ModelDocument.create(model, artifact.artifact, spec, options, result, accounting, Some(target))
      }
    } finally objective.close()
  }

  private def boundedGroupFit(
      rows: Vector[NativeRow],
      model: NativeModel,
      artifact: DistributedArtifact,
      options: FitOptions,
      spec: FitSpecification,
      taskDeadline: NativeDeadline
  ): String = {
    require(rows.nonEmpty, "Cannot fit an empty group")
    var accounting: Option[GlobalEvaluation] = None
    def evaluateRaw(theta: Vector[Double]): GlobalEvaluation = {
      taskDeadline.check()
      artifact.artifact.requireLoadedJvm(classOf[NativeWorker])
      val worker =
        new NativeWorker(
          artifact.artifact,
          artifact.executable,
          options.taskTimeoutSeconds,
          registerCompletionHook = false,
          sharedDeadline = Some(taskDeadline)
        )
      try {
        worker.handshake()
        val sums = new Accumulator(theta.size)
        val batches =
          if (model.fitKind == "unit") Iterator(rows)
          else Data.batches(rows.iterator, options.batchRows)
        batches.foreach(batch => sums.add(NativeCalls.evaluate(worker, model, theta, batch), batch))
        worker.finish()
        val result = sums.summary(0, model, artifact.artifact)
        require(result.weight > 0, "Independent fit has zero effective likelihood weight")
        val value = GlobalEvaluation(result.loss, result.gradient, result.rows, result.units, result.weight, result.ledger)
        accounting = Some(value)
        value
      } catch {
        case error: NativeFailure if NumericalRejection.reviewed(error) =>
          throw new Optimizer.DomainFailure("Independent native candidate rejected: " + error.code)
      } finally worker.close()
    }

    options.extension match {
      case None =>
        def evaluate(theta: Vector[Double]): Optimizer.Evaluation = {
          val raw = evaluateRaw(theta)
          val denominator = if (options.reduction == "weighted_mean") raw.weight else 1.0
          val value = raw.value / denominator + GlobalPenalty.value(theta, options.l2Strength)
          val gradient = theta.indices.map(i => raw.gradient(i) / denominator + options.l2Strength * theta(i)).toVector
          accounting = Some(raw.copy(value = value, gradient = gradient))
          Optimizer.Evaluation(value, gradient)
        }
        val fit = Optimizer.minimize(evaluate, options.initial, options.optimizer, Some(model.bounds))
        ModelDocument.create(model, artifact.artifact, spec, options, fit, accounting.get)
      case Some(settings) =>
        val (fit, accepted, target) = FitTarget.solve(evaluateRaw, settings)
        ModelDocument.create(model, artifact.artifact, spec, options, fit, accepted, Some(target))
    }
  }

  def independent(
      frame: DataFrame,
      spec: FitSpecification,
      model: NativeModel,
      artifact: DistributedArtifact,
      options: FitOptions
  ): DataFrame = {
    require(spec.groupColumns.nonEmpty, "Independent fits require explicit group columns")
    val reserved = Vector(
      "tmbad_model_json",
      "tmbad_converged",
      "tmbad_status",
      "tmbad_loss",
      "tmbad_raw_gradient_inf",
      "tmbad_projected_gradient_inf",
      "tmbad_row_count",
      "tmbad_unit_count",
      "tmbad_weight_sum"
    )
    require(
      !spec.groupColumns.exists(name =>
        reserved.exists(output => ColumnNames.equivalent(name, output))
      ),
      "Group column collides with fitted output columns"
    )
    val projected = Data.project(
      frame,
      model.fitFields,
      spec.columns,
      spec.idColumns,
      spec.groupColumns,
      spec.orderColumns,
      spec.weightColumn
    )
    require(
      projected.rdd.getNumPartitions > 0 && projected.rdd.getNumPartitions <= options.maxPartitions,
      "Independent-fit partition count exceeds its bound"
    )
    Data.checkUniqueIds(projected.rdd)
    val ordered = Data.sortedGroups(projected.rdd, projected.rdd.getNumPartitions)
    val outputSchema = StructType(
      spec.groupColumns.map(name =>
        StructField(name, frame.schema(name).dataType, nullable = false)
      ) ++ Vector(
        StructField("tmbad_model_json", StringType, nullable = false),
        StructField("tmbad_converged", BooleanType, nullable = false),
        StructField("tmbad_status", StringType, nullable = false),
        StructField("tmbad_loss", DoubleType, nullable = false),
        StructField("tmbad_raw_gradient_inf", DoubleType, nullable = false),
        StructField("tmbad_projected_gradient_inf", DoubleType, nullable = false),
        StructField("tmbad_row_count", LongType, nullable = false),
        StructField("tmbad_unit_count", LongType, nullable = false),
        StructField("tmbad_weight_sum", DoubleType, nullable = false)
      )
    )
    val rows = ordered.mapPartitions { input =>
      val taskDeadline = new NativeDeadline(options.taskTimeoutSeconds)
      val spool = new TaskSpool
      try {
        val groups = Data.grouped(
          input,
          if (model.fitKind == "unit") model.maxUnitRows else 8192,
          model.ordered
        )
        groups.foreach { group =>
          taskDeadline.check()
          val encoded = boundedGroupFit(group, model, artifact, options, spec, taskDeadline)
          val record = Json.obj()
          record.set[JsonNode]("keys", OutputRows.keys(group.head.groups))
          record.put("model", encoded); spool.append(record)
        }
        spool.result { record =>
          Json.fields(record, Set("keys", "model"))
          val keys = OutputRows.parseKeys(record.get("keys"))
          require(keys.size == spec.groupColumns.size, "Independent model group identity differs")
          val encoded = Json.text(record, "model", 1000000)
          val fit = Json.read(encoded).get("fit")
          Row.fromSeq(
            keys.map(_.sparkValue) ++ Vector[Any](
              encoded,
              Json.boolean(fit, "converged"),
              Json.text(fit, "status"),
              Json.fieldNumber(fit, "loss"),
              Json.fieldNumber(fit, "raw_gradient_inf"),
              Json.fieldNumber(fit, "projected_gradient_inf"),
              Json.integer(fit, "row_count", 1, 9007199254740991L),
              Json.integer(fit, "unit_count", 0, 9007199254740991L),
              Json.fieldNumber(fit, "weight_sum")
            )
          )
        }
      } catch { case error: Throwable => spool.close(); throw error }
    }
    frame.sparkSession.createDataFrame(rows, outputSchema)
  }
}
