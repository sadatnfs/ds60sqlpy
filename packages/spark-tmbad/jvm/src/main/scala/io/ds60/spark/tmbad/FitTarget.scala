// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import java.io.{ByteArrayOutputStream, DataOutputStream}
import java.nio.charset.StandardCharsets
import scala.jdk.CollectionConverters._

/** Resolved named target and truthful optimizer metadata; numerical data remain in the existing reducer. */
object FitTarget {
  val NewNormalization = "summed_likelihood_target"
  val LegacyNormalization = "legacy_post_reduction_l2"

  def domain(model: NativeModel): NamedRegularization.Domain =
    NamedRegularization.Domain(model.parameterNames, model.bounds.lower, model.bounds.upper)

  private def nonnegative(value: Double, label: String): Double = {
    require(value.isFinite && value >= 0.0, s"Invalid $label"); value
  }
  private def close(actual: Double, expected: Double, label: String): Unit =
    require(actual.isFinite && expected.isFinite &&
      math.abs(actual - expected) <= 1e-9 * math.max(1.0, math.max(math.abs(actual), math.abs(expected))),
      s"Inconsistent $label")
  private def norm(values: Vector[Double]): Double = values.map(math.abs).max
  private def projected(point: Vector[Double], gradient: Vector[Double], bounds: NamedRegularization.Domain): Vector[Double] =
    point.indices.map { i =>
      if (bounds.equality(i) || (point(i) == bounds.lower(i) && gradient(i) > 0.0) ||
          (point(i) == bounds.upper(i) && gradient(i) < 0.0)) 0.0 else gradient(i)
    }.toVector

  def digest(planDigest: String, normalization: String, legacyL2: Double): String = {
    val buffer = new ByteArrayOutputStream()
    val stream = new DataOutputStream(buffer)
    def text(value: String): Unit = {
      val bytes = value.getBytes(StandardCharsets.UTF_8)
      stream.writeInt(bytes.length); stream.write(bytes)
    }
    text("spark-tmbad-fit-target-v2"); text(planDigest); text(normalization)
    stream.writeDouble(if (legacyL2 == 0.0) 0.0 else legacyL2)
    stream.close(); Json.sha(buffer.toByteArray)
  }

  def parameterDigest(model: NativeModel, parameters: Vector[Double]): String = {
    model.validateTheta(parameters)
    val buffer = new ByteArrayOutputStream()
    val stream = new DataOutputStream(buffer)
    def text(value: String): Unit = {
      val bytes = value.getBytes(StandardCharsets.UTF_8)
      stream.writeInt(bytes.length); stream.write(bytes)
    }
    text("spark-tmbad-parameters-v1"); text(model.digest); stream.writeInt(parameters.size)
    parameters.foreach(value => stream.writeDouble(if (value == 0.0) 0.0 else value))
    stream.close(); Json.sha(buffer.toByteArray)
  }

  private[tmbad] final case class Evaluated(
      data: GlobalEvaluation,
      smooth: NamedRegularization.SmoothEvaluation,
      l1: Double,
      legacyL2Reduced: Double,
      totalReduced: Double,
      summedKkt: Double,
      reducedKkt: Double
  ) {
    def components: JsonNode = Json.obj()
      .put("data_sum", data.value)
      .put("gaussian_quadratic_sum", smooth.gaussianQuadratic)
      .put("gaussian_log_normalizer_sum", smooth.gaussianNormalizer)
      .put("l1_sum", l1)
      .put("legacy_l2_reduced", legacyL2Reduced)
      .put("denominator", smooth.scaling.denominator)
      .put("total_reduced", totalReduced)
  }

