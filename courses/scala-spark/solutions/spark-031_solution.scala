import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery, Trigger}
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import com.fasterxml.jackson.databind.ObjectMapper

object Main {
  val eventSchema = StructType(
    Seq(
      StructField("id", LongType, true),
      StructField("team", StringType, true),
      StructField("amount", LongType, true)
    )
  )
  def deleteOwned(root: Path): Unit = {
    val paths = Files.walk(root)
    try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally paths.close()
  }

  def publishFile(root: Path, name: String, lines: Seq[String]): Unit = {
    require(name.matches("batch-[0-9]+\\.json"), "Invalid input filename")
    val target = root.resolve("input").resolve(name)
    require(!Files.exists(target), "Input file already exists")
    val pending = Files.createTempFile(root.resolve("staging"), "arrival-", ".tmp")
    try {
      Files.writeString(
        pending,
        lines.mkString("\n") + "\n",
        StandardCharsets.UTF_8,
        StandardOpenOption.TRUNCATE_EXISTING
      )
      Files.move(pending, target, StandardCopyOption.ATOMIC_MOVE)
    } finally Files.deleteIfExists(pending)
  }

  def inputStream(spark: SparkSession, root: Path): DataFrame = {
    spark.readStream
      .schema(eventSchema)
      .option("maxFilesPerTrigger", 1)
      .json(root.resolve("input").toString)
  }

  def teamSummary(frame: DataFrame): DataFrame = {
    frame
      .groupBy("team")
      .agg(
        count(lit(1)).as("row_count"),
        count("amount").as("known_amounts"),
        sum("amount").as("total_amount")
      )
  }

  def runAvailable(summary: DataFrame, checkpoint: Path, table: String): StreamingQuery = {
    val query = summary.writeStream
      .format("memory")
      .queryName(table)
      .outputMode("complete")
      .option("checkpointLocation", checkpoint.toString)
      .trigger(Trigger.AvailableNow())
      .start()
    try {
      require(query.awaitTermination(30000L), "AvailableNow deadline exceeded")
      require(!query.isActive && query.exception.isEmpty, "Query did not terminate cleanly")
      query
    } finally query.stop()
  }

  def inputProgress(query: StreamingQuery): Seq[(Long, Long)] = {
    query.recentProgress.toSeq.map(progress => (progress.batchId, progress.numInputRows))
  }

  def summaryRows(frame: DataFrame): Seq[(String, Long, Long, Long)] = {
    frame
      .orderBy("team")
      .collect()
      .toSeq
      .map(r => (r.getString(0), r.getLong(1), r.getLong(2), r.getLong(3)))
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    var ownedTable: String = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-031")
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
      spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
      ownedRoot =
        Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-031-")
      Files.createDirectory(ownedRoot.resolve("input"));
      Files.createDirectory(ownedRoot.resolve("staging"))
      ownedTable = "ds60_s031_" + UUID.randomUUID().toString.replace("-", "")
      val batches = Seq(
        Seq(
          """{"id":1,"team":"A","amount":10}""",
          """{"id":2,"team":"B","amount":20}""",
          """{"id":3,"team":"A","amount":0}"""
        ),
        Seq(
          """{"id":4,"team":"B","amount":null}""",
          """{"id":5,"team":"C","amount":30}""",
          """{"id":6,"team":"A","amount":5}"""
        ),
        Seq(
          """{"id":7,"team":"C","amount":0}""",
          """{"id":8,"team":"B","amount":15}""",
          """{"id":9,"team":"A","amount":null}"""
        )
      )
      // Exercise 1: Publish complete input files atomically
      batches.zipWithIndex.foreach { case (lines, index) =>
        publishFile(ownedRoot, s"batch-$index.json", lines)
      }
      val inputFiles = Files.list(ownedRoot.resolve("input"))
      try assert(inputFiles.count() == 3L)
      finally inputFiles.close()
      var duplicateRejected = false
      try publishFile(ownedRoot, "batch-0.json", batches.head)
      catch { case _: IllegalArgumentException => duplicateRejected = true }
      assert(duplicateRejected)
      // Exercise 2: Construct an explicit streaming relation without starting it
      val stream = inputStream(spark, ownedRoot)
      assert(
        stream.isStreaming && stream.schema.fields.toSeq.map(f =>
          (f.name, f.dataType.simpleString)
        ) == Seq(("id", "bigint"), ("team", "string"), ("amount", "bigint"))
      )
      assert(spark.streams.active.isEmpty)
      // Exercise 3: Define a cumulative aggregate with separate completeness counts
      val summary = teamSummary(stream)
      assert(
        summary.isStreaming && summary.columns.toSeq == Seq(
          "team",
          "row_count",
          "known_amounts",
          "total_amount"
        )
      )
      // Exercise 4: Run AvailableNow with a deadline and owned cleanup
      val query = runAvailable(summary, ownedRoot.resolve("checkpoint"), ownedTable)
      assert(!query.isActive && spark.streams.active.isEmpty)
      // Exercise 5: Reconcile processed input through progress evidence
      val progress = inputProgress(query)
      val positive = progress.filter(_._2 > 0L)
      assert(progress.map(_._2).sum == 9L && positive.size == 3 && positive.forall(_._2 == 3L))
      assert(progress.map(_._1).distinct.size == progress.size)
      println("input_progress=" + progress)
      // Exercise 6: Compare final streaming output with batch and literal oracles
      val actual = summaryRows(spark.table(ownedTable))
      val batch = spark.read.schema(eventSchema).json(ownedRoot.resolve("input").toString)
      val expected = Seq(("A", 4L, 3L, 15L), ("B", 3L, 2L, 35L), ("C", 2L, 2L, 30L))
      assert(actual == expected && summaryRows(teamSummary(batch)) == expected)
      assert(
        actual.map(_._2).sum == 9L && actual.map(_._3).sum == 7L && actual
          .map(_._4)
          .sum == 80L && spark.streams.active.isEmpty
      )
      println(
        "spark-031: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString
      )
    } finally {
      try {
        require(
          !spark.streams.active.exists(q => q.name == ownedTable),
          "Owned query still active; preserve scratch"
        );
        if (ownedTable != null) spark.catalog.dropTempView(ownedTable);
        if (ownedRoot != null) deleteOwned(ownedRoot)
      } finally { spark.stop() }
    }
  }
}

