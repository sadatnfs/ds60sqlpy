// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import NamedRegularization._

/** Large row sums must not discard an already certified, non-increasing point. */
object ProximalRoundoffChecks {
  def main(args: Array[String]): Unit = {
    val n = 32768.0
    val domain = Domain(
      Vector("mu", "log_sigma"),
      Vector(Double.NegativeInfinity, -20.0),
      Vector(Double.PositiveInfinity, 20.0)
    )
    val plan = prepare(
      "a" * 64,
      domain,
      Vector(Gaussian("mu", 1.0, n)),
      Vector(L1("mu", n)),
      Vector(Fixed("log_sigma", 0.0))
    )
    // Reproduce the native per-batch arithmetic, followed by 32 equal blocks.
    // At mu=3.75 the smooth summed score is -n and exact L1 cancels it.
    def normal(point: Vector[Double]): RawEvaluation = {
      val inverse = math.exp(-2 * point(1))
      var value = 0.0
      var meanScore = 0.0
      var scaleScore = 0.0
      for (i <- 0 until 1024) {
        val residual = point(0) - (i % 16)
        value += point(1) + 0.5 * math.log(2 * math.Pi) + 0.5 * residual * residual * inverse
        meanScore += residual * inverse
        scaleScore += 1.0 - residual * residual * inverse
      }
      RawEvaluation(value * 32, Vector(meanScore * 32, scaleScore * 32), n)
    }
    for (reduction <- Vector(Sum, WeightedMean)) {
      val denominator = if (reduction == WeightedMean) n else 1.0
      val initialPoint = Vector(0.0, 0.0)
      val expectedPoint = Vector(3.75, 0.0)
      val scaling = Scaling(reduction, n)
      val initial = plan.smooth(normal(initialPoint), initialPoint, scaling)
      val expected = plan.smooth(normal(expectedPoint), expectedPoint, scaling)
      val linear = initial.gradient(0) * 3.75
      val scaledDelta = 3.75 / math.sqrt(denominator / (2 * n))
      val majorant = initial.value + linear + 0.5 * scaledDelta * scaledDelta
      println(
        s"Roundoff reproduction ${reduction.name}: initial=${initial.value}, " +
          s"stationary=${expected.value}, majorant=$majorant, " +
          s"gap=${expected.value - majorant}, rawKkt=${plan.rawKkt(expectedPoint, expected.rawGradient)}"
      )
      val result = ProximalGradient.minimize(
        normal,
        Vector(0.0, 0.0),
        plan,
        reduction,
        ProximalGradient.Settings(
          maxIterations = 1,
          maxEvaluations = 3,
          initialStep = denominator / (2 * n),
          maximumBacktracks = 1
        )
      )
      require(
        result.converged && result.parameters == Vector(3.75, 0.0),
        s"Exact large-row optimum was discarded: ${reduction.name}, ${result.status}"
      )
      require(
        result.rawKktInfinityNorm <= 1e-6 && result.iterations == 1 &&
          result.objectiveCalls == 2 && result.trace.head.backtracks == 0,
        "Termination changed the KKT tolerance or fabricated its evaluation trace"
      )
      require(
        result.compositeValue <= plan.composite(initial, Vector(0.0, 0.0)),
        "Certified terminal point increased the composite objective"
      )
    }

    val one = Domain(Vector("x"), Vector(Double.NegativeInfinity), Vector(Double.PositiveInfinity))
    val bare = prepare("b" * 64, one, Vector.empty, Vector.empty, Vector.empty)
    // This true quartic trial decreases the objective but violates the smooth
    // majorant and is not stationary. It must still be rejected.
    for (reduction <- Vector(Sum, WeightedMean)) {
      val weight = 1e8
      def quartic(point: Vector[Double]): RawEvaluation =
        RawEvaluation(math.pow(point.head, 4), Vector(4 * math.pow(point.head, 3)), weight)
      val step = if (reduction == WeightedMean) 0.4 * weight else 0.4
      val result = ProximalGradient.minimize(
        quartic,
        Vector(1.0),
        bare,
        reduction,
        ProximalGradient.Settings(
          maxIterations = 1,
          maxEvaluations = 3,
          initialStep = step,
          maximumStep = 1e8,
          maximumBacktracks = 1
        )
      )
      require(
        !result.converged && result.iterations == 0 && result.parameters == Vector(1.0),
        "An uncertified trial bypassed majorization or used reduced KKT units"
      )
    }
    // x=1 is stationary for this polynomial, but has greater objective than
    // x=0. An exact zero score does not authorize accepting that increase.
    def higherStationary(point: Vector[Double]): RawEvaluation = {
      val x = point.head
      RawEvaluation(-3 * x * x * x + 5 * x * x - x, Vector(-9 * x * x + 10 * x - 1), 1.0)
    }
    val rejected = ProximalGradient.minimize(
      higherStationary,
      Vector(0.0),
      bare,
      Sum,
      ProximalGradient.Settings(
        maxIterations = 1,
        maxEvaluations = 3,
        initialStep = 1.0,
        maximumBacktracks = 1
      )
    )
    require(
      !rejected.converged && rejected.iterations == 0 && rejected.parameters == Vector(0.0),
      "A stationary but objective-increasing candidate was accepted"
    )
    println(
      "Proximal terminal-certificate checks passed: large sums, raw KKT units and no objective increase"
    )
  }
}
