package io.ds60.spark.tmbad

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.databind.{JsonNode, ObjectMapper}
import com.fasterxml.jackson.databind.node.{ArrayNode, ObjectNode}
import java.nio.ByteBuffer
import java.nio.charset.{CodingErrorAction, StandardCharsets}
import java.nio.file.{Files, Path, Paths}
import java.security.MessageDigest
import scala.jdk.CollectionConverters._
import scala.util.Using

private[tmbad] object Json {
  val MaxBytes: Int = 4 * 1024 * 1024
  private val parser = new ObjectMapper().enable(JsonParser.Feature.STRICT_DUPLICATE_DETECTION)
  private def scalarLength(text: String): Int = {
    StandardCharsets.UTF_8
      .newEncoder()
      .onMalformedInput(CodingErrorAction.REPORT)
      .onUnmappableCharacter(CodingErrorAction.REPORT)
      .encode(java.nio.CharBuffer.wrap(text))
    text.codePointCount(0, text.length)
  }
  def obj(): ObjectNode = parser.createObjectNode()
  def array(): ArrayNode = parser.createArrayNode()
  def text(node: JsonNode, name: String, maximum: Int = 4096): String = {
    val value = node.get(name)
    require(value != null && value.isTextual, s"Expected string field $name")
    val result = value.textValue()
    require(
      result.nonEmpty && scalarLength(result) <= maximum,
      s"String field $name exceeds its bound"
    )
    result
  }
  def integer(node: JsonNode, name: String, minimum: Long, maximum: Long): Long = {
    val value = node.get(name)
    require(
      value != null && value.isIntegralNumber && value.canConvertToLong,
      s"Expected exact integer field $name"
    )
    val result = value.longValue()
    require(result >= minimum && result <= maximum, s"Integer field $name is outside its bound")
    result
  }
  private def exactIntegral(value: JsonNode): Unit = {
    if (value.isIntegralNumber) {
      val bound = java.math.BigInteger.valueOf(9007199254740991L)
      require(
        value.bigIntegerValue().abs().compareTo(bound) <= 0,
        "Integral JSON values must be exactly supported without float rounding"
      )
    }
  }
  def number(value: JsonNode, label: String): Double = {
    require(value != null && value.isNumber, s"Expected numeric $label")
    exactIntegral(value)
    val result = value.doubleValue()
    require(result.isFinite, s"Nonfinite $label")
    result
  }
  def fieldNumber(node: JsonNode, name: String): Double = number(node.get(name), name)
  def boolean(node: JsonNode, name: String): Boolean = {
    val value = node.get(name)
    require(value != null && value.isBoolean, s"Expected boolean field $name")
    value.booleanValue()
  }
  def fields(node: JsonNode, required: Set[String], optional: Set[String] = Set.empty): Unit = {
    require(node != null && node.isObject, "Expected a JSON object")
    val found = node.fieldNames().asScala.toSet
    require(
      required.subsetOf(found) && found.subsetOf(required ++ optional),
      "JSON fields differ from the supported contract"
    )
  }
  def elements(node: JsonNode, maximum: Int, label: String): Vector[JsonNode] = {
    require(
      node != null && node.isArray && node.size() <= maximum,
      s"Expected bounded $label array"
    )
    node.elements().asScala.toVector
  }
  def strings(
      node: JsonNode,
      maximum: Int,
      label: String,
      allowEmpty: Boolean = true
  ): Vector[String] = {
    val values = elements(node, maximum, label).map { item =>
      require(
        item.isTextual && item.textValue().nonEmpty && scalarLength(item.textValue()) <= 256,
        s"Invalid string in $label"
      )
      item.textValue()
    }
    require(allowEmpty || values.nonEmpty, s"$label cannot be empty")
    require(values.distinct.size == values.size, s"Duplicate names in $label")
    values
  }
  def numbers(node: JsonNode, maximum: Int, label: String): Vector[Double] =
    elements(node, maximum, label).map(item => number(item, label))
  private def validate(node: JsonNode, depth: Int): Unit = {
    require(node != null && depth <= 32, "JSON nesting exceeds its bound")
    if (node.isObject) {
      require(node.size() <= 1024, "JSON object exceeds its field bound")
      node.fields().asScala.foreach { field =>
        require(scalarLength(field.getKey) <= 256, "JSON field name exceeds its bound")
        validate(field.getValue, depth + 1)
      }
    } else if (node.isArray) {
      require(node.size() <= 8192, "JSON array exceeds its element bound")
      node.elements().asScala.foreach(validate(_, depth + 1))
    } else if (node.isNumber) {
      exactIntegral(node)
      require(node.doubleValue().isFinite, "Nonfinite JSON number")
    } else if (node.isTextual) {
      require(scalarLength(node.textValue()) <= 1000000, "JSON string exceeds its bound")
    } else require(node.isBoolean || node.isNull, "Unsupported JSON token")
  }
  def read(bytes: Array[Byte]): JsonNode = {
    require(bytes.nonEmpty && bytes.length <= MaxBytes, "JSON payload exceeds frame bound")
    val decoder = StandardCharsets.UTF_8
      .newDecoder()
      .onMalformedInput(CodingErrorAction.REPORT)
      .onUnmappableCharacter(CodingErrorAction.REPORT)
    val text = decoder.decode(ByteBuffer.wrap(bytes)).toString
    val reader = parser.createParser(text)
    try {
      val value = parser.readTree[JsonNode](reader)
      require(reader.nextToken() == null, "Trailing JSON values are not allowed")
      validate(value, 0)
      value
    } finally reader.close()
  }
  def read(text: String): JsonNode = {
    val encoded = StandardCharsets.UTF_8
      .newEncoder()
      .onMalformedInput(CodingErrorAction.REPORT)
      .onUnmappableCharacter(CodingErrorAction.REPORT)
      .encode(java.nio.CharBuffer.wrap(text))
    val bytes = new Array[Byte](encoded.remaining())
    encoded.get(bytes)
    read(bytes)
  }
  def bytes(node: JsonNode): Array[Byte] = {
    validate(node, 0)
    val result = parser.writeValueAsBytes(node)
    require(result.length <= MaxBytes, "Encoded JSON exceeds frame bound; reduce batch_rows")
    result
  }
  def write(node: JsonNode): String = new String(bytes(node), StandardCharsets.UTF_8)
  def sha(bytes: Array[Byte]): String =
    MessageDigest.getInstance("SHA-256").digest(bytes).map(value => f"${value & 0xff}%02x").mkString
  def hash(value: String): String = {
    require(value.matches("[a-f0-9]{64}"), "Expected lowercase SHA256 identity")
    value
  }
  def fileHash(path: Path, maximum: Long = 256L * 1024 * 1024): String = {
    require(
      path.isAbsolute && Files.isRegularFile(path) && !Files.isSymbolicLink(path),
      "Prepared artifact must be an absolute ordinary file"
    )
    var parent = path.getParent
    while (parent != null) {
      require(!Files.isSymbolicLink(parent), "Prepared artifact ancestry cannot contain links")
      parent = parent.getParent
    }
    require(Files.size(path) <= maximum, "Prepared artifact exceeds its size bound")
    val digest = MessageDigest.getInstance("SHA-256")
    Using.resource(Files.newInputStream(path)) { input =>
      val buffer = new Array[Byte](65536)
      var count = input.read(buffer)
      var total = 0L
      while (count >= 0) {
        total = Math.addExact(total, count.toLong)
        require(total <= maximum, "Prepared artifact grew beyond its size bound")
        if (count > 0) digest.update(buffer, 0, count)
        count = input.read(buffer)
      }
    }
    digest.digest().map(value => f"${value & 0xff}%02x").mkString
  }
  def putStrings(parent: ObjectNode, name: String, values: Seq[String]): Unit = {
    val out = parent.putArray(name); values.foreach(out.add)
  }
  def putNumbers(parent: ObjectNode, name: String, values: Seq[Double]): Unit = {
    val out = parent.putArray(name)
    values.foreach { value =>
      require(value.isFinite, "Nonfinite serialized value"); out.add(value)
    }
  }
}

