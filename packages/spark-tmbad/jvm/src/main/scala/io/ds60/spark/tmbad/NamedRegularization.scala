// SPDX-License-Identifier: MIT
package io.ds60.spark.tmbad

import java.io.{ByteArrayOutputStream, DataOutputStream}
import java.nio.charset.StandardCharsets
import java.security.MessageDigest

/** Named coordinate targets. Native/Spark evaluation and JSON admission stay outside this module. */
object NamedRegularization {
  final case class Gaussian(name: String, center: Double, precision: Double) extends Serializable {
    require(center.isFinite && precision.isFinite && precision > 0.0, "Invalid named Gaussian prior")
  }
  final case class L1(name: String, strength: Double) extends Serializable {
    require(strength.isFinite && strength > 0.0, "Invalid selected L1 strength")
  }
  final case class Fixed(name: String, value: Double) extends Serializable {
    require(value.isFinite, "Fixed coordinate must be finite")
  }

  final case class Domain(names: Vector[String], lower: Vector[Double], upper: Vector[Double])
      extends Serializable {
    require(names.nonEmpty && names.size <= 64 && names.distinct.size == names.size,
      "Expected one to 64 distinct prepared parameter names")
    require(names.forall(name => name != null && name.nonEmpty &&
      name.codePointCount(0, name.length) <= 256 && StandardCharsets.UTF_8.newEncoder().canEncode(name)),
      "Invalid prepared parameter name")
    require(lower.size == names.size && upper.size == names.size, "Bound dimensions differ")
    require(names.indices.forall { i =>
      !lower(i).isNaN && !upper(i).isNaN && lower(i) <= upper(i) &&
        lower(i) != Double.PositiveInfinity && upper(i) != Double.NegativeInfinity
    }, "Invalid parameter domain")

    def check(point: Vector[Double]): Unit = {
      require(point.size == names.size && point.forall(_.isFinite), "Invalid full parameter vector")
      require(point.indices.forall(i => point(i) >= lower(i) && point(i) <= upper(i)),
        "Parameter is outside its native/fixed domain")
    }
    def clamp(index: Int, value: Double): Double = math.max(lower(index), math.min(upper(index), value))
    def equality(index: Int): Boolean = lower(index) == upper(index)
    def freeIndices: Vector[Int] = names.indices.filterNot(equality).toVector
    def impose(values: Vector[Fixed]): Domain = {
      require(values.map(_.name).distinct.size == values.size, "Duplicate fixed parameter")
      var lo = lower
      var hi = upper
      values.foreach { fixed =>
        val index = names.indexOf(fixed.name)
        require(index >= 0, "Unknown fixed parameter")
        require(fixed.value >= lower(index) && fixed.value <= upper(index),
          "Fixed value is outside the native model domain")
        lo = lo.updated(index, fixed.value)
        hi = hi.updated(index, fixed.value)
      }
      Domain(names, lo, hi)
    }
    def effectiveInitial(initial: Vector[Double]): Vector[Double] = {
      require(initial.size == names.size && initial.forall(_.isFinite), "Invalid initial vector")
      val result = initial.indices.map(i => if (equality(i)) lower(i) else initial(i)).toVector
      check(result)
      result
    }
  }

  sealed trait Reduction extends Serializable { def name: String }
  case object Sum extends Reduction { val name = "sum" }
  case object WeightedMean extends Reduction { val name = "weighted_mean" }

  final case class Scaling(reduction: Reduction, likelihoodWeight: Double) extends Serializable {
    require(likelihoodWeight.isFinite && likelihoodWeight > 0.0, "Invalid likelihood weight mass")
    val denominator: Double = if (reduction == WeightedMean) likelihoodWeight else 1.0
    def checkWeight(observed: Double): Unit = {
      require(observed.isFinite && observed > 0.0 &&
        math.abs(observed - likelihoodWeight) <= 1e-12 * likelihoodWeight,
        "Likelihood weight mass changed after target binding")
    }
    def positiveStrength(value: Double): Double = {
      require(value.isFinite && value >= 0.0, "Invalid nonnegative target strength")
      val scaled = value / denominator
      require(scaled.isFinite && (value == 0.0 || scaled > 0.0),
        "Selected L1 strength is not representable under this reduction; use sum or rescale weights")
      scaled
    }
  }

