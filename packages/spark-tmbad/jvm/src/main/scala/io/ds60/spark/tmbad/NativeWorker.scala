package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.io.{ByteArrayOutputStream, DataInputStream, DataOutputStream}
import java.nio.file.{Files, Path, StandardOpenOption}
import java.nio.file.attribute.PosixFilePermissions
import java.util.UUID
import java.util.concurrent.{Callable, ExecutionException, Executors, TimeUnit, TimeoutException}
import java.util.concurrent.atomic.{AtomicBoolean, AtomicReference}
import org.apache.spark.TaskContext
import scala.jdk.CollectionConverters._
import scala.util.Using

final class NativeFailure(
    val code: String,
    message: String,
    val verifiedTerminal: Boolean = false,
    val operation: String = ""
) extends RuntimeException(s"Native worker [$code]: $message")

/** One executor-owned fitting-phase budget, shared across its sequential sessions. */
private[tmbad] final class NativeDeadline(seconds: Int) {
  require(seconds >= 1 && seconds <= 3600, "Invalid native fitting-phase deadline")
  private val started = System.nanoTime()
  private val budget = TimeUnit.SECONDS.toNanos(seconds.toLong)
  def check(): Unit = if (System.nanoTime() - started >= budget)
    throw new NativeFailure("deadline", "Owned native fitting phase exceeded its task deadline")
}

