package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.nio.file.{Files, Path}
import java.util.concurrent.TimeUnit
import org.apache.spark.TaskContext
import org.apache.spark.sql.SparkSession

/** Real task/session retention and bounded package-owned artifact cleanup. */
object ResourceChecks {
  private def listenerCount(): Int = {
    val context = TaskContext.get()
    require(
      context.getClass.getName == "org.apache.spark.TaskContextImpl",
      "Exact Spark4 task context required"
    )
    val callbacks = context.getClass.getDeclaredField("onCompleteCallbacks")
    callbacks.setAccessible(true)
    callbacks.get(context).asInstanceOf[java.util.Stack[_]].size()
  }
  private def process(worker: NativeWorker): Process = {
    val field = classOf[NativeWorker].getDeclaredField("process")
    field.setAccessible(true)
    field.get(worker).asInstanceOf[Process]
  }
  def main(args: Array[String]): Unit = {
    require(args.length == 2, "Usage: artifact.json report.json")
    val encoded = Files.readString(Path.of(args(0)))
    val artifact = PreparedArtifact.parse(encoded)
    val spark = SparkSession
      .builder()
      .appName("Native session and artifact retention contracts")
      .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    val inputDirectory = Files.createTempDirectory("tmbad-cache-fixtures-").toRealPath()
    var blockedDirectory: Option[Path] = None
    var secondSession: Option[SparkSession] = None
    try {
      val distributed = ArtifactFiles.prepare(spark.sparkContext, artifact, PythonBridge.getClass)
      val sessions = spark.sparkContext
        .parallelize(Vector(1), 1)
        .mapPartitions { _ =>
          val before = listenerCount()
          val control = new NativeWorker(artifact, distributed.executable, 30)
          try { control.handshake(); control.finish() }
          finally control.close()
          val baseline = listenerCount()
          require(baseline == before + 1, "Default task-owned cleanup hook was not registered")
          val ids = Vector.newBuilder[Long]
          for (_ <- 0 until 32) {
            val worker =
              new NativeWorker(artifact, distributed.executable, 30, registerCompletionHook = false)
            val pid = process(worker).pid()
            ids += pid
            try { worker.handshake(); worker.finish() }
            finally worker.close()
            require(
              !Files.exists(Path.of("/proc", pid.toString)),
              "Completed native child was not reaped"
            )
            require(
              listenerCount() == baseline,
              "Lexically owned sessions retained per-evaluation listeners"
            )
          }
          val deadline = new NativeDeadline(1)
          val first = new NativeWorker(
            artifact,
            distributed.executable,
            30,
            registerCompletionHook = false,
            sharedDeadline = Some(deadline)
          )
          try { first.handshake(); first.finish() }
          finally first.close()
          Thread.sleep(1100)
          var expired = false
          try {
            val second = new NativeWorker(
              artifact,
              distributed.executable,
              30,
              registerCompletionHook = false,
              sharedDeadline = Some(deadline)
            )
            try { second.handshake(); second.finish() }
            finally second.close()
          } catch { case failure: NativeFailure => expired = failure.code == "deadline" }
          require(
            expired && listenerCount() == baseline,
            "Fresh session reset its owned fitting-phase deadline"
          )
          val result = Json.obj();
          result
            .put("before", before)
            .put("after_default_control", baseline)
            .put("after_32_lexical_sessions", listenerCount())
            .put("lexical_retention_sessions", 32)
            .put("default_hook_control_sessions", 1)
            .put("shared_deadline_expiry", true)
            .put("children_reaped", true)
          val pids = result.putArray("pids"); ids.result().foreach(pids.add)
          Iterator(Json.write(result))
        }
        .collect()
      require(sessions.length == 1)
      for (index <- 0 until 15) {
        // Metadata-only cache fixtures are never executed or called native acceptance.
        val path = inputDirectory.resolve("fake-" + index)
        Files.writeString(path, "metadata-only fake worker " + index)
        val document = Json.read(encoded).deepCopy[ObjectNode]()
        document
          .get("binary")
          .asInstanceOf[ObjectNode]
          .put("path", path.toString)
          .put("sha256", Json.fileHash(path))
        ArtifactFiles.prepare(
          spark.sparkContext,
          PreparedArtifact.parse(Json.write(document)),
          PythonBridge.getClass
        )
      }
      val copies = ArtifactFiles.retainedCopies(spark.sparkContext)
      require(
        copies.size == 16 && copies.forall(Files.exists(_)),
        "Prepared cache coverage differs"
      )
      val extra = inputDirectory.resolve("extra")
      Files.writeString(extra, "one more metadata-only worker")
      val overflow = Json.read(encoded).deepCopy[ObjectNode]()
      overflow
        .get("binary")
        .asInstanceOf[ObjectNode]
        .put("path", extra.toString)
        .put("sha256", Json.fileHash(extra))
      var refused = false
      try
        ArtifactFiles.prepare(
          spark.sparkContext,
          PreparedArtifact.parse(Json.write(overflow)),
          PythonBridge.getClass
        )
      catch {
        case error: IllegalArgumentException => refused = error.getMessage.contains("cache exceeds")
      }
      require(
        refused && ArtifactFiles.retainedCopies(spark.sparkContext).toSet == copies.toSet,
        "Cache overflow evicted or allocated an artifact"
      )
      require(
        Json.boolean(Json.read(PythonBridge.probe(spark, encoded, "normal")), "passed"),
        "Existing artifact stopped working at the cap"
      )
      val context = spark.sparkContext
      val blocked = copies.head
      blockedDirectory = Some(blocked.getParent)
      Files.setPosixFilePermissions(
        blocked.getParent,
        java.nio.file.attribute.PosixFilePermissions.fromString("r-x------")
      )
      val endHook = ArtifactFiles.endListener(context).get
      context.removeSparkListener(endHook)
      spark.stop()
      val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(8)
      while (ArtifactFiles.retainedCopies(context).nonEmpty && System.nanoTime() < deadline)
        Thread.sleep(25)
      require(
        ArtifactFiles.retainedCopies(context).isEmpty && Files.exists(blocked),
        "Failed deletion did not retain its exact owned file for retry"
      )
      val next = SparkSession
        .builder()
        .appName("Pending artifact cleanup refusal")
        .master("local[1]")
        .getOrCreate()
      next.sparkContext.setLogLevel("WARN")
      secondSession = Some(next)
      var cleanupBlocked = false
      try ArtifactFiles.prepare(next.sparkContext, artifact, PythonBridge.getClass)
      catch {
        case error: IllegalArgumentException =>
          cleanupBlocked = error.getMessage.contains("cleanup is pending")
      }
      require(
        cleanupBlocked && ArtifactFiles.retainedCopies(next.sparkContext).isEmpty,
        "Failed cleanup allowed another allocation"
      )
      Files.setPosixFilePermissions(
        blocked.getParent,
        java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")
      )
      val retryDeadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(8)
      while (copies.exists(Files.exists(_)) && System.nanoTime() < retryDeadline) Thread.sleep(25)
      require(
        copies.forall(path => !Files.exists(path)),
        "Missed end callback did not eventually remove its owned copies"
      )
      ArtifactFiles.prepare(next.sparkContext, artifact, PythonBridge.getClass)
      val replacement = ArtifactFiles.retainedCopies(next.sparkContext)
      require(replacement.size == 1)
      next.stop()
      val finalDeadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(8)
      while (replacement.exists(Files.exists(_)) && System.nanoTime() < finalDeadline)
        Thread.sleep(25)
      require(
        replacement.forall(path => !Files.exists(path)),
        "Normal end cleanup did not remove the replacement copy"
      )
      var stoppedRefused = false
      try ArtifactFiles.prepare(context, artifact, PythonBridge.getClass)
      catch {
        case error: IllegalArgumentException =>
          stoppedRefused = error.getMessage.contains("stopped SparkContext")
      }
      require(stoppedRefused && ArtifactFiles.retainedCopies(context).isEmpty)
      val report = Json.obj();
      report
        .put("kind", "spark-tmbad-bounded-resources")
        .put("passed", true)
        .put("cache_entries", 16)
        .put("metadata_only_fixture_entries", 15)
        .put("overflow_refused_without_eviction", true)
        .put("missed_end_callback_cleanup", true)
        .put("stopped_context_refused", true)
        .put("failed_deletion_blocked_allocation_and_retried", true)
      report.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
      report.set[JsonNode]("session_retention", Json.read(sessions.head))
      report.put(
        "scope",
        "real native sessions and task listener counts; cache cap uses small nonexecuted metadata fixtures"
      )
      Files.writeString(Path.of(args(1)), Json.write(report) + "\n")
      println("DS60_TMBAD_RESOURCES_RESULT " + Json.write(report))
    } finally {
      blockedDirectory
        .filter(Files.exists(_))
        .foreach(path =>
          Files.setPosixFilePermissions(
            path,
            java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")
          )
        )
      secondSession.foreach(session => if (!session.sparkContext.isStopped) session.stop())
      if (!spark.sparkContext.isStopped) spark.stop()
      val files = Files.list(inputDirectory)
      try files.forEach(path => Files.deleteIfExists(path))
      finally files.close()
      Files.deleteIfExists(inputDirectory)
    }
  }
}
