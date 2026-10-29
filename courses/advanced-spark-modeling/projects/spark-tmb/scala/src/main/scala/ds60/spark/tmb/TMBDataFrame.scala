package ds60.spark.tmb

import com.fasterxml.jackson.databind.{JsonNode, ObjectMapper}
import com.fasterxml.jackson.core.JsonParser
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.nio.file.{Files, Path}
import java.security.MessageDigest
import java.util.concurrent.TimeUnit
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Row}
import org.apache.spark.sql.types._
import scala.collection.mutable.ArrayBuffer
import scala.jdk.CollectionConverters._
import scala.util.Using

/** Fixed transport, not a second model/ABI validator. The Python CLI owns those checks. */
object ModelBridge {
  private val Limit = 1000000L
  def mapper(): ObjectMapper =
    new ObjectMapper().enable(JsonParser.Feature.STRICT_DUPLICATE_DETECTION)
  def finite(value: Double): Double = {
    require(value.isFinite, "Nonfinite numerical result")
    value
  }
  def digest(theta: Vector[Double]): String = {
    val bytes = ByteBuffer.allocate(4 + 8 * theta.size).putInt(theta.size)
    theta.foreach(value => bytes.putDouble(finite(value)))
    hex(MessageDigest.getInstance("SHA-256").digest(bytes.array()))
  }
  def hex(bytes: Array[Byte]): String = bytes.map(b => f"${b & 0xff}%02x").mkString
  private def cleanup(process: Process): Unit = {
    val children = Using.resource(process.descendants())(_.iterator().asScala.toVector)
    children.reverse.foreach(_.destroyForcibly())
    if (process.isAlive) process.destroyForcibly()
    try process.waitFor(5, TimeUnit.SECONDS)
    catch { case _: InterruptedException => Thread.currentThread().interrupt() }
  }
  private def delete(directory: Path): Unit =
    Using.resource(Files.walk(directory)) { paths =>
      paths.iterator().asScala.toVector.sortBy(_.getNameCount).reverse.foreach(Files.deleteIfExists)
    }
  def request(payload: JsonNode): JsonNode = {
    val encoded = mapper().writeValueAsBytes(payload)
    require(encoded.length <= Limit, "CLI request exceeds one megabyte")
    val directory = Files.createTempDirectory("ds60-scala-tmb-")
    var process: Process = null
    try {
      val stdout = directory.resolve("stdout.json")
      val stderr = directory.resolve("stderr.json")
      process = new ProcessBuilder("/usr/local/bin/python", "-m", "spark_tmb.cli")
        .redirectOutput(stdout.toFile)
        .redirectError(stderr.toFile)
        .start()
      Using.resource(process.getOutputStream)(_.write(encoded))
      val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(65)
      while (!process.waitFor(100, TimeUnit.MILLISECONDS)) {
        require(System.nanoTime() < deadline, "Prepared-model CLI timed out")
        require(
          Files.size(stdout) <= Limit && Files.size(stderr) <= Limit,
          "Prepared-model CLI output exceeds one megabyte"
        )
      }
      require(
        Files.size(stdout) <= Limit && Files.size(stderr) <= Limit,
        "Prepared-model CLI output exceeds one megabyte"
      )
      if (process.exitValue() != 0) {
        val detail = Using.resource(Files.newInputStream(stderr)) { stream =>
          new String(stream.readNBytes(4096), StandardCharsets.UTF_8)
        }
        throw new IllegalArgumentException(
          s"Prepared-model CLI exit ${process.exitValue()}: $detail"
        )
      }
      val response = mapper().readTree(Files.readAllBytes(stdout))
      validateEnvelope(response, payload)
    } finally {
      if (process != null) cleanup(process)
      delete(directory)
    }
  }
  def validateEnvelope(response: JsonNode, payload: JsonNode): JsonNode = {
    require(response != null && response.isObject, "CLI response must be an object")
    require(
      response.fieldNames().asScala.toSet == Set(
        "schema_version",
        "operation",
        "model_id",
        "result"
      ),
      "CLI response fields differ from the fixed envelope"
    )
    require(
      response
        .path("schema_version")
        .isIntegralNumber && response.path("schema_version").asInt(-1) == 1,
      "Unsupported CLI response version"
    )
    require(
      response.path("operation").isTextual && response.path("model_id").isTextual &&
        response.path("operation") == payload.path("operation") &&
        response.path("model_id") == payload.path("model_id"),
      "CLI response identity mismatch"
    )
    require(response.path("result").isObject, "CLI result must be an object")
    response.get("result")
  }
  def describe(model: String): ModelDescription = {
    val json = mapper().createObjectNode()
    json.put("schema_version", 1).put("operation", "describe").put("model_id", model)
    val result = request(json)
    val spec = result.path("spec")
    require(
      spec.path("factorization").asText() == "independent_rows" && spec.path("random").isNull,
      "Scala row batching only supports registered independent_rows models without random effects"
    )
    val fields = spec
      .path("data")
      .fields()
      .asScala
      .toVector
      .map(e => e.getKey -> e.getValue.asText())
      .sortBy(_._1)
    val parameters = spec.path("fixed_parameters").elements().asScala.toVector.map(_.asText())
    val prepared = result.path("prepared")
    require(
      fields.nonEmpty && parameters.nonEmpty && parameters.size <= 64,
      "Description exceeds this adapter's bounded field/parameter contract"
    )
    val maxRows = result.path("max_rows").asInt(0)
    require(maxRows > 0 && maxRows <= 4096, "Unsupported CLI row bound")
    ModelDescription(
      model,
      fields,
      parameters,
      maxRows,
      prepared.path("source_sha256").asText(),
      prepared.path("library_sha256").asText(),
      prepared.path("registry_sha256").asText(),
      prepared.path("abi").toString
    )
  }
  def evaluate(
      description: ModelDescription,
      rows: Vector[Row],
      theta: Vector[Double]
  ): Evaluation = {
    require(rows.nonEmpty && rows.size <= description.maxRows, "Bounded nonempty batch required")
    val json = mapper().createObjectNode()
    json.put("schema_version", 1).put("operation", "evaluate").put("model_id", description.model)
    val parameters = json.putArray("parameters")
    theta.foreach(value => parameters.add(finite(value)))
    val data = json.putObject("data")
    description.fields.zipWithIndex.foreach { case ((name, _), index) =>
      val values = data.putArray(name)
      rows.foreach { row =>
        require(!row.isNullAt(index + 1), s"Null in declared field $name")
        row.get(index + 1) match {
          case value: java.lang.Byte    => values.add(value.intValue())
          case value: java.lang.Short   => values.add(value.intValue())
          case value: java.lang.Integer => values.add(value.intValue())
          case value: java.lang.Long    => values.add(value.longValue())
          case value: java.lang.Float   => values.add(finite(value.doubleValue()))
          case value: java.lang.Double  => values.add(finite(value.doubleValue()))
          case _ => throw new IllegalArgumentException(s"Nonprimitive numeric field $name")
        }
      }
    }
    val result = request(json)
    require(
      result.path("schema_version").isIntegralNumber &&
        result.path("schema_version").asInt(-1) == 1 && result
          .path("model_id")
          .asText() == description.model,
      "Prepared result identity mismatch"
    )
    require(
      result.path("nobs").isIntegralNumber && result.path("nobs").asLong() == rows.size,
      "Prepared result row count mismatch"
    )
    require(
      result.path("parameter_digest_input").asText() == digest(theta),
      "Stale parameter result"
    )
    val names = result.path("parameter_names").elements().asScala.toVector.map(_.asText())
    require(names == description.parameters, "Prepared parameter order changed")
    require(
      result.path("artifact_source_sha256").asText() == description.sourceSha &&
        result.path("artifact_library_sha256").asText() == description.librarySha &&
        result.path("artifact_registry_sha256").asText() == description.registrySha &&
        result.path("abi") == mapper().readTree(description.abiJson),
      "Prepared artifact/ABI changed"
    )
    require(
      result
        .path("gradient")
        .isArray && result.path("gradient").elements().asScala.forall(_.isNumber),
      "Gradient must be a JSON numeric array"
    )
    val gradient =
      result.path("gradient").elements().asScala.toVector.map(x => finite(x.doubleValue()))
    require(
      gradient.size == theta.size && result.path("value").isNumber,
      "Malformed numerical result"
    )
    Evaluation(finite(result.get("value").doubleValue()), gradient, rows.size.toLong)
  }
}

