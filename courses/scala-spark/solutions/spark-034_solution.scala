import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery,StreamingQueryProgress,Trigger}
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.time.Instant
import scala.jdk.CollectionConverters._

object Main {
  val impressionSchema = StructType(Seq(StructField("impression_id",StringType,true),StructField("key",StringType,true),StructField("impression_time",TimestampType,true)))
  val clickSchema = StructType(Seq(StructField("click_id",StringType,true),StructField("key",StringType,true),StructField("click_time",TimestampType,true)))
  val resultSchema = StructType(Seq(StructField("impression_id",StringType,true),StructField("click_id",StringType,true),StructField("impression_time",TimestampType,true),StructField("click_time",TimestampType,true)))
  def publish(root: Path, side: String, index: Int, lines: Seq[String]): Unit = {
    require(Set("impressions","clicks").contains(side),"Unknown input side")
    val target = root.resolve(side).resolve(s"batch-$index.json");require(!Files.exists(target),"New input filename required")
    val staged = Files.createTempFile(root.resolve("staging"),"arrival-",".tmp")
    try { Files.writeString(staged,lines.mkString("\n")+"\n",StandardCharsets.UTF_8,StandardOpenOption.TRUNCATE_EXISTING);Files.move(staged,target,StandardCopyOption.ATOMIC_MOVE) } finally Files.deleteIfExists(staged)
  }
  def deleteOwned(root: Path): Unit = { val paths = Files.walk(root);try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p)) finally paths.close() }

  def inputs(spark: SparkSession, root: Path): (DataFrame,DataFrame) = {
    val impressions = spark.readStream.schema(impressionSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(root.resolve("impressions").toString).withWatermark("impression_time","5 minutes")
    val clicks = spark.readStream.schema(clickSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(root.resolve("clicks").toString).withWatermark("click_time","5 minutes")
    (impressions,clicks)
  }

  def boundedJoin(impressions: DataFrame, clicks: DataFrame, kind: String): DataFrame = {
    require(Set("inner","left_outer").contains(kind),"Unsupported join kind")
    val i = impressions.as("i");val c = clicks.as("c")
    val condition = col("i.key") === col("c.key") && col("c.click_time") >= col("i.impression_time") && col("c.click_time") < col("i.impression_time") + expr("INTERVAL 10 MINUTES")
    i.join(c,condition,kind).select(col("i.impression_id"),col("c.click_id"),col("i.impression_time"),col("c.click_time"))
  }

  def runJoin(spark: SparkSession, root: Path, kind: String): Seq[StreamingQueryProgress] = {
    val sources = inputs(spark,root)
    val query = boundedJoin(sources._1,sources._2,kind).writeStream.format("parquet").outputMode("append").option("checkpointLocation",root.resolve(kind+"-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve(kind+"-output").toString)
    try { require(query.awaitTermination(30000L),"Finite join deadline exceeded");require(query.exception.isEmpty && !query.isActive,"Join failed");query.recentProgress.toSeq } finally query.stop()
  }

  def pairs(spark: SparkSession, root: Path, kind: String): Seq[(String,Option[String])] = {
    spark.read.schema(resultSchema).parquet(root.resolve(kind+"-output").toString).select("impression_id","click_id").orderBy(col("impression_id"),col("click_id").asc_nulls_last).collect().toSeq.map(r => (r.getString(0),if(r.isNullAt(1)) None else Some(r.getString(1))))
  }

  def progressEvidence(progress: Seq[StreamingQueryProgress]): (Long,Seq[String],Long) = {
    require(progress.exists(_.stateOperators.nonEmpty),"Missing join state evidence")
    (progress.map(_.numInputRows).sum,progress.flatMap(p => Option(p.eventTime.get("watermark"))),progress.flatMap(_.stateOperators).map(_.numRowsRemoved).sum)
  }

  def rejectUnboundedOuter(spark: SparkSession, root: Path): Unit = {
    val sources = inputs(spark,root)
    val invalid = sources._1.as("i").join(sources._2.as("c"),col("i.key") === col("c.key"),"left_outer").select(col("i.impression_id"),col("c.click_id"))
    var query: StreamingQuery = null;var rejected = false
    try {
     query = invalid.writeStream.format("parquet").outputMode("append").option("checkpointLocation",root.resolve("invalid-checkpoint").toString).trigger(Trigger.AvailableNow()).start(root.resolve("invalid-output").toString)
     query.awaitTermination(30000L)
    } catch { case _: org.apache.spark.sql.AnalysisException => rejected = true }
    finally { if(query != null) query.stop() }
    require(rejected,"Unbounded outer join unexpectedly accepted")
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-034").master("local[2]")
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
      spark.conf.set("spark.sql.streaming.multipleWatermarkPolicy","min")
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-034-")
      Seq("impressions","clicks","staging").foreach(name => Files.createDirectory(ownedRoot.resolve(name)))
      val impressionLines = Seq("""{"impression_id":"i1","key":"A","impression_time":"2024-01-01T00:00:00Z"}""","""{"impression_id":"i2","key":"B","impression_time":"2024-01-01T00:00:00Z"}""","""{"impression_id":"i3","key":"C","impression_time":"2024-01-01T00:05:00Z"}""")
      val clickLines = Seq("""{"click_id":"c1","key":"A","click_time":"2024-01-01T00:03:00Z"}""","""{"click_id":"c2","key":"C","click_time":"2024-01-01T00:10:00Z"}""","""{"click_id":"c3","key":"A","click_time":"2024-01-01T00:10:00Z"}""","""{"click_id":"c4","key":"Z","click_time":"2024-01-01T00:04:00Z"}""")
      // Exercise 1: Declare both streaming schemas and watermark policies
      publish(ownedRoot,"impressions",0,impressionLines);publish(ownedRoot,"clicks",0,clickLines)
      val sources = inputs(spark,ownedRoot)
      assert(sources._1.isStreaming && sources._2.isStreaming && sources._1.schema("impression_time").dataType == TimestampType && sources._2.schema("click_time").dataType == TimestampType)
      assert(spark.conf.get("spark.sql.streaming.multipleWatermarkPolicy") == "min" && spark.streams.active.isEmpty)
      // Exercise 2: Express key equality and the exact time range
      val planned = boundedJoin(sources._1,sources._2,"inner")
      assert(planned.isStreaming && planned.columns.toSeq == Seq("impression_id","click_id","impression_time","click_time"))
      var rejectedKind = false
      try boundedJoin(sources._1,sources._2,"cross") catch { case _: IllegalArgumentException => rejectedKind = true }
      assert(rejectedKind)
      // Exercise 3: Run inner and outer queries with separate owned recovery state
      val innerFirst = runJoin(spark,ownedRoot,"inner");val outerFirst = runJoin(spark,ownedRoot,"left_outer")
      assert(innerFirst.map(_.numInputRows).sum == 7L && outerFirst.map(_.numInputRows).sum == 7L && spark.streams.active.isEmpty)
      // Exercise 4: Distinguish immediate matches frompending unmatched impressions
      val expectedMatched = Seq(("i1",Some("c1")),("i3",Some("c2")))
      assert(pairs(spark,ownedRoot,"inner") == expectedMatched && pairs(spark,ownedRoot,"left_outer") == expectedMatched)
      // Exercise 5: Advance both sides and observe delayed outer finalization
      publish(ownedRoot,"impressions",1,Seq("""{"impression_id":"__left_advance__","key":"__left__","impression_time":"2024-01-01T00:30:00Z"}"""))
      publish(ownedRoot,"clicks",1,Seq("""{"click_id":"__right_advance__","key":"__right__","click_time":"2024-01-01T00:30:00Z"}"""))
      val innerSecond = runJoin(spark,ownedRoot,"inner");val outerSecond = runJoin(spark,ownedRoot,"left_outer")
      assert(pairs(spark,ownedRoot,"inner") == expectedMatched)
      assert(pairs(spark,ownedRoot,"left_outer") == Seq(("i1",Some("c1")),("i2",None),("i3",Some("c2"))))
      val progress = progressEvidence(outerSecond)
      assert(progress._1 == 2L && innerSecond.map(_.numInputRows).sum == 2L && progress._3 > 0L)
      assert(progress._2.exists(value => !Instant.parse(value).isBefore(Instant.parse("2024-01-01T00:25:00Z"))))
      println("outer_finalization_progress=" + progress)
      // Exercise 6: Reject an outer join without an event-time bound
      rejectUnboundedOuter(spark,ownedRoot)
      assert(spark.streams.active.isEmpty && pairs(spark,ownedRoot,"left_outer") == Seq(("i1",Some("c1")),("i2",None),("i3",Some("c2"))))
      println("spark-034: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { require(spark.streams.active.isEmpty,"Query still active; preserve scratch"); if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Declare both streaming schemas and watermark policies. Inputs/task: Read the owned impression and click file directories with their explicit schemas, maxFilesPerTrigger 1 and five-minute watermarks on their respective event-time columns. Expected: Both relations are streaming;the minimum multiple-watermark policy isexplicit and no query runs merely fromconstruction. Verify: Assert both streaming flags, the declared timestamp fields and policymin before execution.
// Exercise 2: Express key equality and the exact time range. Inputs/task: Build either an inner orleft_outer join using key equality, click_time>=impression_time and click_time<impression_time+10minutes. Project impression_id, click_id and both timestamps. Expected: A streaming relation with the four declared columns. The condition can matchi 1/c1 and i 3/c2 butnot boundaryclickc 3. Verify: Assert output shape and reject an unsupported kind value;later exact pair checks validate both predicates.
// Exercise 3: Run inner and outer queries with separate owned recovery state. Inputs/task: Execute a named join kind with AvailableNow, Parquet append and its own checkpoint/output paths. Await at most 30 seconds and stop in finally. Run both kinds for the first input phase. Expected: Each query consumes 7 source rows across its two inputs and terminates. The two checkpoints are distinct. Verify: Assert input 7 for each query and inactive state after both bounded runs;do not combine their processing counts into 14 unique source events.
// Exercise 4: Distinguish immediate matches frompending unmatched impressions. Inputs/task: Read either owned output as ordered(impression_id, click_id) pairs. After phase 1, compare inner and outer sinks with the two-pair literal oracle. Expected: Both sinks contain(i1, c1),(i3, c2). i2/NULL isabsent because its possible match interval isnot yet finalized. c3 and c 4 produce no pair. Verify: Assert exact pair lists and absence of prematurei 2/NULL;do not rely only on output count 2.
// Exercise 5: Advance both sides and observe delayed outer finalization. Inputs/task: Publish distinct-key 00:30 advancers toboth sources, rerun both compatible queries and extract actual watermark/state-removal evidence. Expected: Inner remains two pairs. Outer becomes(i1, c1),(i2, NULL),(i3, c2). Actual watermark reaches at least 00:25 and state removal ispositive;the new advancer impression remains pending. Verify: Assert the complete outer ledger, input 2 for each new run, observed progress boundary and removed-state count.
// Exercise 6: Reject an outer join without an event-time bound. Inputs/task: In a separate owned checkpoint/output namespace, attempt a stream-stream left outer join using only key equality despite input watermarks. Require analysis rejection and stop any unexpectedly created query. Expected: AnalysisException because this design lacks the required bounded match/finalization condition. The valid inner/outer sinks remain unchanged and no query isactive. Verify: Assert the named rejection, inactive state and unchanged final valid outer pairs.
