import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery,StreamingQueryProgress,Trigger}
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.time.Instant
import scala.jdk.CollectionConverters._

object Main {
  val eventSchema = StructType(Seq(StructField("id",LongType,true),StructField("team",StringType,true),StructField("amount",LongType,true),StructField("event_time",TimestampType,true)))
  val resultSchema = StructType(Seq(StructField("window",StructType(Seq(StructField("start",TimestampType,true),StructField("end",TimestampType,true))),true),StructField("team",StringType,true),StructField("records",LongType,true),StructField("total",LongType,true)))
  def publish(root: Path, index: Int, lines: Seq[String]): Unit = {
    val target = root.resolve("input").resolve(s"batch-$index.json")
    require(!Files.exists(target),"Input filename already published")
    val staged = Files.createTempFile(root.resolve("staging"),"arrival-",".tmp")
    try { Files.writeString(staged,lines.mkString("\n")+"\n",StandardCharsets.UTF_8,StandardOpenOption.TRUNCATE_EXISTING);Files.move(staged,target,StandardCopyOption.ATOMIC_MOVE) }
    finally Files.deleteIfExists(staged)
  }
  def stream(spark: SparkSession, root: Path): DataFrame = spark.readStream.schema(eventSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(root.resolve("input").toString)
  def runPhase(spark: SparkSession, root: Path): Seq[StreamingQueryProgress] = {
    val query = windowed(stream(spark,root)).writeStream.format("parquet").outputMode("append").option("checkpointLocation",root.resolve("checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve("output").toString)
    try { require(query.awaitTermination(30000L),"Finite phase timed out");require(query.exception.isEmpty && !query.isActive,"Phase did not terminate cleanly");query.recentProgress.toSeq }
    finally query.stop()
  }
  def deleteOwned(root: Path): Unit = { val paths = Files.walk(root);try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p)) finally paths.close() }

  def windowed(events: DataFrame): DataFrame = {
    events.withWatermark("event_time","5 minutes").groupBy(window(col("event_time"),"5 minutes"),col("team")).agg(count(lit(1)).as("records"),sum("amount").as("total"))
  }

  def watermarks(progress: Seq[StreamingQueryProgress]): Seq[String] = {
    progress.flatMap(p => Option(p.eventTime.get("watermark")))
  }

  def finalRows(spark: SparkSession, root: Path): Seq[(String,String,Long,Long)] = {
    spark.read.schema(resultSchema).parquet(root.resolve("output").toString).select(date_format(col("window.start"),"HH:mm").as("start"),col("team"),col("records"),col("total")).orderBy("start","team").collect().toSeq.map(r => (r.getString(0),r.getString(1),r.getLong(2),r.getLong(3)))
  }

  def droppedRows(progress: Seq[StreamingQueryProgress]): Long = {
    require(progress.exists(_.stateOperators.nonEmpty),"No state-operator evidence")
    progress.flatMap(_.stateOperators).map(_.numRowsDroppedByWatermark).sum
  }

  def eventLedger(phases: Seq[Seq[StreamingQueryProgress]], output: Seq[(String,String,Long,Long)]): (Long,Long,Long) = {
    (phases.flatten.map(_.numInputRows).sum,phases.map(droppedRows).sum,output.map(_._3).sum)
  }

  def rejectUnsupported(spark: SparkSession, root: Path, kind: String): Unit = {
    require(Set("update-file","append-unwatermarked").contains(kind),"Unknown invalid case")
    val relation = if(kind == "update-file") windowed(stream(spark,root)) else stream(spark,root).groupBy("team").count()
    val mode = if(kind == "update-file") "update" else "append"
    var query: StreamingQuery = null
    var rejected = false
    try {
     query = relation.writeStream.format("parquet").outputMode(mode).option("checkpointLocation",root.resolve(kind+"-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve(kind+"-output").toString)
     query.awaitTermination(30000L)
    } catch { case _: org.apache.spark.sql.AnalysisException => rejected = true }
    finally { if(query != null) query.stop() }
    require(rejected,"Unsupported output configuration was accepted")
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-032").master("local[2]")
      .config("spark.ui.enabled","false")
      .config("spark.driver.host","127.0.0.1")
      .config("spark.driver.bindAddress","127.0.0.1")
      .config("spark.sql.shuffle.partitions","2")
      .config("spark.sql.adaptive.enabled","false")
      .config("spark.sql.ansi.enabled","true")
      .config("spark.sql.session.timeZone","UTC").getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]", "local-only course session")
      spark.sparkContext.setLogLevel("ERROR")
      spark.conf.set("spark.sql.streaming.stopTimeout","10000")
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-032-")
      Files.createDirectory(ownedRoot.resolve("input"));Files.createDirectory(ownedRoot.resolve("staging"))
      val batches = Seq(
       Seq("""{"id":1,"team":"A","amount":10,"event_time":"2024-01-01T00:01:00Z"}""","""{"id":2,"team":"A","amount":20,"event_time":"2024-01-01T00:04:00Z"}"""),
       Seq("""{"id":3,"team":"A","amount":5,"event_time":"2024-01-01T00:03:00Z"}""","""{"id":4,"team":"A","amount":30,"event_time":"2024-01-01T00:12:00Z"}"""),
       Seq("""{"id":5,"team":"A","amount":999,"event_time":"2024-01-01T00:02:00Z"}""","""{"id":6,"team":"B","amount":7,"event_time":"2024-01-01T00:13:00Z"}"""),
       Seq("""{"id":7,"team":"__advance__","amount":0,"event_time":"2024-01-01T00:30:00Z"}"""))
      // Exercise 1: Define watermark placement and window state
      publish(ownedRoot,0,batches(0))
      val planned = windowed(stream(spark,ownedRoot))
      assert(planned.isStreaming && planned.columns.toSeq == Seq("window","team","records","total"))
      // Exercise 2: Record actual watermark progress after the first phase
      val phase1 = runPhase(spark,ownedRoot)
      assert(phase1.map(_.numInputRows).sum == 2L)
      val marks1 = watermarks(phase1)
      assert(marks1.nonEmpty && !Instant.parse(marks1.last).isAfter(Instant.parse("2024-01-01T00:00:00Z")))
      println("phase1_watermarks=" + marks1)
      // Exercise 3: Accept a retained out-of-order event and observe finalization
      publish(ownedRoot,1,batches(1))
      val phase2 = runPhase(spark,ownedRoot)
      assert(finalRows(spark,ownedRoot) == Seq(("00:00","A",3L,35L)))
      assert(watermarks(phase2).exists(value => !Instant.parse(value).isBefore(Instant.parse("2024-01-01T00:07:00Z"))))
      // Exercise 4: Observe a far-late drop after the window has closed
      publish(ownedRoot,2,batches(2))
      val phase3 = runPhase(spark,ownedRoot)
      assert(phase3.map(_.numInputRows).sum == 2L && droppedRows(phase3) == 1L)
      assert(finalRows(spark,ownedRoot) == Seq(("00:00","A",3L,35L)))
      println("phase3_dropped_by_watermark=" + droppedRows(phase3))
      // Exercise 5: Advance event time and distinguish finalized frompending output
      publish(ownedRoot,3,batches(3))
      val phase4 = runPhase(spark,ownedRoot)
      val output = finalRows(spark,ownedRoot)
      assert(output == Seq(("00:00","A",3L,35L),("00:10","A",1L,30L),("00:10","B",1L,7L)))
      assert(eventLedger(Seq(phase1,phase2,phase3,phase4),output) == (7L,1L,5L))
      assert(watermarks(phase4).exists(value => !Instant.parse(value).isBefore(Instant.parse("2024-01-01T00:25:00Z"))))
      // Exercise 6: Verify output-mode and sink eligibility through explicit failures
      rejectUnsupported(spark,ownedRoot,"update-file");rejectUnsupported(spark,ownedRoot,"append-unwatermarked")
      assert(spark.streams.active.isEmpty && finalRows(spark,ownedRoot) == output)
      println("spark-032: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { require(spark.streams.active.isEmpty,"Query still active; preserve scratch"); if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Define watermark placement and window state. Inputs/task: Apply with Watermark(event_time,5minutes) before grouping by a 5-minute window and team. Aggregate records and total amount, retaining the window struct in the result. Expected: A streaming aggregate with window, team, records, total. The watermark is attached to the same event-time column used by the window. Verify: Assert streaming status and the four output fields before starting the first phase.
// Exercise 2: Record actual watermark progress after the first phase. Inputs/task: Run phase 1 and extract nonmissing watermark strings from retained progress. Parse them as instants rather than wall-clock elapsed duration. Expected: Exactly 2 input rows processed. At least one watermark observation exists;the final observed watermark is no later than 00:00 for this phase. Verify: Assert input count 2 and actual watermark presence/order;do not infer finalization from the file count alone.
// Exercise 3: Accept a retained out-of-order event and observe finalization. Inputs/task: Publish phase 2, run the compatible query again and read finalized sink rows as(start, team, records, total). Verify the 00:03 event contributed before the first window closed. Expected: The finalized sink contains only(00:00, A,3,35) at this point. The actual watermark reaches at least 00:07. Verify: Assert the exact first-window tuple and the observed progress boundary.
// Exercise 4: Observe a far-late drop after the window has closed. Inputs/task: Publish phase 3 after phase 2 has terminated. Read the actual state-operator dropped-by-watermark counters and verify the 999 event does not change the finalized first window. Expected: Two new source rows consumed, one observed watermark drop and unchanged first-window result 35. B at 00:13 remains in pending state. Verify: Assert input 2, drop counter 1 and the unchanged sink tuple. Preserve missing metric evidence as an error rather than guessing zero.
// Exercise 5: Advance event time and distinguish finalized frompending output. Inputs/task: Publish the 00:30 administrative advancer, run phase 4 and return a ledger of total source inputs, observed drops and final business-window records. Expected: Seven total inputs, one observed drop, five finalized business records across three tuples:(00:00, A,3,35),(00:10, A,1,30),(00:10, B,1,7). The advancer window remains pending. Verify: Assert all final tuples, input/drop reconciliation and actual watermark at least 00:25.
// Exercise 6: Verify output-mode and sink eligibility through explicit failures. Inputs/task: Attempt two invalid configurations in separate owned paths:Update mode to Parquet, and Append mode for an unwatermarked team aggregate. Require analysis rejection and stop any unexpectedly created query in finally. Expected: Both configurations raiseAnalysisException;no active query remains. The valid windowed append sink stays intact. Verify: Assert each named analysis failure and the unchanged three-row valid sink after the checks.