  final case class Settings(
      plan: NamedRegularization.Plan,
      regularizationJson: Option[String],
      fixedJson: String,
      method: String,
      proximal: ProximalGradient.Settings,
      base: FitOptions
  ) extends Serializable {
    val normalization: String = if (regularizationJson.nonEmpty) NewNormalization else LegacyNormalization
    val targetDigest: String = digest(plan.digest, normalization, base.l2Strength)
    def reduction: NamedRegularization.Reduction =
      if (base.reduction == "weighted_mean") NamedRegularization.WeightedMean else NamedRegularization.Sum
    def effectiveInitial: Vector[Double] = {
      plan.originalDomain.check(base.initial)
      plan.domain.effectiveInitial(base.initial)
    }
    def solverJson: JsonNode = {
      val node = Json.obj().put("method", method)
        .put("max_iterations", base.maxIterations)
        .put("max_evaluations", base.optimizer.maxEvaluations)
        .put("max_backtracks", base.maxLineSearch)
      if (method == "bfgs") {
        node.put("gradient_tolerance", base.gradientTolerance)
          .put("function_tolerance", base.functionTolerance)
      } else {
        node.put("kkt_tolerance", proximal.kktTolerance)
          .put("kkt_tolerance_units", "summed_target")
          .put("initial_step", proximal.initialStep).put("maximum_step", proximal.maximumStep)
          .put("minimum_step", proximal.minimumStep).put("backtrack_factor", proximal.backtrackFactor)
          .put("step_growth", proximal.stepGrowth).put("relative_step_tolerance", proximal.relativeStepTolerance)
      }
      node
    }
    private[tmbad] def evaluate(data: GlobalEvaluation, theta: Vector[Double], scaling: NamedRegularization.Scaling): Evaluated = {
      plan.domain.check(theta)
      val raw = NamedRegularization.RawEvaluation(data.value, data.gradient, data.weight)
      val named = plan.smooth(raw, theta, scaling)
      val legacy = if (regularizationJson.isEmpty) GlobalPenalty.value(theta, base.l2Strength) else 0.0
      val smooth = if (legacy == 0.0 && base.l2Strength == 0.0) named else {
        val prior = theta.map(value => base.l2Strength * value * scaling.denominator)
        val gradient = theta.indices.map(i => data.gradient(i) + prior(i)).toVector
        NamedRegularization.SmoothEvaluation(data.value + legacy * scaling.denominator, gradient,
          data.value, data.gradient, Vector.fill(theta.size)(0.0), 0.0, 0.0, scaling)
      }
      val l1 = plan.rawL1Value(theta)
      val total = if (regularizationJson.nonEmpty) plan.composite(smooth, theta)
                  else data.value / scaling.denominator + legacy
      require(total.isFinite, "Target objective exceeds finite arithmetic")
      val residual = norm(plan.rawKkt(theta, smooth.rawGradient))
      Evaluated(data, smooth, l1, legacy, total, residual, residual / scaling.denominator)
    }
    private[tmbad] def document(fit: Optimizer.Result, evaluated: Evaluated, proximalTrace: Vector[ProximalGradient.Iteration]): String = {
      val node = Json.obj().put("schema_version", 1)
        .put("coordinate_system", "native_optimizer_parameters")
        .put("normalization", normalization).put("legacy_l2_strength", base.l2Strength)
        .put("plan_digest", plan.digest).put("target_spec_digest", targetDigest)
        .put("free_parameter_count", plan.domain.freeIndices.size)
      node.set[JsonNode]("regularization", regularizationJson.map(Json.read).getOrElse(Json.read("null")))
      node.set[JsonNode]("fixed_parameters", Json.read(fixedJson))
      Json.putNumbers(node, "effective_initial_parameters", effectiveInitial)
      node.set[JsonNode]("solver", solverJson)
      node.set[JsonNode]("loss_components", evaluated.components)
      val stationarity = node.putObject("stationarity")
      stationarity.put("kind", if (plan.l1.nonEmpty) "l1_box_kkt" else "box_gradient")
        .put("summed_inf", evaluated.summedKkt).put("reduced_inf", evaluated.reducedKkt)
        .put("tolerance", if (method == "proximal_gradient") proximal.kktTolerance else base.gradientTolerance)
        .put("tolerance_units", if (method == "proximal_gradient") "summed_target" else "reduced_objective")
      val trace = node.putArray("proximal_trace")
      proximalTrace.foreach { value =>
        trace.add(Json.obj().put("iteration", value.iteration).put("loss", value.compositeValue)
          .put("summed_kkt_inf", value.rawKktInfinityNorm).put("reduced_kkt_inf", value.normalizedKktInfinityNorm)
          .put("relative_step_inf", value.relativeStepInfinityNorm).put("step_size", value.stepSize)
          .put("backtracks", value.backtracks).put("objective_calls", value.objectiveCalls))
      }
      Json.write(node)
    }
  }

