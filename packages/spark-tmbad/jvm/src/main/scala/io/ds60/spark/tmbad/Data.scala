package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import org.apache.spark.Partitioner
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Row}
import org.apache.spark.sql.functions.col
import org.apache.spark.sql.types._
import org.apache.spark.storage.StorageLevel
import scala.jdk.CollectionConverters._

/** Conservative name admission follows Spark's case-insensitive resolver, including Unicode. */
private[tmbad] object ColumnNames {
  def equivalent(left: String, right: String): Boolean = left.equalsIgnoreCase(right)
  def unique(names: Seq[String]): Boolean = {
    val seen = new java.util.TreeSet[String](String.CASE_INSENSITIVE_ORDER)
    names.forall(seen.add)
  }
}

final case class FitSpecification(
    modelId: String,
    columns: Map[String, String],
    idColumns: Vector[String],
    groupColumns: Vector[String],
    orderColumns: Vector[String],
    weightColumn: Option[String],
    json: String
) extends Serializable

object FitSpecification {
  private[tmbad] def mapping(
      node: JsonNode,
      names: Vector[String],
      label: String
  ): Map[String, String] = {
    Json.fields(node, names.toSet)
    names.map(name => name -> Json.text(node, name, 256)).toMap
  }
  def parse(text: String, model: NativeModel): FitSpecification = {
    val value = Json.read(text)
    Json.fields(
      value,
      Set("model_id", "columns", "id_columns", "group_columns", "order_columns", "weight_column")
    )
    require(
      Json.text(value, "model_id", 64) == model.id,
      "Fit specification selects a different model"
    )
    val ids = Json.strings(value.get("id_columns"), 64, "identity columns", allowEmpty = false)
    val groups = Json.strings(value.get("group_columns"), 64, "group columns")
    val order = Json.strings(value.get("order_columns"), 64, "order columns")
    require(
      model.fitKind != "unit" || groups.nonEmpty,
      "Complete-unit likelihood requires group columns"
    )
    require(!model.ordered || order.nonEmpty, "Ordered likelihood requires explicit order columns")
    val weight = Option(value.get("weight_column"))
      .filterNot(_.isNull)
      .map(_ => Json.text(value, "weight_column", 256))
    FitSpecification(
      model.id,
      mapping(value.get("columns"), model.fitFields, "fit fields"),
      ids,
      groups,
      order,
      weight,
      Json.write(value)
    )
  }
}

final case class FitOptions(
    initial: Vector[Double],
    maxIterations: Int,
    gradientTolerance: Double,
    functionTolerance: Double,
    maxLineSearch: Int,
    reduction: String,
    l2Strength: Double,
    batchRows: Int,
    taskTimeoutSeconds: Int,
    maxPartitions: Int,
    extension: Option[FitTarget.Settings] = None
) extends Serializable {
  def optimizer: Optimizer.Settings = Optimizer.Settings(
    maxIterations = maxIterations,
    maxEvaluations = math.min(10000, 1 + maxIterations * (maxLineSearch + 1)),
    gradientTolerance = gradientTolerance,
    functionTolerance = functionTolerance,
    maximumBacktracks = maxLineSearch
  )
}
object FitOptions {
  def parse(text: String, model: NativeModel): FitOptions = {
    val value = Json.read(text)
    Json.fields(
      value,
      Set("initial_parameters"),
      Set(
        "max_iterations",
        "gradient_tolerance",
        "function_tolerance",
        "max_line_search",
        "reduction",
        "l2_strength",
        "batch_rows",
        "task_timeout_seconds",
        "max_partitions",
        "regularization",
        "fixed_parameters",
        "solver"
      )
    )
    def integer(name: String, default: Int, minimum: Int, maximum: Int): Int =
      if (value.has(name)) Json.integer(value, name, minimum, maximum).toInt else default
    def number(name: String, default: Double): Double =
      if (value.has(name)) Json.fieldNumber(value, name) else default
    val initial = Json.numbers(value.get("initial_parameters"), 64, "initial parameters")
    model.validateTheta(initial)
    val reduction = if (value.has("reduction")) Json.text(value, "reduction", 32) else "sum"
    require(Set("sum", "weighted_mean")(reduction), "Unknown likelihood reduction")
    val gradient = number("gradient_tolerance", 1e-6)
    val function = number("function_tolerance", 1e-12)
    val penalty = number("l2_strength", 0.0)
    require(gradient > 0 && function >= 0 && penalty >= 0, "Invalid optimizer tolerance or penalty")
    val base = FitOptions(
      initial,
      integer("max_iterations", 100, 1, 1000),
      gradient,
      function,
      integer("max_line_search", 25, 1, 100),
      reduction,
      penalty,
      integer("batch_rows", 1024, 1, 8192),
      integer("task_timeout_seconds", 120, 1, 3600),
      integer("max_partitions", 4096, 1, 4096)
    )
    if (Vector("regularization", "fixed_parameters", "solver").exists(value.has))
      base.copy(extension = Some(FitTarget.resolve(value, model, base)))
    else base
  }
}

