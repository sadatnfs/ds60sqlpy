package io.ds60.spark.tmbad

/** Original bounded inverse-BFGS driver solver. The evaluator may launch Spark jobs. */
object Optimizer {
  final case class Evaluation(value: Double, gradient: Vector[Double]) extends Serializable
  final case class Bounds(lower: Vector[Double], upper: Vector[Double]) extends Serializable {
    require(lower.nonEmpty && lower.size == upper.size, "Bounds have incompatible dimensions")
    require(
      lower.zip(upper).forall { case (lo, hi) =>
        !lo.isNaN && !hi.isNaN && lo <= hi && lo != Double.PositiveInfinity &&
        hi != Double.NegativeInfinity
      },
      "Invalid optimization bounds"
    )
    def project(point: Vector[Double]): Vector[Double] = {
      require(point.size == lower.size, "Point and bounds dimensions differ")
      point.indices.map(i => math.max(lower(i), math.min(upper(i), point(i)))).toVector
    }
  }
  object Bounds {
    def unbounded(size: Int): Bounds =
      Bounds(Vector.fill(size)(Double.NegativeInfinity), Vector.fill(size)(Double.PositiveInfinity))
  }
  final case class Settings(
      maxIterations: Int = 100,
      maxEvaluations: Int = 400,
      gradientTolerance: Double = 1e-6,
      functionTolerance: Double = 1e-12,
      stepTolerance: Double = 1e-14,
      armijo: Double = 1e-4,
      minimumStep: Double = 1e-12,
      maximumBacktracks: Int = 40
  ) extends Serializable {
    require(maxIterations > 0 && maxIterations <= 1000, "Iterations must be in 1..1000")
    require(maxEvaluations > 0 && maxEvaluations <= 10000, "Evaluations must be in 1..10000")
    require(gradientTolerance.isFinite && gradientTolerance > 0, "Invalid score tolerance")
    require(functionTolerance.isFinite && functionTolerance >= 0, "Invalid function tolerance")
    require(stepTolerance.isFinite && stepTolerance > 0, "Invalid step tolerance")
    require(armijo.isFinite && armijo > 0 && armijo < 0.5, "Invalid Armijo coefficient")
    require(minimumStep.isFinite && minimumStep > 0 && minimumStep < 1, "Invalid minimum step")
    require(maximumBacktracks > 0 && maximumBacktracks <= 100, "Invalid backtracking bound")
  }
  final case class Iteration(
      iteration: Int,
      value: Double,
      rawGradientInfinityNorm: Double,
      projectedGradientInfinityNorm: Double,
      stepInfinityNorm: Double,
      evaluations: Int,
      hessianReset: Boolean
  ) extends Serializable
  final case class Result(
      parameters: Vector[Double],
      value: Double,
      gradient: Vector[Double],
      converged: Boolean,
      status: String,
      iterations: Int,
      evaluations: Int,
      rawGradientInfinityNorm: Double,
      projectedGradientInfinityNorm: Double,
      activeBounds: Vector[Int],
      trace: Vector[Iteration],
      rejectedCandidates: Int
  ) extends Serializable

  /** Only this specific scientific-domain exception may reject a line-search candidate. */
  final class DomainFailure(message: String) extends IllegalArgumentException(message)

  private def finite(point: Vector[Double]): Unit =
    require(
      point.nonEmpty && point.size <= 64 && point.forall(_.isFinite),
      "Expected 1..64 finite parameters or scores"
    )
  private def norm(point: Vector[Double]): Double = point.map(math.abs).max
  private def dot(a: Vector[Double], b: Vector[Double]): Double = {
    require(a.size == b.size, "Vector dimensions differ")
    val result = a.indices.map(i => a(i) * b(i)).sum
    require(result.isFinite, "Nonfinite optimizer inner product")
    result
  }
  private def identity(size: Int): Array[Array[Double]] =
    Array.tabulate(size, size)((i, j) => if (i == j) 1.0 else 0.0)
  private def projectedScore(
      point: Vector[Double],
      gradient: Vector[Double],
      bounds: Bounds
  ): Vector[Double] =
    point.indices.map { i =>
      // Exact activity avoids incorrectly collapsing narrow but valid intervals.
      if (
        (point(i) == bounds.lower(i) && gradient(i) > 0) ||
        (point(i) == bounds.upper(i) && gradient(i) < 0) ||
        bounds.lower(i) == bounds.upper(i)
      ) 0.0
      else gradient(i)
    }.toVector