case class ModelDescription(
    model: String,
    fields: Vector[(String, String)],
    parameters: Vector[String],
    maxRows: Int,
    sourceSha: String,
    librarySha: String,
    registrySha: String,
    abiJson: String
) extends Serializable
case class Evaluation(value: Double, gradient: Vector[Double], rows: Long) extends Serializable
case class Ledger(partition: Int, rows: Long, content: String) extends Serializable
case class PartitionResult(ledger: Ledger, evaluation: Evaluation, batches: Int)
    extends Serializable

/** Compensated constant-memory reduction. This is floating arithmetic, not exact real addition. */
class Compensated extends Serializable {
  private var sum = 0.0
  private var correction = 0.0
  def add(value: Double): Unit = {
    ModelBridge.finite(value)
    val next = ModelBridge.finite(sum + value)
    correction = ModelBridge.finite(
      correction +
        (if (math.abs(sum) >= math.abs(value)) (sum - next) + value else (value - next) + sum)
    )
    sum = next
  }
  def result: Double = ModelBridge.finite(sum + correction)
}

object PartitionWork {
  private val Modulus = BigInt(1) << 256
  def rowIdentity(row: Row): String = {
    require(!row.isNullAt(0), "Observation ID must not be null")
    val id = row.get(0).toString
    require(id.nonEmpty && id.length <= 128, "Observation ID must contain 1..128 characters")
    id
  }
  def rowHash(row: Row): BigInt = {
    val node = ModelBridge.mapper().createArrayNode()
    node.add(rowIdentity(row))
    row.toSeq.drop(1).foreach {
      case null                 => node.addNull()
      case n: java.lang.Byte    => node.add(n.intValue())
      case n: java.lang.Short   => node.add(n.intValue())
      case n: java.lang.Integer => node.add(n.intValue())
      case n: java.lang.Long    => node.add(n.longValue())
      case n: java.lang.Float   => node.add(ModelBridge.finite(n.doubleValue()))
      case n: java.lang.Double  => node.add(ModelBridge.finite(n.doubleValue()))
      case _ => throw new IllegalArgumentException("Projection contains a nonnumeric model field")
    }
    BigInt(
      1,
      MessageDigest.getInstance("SHA-256").digest(ModelBridge.mapper().writeValueAsBytes(node))
    )
  }
  def inspect(index: Int, rows: Iterator[Row]): Ledger = {
    var count = 0L
    var content = BigInt(0)
    rows.foreach { row =>
      count = Math.addExact(count, 1L); content = (content + rowHash(row)) % Modulus
    }
    Ledger(index, count, content.toString(16))
  }
  def evaluate(
      index: Int,
      rows: Iterator[Row],
      descriptor: ModelDescription,
      theta: Vector[Double],
      batchSize: Int
  ): PartitionResult = {
    var count = 0L
    var content = BigInt(0)
    var batches = 0
    val loss = new Compensated
    val gradient = theta.map(_ => new Compensated)
    rows.grouped(batchSize).foreach { group =>
      val batch = group.toVector
      batch.foreach { row =>
        count = Math.addExact(count, 1L); content = (content + rowHash(row)) % Modulus
      }
      val value = ModelBridge.evaluate(descriptor, batch, theta)
      loss.add(value.value)
      gradient.zip(value.gradient).foreach { case (sum, g) => sum.add(g) }
      batches += 1
    }
    PartitionResult(
      Ledger(index, count, content.toString(16)),
      Evaluation(loss.result, gradient.map(_.result), count),
      batches
    )
  }
}

