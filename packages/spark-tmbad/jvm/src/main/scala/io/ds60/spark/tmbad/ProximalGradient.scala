// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import NamedRegularization.{Plan, RawEvaluation, Reduction, Scaling, SmoothEvaluation}

/** Bounded monotone proximal gradient with exact selected L1 and equality/box constraints. */
object ProximalGradient {
  /** Integration may translate ONLY the existing reviewed native DomainFailure into this type. */
  final class ReviewedDomainFailure(message: String) extends IllegalArgumentException(message)

  final case class Settings(
      maxIterations: Int = 100,
      maxEvaluations: Int = 10000,
      kktTolerance: Double = 1e-6,
      initialStep: Double = 1.0,
      maximumStep: Double = 1e6,
      minimumStep: Double = 1e-14,
      backtrackFactor: Double = 0.5,
      stepGrowth: Double = 1.5,
      maximumBacktracks: Int = 60,
      relativeStepTolerance: Double = 1e-14
  ) extends Serializable {
    require(maxIterations >= 1 && maxIterations <= 1000, "Invalid iteration budget")
    require(maxEvaluations >= 1 && maxEvaluations <= 10000, "Invalid evaluation budget")
    require(kktTolerance.isFinite && kktTolerance > 0.0, "Invalid summed-target KKT tolerance")
    require(initialStep.isFinite && initialStep > 0.0 && maximumStep.isFinite &&
      maximumStep >= initialStep && minimumStep.isFinite && minimumStep > 0.0 &&
      minimumStep <= initialStep, "Invalid proximal step limits")
    require(backtrackFactor.isFinite && backtrackFactor > 0.0 && backtrackFactor < 1.0 &&
      stepGrowth.isFinite && stepGrowth >= 1.0, "Invalid proximal step adaptation")
    require(maximumBacktracks >= 1 && maximumBacktracks <= 100, "Invalid backtracking bound")
    require(relativeStepTolerance.isFinite && relativeStepTolerance > 0.0,
      "Invalid coordinatewise relative step tolerance")
  }
  final case class Iteration(
      iteration: Int,
      compositeValue: Double,
      rawKktInfinityNorm: Double,
      normalizedKktInfinityNorm: Double,
      relativeStepInfinityNorm: Double,
      stepSize: Double,
      backtracks: Int,
      objectiveCalls: Int
  ) extends Serializable
  final case class Result(
      parameters: Vector[Double],
      acceptedSmooth: SmoothEvaluation,
      rawL1Value: Double,
      compositeValue: Double,
      converged: Boolean,
      status: String,
      iterations: Int,
      objectiveCalls: Int,
      rejectedCandidates: Int,
      rawKktInfinityNorm: Double,
      normalizedKktInfinityNorm: Double,
      freeParameterCount: Int,
      activeBounds: Vector[Int],
      trace: Vector[Iteration],
      targetDigest: String
  ) extends Serializable

  private def norm(values: Vector[Double]): Double = {
    require(values.nonEmpty && values.forall(_.isFinite), "Invalid finite residual vector")
    values.map(math.abs).max
  }
  private def sum(values: Iterable[Double]): Double = {
    var total = 0.0
    var correction = 0.0
    values.foreach { value =>
      require(value.isFinite, "Nonfinite line-search arithmetic")
      val adjusted = value - correction
      val next = total + adjusted
      correction = (next - total) - adjusted
      total = next
    }
    require(total.isFinite, "Line-search sum is not representable")
    total
  }
  private def allowance(values: Double*): Double = {
    require(values.forall(_.isFinite), "Nonfinite descent comparison")
    16.0 * math.ulp(values.map(math.abs).max)
  }
  private def relativeStep(before: Vector[Double], after: Vector[Double], plan: Plan): Double = {
    val values = plan.domain.freeIndices.map { i =>
      math.abs(after(i) - before(i)) / math.max(1.0, math.max(math.abs(before(i)), math.abs(after(i))))
    }
    if (values.isEmpty) 0.0 else norm(values)
  }

