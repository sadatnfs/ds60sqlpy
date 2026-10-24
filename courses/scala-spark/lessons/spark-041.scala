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

  val compatibilityMapper = new com.fasterxml.jackson.databind.ObjectMapper()
  def runtimeVersions(spark: SparkSession): Map[String, String] = {
    val script =
      "import json,sys,importlib.metadata as m\ntry:\n a=m.version('pyarrow')\nexcept m.PackageNotFoundError:\n a='not-installed'\nprint(json.dumps({'python':sys.version.split()[0],'arrow':a}))"
    val process = new ProcessBuilder("python3", "-c", script).redirectErrorStream(true).start()
    if (!process.waitFor(5L, java.util.concurrent.TimeUnit.SECONDS)) {
      process.destroyForcibly(); throw new IllegalStateException("Version probe deadline")
    }
    val bytes = process.getInputStream.readAllBytes();
    require(bytes.length <= 4096 && process.exitValue() == 0)
    val python = compatibilityMapper.readTree(new String(bytes, StandardCharsets.UTF_8))
    Map(
      "spark" -> spark.version,
      "scala" -> scala.util.Properties.versionNumberString,
      "scala_binary" -> "2.13",
      "java" -> System.getProperty("java.version"),
      "java_major" -> System.getProperty("java.specification.version"),
      "python" -> python.get("python").asText(),
      "arrow" -> python.get("arrow").asText()
    )
  }
  def runKeys(
      spark: SparkSession,
      input: Path,
      checkpoint: Path,
      output: Path,
      keys: Seq[String]
  ): RunReceipt = {
    require(keys == Seq("id") || keys == Seq("id", "cents"))
    val frame = spark.readStream
      .schema(eventSchema)
      .option("maxFilesPerTrigger", 1)
      .json(input.toString)
      .dropDuplicates(keys)
    val query = frame.writeStream
      .format("parquet")
      .outputMode("append")
      .option("checkpointLocation", checkpoint.toString)
      .trigger(Trigger.AvailableNow())
      .start(output.toString)
    ownedQueries += query
    try {
      require(query.awaitTermination(45000L), "Compatibility rehearsal deadline")
      require(query.exception.isEmpty)
      RunReceipt(
        query.id.toString,
        query.runId.toString,
        query.recentProgress.map(_.numInputRows).sum,
        query.recentProgress.map(_.batchId).toSeq
      )
    } finally { if (query.isActive) query.stop() }
  }

  def versionReceipt(spark: SparkSession): Map[String, String] =
    throw new UnsupportedOperationException("Complete versionReceipt")

  def goldenMetrics(frame: DataFrame): Seq[Long] =
    throw new UnsupportedOperationException("Complete goldenMetrics")

  def requireCompatible(oldKeys: Seq[String], newKeys: Seq[String]): Unit =
    throw new UnsupportedOperationException("Complete requireCompatible")

  def candidateRun(spark: SparkSession, root: Path, input: Path): RunReceipt =
    throw new UnsupportedOperationException("Complete candidateRun")

  def rollback(spark: SparkSession, input: Path, checkpoint: Path, output: Path): RunReceipt =
    throw new UnsupportedOperationException("Complete rollback")

  def mayPromote(
      profileQualified: Boolean,
      goldenPassed: Boolean,
      recoveryReviewed: Boolean,
      productPassed: Boolean
  ): Boolean =
    throw new UnsupportedOperationException("Complete mayPromote")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-041")
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
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), "spark-041-")
      val input = ownedRoot.resolve("input");
      val oldCheckpoint = ownedRoot.resolve("baseline-checkpoint");
      val oldOutput = ownedRoot.resolve("baseline-output")
      publishFile(
        ownedRoot,
        input,
        "batch-01.json",
        Seq("""{"id":1,"cents":100}""", """{"id":2,"cents":200}""")
      )
      val golden = spark.createDataFrame(
        spark.sparkContext.parallelize(
          Seq(Row(1L, 100L), Row(1L, 100L), Row(2L, null), Row(3L, 0L))
        ),
        eventSchema
      )
      locally {
        val keys = Seq("id")
        val changed = Seq("id", "cents")
        assert(keys != changed)
      }
      locally {
        val sameInstant = spark
          .sql("SELECT CAST(to_timestamp('2026-10-23T12:00:00-07:00') AS STRING)")
          .first()
          .getString(0)
        assert(sameInstant == "2026-10-23 19:00:00")
      }
      println("spark-041: worked examples passed; six task implementations remain")
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

// Exercise 1: Capture the actual runtime tuple. Inputs/task: Record Spark, Scala binary and patch, JDK major and patch, Python version and optional PyArrow distribution version without installing anything. Expected: Spark 4.0.1, Scala 2.13 family, JDK 17;actual patch strings and explicit not-installed Arrow when absent. Verify: Inspect actual values and reject a claimed target qualification based only on a proposed version string.
// Exercise 2: Run a type, NULL and multiplicity golden suite. Inputs/task: Evaluate the supplied four-row bag plus exact decimal and timezone expressions. Expected: 4 rows,3 known amounts, total 200,3 distinct IDs;decimal 12345678.90;instant 19:00UTC. Verify: Compare exact metrics and rendered values under the UTC baseline.
// Exercise 3: Preserve baseline state and reject incompatible reuse. Inputs/task: Run the baseline ID-only deduplication query, then reject a request to change its state keys to id, cents while retaining that checkpoint. Expected: Baseline output 1:100,2:200;preflight rejects changed keys before starting a new query. Verify: Compare owned-query count before/after the refusal and confirm the old checkpoint/output remain present and unchanged.
// Exercise 4: Run the changed query in a separate candidate namespace. Inputs/task: Add a new occurrence 1:999 and run id, cents deduplication using a new checkpoint/output. Expected: Candidate bag 1:100,1:999,2:200, which fails the baseline one-row-per-ID product gate. Verify: Compare candidate and baseline exact bags and preserve old checkpoint/output.
// Exercise 5: Rehearse rollback to the preserved compatible query. Inputs/task: Resume the original ID-only query with its original checkpoint after the candidate is rejected. Expected: The same baseline query ID resumes;the new occurrence of already-seen ID 1 does not add a row;baseline output stays 1:100,2:200. Verify: Check query identity and exact sink bag without deleting either checkpoint.
// Exercise 6: Gate a proposed runtime change on actual evidence. Inputs/task: Require a qualified target profile, golden-suite pass, compatible recovery design and product acceptance before promotion. Expected: The supplied unqualified target or failed candidate is rejected;all four true permits a proposal in this pure decision model. Verify: Check missing-profile and wrong-product negatives, then record that no second runtime was provisioned.