  private def fixed(node: JsonNode, model: NativeModel): (Vector[NamedRegularization.Fixed], String) = {
    Json.fields(node, Set.empty, model.parameterNames.toSet)
    val output = Json.obj()
    val values = model.parameterNames.filter(node.has).map { name =>
      val value = Json.fieldNumber(node, name)
      output.put(name, value); NamedRegularization.Fixed(name, value)
    }
    (values, Json.write(output))
  }
  private def regularization(node: JsonNode, model: NativeModel):
      (Vector[NamedRegularization.Gaussian], Vector[NamedRegularization.L1], String) = {
    Json.fields(node, Set("schema_version", "coordinate_system", "normalization", "gaussian", "l1"))
    require(Json.integer(node, "schema_version", 1, 1) == 1 &&
      Json.text(node, "coordinate_system") == "native_optimizer_parameters" &&
      Json.text(node, "normalization") == NewNormalization, "Unsupported prior coordinates/normalization")
    val prior = node.get("gaussian"); val l1 = node.get("l1")
    Json.fields(prior, Set.empty, model.parameterNames.toSet)
    Json.fields(l1, Set.empty, model.parameterNames.toSet)
    val canonical = Json.obj().put("schema_version", 1)
      .put("coordinate_system", "native_optimizer_parameters").put("normalization", NewNormalization)
    val gaussianOutput = canonical.putObject("gaussian")
    val gaussianTerms = model.parameterNames.filter(prior.has).map { name =>
      val term = prior.get(name)
      Json.fields(term, Set("mean", "precision"))
      val center = Json.fieldNumber(term, "mean"); val precision = Json.fieldNumber(term, "precision")
      gaussianOutput.putObject(name).put("mean", center).put("precision", precision)
      NamedRegularization.Gaussian(name, center, precision)
    }
    val l1Output = canonical.putObject("l1")
    val l1Terms = model.parameterNames.filter(l1.has).map { name =>
      val strength = Json.fieldNumber(l1, name); l1Output.put(name, strength)
      NamedRegularization.L1(name, strength)
    }
    (gaussianTerms, l1Terms, Json.write(canonical))
  }

