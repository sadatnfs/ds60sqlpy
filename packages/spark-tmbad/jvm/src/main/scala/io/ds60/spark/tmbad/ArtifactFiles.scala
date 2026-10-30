package io.ds60.spark.tmbad

import java.lang.ref.WeakReference
import java.nio.file.{Files, Path, Paths, StandardOpenOption}
import java.nio.file.attribute.PosixFilePermissions
import java.util.concurrent.{Executors, TimeUnit}
import org.apache.spark.{SparkContext, SparkFiles}
import org.apache.spark.scheduler.{SparkListener, SparkListenerApplicationEnd}
import scala.collection.mutable
import scala.util.Using

private[tmbad] final case class DistributedArtifact(artifact: PreparedArtifact, fileName: String)
    extends Serializable {
  def executable: Path = {
    val path = Paths.get(SparkFiles.get(fileName)).toAbsolutePath
    artifact.verifyBinary(path)
    path
  }
}

/** Explicit accounting is tested with tiny fixtures, never multi-gigabyte allocations. */
private[tmbad] final class ArtifactBudget(
    val maxEntries: Int = 16,
    val maxBytes: Long = 256L * 1024 * 1024
) {
  require(maxEntries > 0 && maxEntries <= 16 && maxBytes > 0 && maxBytes <= 256L * 1024 * 1024)
  private val entries = mutable.Map.empty[String, Long]
  def count: Int = entries.size
  def bytes: Long = entries.values.sum
  def check(key: String, size: Long): Unit = {
    require(size >= 0 && size <= maxBytes, "Prepared artifact exceeds the context byte budget")
    entries.get(key) match {
      case Some(existing) => require(existing == size, "Prepared artifact size changed")
      case None           =>
        require(
          count < maxEntries && size <= maxBytes - bytes,
          s"SparkContext prepared-artifact cache exceeds $maxEntries entries or $maxBytes bytes; use a new context"
        )
    }
  }
  def add(key: String, size: Long): Unit = { check(key, size); entries.update(key, size) }
}

private[tmbad] object ArtifactFiles {
  private final class State(val context: WeakReference[SparkContext], val listener: SparkListener) {
    val copies = mutable.Map.empty[String, Path]
    val budget = new ArtifactBudget
  }
  private val states = mutable.Map.empty[Long, State]
  private val pendingRemoval = mutable.Set.empty[Path]
  private var serial = 0L
  private var maintenanceStarted = false
  private val maintenance = Executors.newSingleThreadScheduledExecutor((runnable: Runnable) => {
    val thread = new Thread(runnable, "spark-tmbad-artifact-cleanup")
    thread.setDaemon(true)
    thread
  })

  private def removeOwned(path: Path): Unit = {
    // Only exact files/directories created by this object are recorded here.
    try {
      Files.deleteIfExists(path); Files.deleteIfExists(path.getParent); pendingRemoval.remove(path)
    } catch { case _: java.io.IOException => pendingRemoval.add(path) }
  }
  private def clean(id: Long): Unit = states.remove(id).foreach { state =>
    Option(state.context.get()).foreach { context =>
      try context.removeSparkListener(state.listener)
      catch { case _: IllegalStateException => () }
    }
    state.copies.values.foreach(removeOwned)
  }
  private def sweep(): Unit = synchronized {
    states.toVector.foreach { case (id, state) =>
      val context = state.context.get()
      if (context == null || context.isStopped) clean(id)
    }
    pendingRemoval.toVector.foreach(removeOwned)
  }
  private def register(context: SparkContext): (Long, State) = {
    sweep()
    require(!context.isStopped, "Cannot prepare artifacts for a stopped SparkContext")
    states.find { case (_, state) => state.context.get() eq context } match {
      case Some(existing) => existing
      case None           =>
        serial = Math.addExact(serial, 1L)
        val id = serial
        val listener = new SparkListener {
          override def onApplicationEnd(event: SparkListenerApplicationEnd): Unit =
            ArtifactFiles.synchronized { clean(id) }
        }
        val state = new State(new WeakReference(context), listener)
        states.update(id, state)
        try {
          // Register cleanup before allocating any artifact directory or copy.
          context.addSparkListener(listener)
          if (!maintenanceStarted) {
            maintenance.scheduleWithFixedDelay(
              new Runnable { override def run(): Unit = sweep() },
              1,
              1,
              TimeUnit.SECONDS
            )
            maintenanceStarted = true
          }
          require(!context.isStopped, "SparkContext stopped while registering artifact cleanup")
          id -> state
        } catch { case error: Throwable => clean(id); throw error }
    }
  }

  /** Package-internal diagnostics for exact-version lifecycle acceptance. */
  private[tmbad] def retainedCopies(context: SparkContext): Vector[Path] = synchronized {
    states.values.filter(state => state.context.get() eq context).flatMap(_.copies.values).toVector
  }
  private[tmbad] def endListener(context: SparkContext): Option[SparkListener] = synchronized {
    states.values.find(state => state.context.get() eq context).map(_.listener)
  }

  def prepare(
      context: SparkContext,
      artifact: PreparedArtifact,
      adapterClass: Class[_]
  ): DistributedArtifact = synchronized {
    require(context.version == "4.0.1", "Use the prepared Spark4.0.1 runtime")
    require(!context.isStopped, "Cannot prepare artifacts for a stopped SparkContext")
    artifact.requireJvm(adapterClass)
    val source = Paths.get(artifact.binaryPath)
    artifact.verifyBinary(source)
    val size = Files.size(source)
    val (id, state) = register(context)
    state.budget.check(artifact.binarySha256, size)
    if (!state.copies.contains(artifact.binarySha256))
      require(
        pendingRemoval.isEmpty,
        "Owned artifact cleanup is pending; restore filesystem access before preparing another artifact"
      )
    val copy = state.copies.getOrElseUpdate(
      artifact.binarySha256, {
        val directory = Files.createTempDirectory("spark-tmbad-distribution-").toRealPath()
        val target = directory.resolve("tmbad-worker-" + artifact.binarySha256)
        try {
          Files.setPosixFilePermissions(directory, PosixFilePermissions.fromString("rwx------"))
          Using.resources(
            Files.newInputStream(source),
            Files.newOutputStream(target, StandardOpenOption.CREATE_NEW)
          ) { (input, output) =>
            val buffer = new Array[Byte](65536)
            var copied = 0L
            var count = input.read(buffer)
            while (count >= 0) {
              copied = Math.addExact(copied, count.toLong)
              require(copied <= size, "Prepared artifact grew during bounded materialization")
              if (count > 0) output.write(buffer, 0, count)
              count = input.read(buffer)
            }
            require(copied == size, "Prepared artifact size changed during materialization")
          }
          artifact.verifyBinary(target)
          Files.setPosixFilePermissions(target, PosixFilePermissions.fromString("r--------"))
          require(!context.isStopped, "SparkContext stopped while copying its artifact")
          context.addFile(target.toUri.toString)
          require(!context.isStopped, "SparkContext stopped while publishing its artifact")
          state.budget.add(artifact.binarySha256, size)
          target
        } catch {
          case error: Throwable =>
            removeOwned(target)
            if (context.isStopped) clean(id)
            throw error
        }
      }
    )
    if (context.isStopped) {
      clean(id); throw new IllegalStateException("SparkContext stopped during artifact preparation")
    }
    artifact.verifyBinary(copy)
    DistributedArtifact(artifact, copy.getFileName.toString)
  }
}