/** Own a derived RDD, never unpersist a caller's cached frame. No observation table is collected.
  */
class DataFrameObjective private (
    val description: ModelDescription,
    private val rows: RDD[Row],
    val ledger: Vector[Ledger],
    val batchSize: Int
) extends AutoCloseable {
  private var closed = false
  val rowCount: Long = ledger.map(_.rows).foldLeft(0L)(Math.addExact)
  var evaluationCount = 0
  var lastBatchCount = 0
  def evaluate(theta: Vector[Double]): Evaluation = {
    require(!closed, "Objective has been closed")
    require(theta.size == description.parameters.size, "Parameter vector has the wrong dimension")
    theta.foreach(ModelBridge.finite)
    val descriptor = description
    val bound = batchSize
    val results = rows
      .mapPartitionsWithIndex { (index, iterator) =>
        Iterator(PartitionWork.evaluate(index, iterator, descriptor, theta, bound))
      }
      .collect()
      .toVector
      .sortBy(_.ledger.partition)
    require(
      results.map(_.ledger) == ledger,
      "Observation membership or values changed after materialization"
    )
    val loss = new Compensated
    val gradient = theta.map(_ => new Compensated)
    results.foreach { part =>
      loss.add(part.evaluation.value)
      gradient.zip(part.evaluation.gradient).foreach { case (sum, g) => sum.add(g) }
    }
    evaluationCount += 1
    lastBatchCount = results.map(_.batches).sum
    Evaluation(loss.result, gradient.map(_.result), rowCount)
  }
  override def close(): Unit = if (!closed) { rows.unpersist(blocking = true); closed = true }
}