  def resolve(node: JsonNode, model: NativeModel, base: FitOptions): Settings = {
    val (fixedTerms, fixedJson) = fixed(if (node.has("fixed_parameters")) node.get("fixed_parameters") else Json.obj(), model)
    val (gaussian, l1, regularizationJson) = if (node.has("regularization")) {
      require(base.l2Strength == 0.0, "Nonzero legacy L2 cannot be mixed with regularization")
      val (a, b, c) = regularization(node.get("regularization"), model)
      (a, b, Some(c))
    } else (Vector.empty[NamedRegularization.Gaussian], Vector.empty[NamedRegularization.L1], None)
    val plan = NamedRegularization.prepare(model.digest, domain(model), gaussian, l1, fixedTerms)
    val solver = if (node.has("solver")) node.get("solver") else Json.obj()
    val method = if (solver.has("method")) Json.text(solver, "method", 64)
                 else if (l1.nonEmpty) "proximal_gradient" else "bfgs"
    require(Set("bfgs", "proximal_gradient")(method), "Unknown solver method")
    if (method == "bfgs") {
      Json.fields(solver, Set.empty, Set("method"))
      require(l1.isEmpty, "Exact selected L1 requires proximal_gradient")
    } else {
      Json.fields(solver, Set.empty, Set("method", "kkt_tolerance", "kkt_tolerance_units",
        "initial_step", "maximum_step", "minimum_step", "backtrack_factor", "step_growth", "relative_step_tolerance"))
      require(regularizationJson.nonEmpty && base.l2Strength == 0.0,
        "Proximal solver requires an explicit named target and zero legacy L2")
      if (solver.has("kkt_tolerance_units"))
        require(Json.text(solver, "kkt_tolerance_units") == "summed_target", "KKT tolerance must use summed-target units")
    }
    def number(name: String, default: Double): Double =
      if (solver.has(name)) Json.fieldNumber(solver, name) else default
    val proximal = ProximalGradient.Settings(maxIterations = base.maxIterations,
      maxEvaluations = base.optimizer.maxEvaluations, kktTolerance = number("kkt_tolerance", base.gradientTolerance),
      initialStep = number("initial_step", 1.0), maximumStep = number("maximum_step", 1e6),
      minimumStep = number("minimum_step", 1e-14), backtrackFactor = number("backtrack_factor", 0.5),
      stepGrowth = number("step_growth", 1.5), maximumBacktracks = base.maxLineSearch,
      relativeStepTolerance = number("relative_step_tolerance", 1e-14))
    Settings(plan, regularizationJson, fixedJson, method, proximal, base.copy(extension = None))
  }

  private[tmbad] def solve(raw: Vector[Double] => GlobalEvaluation, settings: Settings): (Optimizer.Result, GlobalEvaluation, String) = {
    val initial = settings.effectiveInitial
    if (settings.method == "proximal_gradient") {
      var accounting: Option[GlobalEvaluation] = None
      val result = ProximalGradient.minimize(theta => {
        try {
          val data = raw(theta); accounting = Some(data)
          NamedRegularization.RawEvaluation(data.value, data.gradient, data.weight)
        } catch { case error: Optimizer.DomainFailure =>
          throw new ProximalGradient.ReviewedDomainFailure(error.getMessage) }
      }, initial, settings.plan, settings.reduction, settings.proximal)
      val accepted = accounting.get.copy(value = result.acceptedSmooth.rawDataValue,
        gradient = result.acceptedSmooth.rawDataGradient)
      val evaluated = settings.evaluate(accepted, result.parameters, result.acceptedSmooth.scaling)
      close(evaluated.totalReduced, result.compositeValue, "accepted proximal objective")
      val smooth = result.acceptedSmooth.gradient
      val projectedScore = projected(result.parameters, smooth, settings.plan.domain)
      val fit = Optimizer.Result(result.parameters, result.compositeValue, smooth, result.converged,
        result.status, result.iterations, result.objectiveCalls, norm(smooth), norm(projectedScore),
        result.activeBounds, Vector.empty, result.rejectedCandidates)
      (fit, accepted, settings.document(fit, evaluated, result.trace))
    } else {
      var scaling: Option[NamedRegularization.Scaling] = None
      var latest: Option[(Vector[Double], Evaluated)] = None
      var accepted: Option[Evaluated] = None
      val solved = Optimizer.minimize(theta => {
        val data = raw(theta)
        if (scaling.isEmpty) scaling = Some(NamedRegularization.Scaling(settings.reduction, data.weight))
        val evaluated = settings.evaluate(data, theta, scaling.get)
        latest = Some(theta -> evaluated)
        Optimizer.Evaluation(evaluated.totalReduced, evaluated.smooth.gradient)
      }, initial, settings.base.optimizer,
        Some(Optimizer.Bounds(settings.plan.domain.lower, settings.plan.domain.upper)),
        onAccepted = (point, evaluation) => {
          val (observedPoint, value) = latest.get
          require(point == observedPoint && evaluation.value == value.totalReduced &&
            evaluation.gradient == value.smooth.gradient, "Accepted-point target metadata differs")
          accepted = Some(value)
        })
      val result = if (settings.plan.domain.freeIndices.isEmpty) solved.copy(status = "all_parameters_fixed") else solved
      val evaluated = accepted.get
      (result, evaluated.data, settings.document(result, evaluated, Vector.empty))
    }
  }