  def minimize(
      objective: Vector[Double] => Evaluation,
      initial: Vector[Double],
      settings: Settings = Settings(),
      specifiedBounds: Option[Bounds] = None,
      onAccepted: (Vector[Double], Evaluation) => Unit = (_, _) => ()
  ): Result = {
    finite(initial)
    val bounds = specifiedBounds.getOrElse(Bounds.unbounded(initial.size))
    require(bounds.lower.size == initial.size, "Parameter and bound counts differ")
    var point = bounds.project(initial)
    var calls = 0
    var rejectedCandidates = 0
    def evaluate(candidate: Vector[Double]): Evaluation = {
      require(calls < settings.maxEvaluations, "Optimizer evaluation budget exhausted")
      if (Thread.currentThread().isInterrupted)
        throw new InterruptedException("Optimization cancelled")
      calls += 1
      val result = objective(candidate)
      require(result.value.isFinite, "Objective value is nonfinite")
      finite(result.gradient)
      require(result.gradient.size == candidate.size, "Objective gradient dimension differs")
      result
    }
    var current = evaluate(point)
    onAccepted(point, current)
    var inverse = identity(initial.size)
    var iteration = 0
    var status = "maximum_iterations"
    var converged = false
    val trace = scala.collection.mutable.ArrayBuffer.empty[Iteration]
    var finished = false
    while (!finished) {
      val score = projectedScore(point, current.gradient, bounds)
      if (norm(score) <= settings.gradientTolerance) {
        status = "projected_gradient_tolerance"
        converged = true
        finished = true
      } else if (iteration >= settings.maxIterations) {
        status = "maximum_iterations"
        finished = true
      } else if (calls >= settings.maxEvaluations) {
        status = "maximum_evaluations"
        finished = true
      } else {
        var reset = false
        var direction = point.indices.map { i =>
          -point.indices.map(j => inverse(i)(j) * score(j)).sum
        }.toVector
        val trial = bounds.project(point.indices.map(i => point(i) + direction(i)).toVector)
        val projectedDirection = trial.indices.map(i => trial(i) - point(i)).toVector
        if (
          !direction.forall(_.isFinite) || !trial.forall(_.isFinite) ||
          dot(direction, score) >= 0 || dot(current.gradient, projectedDirection) >= 0
        ) {
          inverse = identity(point.size)
          direction = score.map(-_)
          reset = true
        }
        var scale = 1.0
        var backtracks = 0
        var accepted: Option[(Vector[Double], Evaluation)] = None
        while (
          accepted.isEmpty && backtracks < settings.maximumBacktracks &&
          scale >= settings.minimumStep && calls < settings.maxEvaluations
        ) {
          val candidate =
            bounds.project(point.indices.map(i => point(i) + scale * direction(i)).toVector)
          val displacement = candidate.indices.map(i => candidate(i) - point(i)).toVector
          val slope =
            if (candidate.forall(_.isFinite)) dot(current.gradient, displacement)
            else Double.PositiveInfinity
          if (norm(displacement) > 0 && slope < 0) {
            try {
              val proposed = evaluate(candidate)
              if (proposed.value <= current.value + settings.armijo * slope)
                accepted = Some(candidate -> proposed)
            } catch {
              case _: DomainFailure => rejectedCandidates += 1
            }
          }
          if (accepted.isEmpty) {
            scale *= 0.5
            backtracks += 1
          }
        }
        accepted match {
          case None =>
            status =
              if (calls >= settings.maxEvaluations) "maximum_evaluations" else "line_search_failed"
            finished = true
          case Some((next, proposed)) =>
            val step = next.indices.map(i => next(i) - point(i)).toVector
            // Equality-fixed coordinates do not belong to the optimization
            // tangent space. Their changing gradients must not contaminate the
            // free-coordinate inverse-Hessian secant update.
            val delta = next.indices.map { i =>
              if (bounds.lower(i) == bounds.upper(i)) 0.0
              else proposed.gradient(i) - current.gradient(i)
            }.toVector
            val curvature = dot(step, delta)
            val threshold = 1e-12 * math.max(1.0, norm(step) * norm(delta))
            if (curvature > threshold) {
              val product =
                step.indices.map(i => step.indices.map(j => inverse(i)(j) * delta(j)).sum).toVector
              val quadratic = dot(delta, product)
              val factor = (1.0 + quadratic / curvature) / curvature
              val updated = Array.tabulate(step.size, step.size) { (i, j) =>
                inverse(i)(j) + factor * step(i) * step(j) -
                  (product(i) * step(j) + step(i) * product(j)) / curvature
              }
              if (updated.forall(_.forall(_.isFinite))) inverse = updated
              else { inverse = identity(point.size); reset = true }
            } else { inverse = identity(point.size); reset = true }
            val relativeStep =
              next.indices.filter(i => bounds.lower(i) != bounds.upper(i)).map { i =>
                math.abs(step(i)) / math.max(1.0, math.max(math.abs(point(i)), math.abs(next(i))))
              }
            val fixedCoordinates =
              bounds.lower.indices.exists(i => bounds.lower(i) == bounds.upper(i))
            val smallStepInFreeSpace =
              if (fixedCoordinates) relativeStep.forall(_ <= settings.stepTolerance)
              else norm(step) <= settings.stepTolerance * math.max(1.0, norm(next))
            val lossChange = math.abs(current.value - proposed.value)
            val lossScale =
              math.max(1.0, math.max(math.abs(current.value), math.abs(proposed.value)))
            point = next
            current = proposed
            onAccepted(point, current)
            iteration += 1
            val projected = projectedScore(point, current.gradient, bounds)
            trace += Iteration(
              iteration,
              current.value,
              norm(current.gradient),
              norm(projected),
              norm(step),
              calls,
              reset
            )
            if (smallStepInFreeSpace && norm(projected) > settings.gradientTolerance) {
              status = "step_stalled_without_stationarity"
              finished = true
            } else if (
              lossChange <= settings.functionTolerance * lossScale &&
              norm(projected) > settings.gradientTolerance
            ) {
              status = "function_stalled_without_stationarity"
              finished = true
            }
        }
      }
    }
    val projected = projectedScore(point, current.gradient, bounds)
    Result(
      point,
      current.value,
      current.gradient,
      converged,
      status,
      iteration,
      calls,
      norm(current.gradient),
      norm(projected),
      point.indices
        .filter(i => point(i) == bounds.lower(i) || point(i) == bounds.upper(i))
        .toVector,
      trace.toVector,
      rejectedCandidates
    )
  }
}