  final case class RawEvaluation(value: Double, gradient: Vector[Double], weight: Double)
      extends Serializable {
    require(value.isFinite && gradient.nonEmpty && gradient.size <= 64 && gradient.forall(_.isFinite),
      "Raw numerical result is invalid")
    require(weight.isFinite && weight > 0.0, "Raw result has invalid effective likelihood weight")
  }
  final case class SmoothEvaluation(
      rawValue: Double,
      rawGradient: Vector[Double],
      rawDataValue: Double,
      rawDataGradient: Vector[Double],
      gaussianGradient: Vector[Double],
      gaussianQuadratic: Double,
      gaussianNormalizer: Double,
      scaling: Scaling
  ) extends Serializable {
    require(rawValue.isFinite && rawGradient.nonEmpty && rawGradient.forall(_.isFinite),
      "Smooth target is nonfinite")
    val value: Double = rawValue / scaling.denominator
    val gradient: Vector[Double] = rawGradient.map(_ / scaling.denominator)
    require(value.isFinite && gradient.forall(_.isFinite), "Reduced smooth target is nonfinite")
  }

  private def sum(values: Iterable[Double]): Double = {
    var total = 0.0
    var correction = 0.0
    values.foreach { value =>
      require(value.isFinite, "Nonfinite regularization contribution")
      val next = total + value
      correction += (if (math.abs(total) >= math.abs(value)) (total - next) + value
                     else (value - next) + total)
      total = next
    }
    val result = total + correction
    require(result.isFinite, "Regularization sum exceeds finite arithmetic")
    result
  }