/** Lossless keys are separate from the native floating-point numerical matrix. */
private[tmbad] final case class KeyAtom(kind: String, value: String) extends Serializable {
  require(Set("string", "boolean", "byte", "short", "integer", "long")(kind), "Unknown key type")
  require(value != null && value.codePointCount(0, value.length) <= 4096, "Key exceeds its bound")
  kind match {
    case "boolean" => require(Set("true", "false")(value), "Invalid boolean key")
    case "byte"    => require(value.toByte.toString == value, "Noncanonical byte key")
    case "short"   => require(value.toShort.toString == value, "Noncanonical short key")
    case "integer" => require(value.toInt.toString == value, "Noncanonical integer key")
    case "long"    => require(value.toLong.toString == value, "Noncanonical long key")
    case _         => ()
  }
  def sparkValue: Any = kind match {
    case "string"  => value
    case "boolean" => value == "true"
    case "byte"    => value.toByte
    case "short"   => value.toShort
    case "integer" => value.toInt
    case "long"    => value.toLong
    case _         => throw new IllegalArgumentException("Unknown key type")
  }
}
private[tmbad] object KeyAtom {
  def kind(dataType: DataType): String = dataType match {
    case StringType  => "string"
    case BooleanType => "boolean"
    case ByteType    => "byte"
    case ShortType   => "short"
    case IntegerType => "integer"
    case LongType    => "long"
    case _           =>
      throw new IllegalArgumentException(
        "Keys must be string, boolean or primitive integral Spark columns"
      )
  }
  def from(value: Any, dataType: DataType): KeyAtom = {
    require(value != null, "Null identity/group/order key")
    val tag = kind(dataType)
    val text = value.toString
    require(text.codePointCount(0, text.length) <= 4096, "Key exceeds its scalar-length bound")
    // Strict UTF-8 validation rejects unpaired surrogate values without changing them.
    val probe = Json.obj(); probe.put("key", text); Json.bytes(probe)
    KeyAtom(tag, text)
  }
  def encode(values: Vector[KeyAtom]): String = {
    val array = Json.array()
    values.foreach { value =>
      val pair = Json.array(); pair.add(value.kind); pair.add(value.value); array.add(pair)
    }
    Json.write(array)
  }
  private def unicodeCompare(left: String, right: String): Int = {
    var a = 0; var b = 0
    while (a < left.length && b < right.length) {
      val x = left.codePointAt(a); val y = right.codePointAt(b)
      if (x != y) return java.lang.Integer.compare(x, y)
      a += Character.charCount(x); b += Character.charCount(y)
    }
    java.lang.Integer.compare(left.length - a, right.length - b)
  }
  def compare(left: Vector[KeyAtom], right: Vector[KeyAtom]): Int = {
    require(left.size == right.size, "Key dimensions differ")
    var index = 0
    while (index < left.size) {
      val a = left(index); val b = right(index)
      require(a.kind == b.kind, "Key types differ")
      val value = a.kind match {
        case "string"  => unicodeCompare(a.value, b.value)
        case "boolean" => java.lang.Boolean.compare(a.value == "true", b.value == "true")
        case _         => java.lang.Long.compare(a.value.toLong, b.value.toLong)
      }
      if (value != 0) return value
      index += 1
    }
    0
  }
}

private[tmbad] final case class NativeRow(
    ids: Vector[KeyAtom],
    groups: Vector[KeyAtom],
    order: Vector[KeyAtom],
    keys: Vector[KeyAtom],
    values: Vector[Double],
    weight: Double
) extends Serializable {
  def groupKey: String = KeyAtom.encode(groups)
  def idKey: String = KeyAtom.encode(ids)
}