final case class NativeTarget(
    fields: Vector[String],
    columns: Vector[String],
    needsHistory: Boolean,
    conditioning: String,
    uncertainty: String
) extends Serializable

final case class NativeModel(
    id: String,
    version: String,
    digest: String,
    fitKind: String,
    fitFields: Vector[String],
    parameterNames: Vector[String],
    bounds: Optimizer.Bounds,
    marginalization: String,
    randomDimension: Int,
    ordered: Boolean,
    maxUnitRows: Int,
    derivativeOrders: Vector[Int],
    prediction: Map[String, NativeTarget],
    forecasting: Map[String, NativeTarget],
    json: String
) extends Serializable {
  def validateTheta(theta: Vector[Double]): Unit = {
    require(
      theta.size == parameterNames.size && theta.forall(_.isFinite),
      "Invalid parameter vector"
    )
    require(
      theta.indices.forall(i => theta(i) >= bounds.lower(i) && theta(i) <= bounds.upper(i)),
      "Parameters are outside model-declared bounds"
    )
  }
  def sameDefinition(other: NativeModel): Boolean =
    copy(json = "") == other.copy(json = "")
}

object NativeModel {
  private def targets(node: JsonNode): Map[String, NativeTarget] = {
    require(
      node != null && node.isObject && node.size() <= 64,
      "Expected bounded target definitions"
    )
    node
      .fields()
      .asScala
      .map { field =>
        require(field.getKey.matches("[a-z][a-z0-9_]{0,63}"), "Invalid target identifier")
        val value = field.getValue
        Json.fields(value, Set("fields", "columns", "needs_history", "conditioning", "uncertainty"))
        field.getKey -> NativeTarget(
          Json.strings(value.get("fields"), 256, "target fields"),
          Json.strings(value.get("columns"), 256, "target output columns", allowEmpty = false),
          Json.boolean(value, "needs_history"),
          Json.text(value, "conditioning"),
          Json.text(value, "uncertainty")
        )
      }
      .toMap
  }
  def parse(node: JsonNode): NativeModel = {
    Json.fields(
      node,
      Set(
        "id",
        "version",
        "digest",
        "fit_kind",
        "fit_fields",
        "parameter_names",
        "parameter_bounds",
        "marginalization",
        "random_dimension",
        "ordered",
        "max_unit_rows",
        "derivative_orders",
        "predict",
        "forecast"
      )
    )
    val id = Json.text(node, "id", 64)
    require(id.matches("[a-z][a-z0-9_]{0,63}"), "Invalid model identifier")
    val kind = Json.text(node, "fit_kind", 16)
    require(Set("rows", "unit")(kind), "Unsupported likelihood factorization")
    val parameters =
      Json.strings(node.get("parameter_names"), 64, "parameter names", allowEmpty = false)
    val rawBounds = Json.elements(node.get("parameter_bounds"), 64, "parameter bounds")
    require(rawBounds.size == parameters.size, "Parameter bounds and names differ")
    val limits = rawBounds.map { pair =>
      val values = Json.elements(pair, 2, "bound pair")
      require(values.size == 2, "Each parameter needs a lower/upper bound")
      val lower =
        if (values.head.isNull) Double.NegativeInfinity else Json.number(values.head, "lower bound")
      val upper =
        if (values.last.isNull) Double.PositiveInfinity else Json.number(values.last, "upper bound")
      lower -> upper
    }
    val marginalization = Json.text(node, "marginalization", 32)
    require(Set("none", "exact", "laplace")(marginalization), "Unknown marginalization declaration")
    val orders = Json.elements(node.get("derivative_orders"), 2, "derivative orders").map { value =>
      require(
        value.isIntegralNumber && value.canConvertToInt && Set(1, 2)(value.intValue()),
        "Unsupported derivative order"
      )
      value.intValue()
    }
    require(
      orders.contains(1) && orders.distinct == orders,
      "First derivatives and unique orders required"
    )
    NativeModel(
      id,
      Json.text(node, "version", 32),
      Json.hash(Json.text(node, "digest", 64)),
      kind,
      Json.strings(node.get("fit_fields"), 256, "fit fields", allowEmpty = false),
      parameters,
      Optimizer.Bounds(limits.map(_._1), limits.map(_._2)),
      marginalization,
      Json.integer(node, "random_dimension", 0, 8).toInt,
      Json.boolean(node, "ordered"),
      Json.integer(node, "max_unit_rows", 1, 256).toInt,
      orders,
      targets(node.get("predict")),
      targets(node.get("forecast")),
      Json.write(node)
    )
  }
}

