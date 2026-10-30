package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode

private[tmbad] final case class NativeEvaluation(
    loss: Double,
    gradient: Vector[Double],
    rowCount: Long,
    unitCount: Long,
    weightSum: Double,
    diagnostics: String
) extends Serializable

private[tmbad] object NativeCalls {
  private val envelope = Set(
    "protocol",
    "request_id",
    "status",
    "request_sha256",
    "model_id",
    "model_digest",
    "build_id"
  )
  private def matrix(request: ObjectNode, name: String, rows: Vector[NativeRow]): Unit = {
    val array = request.putArray(name)
    rows.foreach { row =>
      val values = Json.array(); row.values.foreach(values.add); array.add(values)
    }
  }
  def evaluate(
      worker: NativeWorker,
      model: NativeModel,
      theta: Vector[Double],
      rows: Vector[NativeRow]
  ): NativeEvaluation = {
    val unit = model.fitKind == "unit"
    require(
      rows.nonEmpty && rows.size <= (if (unit) model.maxUnitRows else 8192),
      "Invalid native batch/unit size"
    )
    require(rows.forall(_.values.size == model.fitFields.size), "Native fit field width differs")
    val request = NativeWorker.modelRequest("evaluate", model, theta)
    request.put("kind", model.fitKind).put("hessian", false)
    matrix(request, "rows", rows)
    val weight = if (unit) {
      require(
        rows.forall(_.weight == rows.head.weight),
        "A complete unit needs one consistent weight, applied once"
      )
      request.put("unit_weight", rows.head.weight)
      rows.head.weight
    } else {
      val weights = request.putArray("weights"); rows.foreach(row => weights.add(row.weight))
      val sum = new StableSum; rows.foreach(row => sum.add(row.weight)); sum.value
    }
    val response = worker.exchange(request)
    Json.fields(
      response,
      envelope ++ Set("loss", "gradient", "row_count", "unit_count", "weight_sum", "diagnostics")
    )
    require(
      Json.integer(response, "row_count", 0, 8192) == rows.size &&
        Json.integer(response, "unit_count", 0, 1) == (if (unit) 1 else 0),
      "Native row/unit coverage differs"
    )
    val mass = Json.fieldNumber(response, "weight_sum")
    require(
      math.abs(mass - weight) <= 1e-12 * math.max(1.0, math.abs(weight)),
      "Native weight accounting differs"
    )
    val gradient = Json.numbers(response.get("gradient"), 64, "gradient")
    require(gradient.size == theta.size, "Native gradient dimension differs")
    val diagnostics = response.get("diagnostics")
    require(
      diagnostics.isObject && Json.text(diagnostics, "marginalization") == model.marginalization,
      "Native marginalization declaration differs"
    )
    if (model.marginalization == "laplace") {
      require(
        Json.fieldNumber(diagnostics, "inner_score_inf") <= 1e-9 &&
          Json.fieldNumber(diagnostics, "inner_score_inf") >= 0,
        "Latent mode has not reached required stationarity"
      )
      val minimum = Json.fieldNumber(diagnostics, "minimum_eigenvalue")
      val maximum = Json.fieldNumber(diagnostics, "maximum_eigenvalue")
      require(
        minimum > 1e-10 * math.max(1.0, maximum),
        "Latent mode curvature is not positive and conditioned"
      )
    }
    val loss = Json.fieldNumber(response, "loss")
    if (weight == 0)
      require(
        loss == 0 && gradient.forall(_ == 0),
        "Zero-weight likelihood has a nonzero contribution"
      )
    NativeEvaluation(
      loss,
      gradient,
      rows.size.toLong,
      if (unit) 1L else 0L,
      mass,
      Json.write(diagnostics)
    )
  }
  def predict(
      worker: NativeWorker,
      model: NativeModel,
      theta: Vector[Double],
      targetName: String,
      target: NativeTarget,
      rows: Vector[NativeRow],
      history: Vector[NativeRow],
      forecast: Boolean
  ): Vector[Vector[Double]] = {
    require(
      rows.nonEmpty && rows.size <= (if (forecast || model.fitKind == "unit") model.maxUnitRows
                                     else 8192),
      "Prediction/forecast rows exceed the declared bound"
    )
    require(rows.forall(_.values.size == target.fields.size), "Prediction field width differs")
    require(
      history.size <= model.maxUnitRows && history.forall(_.values.size == model.fitFields.size),
      "History field width or unit bound differs"
    )
    require(
      !target.needsHistory || history.nonEmpty,
      "Declared conditional target requires complete history"
    )
    val request = NativeWorker.modelRequest(if (forecast) "forecast" else "predict", model, theta)
    request.put("target", targetName)
    matrix(request, "rows", rows)
    if (forecast || target.needsHistory || history.nonEmpty) matrix(request, "history", history)
    val response = worker.exchange(request)
    Json.fields(
      response,
      envelope ++ Set("columns", "values", "row_count", "conditioning", "uncertainty")
    )
    require(
      Json.strings(
        response.get("columns"),
        256,
        "prediction columns",
        allowEmpty = false
      ) == target.columns &&
        Json.integer(response, "row_count", 0, 8192) == rows.size,
      "Native output column/cardinality contract differs"
    )
    require(
      Json.text(response, "conditioning") == target.conditioning &&
        Json.text(response, "uncertainty") == target.uncertainty,
      "Native prediction interpretation differs"
    )
    Json.elements(response.get("values"), 8192, "prediction values").map { row =>
      val result = Json.numbers(row, 256, "prediction row")
      require(result.size == target.columns.size, "Native prediction row width differs")
      result
    } match {
      case values if values.size == rows.size => values
      case _                                  =>
        throw new IllegalArgumentException("Native prediction rows are missing or duplicated")
    }
  }
}

/** Neumaier summation reduces partition and batch accumulation error without changing weights. */
private[tmbad] final class StableSum extends Serializable {
  private var total = 0.0
  private var compensation = 0.0
  def add(value: Double): Unit = {
    require(value.isFinite, "Cannot accumulate a nonfinite value")
    val updated = total + value
    compensation += (if (math.abs(total) >= math.abs(value)) (total - updated) + value
                     else (value - updated) + total)
    total = updated
    require(total.isFinite && compensation.isFinite, "Numerical accumulation overflow")
  }
  def value: Double = {
    val result = total + compensation
    require(result.isFinite, "Nonfinite accumulated result")
    result
  }
}

private[tmbad] final case class Ledger(count: Long, xor: BigInt, sum: BigInt) extends Serializable {
  def +(other: Ledger): Ledger =
    Ledger(Math.addExact(count, other.count), xor ^ other.xor, (sum + other.sum) & Ledger.mask)
  def json: JsonNode = {
    val node = Json.obj()
    node.put("count", count).put("xor", xor.toString(16)).put("sum", sum.toString(16))
    node
  }
}
private[tmbad] object Ledger {
  val mask: BigInt = (BigInt(1) << 256) - 1
  val empty: Ledger = Ledger(0, BigInt(0), BigInt(0))
  def row(value: NativeRow): Ledger = {
    val node = Json.obj()
    node
      .put("ids", value.idKey)
      .put("groups", value.groupKey)
      .put("order", KeyAtom.encode(value.order))
    Json.putNumbers(node, "values", value.values); node.put("weight", value.weight)
    val hash = BigInt(Json.sha(Json.bytes(node)), 16)
    Ledger(1, hash, hash)
  }
}