/** Conservative retained-key and numeric-buffer budget, independent of native frame bounds. */
private[tmbad] final class RowBudget(val maximum: Long = 8L * 1024 * 1024) {
  require(maximum > 0 && maximum <= 8L * 1024 * 1024, "Invalid row-buffer byte budget")
  private var used = 0L
  def add(row: NativeRow): Unit = {
    val keys = row.ids ++ row.groups ++ row.order ++ row.keys
    val estimate = 256L + 32L * row.values.size + keys.foldLeft(0L)((size, key) =>
      Math.addExact(size, 64L + 6L * key.value.length)
    )
    require(estimate <= maximum - used, "Complete unit/batch exceeds its retained-byte budget")
    used += estimate
  }
  def clear(): Unit = { used = 0L }
}
private[tmbad] trait GroupSortKey extends Serializable { def group: String }
private[tmbad] final case class SortedKey(
    group: String,
    order: Vector[KeyAtom],
    id: Vector[KeyAtom]
) extends GroupSortKey
private[tmbad] object SortedKey {
  implicit val ordering: Ordering[SortedKey] = new Ordering[SortedKey] with Serializable {
    override def compare(a: SortedKey, b: SortedKey): Int = {
      val group = a.group.compareTo(b.group)
      if (group != 0) group
      else {
        val order = KeyAtom.compare(a.order, b.order)
        if (order != 0) order else KeyAtom.compare(a.id, b.id)
      }
    }
  }
}
private[tmbad] final class GroupPartitioner(override val numPartitions: Int) extends Partitioner {
  require(numPartitions >= 1 && numPartitions <= 4096, "Invalid group partition count")
  override def getPartition(key: Any): Int = key match {
    case value: GroupSortKey => Math.floorMod(value.group.hashCode, numPartitions)
    case _ => throw new IllegalArgumentException("Expected a native group sort key")
  }
  override def equals(other: Any): Boolean = other match {
    case value: GroupPartitioner => value.numPartitions == numPartitions
    case _                       => false
  }
  override def hashCode(): Int = numPartitions
}

private[tmbad] final case class Layout(
    names: Vector[String],
    types: Vector[DataType],
    fieldIndices: Vector[Int],
    idIndices: Vector[Int],
    groupIndices: Vector[Int],
    orderIndices: Vector[Int],
    keyIndices: Vector[Int],
    weightIndex: Option[Int]
) extends Serializable {
  private def numeric(row: Row, index: Int): Double = {
    require(!row.isNullAt(index), "Null numeric model input")
    val value = row.get(index) match {
      case number: java.lang.Byte    => number.doubleValue()
      case number: java.lang.Short   => number.doubleValue()
      case number: java.lang.Integer => number.doubleValue()
      case number: java.lang.Long    =>
        require(
          number.longValue() >= -9007199254740991L && number.longValue() <= 9007199254740991L,
          "Integral model input would lose floating-point precision"
        )
        number.doubleValue()
      case number: java.lang.Float  => number.doubleValue()
      case number: java.lang.Double => number.doubleValue()
      case _                        =>
        throw new IllegalArgumentException("Model inputs require primitive numeric Spark types")
    }
    require(value.isFinite, "Nonfinite numerical model input")
    value
  }
  def row(source: Row): NativeRow = {
    def keys(indices: Vector[Int]): Vector[KeyAtom] =
      indices.map(i => KeyAtom.from(source.get(i), types(i)))
    val weight = weightIndex.map(numeric(source, _)).getOrElse(1.0)
    require(weight >= 0, "Negative likelihood weight")
    NativeRow(
      keys(idIndices),
      keys(groupIndices),
      keys(orderIndices),
      keys(keyIndices),
      fieldIndices.map(numeric(source, _)),
      weight
    )
  }
  def keySchema: Vector[StructField] =
    keyIndices.map(i => StructField(names(i), types(i), nullable = false))
}