final case class PreparedArtifact(
    buildId: String,
    binaryPath: String,
    binarySha256: String,
    architecture: String,
    engineJson: String,
    models: Map[String, NativeModel],
    jvmPath: Option[String],
    jvmSha256: Option[String],
    identityJson: String,
    packageVersion: String = "0.1.0"
) extends Serializable {
  def model(id: String): NativeModel =
    models.getOrElse(
      id,
      throw new IllegalArgumentException("Model is absent from prepared registry")
    )
  def verifyBinary(path: Path): Unit =
    require(Json.fileHash(path) == binarySha256, "Prepared native binary digest differs")
  def requireExecutorPlatform(): Unit = {
    val aliases =
      Map("aarch64" -> "arm64", "arm64" -> "arm64", "x86_64" -> "amd64", "amd64" -> "amd64")
    require(
      System.getProperty("os.name").toLowerCase(java.util.Locale.ROOT).startsWith("linux") &&
        aliases
          .get(System.getProperty("os.arch").toLowerCase(java.util.Locale.ROOT))
          .contains(architecture),
      "Native executor OS/architecture differs from prepared artifact; emulation is not supported"
    )
  }
  def requireLoadedJvm(adapterClass: Class[_]): Unit = {
    require(jvmSha256.nonEmpty, "Spark execution requires prepared JVM identity")
    val source = Option(adapterClass.getProtectionDomain)
      .flatMap(x => Option(x.getCodeSource))
      .map(_.getLocation.toURI)
      .getOrElse(throw new IllegalArgumentException("Loaded JVM adapter has no code source"))
    require(source.getScheme == "file", "Loaded JVM adapter must come from a prepared local JAR")
    val loaded = Paths.get(source).toRealPath()
    require(
      Files.isRegularFile(loaded) && loaded.getFileName.toString.endsWith(".jar"),
      "Directory-loaded development classes are not prepared-JAR acceptance"
    )
    require(Json.fileHash(loaded) == jvmSha256.get, "Actually loaded JVM adapter digest differs")
  }
  def requireJvm(adapterClass: Class[_]): Unit = {
    require(
      jvmPath.nonEmpty && jvmSha256.nonEmpty,
      "Spark execution requires prepared JVM identity"
    )
    require(
      Json.fileHash(Paths.get(jvmPath.get)) == jvmSha256.get,
      "Prepared JVM JAR digest differs"
    )
    requireLoadedJvm(adapterClass)
  }
}