object DataFrameObjective {
  def prepare(
      frame: DataFrame,
      observationId: String,
      model: String,
      fieldColumns: Map[String, String],
      batchSize: Int = 256
  ): DataFrameObjective = {
    val descriptor = ModelBridge.describe(model)
    require(
      fieldColumns.keySet == descriptor.fields.map(_._1).toSet,
      "Projection keys must exactly match the authoritative prepared model description"
    )
    require(batchSize >= 1 && batchSize <= descriptor.maxRows, "Invalid batch bound")
    require(frame.columns.toSet.size == frame.columns.length, "Duplicate DataFrame column names")
    require(
      Set[DataType](StringType, IntegerType, LongType)
        .contains(frame.schema(observationId).dataType),
      "Use explicit string or integral observation IDs"
    )
    val numeric = Set[DataType](ByteType, ShortType, IntegerType, LongType, FloatType, DoubleType)
    descriptor.fields.foreach { case (field, _) =>
      require(
        numeric.contains(frame.schema(fieldColumns(field)).dataType),
        s"Explicit primitive numeric column required for $field"
      )
    }
    val projected = frame.select(
      (Vector(frame(observationId)) ++
        descriptor.fields.map { case (field, _) => frame(fieldColumns(field)) }): _*
    )
    val owned = projected.rdd.map(row => row.copy())
    require(
      owned.getNumPartitions >= 1 && owned.getNumPartitions <= 64,
      "Adapter permits 1..64 partitions"
    )
    owned.persist(org.apache.spark.storage.StorageLevel.MEMORY_AND_DISK)
    try {
      val ledger = owned
        .mapPartitionsWithIndex((index, data) => Iterator(PartitionWork.inspect(index, data)))
        .collect()
        .toVector
        .sortBy(_.partition)
      require(
        ledger.map(_.partition) == (0 until owned.getNumPartitions).toVector,
        "Incomplete partition ledger"
      )
      require(ledger.map(_.rows).sum > 0, "Empty training frame")
      val duplicates = owned
        .map(row => (PartitionWork.rowIdentity(row), 1L))
        .reduceByKey((a, b) => Math.addExact(a, b))
        .filter(_._2 > 1L)
        .count()
      require(duplicates == 0, "Observation IDs must be globally unique")
      new DataFrameObjective(descriptor, owned, ledger, batchSize)
    } catch {
      case error: Throwable => owned.unpersist(blocking = true); throw error
    }
  }
}