  def validateDocument(node: JsonNode, model: NativeModel, theta: Vector[Double], fit: JsonNode): Unit = {
    Json.fields(node, Set("schema_version", "coordinate_system", "normalization", "regularization",
      "fixed_parameters", "legacy_l2_strength", "plan_digest", "target_spec_digest",
      "effective_initial_parameters", "free_parameter_count", "solver", "loss_components",
      "stationarity", "proximal_trace"))
    require(Json.integer(node, "schema_version", 1, 1) == 1 &&
      Json.text(node, "coordinate_system") == "native_optimizer_parameters", "Unknown fitted target schema")
    val (fixedTerms, _) = fixed(node.get("fixed_parameters"), model)
    val (gaussian, l1) = if (node.get("regularization").isNull) {
      (Vector.empty[NamedRegularization.Gaussian], Vector.empty[NamedRegularization.L1])
    } else {
      val (a, b, _) = regularization(node.get("regularization"), model); (a, b)
    }
    val legacy = nonnegative(Json.fieldNumber(node, "legacy_l2_strength"), "legacy L2")
    require(node.get("regularization").isNull || legacy == 0.0, "Mixed saved penalties")
    val normalization = if (node.get("regularization").isNull) LegacyNormalization else NewNormalization
    val plan = NamedRegularization.prepare(model.digest, domain(model), gaussian, l1, fixedTerms)
    require(Json.text(node, "normalization") == normalization && Json.text(node, "plan_digest", 64) == plan.digest &&
      Json.text(node, "target_spec_digest", 64) == digest(plan.digest, normalization, legacy), "Saved target digest differs")
    plan.domain.check(theta)
    val initial = Json.numbers(node.get("effective_initial_parameters"), 64, "effective initial parameters")
    plan.domain.check(initial)
    require(Json.integer(node, "free_parameter_count", 0, theta.size) == plan.domain.freeIndices.size,
      "Saved free parameter count differs")
    require(fit.has("reduction") && fit.has("l2_strength") && fit.has("data_ledger"), "Extended fit requires reduction/penalty/ledger")
    close(Json.fieldNumber(fit, "l2_strength"), legacy, "saved legacy L2")
    val reduction = Json.text(fit, "reduction")
    val scaling = NamedRegularization.Scaling(if (reduction == "weighted_mean") NamedRegularization.WeightedMean else NamedRegularization.Sum,
      Json.fieldNumber(fit, "weight_sum"))
    val components = node.get("loss_components")
    Json.fields(components, Set("data_sum", "gaussian_quadratic_sum", "gaussian_log_normalizer_sum",
      "l1_sum", "legacy_l2_reduced", "denominator", "total_reduced"))
    Vector("gaussian_quadratic_sum", "l1_sum", "legacy_l2_reduced").foreach(name =>
      nonnegative(Json.fieldNumber(components, name), name))
    val prior = plan.smooth(NamedRegularization.RawEvaluation(0.0, Vector.fill(theta.size)(0.0), scaling.likelihoodWeight), theta, scaling)
    close(Json.fieldNumber(components, "denominator"), scaling.denominator, "normalization denominator")
    close(Json.fieldNumber(components, "gaussian_quadratic_sum"), prior.gaussianQuadratic, "Gaussian prior value")
    close(Json.fieldNumber(components, "gaussian_log_normalizer_sum"), prior.gaussianNormalizer, "Gaussian normalizer")
    val l1Value = plan.rawL1Value(theta)
    close(Json.fieldNumber(components, "l1_sum"), l1Value, "L1 value")
    val legacyValue = GlobalPenalty.value(theta, legacy)
    close(Json.fieldNumber(components, "legacy_l2_reduced"), legacyValue, "legacy L2 value")
    val total = (Json.fieldNumber(components, "data_sum") + prior.rawValue + l1Value) / scaling.denominator + legacyValue
    close(Json.fieldNumber(components, "total_reduced"), total, "target total")
    close(Json.fieldNumber(fit, "loss"), total, "fitted target loss")
    val solver = node.get("solver")
    val method = Json.text(solver, "method")
    val common = Set("method", "max_iterations", "max_evaluations", "max_backtracks")
    if (method == "bfgs") {
      Json.fields(solver, common ++ Set("gradient_tolerance", "function_tolerance"))
      require(l1.isEmpty, "Saved BFGS fit has nonsmooth L1")
      require(Json.fieldNumber(solver, "gradient_tolerance") > 0.0 && Json.fieldNumber(solver, "function_tolerance") >= 0.0,
        "Invalid saved BFGS settings")
    } else {
      require(method == "proximal_gradient" && !node.get("regularization").isNull && legacy == 0.0,
        "Invalid saved proximal target")
      Json.fields(solver, common ++ Set("kkt_tolerance", "kkt_tolerance_units", "initial_step", "maximum_step",
        "minimum_step", "backtrack_factor", "step_growth", "relative_step_tolerance"))
      require(Json.text(solver, "kkt_tolerance_units") == "summed_target", "Invalid saved KKT measure")
      ProximalGradient.Settings(Json.integer(solver, "max_iterations", 1, 1000).toInt,
        Json.integer(solver, "max_evaluations", 1, 10000).toInt, Json.fieldNumber(solver, "kkt_tolerance"),
        Json.fieldNumber(solver, "initial_step"), Json.fieldNumber(solver, "maximum_step"),
        Json.fieldNumber(solver, "minimum_step"), Json.fieldNumber(solver, "backtrack_factor"),
        Json.fieldNumber(solver, "step_growth"), Json.integer(solver, "max_backtracks", 1, 100).toInt,
        Json.fieldNumber(solver, "relative_step_tolerance"))
    }
    val maxIterations = Json.integer(solver, "max_iterations", 1, 1000)
    val maxEvaluations = Json.integer(solver, "max_evaluations", 1, 10000)
    val maxBacktracks = Json.integer(solver, "max_backtracks", 1, 100)
    require(maxEvaluations == math.min(10000L, 1 + maxIterations * (maxBacktracks + 1)) &&
      Json.integer(fit, "iterations", 0, 1000) <= maxIterations &&
      Json.integer(fit, "objective_calls", 1, 10000) <= maxEvaluations, "Saved solver budget differs")
    val stationarity = node.get("stationarity")
    Json.fields(stationarity, Set("kind", "summed_inf", "reduced_inf", "tolerance", "tolerance_units"))
    require(Json.text(stationarity, "kind") == (if (l1.nonEmpty) "l1_box_kkt" else "box_gradient"), "Wrong stationarity kind")
    val summed = nonnegative(Json.fieldNumber(stationarity, "summed_inf"), "summed stationarity")
    val reduced = nonnegative(Json.fieldNumber(stationarity, "reduced_inf"), "reduced stationarity")
    close(reduced, summed / scaling.denominator, "stationarity scaling")
    val tolerance = Json.fieldNumber(stationarity, "tolerance")
    val expectedTolerance = Json.fieldNumber(solver, if (method == "bfgs") "gradient_tolerance" else "kkt_tolerance")
    require(tolerance > 0.0 && tolerance == expectedTolerance, "Stationarity tolerance differs from solver settings")
    require(Json.text(stationarity, "tolerance_units") == (if (method == "bfgs") "reduced_objective" else "summed_target"),
      "Wrong convergence tolerance units")
    if (method == "bfgs") close(Json.fieldNumber(fit, "projected_gradient_inf"), reduced, "box-gradient stationarity")
    val successfulStatuses = if (method == "bfgs") Set("projected_gradient_tolerance", "all_parameters_fixed")
      else Set("summed_target_kkt_tolerance", "all_parameters_fixed")
    val failedStatuses = if (method == "bfgs") Set("maximum_iterations", "maximum_evaluations", "line_search_failed",
      "step_stalled_without_stationarity", "function_stalled_without_stationarity")
      else Set("maximum_iterations", "maximum_evaluations", "step_stalled_without_kkt", "proximal_backtracking_failed")
    val status = Json.text(fit, "status")
    if (Json.boolean(fit, "converged")) {
      require(successfulStatuses(status) && (if (method == "bfgs") reduced else summed) <= tolerance,
        "Converged flag contradicts solver status/stationarity")
    } else require(failedStatuses(status), "Failed fit has an unsupported/successful status")
    if (status == "all_parameters_fixed") require(plan.domain.freeIndices.isEmpty &&
      Json.integer(fit, "iterations", 0, 1000) == 0 && Json.integer(fit, "objective_calls", 1, 10000) == 1,
      "All-fixed result claims an optimization history")
    if (plan.domain.freeIndices.isEmpty) require(status == "all_parameters_fixed" && Json.boolean(fit, "converged") &&
      summed == 0.0 && reduced == 0.0 && Json.fieldNumber(fit, "projected_gradient_inf") == 0.0 &&
      Json.elements(fit.get("trace"), 1000, "fixed fit history").isEmpty &&
      Json.elements(node.get("proximal_trace"), 1000, "fixed proximal history").isEmpty,
      "Zero-free-coordinate result must be one successful fixed evaluation without optimization history")
    val active = Json.elements(fit.get("active_bounds"), theta.size, "active bounds").map(_.intValue())
    require(active == theta.indices.filter(i => theta(i) == plan.domain.lower(i) || theta(i) == plan.domain.upper(i)).toVector,
      "Saved active-bound mask differs from parameter values")
    val trace = Json.elements(node.get("proximal_trace"), 1000, "proximal trace")
    if (method == "bfgs") require(trace.isEmpty, "BFGS model contains a proximal trace")
    else {
      require(Json.elements(fit.get("trace"), 1000, "BFGS trace").isEmpty &&
        trace.size == Json.integer(fit, "iterations", 0, 1000), "Proximal fit trace coverage differs")
      var previousCalls = 0L
      trace.zipWithIndex.foreach { case (entry, index) =>
        Json.fields(entry, Set("iteration", "loss", "summed_kkt_inf", "reduced_kkt_inf", "relative_step_inf",
          "step_size", "backtracks", "objective_calls"))
        require(Json.integer(entry, "iteration", 1, 1000) == index + 1, "Proximal trace iteration order differs")
        Json.fieldNumber(entry, "loss")
        Vector("summed_kkt_inf", "reduced_kkt_inf", "relative_step_inf").foreach(name => nonnegative(Json.fieldNumber(entry, name), name))
        val step = Json.fieldNumber(entry, "step_size")
        require(step >= Json.fieldNumber(solver, "minimum_step") && step <= Json.fieldNumber(solver, "maximum_step"),
          "Invalid trace step")
        close(Json.fieldNumber(entry, "reduced_kkt_inf"), Json.fieldNumber(entry, "summed_kkt_inf") / scaling.denominator,
          "Trace KKT scaling")
        Json.integer(entry, "backtracks", 0, maxBacktracks)
        val calls = Json.integer(entry, "objective_calls", 1, maxEvaluations)
        require(calls > previousCalls && calls <= Json.integer(fit, "objective_calls", 1, maxEvaluations), "Trace call counts differ")
        previousCalls = calls
      }
      trace.lastOption.foreach { last =>
        close(Json.fieldNumber(last, "loss"), total, "final proximal loss")
        close(Json.fieldNumber(last, "summed_kkt_inf"), summed, "final proximal KKT")
        close(Json.fieldNumber(last, "reduced_kkt_inf"), reduced, "final reduced KKT")
      }
    }
  }
}