private[tmbad] final case class Projected(rdd: RDD[NativeRow], layout: Layout)
private[tmbad] object Data {
  def literal(name: String): org.apache.spark.sql.Column = col("`" + name.replace("`", "``") + "`")
  private def numericType(value: DataType): Boolean =
    Set[DataType](ByteType, ShortType, IntegerType, LongType, FloatType, DoubleType)(value)
  def project(
      frame: DataFrame,
      fields: Vector[String],
      mapping: Map[String, String],
      ids: Vector[String],
      groups: Vector[String],
      order: Vector[String],
      weight: Option[String]
  ): Projected = {
    require(!frame.isStreaming, "Use an immutable batch DataFrame snapshot")
    require(
      ids.nonEmpty && ids.size <= 64 && groups.size <= 64 && order.size <= 64,
      "Invalid key dimensions"
    )
    require(
      frame.schema.fieldNames.distinct.length == frame.schema.fields.length,
      "Ambiguous duplicate DataFrame columns"
    )
    require(
      ColumnNames.unique(frame.schema.fieldNames.toVector),
      "Case-ambiguous DataFrame columns are unsupported"
    )
    require(
      mapping.keySet == fields.toSet,
      "Native field mapping differs from declared model fields"
    )
    val keyNames = (ids ++ groups ++ order).distinct
    val names = (keyNames ++ fields.map(mapping) ++ weight.toVector).distinct
    require(
      names.size <= 512 && names.forall(name => frame.schema.fieldNames.contains(name)),
      "Missing or excessive declared columns"
    )
    val types = names.map(name => frame.schema(name).dataType)
    keyNames.foreach(name => KeyAtom.kind(frame.schema(name).dataType))
    (fields.map(mapping) ++ weight.toVector).foreach(name =>
      require(
        numericType(frame.schema(name).dataType),
        "Model fields/weights must have primitive numeric types"
      )
    )
    def indices(values: Vector[String]): Vector[Int] = values.map(names.indexOf)
    val layout = Layout(
      names,
      types,
      indices(fields.map(mapping)),
      indices(ids),
      indices(groups),
      indices(order),
      indices(keyNames),
      weight.map(names.indexOf)
    )
    // This new mapped RDD owns its cache, independently of any caller DataFrame cache.
    val projected = frame.select(names.map(literal): _*).rdd.map(row => layout.row(row))
    Projected(projected, layout)
  }
  def checkUniqueIds(rows: RDD[NativeRow]): Unit = {
    val duplicate = rows
      .map(row => row.idKey -> 1L)
      .reduceByKey((a, b) => math.min(2L, a + b))
      .values
      .filter(_ > 1)
      .map(_ => 1)
      .take(1)
    require(duplicate.isEmpty, "Duplicate observation identity")
  }
  def sortedGroups(rows: RDD[NativeRow], partitions: Int): RDD[NativeRow] = {
    import SortedKey.ordering
    rows
      .map(row => SortedKey(row.groupKey, row.order, row.ids) -> row)
      .repartitionAndSortWithinPartitions(new GroupPartitioner(partitions))
      .values
  }
  def batches(rows: Iterator[NativeRow], maximum: Int): Iterator[Vector[NativeRow]] =
    new Iterator[Vector[NativeRow]] {
      require(maximum >= 1 && maximum <= 8192, "Invalid batch row bound")
      override def hasNext: Boolean = rows.hasNext
      override def next(): Vector[NativeRow] = {
        if (!hasNext) throw new NoSuchElementException("No remaining native batch")
        val budget = new RowBudget
        val output = scala.collection.mutable.ArrayBuffer.empty[NativeRow]
        while (rows.hasNext && output.size < maximum) {
          val row = rows.next(); budget.add(row); output += row
        }
        output.toVector
      }
    }
  def grouped(
      rows: Iterator[NativeRow],
      maximum: Int,
      ordered: Boolean
  ): Iterator[Vector[NativeRow]] =
    new Iterator[Vector[NativeRow]] {
      private val input = rows.buffered
      override def hasNext: Boolean = input.hasNext
      override def next(): Vector[NativeRow] = {
        if (!hasNext) throw new NoSuchElementException("No remaining native unit")
        val key = input.head.groupKey
        val output = scala.collection.mutable.ArrayBuffer.empty[NativeRow]
        val budget = new RowBudget
        while (input.hasNext && input.head.groupKey == key) {
          require(output.size < maximum, "Complete unit exceeds its declared row bound")
          val current = input.next()
          budget.add(current)
          if (ordered && output.nonEmpty)
            require(
              KeyAtom.compare(output.last.order, current.order) < 0,
              "Ordered unit has duplicate or nonincreasing order keys"
            )
          output += current
        }
        output.toVector
      }
    }
  def ownedCache(rows: RDD[NativeRow]): RDD[NativeRow] = rows.persist(StorageLevel.MEMORY_AND_DISK)
}
