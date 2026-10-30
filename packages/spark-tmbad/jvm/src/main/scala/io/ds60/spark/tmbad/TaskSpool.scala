package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import java.io.{DataInputStream, DataOutputStream}
import java.nio.file.{Files, Path}
import java.nio.file.attribute.PosixFilePermissions
import java.util.concurrent.atomic.AtomicBoolean
import org.apache.spark.TaskContext
import org.apache.spark.sql.Row

/** Bounded private task output. Numerical rows are exposed only after child exit0. */
private[tmbad] final class TaskSpool extends AutoCloseable {
  private val path: Path = Files.createTempFile("spark-tmbad-output-", ".frames").toRealPath()
  Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rw-------"))
  private val closed = new AtomicBoolean(false)
  private var writer: DataOutputStream = new DataOutputStream(Files.newOutputStream(path))
  private var reader: DataInputStream = null
  private var total = 0L
  private var records = 0L
  private var sealedOutput = false
  Option(TaskContext.get()).foreach(_.addTaskCompletionListener[Unit](_ => close()))
  def append(value: JsonNode): Unit = {
    require(!closed.get() && !sealedOutput, "Task output is already sealed")
    val bytes = Json.bytes(value)
    total = Math.addExact(total, 4L + bytes.length)
    require(
      total <= 128L * 1024 * 1024,
      "Task output exceeds128MiB; explicitly repartition to smaller outputs"
    )
    writer.writeInt(bytes.length); writer.write(bytes)
    records = Math.addExact(records, 1L)
  }
  def result(decode: JsonNode => Row): Iterator[Row] = {
    require(!closed.get() && !sealedOutput, "Task output cannot be read twice")
    writer.close(); writer = null; sealedOutput = true
    reader = new DataInputStream(Files.newInputStream(path))
    new Iterator[Row] {
      private var remaining = records
      override def hasNext: Boolean = {
        if (remaining == 0) { TaskSpool.this.close(); false }
        else { require(!closed.get(), "Task output was cancelled"); true }
      }
      override def next(): Row = {
        if (!hasNext) throw new NoSuchElementException("No remaining task output")
        val size = reader.readInt()
        require(size > 0 && size <= Json.MaxBytes, "Corrupt task output frame")
        val bytes = new Array[Byte](size); reader.readFully(bytes)
        remaining -= 1
        val result = decode(Json.read(bytes))
        if (remaining == 0) TaskSpool.this.close()
        result
      }
    }
  }
  override def close(): Unit = if (closed.compareAndSet(false, true)) {
    if (writer != null)
      try writer.close()
      catch { case _: java.io.IOException => () }
    if (reader != null)
      try reader.close()
      catch { case _: java.io.IOException => () }
    try Files.deleteIfExists(path)
    catch { case _: java.io.IOException => () }
  }
}

private[tmbad] object OutputRows {
  def keys(values: Vector[KeyAtom]): JsonNode = Json.read(KeyAtom.encode(values))
  def parseKeys(value: JsonNode): Vector[KeyAtom] =
    Json.elements(value, 192, "output keys").map { pair =>
      val values = Json.elements(pair, 2, "output key")
      require(values.size == 2 && values.forall(_.isTextual), "Malformed output identity")
      KeyAtom(values.head.textValue(), values.last.textValue())
    }
  def prediction(keys: Vector[KeyAtom], values: Vector[Double]): JsonNode = {
    val node = Json.obj(); node.set[JsonNode]("keys", OutputRows.keys(keys))
    Json.putNumbers(node, "values", values); node
  }
  def predictionRow(node: JsonNode, keyCount: Int, columns: Int): Row = {
    Json.fields(node, Set("keys", "values"))
    val keys = parseKeys(node.get("keys"));
    val values = Json.numbers(node.get("values"), 256, "output values")
    require(keys.size == keyCount && values.size == columns, "Output schema/cardinality differs")
    Row.fromSeq(keys.map(_.sparkValue) ++ values)
  }
}