  def minimize(
      evaluateData: Vector[Double] => RawEvaluation,
      suppliedInitial: Vector[Double],
      plan: Plan,
      reduction: Reduction,
      settings: Settings = Settings()
  ): Result = {
    // A caller must validate the supplied initial point against the ORIGINAL
    // native domain before equality masks explicitly replace fixed coordinates.
    plan.originalDomain.check(suppliedInitial)
    var point = plan.domain.effectiveInitial(suppliedInitial)
    var scaling: Option[Scaling] = None
    var calls = 0
    var rejected = 0
    def evaluate(candidate: Vector[Double]): SmoothEvaluation = {
      require(calls < settings.maxEvaluations, "Proximal objective budget exhausted")
      if (Thread.currentThread().isInterrupted) throw new InterruptedException("Fit cancelled")
      plan.domain.check(candidate)
      calls += 1
      val raw = evaluateData(candidate)
      if (scaling.isEmpty) scaling = Some(Scaling(reduction, raw.weight))
      plan.smooth(raw, candidate, scaling.get)
    }
    // Deliberately outside the later-trial rejection handler: initial failure is fatal.
    var current = evaluate(point)
    var total = plan.composite(current, point)
    var step = settings.initialStep
    var iteration = 0
    var status = "maximum_iterations"
    var converged = false
    var finished = false
    val trace = scala.collection.mutable.ArrayBuffer.empty[Iteration]

    while (!finished) {
      val residual = norm(plan.rawKkt(point, current.rawGradient))
      if (residual <= settings.kktTolerance) {
        status = if (plan.domain.freeIndices.isEmpty) "all_parameters_fixed" else "summed_target_kkt_tolerance"
        converged = true
        finished = true
      } else if (iteration >= settings.maxIterations) {
        status = "maximum_iterations"
        finished = true
      } else if (calls >= settings.maxEvaluations) {
        status = "maximum_evaluations"
        finished = true
      } else {
        var trialStep = step
        var backtracks = 0
        var accepted: Option[(Vector[Double], SmoothEvaluation, Double)] = None
        var stalled = false
        while (accepted.isEmpty && !stalled && backtracks < settings.maximumBacktracks &&
               trialStep >= settings.minimumStep && calls < settings.maxEvaluations) {
          plan.proximal(point, current.gradient, trialStep, current.scaling) match {
            case None => () // Unrepresentable trial arithmetic shrinks the step without a native call.
            case Some(candidate) =>
              val relative = relativeStep(point, candidate, plan)
              if (relative == 0.0) stalled = true
              else {
                val delta = candidate.indices.map(i => candidate(i) - point(i)).toVector
                val linear = sum(delta.indices.map(i => current.gradient(i) * delta(i)))
                val rootStep = math.sqrt(trialStep)
                val quadratic = sum(delta.map(value => {
                  val scaled = value / rootStep
                  0.5 * scaled * scaled
                }))
                val majorant = sum(Vector(current.value, linear, quadratic))
                try {
                  val proposed = evaluate(candidate)
                  val composite = plan.composite(proposed, candidate)
                  val majorizationAccepted = proposed.value <= majorant +
                    allowance(proposed.value, majorant, current.value)
                  val compositeAccepted = composite <= total + allowance(composite, total)
                  // Summing many row losses can round the smooth majorant past
                  // an already stationary trial. The same summed KKT certificate
                  // used at loop entry can terminate there, but this exception
                  // permits no objective increase, including an ULP allowance.
                  val certifiedTerminal = composite <= total &&
                    norm(plan.rawKkt(candidate, proposed.rawGradient)) <= settings.kktTolerance
                  if ((majorizationAccepted && compositeAccepted) || certifiedTerminal)
                    accepted = Some((candidate, proposed, composite))
                } catch {
                  case _: ReviewedDomainFailure => rejected += 1
                }
              }
          }
          if (accepted.isEmpty && !stalled) {
            trialStep *= settings.backtrackFactor
            backtracks += 1
          }
        }
        accepted match {
          case None =>
            status = if (stalled) "step_stalled_without_kkt"
                     else if (calls >= settings.maxEvaluations) "maximum_evaluations"
                     else "proximal_backtracking_failed"
            finished = true
          case Some((next, proposed, composite)) =>
            val relative = relativeStep(point, next, plan)
            point = next
            current = proposed
            total = composite
            iteration += 1
            val residual = norm(plan.rawKkt(point, current.rawGradient))
            trace += Iteration(iteration, total, residual,
              residual / current.scaling.denominator, relative, trialStep, backtracks, calls)
            if (relative <= settings.relativeStepTolerance && residual > settings.kktTolerance) {
              status = "step_stalled_without_kkt"
              finished = true
            }
            step = math.min(settings.maximumStep, trialStep * settings.stepGrowth)
        }
      }
    }
    val residual = norm(plan.rawKkt(point, current.rawGradient))
    Result(point, current, plan.rawL1Value(point), total, converged, status,
      iteration, calls, rejected, residual, residual / current.scaling.denominator,
      plan.domain.freeIndices.size,
      point.indices.filter(i => point(i) == plan.domain.lower(i) || point(i) == plan.domain.upper(i)).toVector,
      trace.toVector, plan.digest)
  }
}