/** One serial, bounded process session. Results remain provisional until finish() succeeds. */
private[tmbad] final class NativeWorker(
    artifact: PreparedArtifact,
    preparedBinary: Path,
    timeoutSeconds: Int,
    task: Option[TaskContext] = Option(TaskContext.get()),
    registerCompletionHook: Boolean = true,
    sharedDeadline: Option[NativeDeadline] = None
) extends AutoCloseable {
  require(timeoutSeconds >= 1 && timeoutSeconds <= 3600, "Invalid native task deadline")
  artifact.requireExecutorPlatform()
  sharedDeadline.foreach(_.check())
  private val directory = Files.createTempDirectory("spark-tmbad-worker-").toRealPath()
  Files.setPosixFilePermissions(directory, PosixFilePermissions.fromString("rwx------"))
  private val executable = directory.resolve("worker")
  private val closed = new AtomicBoolean(false)
  private val stderrError = new AtomicReference[String](null)
  private val stderrBytes = new ByteArrayOutputStream()
  private val started = System.nanoTime()
  private var process: Process = null
  private var completed = false
  private val io = Executors.newSingleThreadExecutor((runnable: Runnable) => {
    val thread = new Thread(runnable, "spark-tmbad-frame-io")
    thread.setDaemon(true)
    thread
  })
  private var errorThread: Thread = null
  private var output: DataOutputStream = null
  private var input: DataInputStream = null
  try {
    require(
      Files.isRegularFile(preparedBinary) && !Files.isSymbolicLink(preparedBinary),
      "Prepared worker must be an ordinary file"
    )
    val hash = java.security.MessageDigest.getInstance("SHA-256")
    Using.resources(
      Files.newInputStream(preparedBinary),
      Files.newOutputStream(executable, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)
    ) { (source, target) =>
      val buffer = new Array[Byte](65536)
      var count = source.read(buffer)
      var total = 0L
      while (count >= 0) {
        total = Math.addExact(total, count.toLong)
        require(total <= 256L * 1024 * 1024, "Prepared native binary exceeds its bound")
        if (count > 0) { hash.update(buffer, 0, count); target.write(buffer, 0, count) }
        count = source.read(buffer)
      }
    }
    val copiedHash = hash.digest().map(value => f"${value & 0xff}%02x").mkString
    require(copiedHash == artifact.binarySha256, "Materialized native worker digest differs")
    Files.setPosixFilePermissions(executable, PosixFilePermissions.fromString("r-x------"))
    val builder = new ProcessBuilder(executable.toString, "--stdio")
    val environment = builder.environment()
    environment.clear()
    environment.put("PATH", "/usr/bin:/bin")
    environment.put("LANG", "C.UTF-8")
    environment.put("LC_ALL", "C.UTF-8")
    environment.put("HOME", directory.toString)
    environment.put("TMPDIR", directory.toString)
    environment.put("OMP_NUM_THREADS", "1")
    environment.put("OPENBLAS_NUM_THREADS", "1")
    builder.directory(directory.toFile)
    process = NativeLaunch.start(
      () => builder.start(),
      () => {
        checkLive()
        artifact.verifyBinary(executable)
      }
    )
    output = new DataOutputStream(process.getOutputStream)
    input = new DataInputStream(process.getInputStream)
    errorThread = new Thread(
      () => {
        try {
          val stream = process.getErrorStream
          val buffer = new Array[Byte](4096)
          var count = stream.read(buffer)
          while (count >= 0) {
            if (count > 0) {
              stderrBytes.synchronized {
                if (stderrBytes.size() + count > 65536) {
                  stderrError.compareAndSet(null, "Native stderr exceeded 64KiB")
                  process.destroyForcibly()
                } else stderrBytes.write(buffer, 0, count)
              }
            }
            count = stream.read(buffer)
          }
        } catch {
          case _: java.io.IOException => ()
        }
      },
      "spark-tmbad-stderr"
    )
    errorThread.setDaemon(true)
    errorThread.start()
    if (registerCompletionHook) task.foreach(_.addTaskCompletionListener[Unit](_ => close()))
  } catch {
    case error: Throwable => close(); throw error
  }

  private def checkLive(): Unit = {
    sharedDeadline.foreach(_.check())
    if (Thread.currentThread().isInterrupted || task.exists(_.isInterrupted()))
      throw new InterruptedException("Native task was cancelled")
    if (System.nanoTime() - started >= TimeUnit.SECONDS.toNanos(timeoutSeconds.toLong))
      throw new NativeFailure("deadline", "Native task exceeded its deadline")
    Option(stderrError.get()).foreach(detail => throw new NativeFailure("stderr_limit", detail))
    if (closed.get()) throw new NativeFailure("closed", "Native process session is closed")
  }

  private def waitFor[A](operation: Callable[A]): A = {
    checkLive()
    val future = io.submit(operation)
    var result: Option[A] = None
    while (result.isEmpty) {
      checkLive()
      try result = Some(future.get(50, TimeUnit.MILLISECONDS))
      catch {
        case _: TimeoutException       => ()
        case error: ExecutionException =>
          error.getCause match {
            case original: Exception => throw original
            case _ => throw new NativeFailure("transport", "Native transport failed")
          }
      }
    }
    result.get
  }

  def exchange(request: ObjectNode): JsonNode = synchronized {
    require(!completed, "Native protocol is already completed")
    val encoded = Json.bytes(request)
    val expectedHash = Json.sha(encoded)
    val identifier = Json.text(request, "request_id", 128)
    require(
      identifier.forall(character => character >= 32 && character <= 126),
      "Request ID must be ASCII"
    )
    try {
      val result = waitFor(new Callable[JsonNode] {
        override def call(): JsonNode = {
          output.writeInt(encoded.length)
          output.write(encoded)
          output.flush()
          val size = input.readInt().toLong & 0xffffffffL
          require(size > 0 && size <= Json.MaxBytes, "Native frame exceeds its bound")
          val bytes = new Array[Byte](size.toInt)
          input.readFully(bytes)
          Json.read(bytes)
        }
      })
      require(
        result.isObject && Json.integer(result, "protocol", 1, 1) == 1,
        "Unsupported native response protocol"
      )
      require(
        Json.text(result, "request_id", 128) == identifier &&
          Json.text(result, "request_sha256", 64) == expectedHash,
        "Native response request binding differs"
      )
      require(
        Json.text(result, "build_id", 64) == artifact.buildId,
        "Native build identity differs"
      )
      if (request.has("model_id")) {
        require(
          Json.text(result, "model_id", 64) == Json.text(request, "model_id", 64) &&
            Json.text(result, "model_digest", 64) == Json.text(request, "model_digest", 64),
          "Native model identity differs"
        )
      }
      val status = Json.text(result, "status", 16)
      if (status == "error") {
        val base = Set("protocol", "request_id", "request_sha256", "status", "build_id", "error")
        Json.fields(
          result,
          base ++ (if (request.has("model_id")) Set("model_id", "model_digest")
                   else Set.empty[String])
        )
        val error = result.get("error")
        Json.fields(error, Set("code", "message"))
        val code = Json.text(error, "code", 64)
        require(code.matches("[A-Za-z0-9_-]+"), "Invalid native error code")
        val message = Json.text(error, "message", 1024)
        // A framed scientific error is classifiable only after the exact terminal
        // error exit and EOF. Resource/transport/identity failures remain fatal.
        while (!process.waitFor(50, TimeUnit.MILLISECONDS)) checkLive()
        checkLive()
        if (process.exitValue() != 2)
          throw new NativeFailure(
            "nonzero_exit",
            "Native error response had an unexpected terminal exit"
          )
        require(
          waitFor(new Callable[Int] { override def call(): Int = input.read() }) == -1,
          "Native error response has unsolicited trailing output"
        )
        errorThread.join(1000)
        require(!errorThread.isAlive, "Native error stderr drain did not finish")
        Option(stderrError.get()).foreach(detail => throw new NativeFailure("stderr_limit", detail))
        throw new NativeFailure(
          code,
          message,
          verifiedTerminal = true,
          operation = Json.text(request, "op", 32)
        )
      }
      require(status == "ok", "Unknown native response status")
      if (!process.isAlive && process.exitValue() != 0)
        throw new NativeFailure(
          "nonzero_exit",
          s"Worker exited ${process.exitValue()} after output"
        )
      result
    } catch {
      case error: Throwable => close(); throw error
    }
  }

  def handshake(): Unit = {
    val request = NativeWorker.request("describe")
    val result = exchange(request)
    Json.fields(
      result,
      Set("protocol", "request_id", "status", "request_sha256", "build_id", "engine", "models")
    )
    require(
      result.get("engine") == Json.read(artifact.engineJson),
      "Native engine/source identity differs"
    )
    val models = Json.elements(result.get("models"), 128, "native models").map(NativeModel.parse)
    require(
      models.map(_.id).distinct.size == models.size && models
        .map(_.id)
        .toSet == artifact.models.keySet,
      "Native registry model set differs"
    )
    require(
      models.forall(model => model.sameDefinition(artifact.model(model.id))),
      "Native model descriptors differ"
    )
  }

  /** All earlier responses are provisional until EOF and successful exit are observed. */
  def finish(): Unit = synchronized {
    if (!completed) {
      try {
        waitFor(new Callable[Boolean] {
          override def call(): Boolean = { output.close(); true }
        })
        while (!process.waitFor(50, TimeUnit.MILLISECONDS)) checkLive()
        checkLive()
        require(
          process.exitValue() == 0,
          s"Native worker exited ${process.exitValue()} after valid output"
        )
        val trailing = waitFor(new Callable[Int] { override def call(): Int = input.read() })
        require(trailing == -1, "Native worker produced unsolicited trailing output")
        errorThread.join(1000)
        require(!errorThread.isAlive, "Native stderr drain did not finish")
        Option(stderrError.get()).foreach(detail => throw new NativeFailure("stderr_limit", detail))
        completed = true
      } finally close()
    }
  }

  override def close(): Unit = {
    if (closed.compareAndSet(false, true)) {
      if (process != null) {
        try Using.resource(process.descendants())(_.iterator().asScala.foreach(_.destroyForcibly()))
        catch { case _: RuntimeException => () }
        if (process.isAlive) process.destroyForcibly()
        try process.waitFor(5, TimeUnit.SECONDS)
        catch { case _: InterruptedException => Thread.currentThread().interrupt() }
        Seq(process.getOutputStream, process.getInputStream, process.getErrorStream).foreach {
          stream =>
            try stream.close()
            catch { case _: java.io.IOException => () }
        }
      }
      io.shutdownNow()
      if (errorThread != null && errorThread != Thread.currentThread()) {
        try errorThread.join(1000)
        catch { case _: InterruptedException => Thread.currentThread().interrupt() }
      }
      try Files.deleteIfExists(executable)
      catch { case _: java.io.IOException => () }
      try Files.deleteIfExists(directory)
      catch { case _: java.io.IOException => () }
    }
  }
}

/** Retry only an observed Linux executable-busy launch failure, never protocol/model work. */
private[tmbad] object NativeLaunch {
  def start(
      launch: () => Process,
      beforeAttempt: () => Unit,
      pause: Long => Unit = milliseconds => Thread.sleep(milliseconds)
  ): Process = {
    var attempts = 0
    var process: Process = null
    while (process == null) {
      beforeAttempt()
      try process = launch()
      catch {
        case error: java.io.IOException
            if attempts < 5 &&
              Option(error.getCause)
                .exists(cause => Option(cause.getMessage).exists(_.startsWith("error=26,"))) =>
          attempts += 1
          pause(10L * attempts)
      }
    }
    process
  }
}

private[tmbad] object NativeWorker {
  def request(operation: String): ObjectNode = {
    val value = Json.obj()
    value.put("protocol", 1).put("request_id", UUID.randomUUID().toString).put("op", operation)
    value
  }
  def modelRequest(operation: String, model: NativeModel, theta: Vector[Double]): ObjectNode = {
    model.validateTheta(theta)
    val value = request(operation)
    value.put("model_id", model.id).put("model_digest", model.digest)
    Json.putNumbers(value, "theta", theta)
    value
  }
}
