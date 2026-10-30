package io.ds60.spark.tmbad

/** Actual JVM numerical/parser checks, independent of a native worker or Spark session. */
object ContractChecks {
  private def refused(body: => Unit): Unit = {
    var failed = false
    try body
    catch { case _: Exception => failed = true }
    assert(failed, "Expected an invalid contract to be refused")
  }
  def main(arguments: Array[String]): Unit = {
    refused { Json.read("{\"x\":1,\"x\":2}"); () }
    refused { Json.read("{\"x\":9007199254740993}"); () }
    refused { Json.number(Json.obj().put("x", 9007199254740993L).get("x"), "integer"); () }
    refused { Json.read("{\"x\":NaN}"); () }
    refused { Json.read("{\"x\":1e999}"); () }
    refused { Json.read("{} {}"); () }
    refused { Json.read(Array[Byte](0xc0.toByte, 0xaf.toByte)); () }
    refused { Json.read("{\"x\":\"" + 0xd800.toChar + "\"}"); () }
    refused { Json.read("{\"x\":\"\\ud800\"}"); () }
    val supplementary = new String(Character.toChars(0x1f4da))
    val keys = Json.obj(); keys.put(supplementary * 256, "valid")
    assert(Json.read(Json.bytes(keys)).size() == 1)
    refused { keys.put(supplementary * 257, "invalid"); Json.bytes(keys); () }

    assert(GlobalPenalty.value(Vector(1e200), 0.0) == 0.0)
    val scaledPenalty = GlobalPenalty.value(Vector(1e200), 1e-300)
    assert(scaledPenalty.isFinite && math.abs(scaledPenalty / 5e99 - 1) < 1e-12)
    refused { GlobalPenalty.value(Vector(1e308), 1.0); () }

    val tiny = NativeRow(
      Vector(KeyAtom("string", "one")),
      Vector.empty,
      Vector.empty,
      Vector(KeyAtom("string", "one")),
      Vector(1.0),
      1.0
    )
    val budget = new RowBudget(512)
    budget.add(tiny)
    refused { budget.add(tiny) }
    assert(Data.batches(Iterator(tiny, tiny, tiny), 2).map(_.size).toVector == Vector(2, 1))

    def executableBusy(): java.io.IOException =
      new java.io.IOException("launch failed", new java.io.IOException("error=26, Text file busy"))
    var launches = 0; var validations = 0
    val pauses = scala.collection.mutable.ArrayBuffer.empty[Long]
    val launched = NativeLaunch.start(
      () => {
        launches += 1
        if (launches <= 2) throw executableBusy()
        new ProcessBuilder("/bin/sh", "-c", "exit 0").start()
      },
      () => { validations += 1 },
      delay => { pauses += delay }
    )
    assert(
      launched.waitFor() == 0 && launches == 3 && validations == 3 && pauses.toVector == Vector(
        10L,
        20L
      )
    )
    var exhaustedLaunches = 0
    refused {
      NativeLaunch.start(
        () => { exhaustedLaunches += 1; throw executableBusy() },
        () => (),
        _ => ()
      );
      ()
    }
    assert(exhaustedLaunches == 6)
    val infrastructure = new java.io.IOException(
      "launch failed",
      new java.io.IOException("error=13, Permission denied")
    )
    var unrelatedLaunches = 0
    var exactInfrastructure = false
    try
      NativeLaunch.start(() => { unrelatedLaunches += 1; throw infrastructure }, () => (), _ => ())
    catch { case error: java.io.IOException => exactInfrastructure = error eq infrastructure }
    assert(exactInfrastructure && unrelatedLaunches == 1)
    var interruptedLaunches = 0
    var interruptionPreserved = false
    try
      NativeLaunch.start(
        () => { interruptedLaunches += 1; throw executableBusy() },
        () => (),
        _ => throw new InterruptedException("cancelled")
      )
    catch { case _: InterruptedException => interruptionPreserved = true }
    assert(interruptionPreserved && interruptedLaunches == 1)

    assert(ColumnNames.equivalent("TMBAD_VARİANCE", "tmbad_variance"))
    assert(ColumnNames.equivalent("TMBAD_ſD", "tmbad_sd"))
    assert(!ColumnNames.unique(Vector("TMBAD_VARİANCE", "tmbad_variance")))
    assert(ColumnNames.unique(Vector("TMBAD_VARİANCE", "prediction_variance")))
    val artifacts = new ArtifactBudget(2, 12)
    artifacts.add("first", 8); artifacts.add("second", 4)
    assert(artifacts.count == 2 && artifacts.bytes == 12)
    refused { artifacts.add("third", 0) }
    refused { artifacts.check("first", 9) }
    val bytesOnly = new ArtifactBudget(2, 10)
    bytesOnly.add("first", 7)
    refused { bytesOnly.add("second", 4) }
    assert(bytesOnly.count == 1 && bytesOnly.bytes == 7)

    import Optimizer._
    def quadratic(target: Double)(point: Vector[Double]): Evaluation =
      Evaluation(0.5 * math.pow(point.head - target, 2), Vector(point.head - target))
    assert(
      NumericalRejection.reviewed(
        new NativeFailure(
          "INNER_MODE_FAILURE",
          "fixture",
          verifiedTerminal = true,
          operation = "evaluate"
        )
      )
    )
    assert(!NumericalRejection.reviewed(new NativeFailure("INNER_MODE_FAILURE", "fixture")))
    assert(
      !NumericalRejection.reviewed(
        new NativeFailure(
          "RESOURCE_LIMIT",
          "fixture",
          verifiedTerminal = true,
          operation = "evaluate"
        )
      )
    )
    assert(
      !NumericalRejection.reviewed(
        new NativeFailure(
          "AD_INVARIANT",
          "fixture",
          verifiedTerminal = true,
          operation = "evaluate"
        )
      )
    )
    val recovered = minimize(
      point => {
        if (point.head < 0) throw new DomainFailure("reviewed scientific candidate")
        Evaluation(5 * math.pow(point.head - 0.5, 2), Vector(10 * (point.head - 0.5)))
      },
      Vector(2.0)
    )
    assert(
      recovered.converged && recovered.rejectedCandidates > 0 && math.abs(
        recovered.parameters.head - 0.5
      ) < 1e-6
    )
    var invalidInitialCalls = 0
    refused {
      minimize(
        _ => { invalidInitialCalls += 1; throw new DomainFailure("invalid initial") },
        Vector(0.0)
      );
      ()
    }
    assert(invalidInitialCalls == 1)
    val interior = minimize(quadratic(3.0), Vector(-2.0))
    assert(interior.converged && math.abs(interior.parameters.head - 3.0) < 1e-8)
    val lower = minimize(
      quadratic(-2.0),
      Vector(0.5),
      specifiedBounds = Some(Bounds(Vector(0.0), Vector(1.0)))
    )
    assert(
      lower.converged && lower.parameters == Vector(
        0.0
      ) && lower.rawGradientInfinityNorm == 2.0 && lower.projectedGradientInfinityNorm == 0
    )
    val upper = minimize(
      quadratic(2.0),
      Vector(0.5),
      specifiedBounds = Some(Bounds(Vector(0.0), Vector(1.0)))
    )
    assert(
      upper.converged && upper.parameters == Vector(
        1.0
      ) && upper.rawGradientInfinityNorm == 1.0 && upper.projectedGradientInfinityNorm == 0
    )
    val fixed = minimize(
      quadratic(5.0),
      Vector(0.0),
      specifiedBounds = Some(Bounds(Vector(2.0), Vector(2.0)))
    )
    assert(fixed.converged && fixed.parameters == Vector(2.0) && fixed.activeBounds == Vector(0))
    val masked = minimize(
      point => {
        val x = point(0); val nuisance = point(1)
        Evaluation(3 * math.pow(x - 5.0 / 3.0, 2) + 20 * nuisance * x * x + 0.5 * nuisance * nuisance,
          Vector(6 * (x - 5.0 / 3.0) + 40 * nuisance * x, 20 * x * x + nuisance))
      },
      Vector(0.0, 0.0),
      Settings(gradientTolerance = 1e-9, functionTolerance = 0.0),
      Some(Bounds(Vector(Double.NegativeInfinity, 0.0), Vector(Double.PositiveInfinity, 0.0)))
    )
    assert(masked.converged && masked.iterations <= 3 && math.abs(masked.parameters.head - 5.0 / 3.0) < 1e-10,
      "Equality-fixed gradients contaminated the free-coordinate secant update")
    val maskedScale = minimize(
      point => Evaluation(1.5 * math.pow(point.head - 1.0, 2), Vector(3 * (point.head - 1.0), 0.0)),
      Vector(0.0, 1e200), Settings(gradientTolerance = 1e-9, functionTolerance = 0.0),
      Some(Bounds(Vector(Double.NegativeInfinity, 1e200), Vector(Double.PositiveInfinity, 1e200)))
    )
    assert(maskedScale.converged && math.abs(maskedScale.parameters.head - 1.0) < 1e-10,
      "A large fixed coordinate caused false free-coordinate step stalling")
    var latestEvaluated = Vector.empty[Double]
    var latestAccepted = Vector.empty[Double]
    val acceptedState = minimize(
      point => { latestEvaluated = point; Evaluation(point.head * point.head, Vector(2 * point.head)) },
      Vector(2.0), Settings(maxEvaluations = 2), None,
      onAccepted = (point, _) => { latestAccepted = point }
    )
    assert(!acceptedState.converged && latestAccepted == acceptedState.parameters && latestEvaluated != latestAccepted,
      "Rejected Armijo metadata replaced the accepted point")
    val narrow = minimize(
      quadratic(1.0),
      Vector(0.0),
      specifiedBounds = Some(Bounds(Vector(0.0), Vector(1e-10)))
    )
    assert(narrow.converged && narrow.parameters == Vector(1e-10))
    val exhausted = minimize(quadratic(3.0), Vector(0.0), Settings(maxEvaluations = 1))
    assert(!exhausted.converged && exhausted.status == "maximum_evaluations")
    val stalled = minimize(
      point => Evaluation(1e-20 * math.exp(point.head), Vector(1e-20 * math.exp(point.head))),
      Vector(0.0),
      Settings(gradientTolerance = 1e-30)
    )
    assert(!stalled.converged)
    var infrastructureCalls = 0
    var infrastructurePropagated = false
    try
      minimize(
        point => {
          infrastructureCalls += 1
          if (infrastructureCalls > 1) throw new java.io.IOException("infrastructure failure")
          quadratic(3.0)(point)
        },
        Vector(0.0)
      )
    catch { case _: java.io.IOException => infrastructurePropagated = true }
    assert(infrastructurePropagated && infrastructureCalls == 2)
    refused { minimize(_ => Evaluation(Double.NaN, Vector(0.0)), Vector(0.0)); () }
    println(
      "{\"kind\":\"spark-tmbad-jvm-contracts\",\"passed\":true,\"scope\":\"JVM parser and original optimizer only; no native/Spark execution claim\"}"
    )
  }
}