// Exercise 1: Publish complete input files atomically. Inputs/task: Write each declared file in the owned staging directory, then atomically move it into input under a new batch-N.json name. Reject invalid names or an existing destination. Expected: Three input files, each with 3 completeJSON records;no staging temporary file remains. Reusing batch-0.json is rejected. Verify: Assert the file count and explicit existing-name rejection before starting any query.
// Exercise 2: Construct an explicit streaming relation without starting it. Inputs/task: Read the owned JSON input through readStream with the declared schema and maxFilesPerTrigger 1. Return the streamingDataFrame;do not call an ordinary batch collect on it. Expected: isStreaming istrue, columns areid, team, amount and their types arebigint, string, bigint. No query is started by construction alone. Verify: Assert streaming status and exact type mapping while the active query list remains empty.
// Exercise 3: Define a cumulative aggregate with separate completeness counts. Inputs/task: Group by team and compute row_count, known_amounts and total_amount. Use the same expression for streaming and batch relations without filling unknown amounts. Expected: The streaming result remains streaming and has one state/result row per team. Its eventual literal result isA(4,3,15), B(3,2,35), C(2,2,30). Verify: Assert output columns and streaming status now;verify the exact final tuples after bounded execution.
// Exercise 4: Run AvailableNow with a deadline and owned cleanup. Inputs/task: Start the aggregate in a uniquely named memory sink with complete mode, a fresh checkpoint and AvailableNow. Await at most 30 seconds, require termination and always stop the query in finally. Expected: The query terminates and isActive isfalse. The memory table holds the final finite aggregate;the checkpoint belongs only to this run. Verify: Assert bounded await success, no query exception and inactive state. No sleep or external producer is used.
// Exercise 5: Reconcile processed input through progress evidence. Inputs/task: Return(batch_id, num_input_rows) from retained query progress. Sum input rows and inspect positive-input batches without confusing cumulative sink snapshots with new input. Expected: Three positive-input batches of 3 records and total input 9. Any zero-input progress entry contributes zero to that total. Verify: Assert total 9, three positive batches of 3 and unique recorded batch IDs;print the actual ledger.
// Exercise 6: Compare final streaming output with batch and literal oracles. Inputs/task: Read the final memory table, compare its ordered summary tuples with a batch read of the same nine source records, and compare both with the literalA/B/C oracle. Expected: ExactlyA(4,3,15), B(3,2,35), C(2,2,30), whose record counts sum 9, known counts 7 and amounts 80. Verify: Assert both path comparisons and the independent literal tuple list;confirm no active query remains before cleanup.
