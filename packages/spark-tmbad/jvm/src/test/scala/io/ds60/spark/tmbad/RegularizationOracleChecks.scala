// SPDX-License-Identifier: MIT
// Pure JVM target oracle checks. Qualification applies only after actual execution.
package io.ds60.spark.tmbad

import NamedRegularization._
import scala.reflect.ClassTag

object RegularizationOracleChecks {
  private val modelDigest = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  private def close(actual: Double, expected: Double, tolerance: Double = 1e-5): Unit =
    require(
      math.abs(actual - expected) <= tolerance * math.max(1.0, math.abs(expected)),
      s"Oracle mismatch: $actual versus $expected"
    )
  private def expect[T <: Throwable: ClassTag](body: => Unit): Unit = {
    var observed = false
    try body
    catch {
      case error: Throwable if implicitly[ClassTag[T]].runtimeClass.isInstance(error) =>
        observed = true
    }
    require(observed, "Expected the precise failure class")
  }

  def main(args: Array[String]): Unit = {
    val settings = ProximalGradient.Settings(maxIterations = 1000, maxEvaluations = 10000)
    RegularizationOracleFixtures.values.foreach { fixture =>
      val plan = prepare(modelDigest, fixture.domain, fixture.gaussian, fixture.l1, fixture.fixed)
      require(
        plan.digest == fixture.expectedDigest,
        "Cross-language canonical target digest differs"
      )
      val results = Vector(Sum, WeightedMean).map { reduction =>
        val result =
          ProximalGradient.minimize(fixture.evaluate, fixture.initial, plan, reduction, settings)
        require(
          result.converged && result.rawKktInfinityNorm <= settings.kktTolerance,
          s"${fixture.id}: ${result.status}, residual=${result.rawKktInfinityNorm}"
        )
        result.parameters.indices.foreach(i => close(result.parameters(i), fixture.expected(i)))
        val divisor = if (reduction == WeightedMean) fixture.weight else 1.0
        close(result.compositeValue, fixture.expectedComposite / divisor)
        require(
          result.trace
            .sliding(2)
            .forall(pair =>
              pair.size < 2 ||
                pair(1).compositeValue <= pair(0).compositeValue +
                32 * math
                  .ulp(math.max(math.abs(pair(0).compositeValue), math.abs(pair(1).compositeValue)))
            ),
          "Composite objective did not descend"
        )
        if (fixture.fixed.size == fixture.names.size)
          require(
            result.status == "all_parameters_fixed" && result.objectiveCalls == 1 &&
              result.freeParameterCount == 0,
            "All-fixed result invented an optimization history"
          )
        result
      }
      results.head.parameters.indices.foreach(i =>
        close(results.head.parameters(i), results(1).parameters(i))
      )
    }

    val domain = Domain(
      Vector("coefficient"),
      Vector(Double.NegativeInfinity),
      Vector(Double.PositiveInfinity)
    )
    val plan = prepare(modelDigest, domain, Vector.empty, Vector.empty, Vector.empty)
    def quadratic(theta: Vector[Double]): RawEvaluation =
      RawEvaluation(math.pow(theta.head - 0.25, 2), Vector(2 * (theta.head - 0.25)), 1.0)
    val recovery = ProximalGradient.minimize(
      theta => {
        if (theta.head < 0.0)
          throw new ProximalGradient.ReviewedDomainFailure("reviewed scientific trial")
        quadratic(theta)
      },
      Vector(1.0),
      plan,
      Sum,
      settings.copy(initialStep = 10.0)
    )
    require(
      recovery.converged && recovery.rejectedCandidates > 0,
      "Reviewed later trial was not recovered"
    )
    close(recovery.parameters.head, 0.25)
    expect[ProximalGradient.ReviewedDomainFailure] {
      ProximalGradient.minimize(
        _ => throw new ProximalGradient.ReviewedDomainFailure("initial"),
        Vector(1.0),
        plan,
        Sum,
        settings
      )
    }
    expect[IllegalStateException] {
      ProximalGradient.minimize(
        theta => {
          if (theta.head < 0.0) throw new IllegalStateException("infrastructure failure")
          quadratic(theta)
        },
        Vector(1.0),
        plan,
        Sum,
        settings.copy(initialStep = 10.0)
      )
    }
    expect[IllegalArgumentException] {
      prepare(
        modelDigest,
        domain,
        Vector(Gaussian("unknown", 0.0, 1.0)),
        Vector.empty,
        Vector.empty
      )
    }
    expect[IllegalArgumentException] {
      prepare(
        modelDigest,
        domain,
        Vector(Gaussian("coefficient", 0.0, 1.0)),
        Vector.empty,
        Vector.empty,
        legacyL2Strength = 0.2
      )
    }
    val hugeDomain = Domain(
      Vector("unselected", "slope"),
      Vector(Double.NegativeInfinity, Double.NegativeInfinity),
      Vector(Double.PositiveInfinity, Double.PositiveInfinity)
    )
    val selected = prepare(
      modelDigest,
      hugeDomain,
      Vector(Gaussian("slope", 0.5, 2.0)),
      Vector.empty,
      Vector.empty
    )
    val huge = selected.smooth(
      RawEvaluation(1.0, Vector(0.0, 0.0), 1.0),
      Vector(1e300, 0.5),
      Scaling(Sum, 1.0)
    )
    require(
      huge.gaussianQuadratic == 0.0 && huge.rawGradient.forall(_ == 0.0),
      "Unselected huge coordinate leaked into the named prior"
    )
    println(
      "Named regularization oracle execution passed: 18 convex fits, canonical digests and bounded failure controls"
    )
  }
}