object PreparedArtifact {
  def parse(text: String): PreparedArtifact = {
    val node = Json.read(text)
    Json.fields(
      node,
      Set(
        "schema_version",
        "kind",
        "package_version",
        "protocol",
        "build_id",
        "platform",
        "binary",
        "engine",
        "models"
      ),
      Set("jvm", "provenance")
    )
    require(
      Json.integer(node, "schema_version", 1, 1) == 1 && Json.integer(node, "protocol", 1, 1) == 1,
      "Unsupported artifact protocol"
    )
    require(
      Json.text(node, "kind") == "spark-tmbad-artifact" &&
        Set("0.1.0", "0.2.0")(Json.text(node, "package_version")),
      "Unsupported artifact kind/version"
    )
    val platform = node.get("platform")
    Json.fields(platform, Set("os", "arch"))
    val architecture = Json.text(platform, "arch", 16)
    require(
      Json.text(platform, "os") == "linux" && Set("amd64", "arm64")(architecture),
      "Unsupported native platform"
    )
    val binary = node.get("binary")
    Json.fields(binary, Set("path", "sha256"))
    val path = Json.text(binary, "path")
    require(Paths.get(path).isAbsolute, "Prepared binary path must be absolute")
    val engine = node.get("engine")
    Json.fields(engine, Set("name", "version", "source_sha256"))
    require(Json.text(engine, "name") == "TMBad", "Unexpected native engine")
    require(Json.text(engine, "version", 64) == "1.9.25", "Unsupported prepared TMBad engine version")
    Json.hash(Json.text(engine, "source_sha256", 64))
    val parsed = Json.elements(node.get("models"), 128, "prepared models").map(NativeModel.parse)
    require(
      parsed.nonEmpty && parsed.map(_.id).distinct.size == parsed.size,
      "Prepared model IDs are empty or duplicated"
    )
    var jvmPath: Option[String] = None
    var jvmHash: Option[String] = None
    if (node.has("jvm")) {
      val jvm = node.get("jvm")
      Json.fields(jvm, Set("path", "sha256", "spark_version", "scala_binary_version", "java_min"))
      require(
        Json.text(jvm, "spark_version") == "4.0.1" && Json
          .text(jvm, "scala_binary_version") == "2.13" &&
          Json.integer(jvm, "java_min", 17, 17) == 17,
        "Unsupported prepared Spark/JVM contract"
      )
      jvmPath = Some(Json.text(jvm, "path"));
      require(Paths.get(jvmPath.get).isAbsolute, "JVM JAR path must be absolute")
      jvmHash = Some(Json.hash(Json.text(jvm, "sha256", 64)))
    }
    val buildId = Json.hash(Json.text(node, "build_id", 64))
    val binaryHash = Json.hash(Json.text(binary, "sha256", 64))
    val identity = Json.obj()
    identity.put("build_id", buildId).put("binary_sha256", binaryHash)
    identity.set[JsonNode]("platform", platform.deepCopy[JsonNode]())
    identity.set[JsonNode]("engine", engine.deepCopy[JsonNode]())
    jvmHash.fold(identity.putNull("jvm_sha256"))(identity.put("jvm_sha256", _))
    PreparedArtifact(
      buildId,
      path,
      binaryHash,
      architecture,
      Json.write(engine),
      parsed.map(x => x.id -> x).toMap,
      jvmPath,
      jvmHash,
      Json.write(identity),
      Json.text(node, "package_version")
    )
  }
}
