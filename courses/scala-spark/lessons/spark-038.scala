import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import org.apache.spark.sql.streaming.{StreamingQuery, Trigger}
import scala.collection.mutable.ArrayBuffer

object Main {
  val eventSchema = StructType(
    Seq(StructField("id", LongType, true), StructField("cents", LongType, true))
  )
  val ownedQueries = ArrayBuffer.empty[StreamingQuery]
  case class RunReceipt(id: String, runId: String, inputRows: Long, batches: Seq[Long])
  def deleteOwned(root: Path): Unit = {
    require(root.getFileName.toString.startsWith("spark-"))
    require(root.getParent == Paths.get(".").toAbsolutePath.normalize())
    val walk = Files.walk(root)
    try
      walk.iterator().asScala.toVector.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally walk.close()
  }
  def publishFile(root: Path, input: Path, name: String, lines: Seq[String]): Unit = {
    require(name.matches("batch-[0-9]{2}\\.json"))
    require(lines.size <= 8 && lines.forall(_.length <= 256))
    Files.createDirectories(input)
    val staged = root.resolve("pending-" + UUID.randomUUID().toString + ".json")
    try {
      Files.writeString(
        staged,
        lines.mkString("\n") + "\n",
        StandardCharsets.UTF_8,
        StandardOpenOption.CREATE_NEW
      )
      Files.move(staged, input.resolve(name), StandardCopyOption.ATOMIC_MOVE)
    } finally Files.deleteIfExists(staged)
  }
  def runParquet(spark: SparkSession, input: Path, checkpoint: Path, output: Path): RunReceipt = {
    val source = spark.readStream
      .schema(eventSchema)
      .option("maxFilesPerTrigger", 1)
      .option("mode", "FAILFAST")
      .json(input.toString)
    val query = source.writeStream
      .format("parquet")
      .outputMode("append")
      .option("checkpointLocation", checkpoint.toString)
      .trigger(Trigger.AvailableNow())
      .start(output.toString)
    ownedQueries += query
    try {
      require(query.awaitTermination(45000L), "Finite query exceeded45-second deadline")
      require(query.exception.isEmpty, "Finite query failed")
      RunReceipt(
        query.id.toString,
        query.runId.toString,
        query.recentProgress.map(_.numInputRows).sum,
        query.recentProgress.map(_.batchId).toSeq
      )
    } finally { if (query.isActive) query.stop() }
  }
  def bag(spark: SparkSession, path: Path): Seq[String] = {
    val frame = spark.read.parquet(path.toString)
    require(
      frame.schema.fields.map(f => (f.name, f.dataType.simpleString)).toSeq == Seq(
        ("id", "bigint"),
        ("cents", "bigint")
      )
    )
    require(frame.count() <= 8L, "Tiny result bound exceeded")
    frame.orderBy("id", "cents").collect().map(r => s"${r.getLong(0)}:${r.getLong(1)}").toSeq
  }

  case class Observation(
      inputRows: Long,
      stateRows: Option[Long],
      stateBytes: Option[Long],
      sinkRows: Option[Long],
      queryId: String,
      runId: String,
      operators: Seq[String]
  )
  def observe(spark: SparkSession, input: Path, checkpoint: Path, output: Path): Observation = {
    val source = spark.readStream
      .schema(eventSchema)
      .option("maxFilesPerTrigger", 1)
      .json(input.toString)
      .dropDuplicates("id")
    val query = source.writeStream
      .format("parquet")
      .outputMode("append")
      .option("checkpointLocation", checkpoint.toString)
      .trigger(Trigger.AvailableNow())
      .start(output.toString)
    ownedQueries += query
    try {
      require(query.awaitTermination(45000L), "Observed query deadline exceeded")
      require(query.exception.isEmpty)
      val progress = query.recentProgress.toSeq
      val state = progress.flatMap(_.stateOperators).lastOption
      Observation(
        progress.map(_.numInputRows).sum,
        state.map(_.numRowsTotal),
        state.map(_.memoryUsedBytes),
        progress.lastOption.map(_.sink.numOutputRows),
        query.id.toString,
        query.runId.toString,
        state.toSeq.map(_.operatorName)
      )
    } finally { if (query.isActive) query.stop() }
  }

