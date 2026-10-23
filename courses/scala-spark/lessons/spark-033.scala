import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQueryProgress,Trigger}
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import scala.jdk.CollectionConverters._

object Main {
  val eventSchema = StructType(Seq(StructField("delivery_id",LongType,true),StructField("event_id",StringType,true),StructField("amount",LongType,true),StructField("event_time",TimestampType,true)))
  def publish(root: Path, index: Int, lines: Seq[String]): Unit = {
    val target = root.resolve("input").resolve(s"batch-$index.json");require(!Files.exists(target),"New source filename required")
    val staged = Files.createTempFile(root.resolve("staging"),"arrival-",".tmp")
    try { Files.writeString(staged,lines.mkString("\n")+"\n",StandardCharsets.UTF_8,StandardOpenOption.TRUNCATE_EXISTING);Files.move(staged,target,StandardCopyOption.ATOMIC_MOVE) } finally Files.deleteIfExists(staged)
  }
  def input(spark: SparkSession, root: Path): DataFrame = spark.readStream.schema(eventSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(root.resolve("input").toString)
  def runSink(frame: DataFrame, root: Path, name: String): Seq[StreamingQueryProgress] = {
    val query = frame.writeStream.format("parquet").outputMode("append").option("checkpointLocation",root.resolve(name+"-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve(name+"-output").toString)
    try { require(query.awaitTermination(30000L),"Finite sink deadline exceeded");require(!query.isActive && query.exception.isEmpty,"Query failed");query.recentProgress.toSeq } finally query.stop()
  }
  def outputRows(spark: SparkSession, root: Path): Seq[(String,Long,Long)] = spark.read.parquet(root.resolve("accepted-output").toString).select("event_id","delivery_id","amount").orderBy("event_id","delivery_id").collect().toSeq.map(r => (r.getString(0),r.getLong(1),r.getLong(2)))
  def deleteOwned(root: Path): Unit = { val paths = Files.walk(root);try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p)) finally paths.close() }

  def classify(events: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete classify")

  def deduplicated(classified: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete deduplicated")

  def runBranches(spark: SparkSession, root: Path): (Seq[StreamingQueryProgress],Seq[StreamingQueryProgress]) =
    throw new UnsupportedOperationException("Complete runBranches")

  def businessRows(spark: SparkSession, root: Path): Seq[(String,Long,Long)] =
    throw new UnsupportedOperationException("Complete businessRows")

  def removedState(progress: Seq[StreamingQueryProgress]): Long =
    throw new UnsupportedOperationException("Complete removedState")

  def deliveryLedger(spark: SparkSession, root: Path): (Long,Long,Long,Long,Long) =
    throw new UnsupportedOperationException("Complete deliveryLedger")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-033").master("local[2]")
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
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-033-")
      Files.createDirectory(ownedRoot.resolve("input"));Files.createDirectory(ownedRoot.resolve("staging"))
      val batches = Seq(
       Seq("""{"delivery_id":1,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}""","""{"delivery_id":2,"event_id":"e2","amount":10,"event_time":"2024-01-01T00:02:00Z"}""","""{"delivery_id":3,"event_id":null,"amount":99,"event_time":"2024-01-01T00:02:00Z"}"""),
       Seq("""{"delivery_id":4,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}""","""{"delivery_id":5,"event_id":"e3","amount":10,"event_time":"2024-01-01T00:03:00Z"}"""),
       Seq("""{"delivery_id":6,"event_id":"__advance__","amount":0,"event_time":"2024-01-01T00:20:00Z"}"""))
      locally {
        val occurrences = Seq(("e1",10L),("e2",10L),("e1",10L),("e3",10L))
        assert(occurrences.map(_._1).distinct.size == 3 && occurrences.map(_._2).distinct.size == 1)
        println("Equal amounts are not equal event identities")
      }
      locally {
        assert(batches.map(_.size) == Seq(3,2,1) && batches.flatten.size == 6)
        println("Six source deliveries feed two independently checkpointed branches")
      }
      println("spark-033: worked examples passed; six task implementations remain")
    } finally { try { require(spark.streams.active.isEmpty,"Query still active; preserve scratch"); if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Classify missing event identity before deduplication. Inputs/task: Add reason missing_event_id for NULL event_id and accepted otherwise, retaining delivery_id, amount and event_time. Expected: Delivery 3 is quarantined;known IDs are eligible for the separate deduplication policy. Verify: Construct the first streaming classification with all declared fields and verify the exact quarantine row after the first phase.
// Exercise 2: Define a bounded event-ID stateful operator. Inputs/task: Filter accepted identities, drop the reason field, attach a five-minute watermark to event_time, and deduplicate within that watermark on event_id only. Expected: The result remains streaming and retains delivery_id, event_id, amount, event_time. Equal amounts across distinct IDs remain distinct. Verify: Assert output shape and use the explicit event_id key, then validate all retained identities through later sink checks.
// Exercise 3: Execute accepted and quarantine branches with separate checkpoints. Inputs/task: Run both first-phase branches with AvailableNow:deduplicated records to accepted-output and missing-ID records to quarantine-output. Use distinct checkpoints and bounded await/stop scopes. Expected: Accepted(e1, delivery 1,10),(e2, delivery 2,10);quarantine(delivery 3, NULL, missing_event_id). The raw source has 3 rows;prepared branch input metrics report 2 accepted-eligible rows and 1 quarantine row. Verify: Assert both exact output populations, branch metrics 2/1 and an independent raw batch-source count 3.
// Exercise 4: Suppress a replay while retaining distinct equal-valued events. Inputs/task: Publish the second file after the first phase terminates and run both compatible branches again. Compare the accepted business identities and their total. Expected: Accepted(e1, delivery 1,10),(e2, delivery 2,10),(e3, delivery 5,10);delivery 4 replay contributes no additional row. Business total 30. Verify: Assert all retained event/delivery pairs, sum 30, raw source total 5 and prepared branch metrics 2 accepted-eligible inputs versus 0 quarantined inputs for this phase.
// Exercise 5: Observe state removal and state the retention limit. Inputs/task: Publish the 00:20 advancer and run both branches. Sum actual numRowsRemoved state metrics from the accepted branch and inspect remaining state. Expected: The three old business-key states are removed under the observed watermark progression;accepted output still retains their committed rows plus the advancer. Verify: Assert removed state rows at least 3, unchanged business rows and one advancer output. Print actual state metrics without promising perpetual deduplication.
// Exercise 6: Reconcile deliveries, quarantine, replay suppression and business totals. Inputs/task: Read the six source deliveries once as a bounded batch and compare them with both sinks. Return source deliveries, known-ID deliveries, quarantine rows, accepted rows including advancer, and business total. Expected: Ledger(6,5,1,4,30). One known-ID delivery is suppressed as an in-horizon replay;three distinct equal-valued business events remain. Verify: Assert the complete ledger and six unique delivery IDs;confirm no active queries remain before cleanup.
