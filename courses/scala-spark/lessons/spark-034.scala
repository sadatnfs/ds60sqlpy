import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery, StreamingQueryProgress, Trigger}
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.time.Instant
import scala.jdk.CollectionConverters._

object Main {
  val impressionSchema = StructType(
    Seq(
      StructField("impression_id", StringType, true),
      StructField("key", StringType, true),
      StructField("impression_time", TimestampType, true)
    )
  )
  val clickSchema = StructType(
    Seq(
      StructField("click_id", StringType, true),
      StructField("key", StringType, true),
      StructField("click_time", TimestampType, true)
    )
  )
  val resultSchema = StructType(
    Seq(
      StructField("impression_id", StringType, true),
      StructField("click_id", StringType, true),
      StructField("impression_time", TimestampType, true),
      StructField("click_time", TimestampType, true)
    )
  )
  def publish(root: Path, side: String, index: Int, lines: Seq[String]): Unit = {
    require(Set("impressions", "clicks").contains(side), "Unknown input side")
    val target = root.resolve(side).resolve(s"batch-$index.json");
    require(!Files.exists(target), "New input filename required")
    val staged = Files.createTempFile(root.resolve("staging"), "arrival-", ".tmp")
    try {
      Files.writeString(
        staged,
        lines.mkString("\n") + "\n",
        StandardCharsets.UTF_8,
        StandardOpenOption.TRUNCATE_EXISTING
      );
      Files.move(staged, target, StandardCopyOption.ATOMIC_MOVE)
    } finally Files.deleteIfExists(staged)
  }
  def deleteOwned(root: Path): Unit = {
    val paths = Files.walk(root);
    try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally paths.close()
  }

  def inputs(spark: SparkSession, root: Path): (DataFrame, DataFrame) =
    throw new UnsupportedOperationException("Complete inputs")

  def boundedJoin(impressions: DataFrame, clicks: DataFrame, kind: String): DataFrame =
    throw new UnsupportedOperationException("Complete boundedJoin")

  def runJoin(spark: SparkSession, root: Path, kind: String): Seq[StreamingQueryProgress] =
    throw new UnsupportedOperationException("Complete runJoin")

  def pairs(spark: SparkSession, root: Path, kind: String): Seq[(String, Option[String])] =
    throw new UnsupportedOperationException("Complete pairs")

  def progressEvidence(progress: Seq[StreamingQueryProgress]): (Long, Seq[String], Long) =
    throw new UnsupportedOperationException("Complete progressEvidence")

  def rejectUnboundedOuter(spark: SparkSession, root: Path): Unit =
    throw new UnsupportedOperationException("Complete rejectUnboundedOuter")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-034")
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
      spark.conf.set("spark.sql.streaming.multipleWatermarkPolicy", "min")
      ownedRoot =
        Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-034-")
      Seq("impressions", "clicks", "staging").foreach(name =>
        Files.createDirectory(ownedRoot.resolve(name))
      )
      val impressionLines = Seq(
        """{"impression_id":"i1","key":"A","impression_time":"2024-01-01T00:00:00Z"}""",
        """{"impression_id":"i2","key":"B","impression_time":"2024-01-01T00:00:00Z"}""",
        """{"impression_id":"i3","key":"C","impression_time":"2024-01-01T00:05:00Z"}"""
      )
      val clickLines = Seq(
        """{"click_id":"c1","key":"A","click_time":"2024-01-01T00:03:00Z"}""",
        """{"click_id":"c2","key":"C","click_time":"2024-01-01T00:10:00Z"}""",
        """{"click_id":"c3","key":"A","click_time":"2024-01-01T00:10:00Z"}""",
        """{"click_id":"c4","key":"Z","click_time":"2024-01-01T00:04:00Z"}"""
      )
      locally {
        val impressionMinute = 0
        assert(3 >= impressionMinute && 3 < impressionMinute + 10)
        assert(!(10 >= impressionMinute && 10 < impressionMinute + 10))
        println("Minute3 matches;minute10 is outside the half-open window")
      }
      locally {
        val impressions = Seq(("i1", "A", 0), ("i2", "B", 0), ("i3", "C", 5))
        val clicks = Seq(("c1", "A", 3), ("c2", "C", 10), ("c3", "A", 10), ("c4", "Z", 4))
        val pairs =
          for (i <- impressions; c <- clicks if i._2 == c._2 && c._3 >= i._3 && c._3 < i._3 + 10)
            yield (i._1, c._1)
        assert(pairs == Seq(("i1", "c1"), ("i3", "c2")))
        println("Independent business pair oracle=" + pairs)
      }
      println("spark-034: worked examples passed; six task implementations remain")
    } finally {
      try {
        require(spark.streams.active.isEmpty, "Query still active; preserve scratch");
        if (ownedRoot != null) deleteOwned(ownedRoot)
      } finally { spark.stop() }
    }
  }
}

// Exercise 1: Declare both streaming schemas and watermark policies. Inputs/task: Read the owned impression and click file directories with their explicit schemas, maxFilesPerTrigger 1 and five-minute watermarks on their respective event-time columns. Expected: Both relations are streaming;the minimum multiple-watermark policy isexplicit and no query runs merely fromconstruction. Verify: Assert both streaming flags, the declared timestamp fields and policymin before execution.
// Exercise 2: Express key equality and the exact time range. Inputs/task: Build either an inner orleft_outer join using key equality, click_time>=impression_time and click_time<impression_time+10minutes. Project impression_id, click_id and both timestamps. Expected: A streaming relation with the four declared columns. The condition can matchi 1/c1 and i 3/c2 butnot boundaryclickc 3. Verify: Assert output shape and reject an unsupported kind value;later exact pair checks validate both predicates.
// Exercise 3: Run inner and outer queries with separate owned recovery state. Inputs/task: Execute a named join kind with AvailableNow, Parquet append and its own checkpoint/output paths. Await at most 30 seconds and stop in finally. Run both kinds for the first input phase. Expected: Each query consumes 7 source rows across its two inputs and terminates. The two checkpoints are distinct. Verify: Assert input 7 for each query and inactive state after both bounded runs;do not combine their processing counts into 14 unique source events.
// Exercise 4: Distinguish immediate matches frompending unmatched impressions. Inputs/task: Read either owned output as ordered(impression_id, click_id) pairs. After phase 1, compare inner and outer sinks with the two-pair literal oracle. Expected: Both sinks contain(i1, c1),(i3, c2). i2/NULL isabsent because its possible match interval isnot yet finalized. c3 and c 4 produce no pair. Verify: Assert exact pair lists and absence of prematurei 2/NULL;do not rely only on output count 2.
// Exercise 5: Advance both sides and observe delayed outer finalization. Inputs/task: Publish distinct-key 00:30 advancers toboth sources, rerun both compatible queries and extract actual watermark/state-removal evidence. Expected: Inner remains two pairs. Outer becomes(i1, c1),(i2, NULL),(i3, c2). Actual watermark reaches at least 00:25 and state removal ispositive;the new advancer impression remains pending. Verify: Assert the complete outer ledger, input 2 for each new run, observed progress boundary and removed-state count.
// Exercise 6: Reject an outer join without an event-time bound. Inputs/task: In a separate owned checkpoint/output namespace, attempt a stream-stream left outer join using only key equality despite input watermarks. Require analysis rejection and stop any unexpectedly created query. Expected: AnalysisException because this design lacks the required bounded match/finalization condition. The valid inner/outer sinks remain unchanged and no query isactive. Verify: Assert the named rejection, inactive state and unchanged final valid outer pairs.