  def capture(spark: SparkSession, input: Path, checkpoint: Path, output: Path): Observation =
    throw new UnsupportedOperationException("Complete capture")

  def knownMetric(value: Option[Long]): Option[Long] =
    throw new UnsupportedOperationException("Complete knownMetric")

  def growState(
      spark: SparkSession,
      root: Path,
      input: Path,
      checkpoint: Path,
      output: Path
  ): Observation =
    throw new UnsupportedOperationException("Complete growState")

  def emptyObservation(spark: SparkSession, root: Path): Observation =
    throw new UnsupportedOperationException("Complete emptyObservation")

  def nextCheck(kind: String): String =
    throw new UnsupportedOperationException("Complete nextCheck")

  def sanitize(event: Map[String, String]): Map[String, String] =
    throw new UnsupportedOperationException("Complete sanitize")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-038")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.sql.ansi.enabled", "true")
      .config("spark.sql.session.timeZone", "UTC")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]", "local-only course session")
      spark.sparkContext.setLogLevel("ERROR")
      require(spark.version == "4.0.1", "Prepared Spark4.0.1 required")
      spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), "spark-038-")
      val input = ownedRoot.resolve("input"); val checkpoint = ownedRoot.resolve("checkpoint");
      val output = ownedRoot.resolve("output")
      publishFile(
        ownedRoot,
        input,
        "batch-01.json",
        Seq("""{"id":1,"cents":100}""", """{"id":1,"cents":100}""", """{"id":2,"cents":200}""")
      )
      locally {
        val result = observe(
          spark,
          input,
          ownedRoot.resolve("demo-checkpoint"),
          ownedRoot.resolve("demo-output")
        )
        assert(result.inputRows == 3L && result.stateRows.contains(2L))
        assert(bag(spark, ownedRoot.resolve("demo-output")) == Seq("1:100", "2:200"))
      }
      locally {
        val milliseconds = Seq(100L, 100L, 10000L)
        val ratio = milliseconds.max.toDouble / milliseconds.sorted.apply(1)
        assert(ratio == 100.0)
      }
      println("spark-038: worked examples passed; six task implementations remain")
    } finally {
      try {
        ownedQueries.foreach(q => if (q.isActive) q.stop())
        require(
          !ownedQueries.exists(_.isActive),
          "Do not remove scratch while an owned query is active"
        )
        if (ownedRoot != null) deleteOwned(ownedRoot)
      } finally { spark.stop() }
    }
  }
}

// Exercise 1: Capture actual finite streaming progress. Inputs/task: Run the supplied three-occurrence stream with ID deduplication and return a bounded observation record. Expected: Input count 3, state rows 2 and exact committed bag 1:100,2:200. Verify: Join the progress record with actual readback and inactive-query evidence.
// Exercise 2: Interpret state and sink metrics with units. Inputs/task: Require a state operator and a nonnegative memory-used measurement;preserve unknown or negative sink-row sentinel values as unavailable. Expected: State memory is reported in bytes. A missing or negative sink output count is not converted into zero. Verify: Check the real state record and explicit None/-1 normalization controls.
// Exercise 3: Observe bounded state growth across restart. Inputs/task: Add a new ID 3:300 and restart the same compatible checkpoint. Expected: One new input row, state rows grow 2 to 3, and output gains 3:300. Verify: Compare actual state totals, query identity and exact committed rows.
// Exercise 4: Distinguish empty input from a stuck query. Inputs/task: Run a separate AvailableNow query over an empty owned input directory. Expected: Zero admitted rows and a terminated query;state/sink metrics may be absent. Verify: Assert zero input and termination without fabricating an output Parquet schema.
// Exercise 5: Diagnose three seeded incident records. Inputs/task: For the explicitly synthetic incident fixtures, choose one reversible check for skew, growing state and zero admitted input. Expected: Inspect key/partition distribution;inspect watermark/key-retention policy;inspect source discovery respectively. Verify: Compare the three exact recommendations and state one success observation for each.
// Exercise 6: Sanitize evidence with an allowlist. Inputs/task: Keep only stage_id, task_id, run_ms and input_records from a supplied task-event dictionary containing fake credential fields. Expected: Exact four-field record, with fake token/password absent. Verify: Assert field set and values;do not print the unfiltered input.