case class Fit(
    parameters: Vector[Double],
    value: Double,
    gradientNorm: Double,
    iterations: Int,
    evaluations: Int,
    converged: Boolean,
    trace: Vector[(Double, Double)]
)

/** Small transparent unconstrained BFGS driver. It is not a global-optimum guarantee. */
object DriverOptimizer {
  private def dot(a: Vector[Double], b: Vector[Double]): Double =
    a.zip(b).map { case (x, y) => x * y }.sum
  private def norm(a: Vector[Double]): Double = a.map(math.abs).max
  def fit(
      evaluate: Vector[Double] => Evaluation,
      initial: Vector[Double],
      maxIterations: Int = 35,
      maxEvaluations: Int = 100,
      tolerance: Double = 1e-7
  ): Fit = {
    require(
      initial.nonEmpty && initial.size <= 64 && maxIterations > 0 && maxIterations <= 100,
      "Bounded nonempty parameter vector and iteration count required"
    )
    require(
      maxEvaluations >= 2 && maxEvaluations <= 500 && tolerance.isFinite && tolerance > 0,
      "Invalid evaluation budget or gradient tolerance"
    )
    var calls = 0
    def checked(theta: Vector[Double]): Evaluation = {
      require(calls < maxEvaluations, "Objective evaluation budget exhausted")
      theta.foreach(ModelBridge.finite)
      val result = evaluate(theta)
      require(
        result.rows > 0 && result.gradient.size == theta.size,
        "Objective response shape mismatch"
      )
      ModelBridge.finite(result.value); result.gradient.foreach(ModelBridge.finite)
      calls += 1
      result
    }
    var theta = initial
    var current = checked(theta)
    val dimension = theta.size
    def identity =
      Array.tabulate(dimension, dimension)((i, j) => if (i == j) 1.0 / current.rows else 0.0)
    var inverse = identity
    val trace = ArrayBuffer((current.value, norm(current.gradient)))
    var iteration = 0
    while (norm(current.gradient) > tolerance && iteration < maxIterations) {
      var direction = Vector.tabulate(dimension)(i => -dot(inverse(i).toVector, current.gradient))
      if (dot(direction, current.gradient) >= 0) {
        inverse = identity; direction = current.gradient.map(-_ / current.rows)
      }
      val slope = dot(current.gradient, direction)
      var step = 1.0
      var candidate = theta.zip(direction).map { case (x, d) => x + step * d }
      var next = checked(candidate)
      while (next.value > current.value + 1e-4 * step * slope && step > 1.0 / 4096) {
        step /= 2
        candidate = theta.zip(direction).map { case (x, d) => x + step * d }
        next = checked(candidate)
      }
      require(next.value <= current.value + 1e-4 * step * slope, "Armijo line search failed")
      val displacement = candidate.zip(theta).map { case (a, b) => a - b }
      val difference = next.gradient.zip(current.gradient).map { case (a, b) => a - b }
      val curvature = dot(displacement, difference)
      if (
        curvature > 1e-12 * math.sqrt(dot(displacement, displacement) * dot(difference, difference))
      ) {
        val hy = Vector.tabulate(dimension)(i => dot(inverse(i).toVector, difference))
        val coefficient = (1 + dot(difference, hy) / curvature) / curvature
        inverse = Array.tabulate(dimension, dimension) { (i, j) =>
          ModelBridge.finite(
            inverse(i)(j) + coefficient * displacement(i) * displacement(j) -
              (displacement(i) * hy(j) + hy(i) * displacement(j)) / curvature
          )
        }
      } else inverse = identity
      theta = candidate; current = next; iteration += 1
      trace += ((current.value, norm(current.gradient)))
    }
    Fit(
      theta,
      current.value,
      norm(current.gradient),
      iteration,
      calls,
      norm(current.gradient) <= tolerance,
      trace.toVector
    )
  }
}
