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

  def windowed(events: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete windowed")

  def watermarks(progress: Seq[StreamingQueryProgress]): Seq[String] =
    throw new UnsupportedOperationException("Complete watermarks")

  def finalRows(spark: SparkSession, root: Path): Seq[(String,String,Long,Long)] =
    throw new UnsupportedOperationException("Complete finalRows")

  def droppedRows(progress: Seq[StreamingQueryProgress]): Long =
    throw new UnsupportedOperationException("Complete droppedRows")

  def eventLedger(phases: Seq[Seq[StreamingQueryProgress]], output: Seq[(String,String,Long,Long)]): (Long,Long,Long) =
    throw new UnsupportedOperationException("Complete eventLedger")

  def rejectUnsupported(spark: SparkSession, root: Path, kind: String): Unit =
    throw new UnsupportedOperationException("Complete rejectUnsupported")

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
      locally {
        val firstWindow = Seq((1,10L),(2,20L),(3,5L))
        assert(firstWindow.map(_._2).sum == 35L)
        println("Retained out-of-order event contributes to35,not30")
      }
      locally {
        val latest = Instant.parse("2024-01-01T00:30:00Z")
        assert(latest.minusSeconds(300L) == Instant.parse("2024-01-01T00:25:00Z"))
        println("Five-minute delay is event-time arithmetic;actual watermark still needs a receipt")
      }
      println("spark-032: worked examples passed; six task implementations remain")
    } finally { try { require(spark.streams.active.isEmpty,"Query still active; preserve scratch"); if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Define watermark placement and window state. Inputs/task: Apply with Watermark(event_time,5minutes) before grouping by a 5-minute window and team. Aggregate records and total amount, retaining the window struct in the result. Expected: A streaming aggregate with window, team, records, total. The watermark is attached to the same event-time column used by the window. Verify: Assert streaming status and the four output fields before starting the first phase.
// Exercise 2: Record actual watermark progress after the first phase. Inputs/task: Run phase 1 and extract nonmissing watermark strings from retained progress. Parse them as instants rather than wall-clock elapsed duration. Expected: Exactly 2 input rows processed. At least one watermark observation exists;the final observed watermark is no later than 00:00 for this phase. Verify: Assert input count 2 and actual watermark presence/order;do not infer finalization from the file count alone.
// Exercise 3: Accept a retained out-of-order event and observe finalization. Inputs/task: Publish phase 2, run the compatible query again and read finalized sink rows as(start, team, records, total). Verify the 00:03 event contributed before the first window closed. Expected: The finalized sink contains only(00:00, A,3,35) at this point. The actual watermark reaches at least 00:07. Verify: Assert the exact first-window tuple and the observed progress boundary.
// Exercise 4: Observe a far-late drop after the window has closed. Inputs/task: Publish phase 3 after phase 2 has terminated. Read the actual state-operator dropped-by-watermark counters and verify the 999 event does not change the finalized first window. Expected: Two new source rows consumed, one observed watermark drop and unchanged first-window result 35. B at 00:13 remains in pending state. Verify: Assert input 2, drop counter 1 and the unchanged sink tuple. Preserve missing metric evidence as an error rather than guessing zero.
// Exercise 5: Advance event time and distinguish finalized frompending output. Inputs/task: Publish the 00:30 administrative advancer, run phase 4 and return a ledger of total source inputs, observed drops and final business-window records. Expected: Seven total inputs, one observed drop, five finalized business records across three tuples:(00:00, A,3,35),(00:10, A,1,30),(00:10, B,1,7). The advancer window remains pending. Verify: Assert all final tuples, input/drop reconciliation and actual watermark at least 00:25.
// Exercise 6: Verify output-mode and sink eligibility through explicit failures. Inputs/task: Attempt two invalid configurations in separate owned paths:Update mode to Parquet, and Append mode for an unwatermarked team aggregate. Require analysis rejection and stop any unexpectedly created query in finally. Expected: Both configurations raiseAnalysisException;no active query remains. The valid windowed append sink stays intact. Verify: Assert each named analysis failure and the unchanged three-row valid sink after the checks.