  final class Plan private[NamedRegularization] (
      val modelDigest: String,
      val originalDomain: Domain,
      val domain: Domain,
      val gaussian: Vector[Gaussian],
      val l1: Vector[L1],
      val fixed: Vector[Fixed]
  ) extends Serializable {
    val coordinateSystem: String = "native_optimizer_parameters"
    val densityMeasure: String = "d_selected_native_optimizer_coordinates"
    val normalization: String = "summed_likelihood_target"
    val l1ConstantConvention: String = "none_penalty_only"
    private val indexedGaussian = gaussian.map(term => originalDomain.names.indexOf(term.name) -> term)
    val l1Strength: Vector[Double] = originalDomain.names.map { name =>
      l1.find(_.name == name).map(_.strength).getOrElse(0.0)
    }

    def smooth(raw: RawEvaluation, theta: Vector[Double], scaling: Scaling): SmoothEvaluation = {
      domain.check(theta)
      scaling.checkWeight(raw.weight)
      l1Strength.foreach(scaling.positiveStrength)
      require(raw.gradient.size == theta.size, "Raw gradient dimension differs")
      val gradient = raw.gradient.toArray
      val priorGradient = Array.fill(theta.size)(0.0)
      val quadratic = Vector.newBuilder[Double]
      val normalizer = Vector.newBuilder[Double]
      indexedGaussian.foreach { case (index, term) =>
        val rootPrecision = math.sqrt(term.precision)
        val difference = theta(index) - term.center
        // Do not form squares/differences on unselected coordinates. The second
        // expression handles a finite scaled difference when an unscaled one overflows.
        val scaled = if (difference.isFinite) rootPrecision * difference
                     else rootPrecision * theta(index) - rootPrecision * term.center
        require(scaled.isFinite, "Gaussian displacement exceeds finite arithmetic")
        quadratic += 0.5 * scaled * scaled
        normalizer += 0.5 * (math.log(2.0 * math.Pi) - math.log(term.precision))
        val score = rootPrecision * scaled
        require(score.isFinite, "Gaussian prior gradient exceeds finite arithmetic")
        priorGradient(index) = score
        gradient(index) = sum(Vector(gradient(index), score))
      }
      val q = sum(quadratic.result())
      val c = sum(normalizer.result())
      SmoothEvaluation(sum(Vector(raw.value, q, c)), gradient.toVector, raw.value,
        raw.gradient, priorGradient.toVector, q, c, scaling)
    }

    def rawL1Value(theta: Vector[Double]): Double = {
      domain.check(theta)
      sum(theta.indices.collect { case i if l1Strength(i) > 0.0 => l1Strength(i) * math.abs(theta(i)) })
    }
    def composite(current: SmoothEvaluation, theta: Vector[Double]): Double =
      sum(Vector(current.rawValue, rawL1Value(theta))) / current.scaling.denominator

    def rawL1Subgradients(theta: Vector[Double]): Vector[(Double, Double)] = {
      domain.check(theta)
      theta.indices.map { i =>
        if (theta(i) == 0.0) (-l1Strength(i), l1Strength(i))
        else {
          val value = math.signum(theta(i)) * l1Strength(i)
          (value, value)
        }
      }.toVector
    }

    /** Minimum absolute stationarity residual over L1 subgradients and box normal cones. */
    def rawKkt(theta: Vector[Double], rawSmoothGradient: Vector[Double]): Vector[Double] = {
      domain.check(theta)
      require(rawSmoothGradient.size == theta.size && rawSmoothGradient.forall(_.isFinite),
        "Invalid smooth gradient for KKT check")
      val intervals = rawL1Subgradients(theta)
      theta.indices.map { i =>
        if (domain.equality(i)) 0.0
        else {
          val low = rawSmoothGradient(i) + intervals(i)._1
          val high = rawSmoothGradient(i) + intervals(i)._2
          val residual =
            if (theta(i) == domain.lower(i)) math.max(0.0, -high)
            else if (theta(i) == domain.upper(i)) math.max(0.0, low)
            else if (low > 0.0) low
            else if (high < 0.0) -high
            else 0.0
          require(residual.isFinite, "KKT residual is not representable")
          residual
        }
      }.toVector
    }

    /** Exact separable proximal map for selected zero-centered L1 plus interval constraints. */
    def proximal(theta: Vector[Double], gradient: Vector[Double], step: Double,
                 scaling: Scaling): Option[Vector[Double]] = {
      domain.check(theta)
      require(gradient.size == theta.size && gradient.forall(_.isFinite), "Invalid proximal gradient")
      require(step.isFinite && step > 0.0, "Invalid proximal step")
      val values = theta.indices.map { i =>
        if (domain.equality(i)) domain.lower(i)
        else {
          val moved = theta(i) - step * gradient(i)
          if (!moved.isFinite) Double.NaN
          else {
            val threshold = step * scaling.positiveStrength(l1Strength(i))
            // Positive overflow here means a threshold larger than every finite
            // moved value, whose soft-thresholded result is exactly zero.
            val softened = if (math.abs(moved) <= threshold) 0.0
                           else math.signum(moved) * (math.abs(moved) - threshold)
            domain.clamp(i, softened)
          }
        }
      }.toVector
      if (values.forall(_.isFinite)) Some(values) else None
    }

    /** Stable binary encoding for cross-language target identity, specified in the design notes. */
    val digest: String = {
      val bytes = new ByteArrayOutputStream()
      val output = new DataOutputStream(bytes)
      def text(value: String): Unit = {
        val encoded = value.getBytes(StandardCharsets.UTF_8)
        output.writeInt(encoded.length); output.write(encoded)
      }
      def number(value: Double): Unit = output.writeDouble(if (value == 0.0) 0.0 else value)
      text("spark-tmbad-named-target-v1"); text(modelDigest)
      text(coordinateSystem); text(densityMeasure); text(normalization); text(l1ConstantConvention)
      output.writeInt(domain.names.size)
      domain.names.indices.foreach { i =>
        text(domain.names(i))
        output.writeBoolean(originalDomain.lower(i).isFinite)
        if (originalDomain.lower(i).isFinite) number(originalDomain.lower(i))
        output.writeBoolean(originalDomain.upper(i).isFinite)
        if (originalDomain.upper(i).isFinite) number(originalDomain.upper(i))
        val prior = gaussian.find(_.name == domain.names(i))
        output.writeBoolean(prior.nonEmpty)
        prior.foreach(term => { number(term.center); number(term.precision) })
        number(l1Strength(i))
        val fixedValue = fixed.find(_.name == domain.names(i))
        output.writeBoolean(fixedValue.nonEmpty)
        fixedValue.foreach(term => number(term.value))
      }
      output.close()
      MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray)
        .map(byte => f"${byte & 0xff}%02x").mkString
    }
  }

  def prepare(modelDigest: String, domain: Domain, gaussian: Vector[Gaussian], l1: Vector[L1],
              fixed: Vector[Fixed], legacyL2Strength: Double = 0.0): Plan = {
    require(modelDigest.matches("[a-f0-9]{64}"), "Expected prepared model digest")
    require(legacyL2Strength == 0.0, "Nonzero legacy L2 cannot be mixed with a named target")
    require(gaussian.map(_.name).distinct.size == gaussian.size &&
      l1.map(_.name).distinct.size == l1.size, "Duplicate named regularization term")
    require((gaussian.map(_.name) ++ l1.map(_.name) ++ fixed.map(_.name))
      .forall(domain.names.contains), "Unknown named target coordinate")
    val positions = domain.names.zipWithIndex.toMap
    new Plan(modelDigest, domain, domain.impose(fixed),
      gaussian.sortBy(term => positions(term.name)), l1.sortBy(term => positions(term.name)),
      fixed.sortBy(term => positions(term.name)))
  }
}
