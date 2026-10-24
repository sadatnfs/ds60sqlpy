import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.expressions.Window

object Main {

  def validateCandidates(events: DataFrame): Unit = {
    val metrics = events.agg(count(lit(1)), countDistinct("event_id")).first()
    require(metrics.getLong(0) == metrics.getLong(1), "event IDs must be known and unique")
    require(
      events.filter(col("event_id") <= 0L || col("entity").isNull).count() == 0L,
      "known positive identities required"
    )
  }

  def rankCandidates(events: DataFrame): DataFrame = {
    val order =
      Window.partitionBy("entity").orderBy(col("event_time").desc_nulls_last, col("event_id").desc)
    events.withColumn("candidate_rank", row_number().over(order))
  }

  def winners(events: DataFrame): DataFrame = {
    validateCandidates(events)
    rankCandidates(events).filter(col("candidate_rank") === 1).drop("candidate_rank")
  }

  def topTimeCandidates(events: DataFrame): DataFrame = {
    val order = Window.partitionBy("entity").orderBy(col("event_time").desc_nulls_last)
    events
      .withColumn("time_rank", dense_rank().over(order))
      .filter(col("time_rank") === 1)
      .drop("time_rank")
  }

  def runningTotals(events: DataFrame): DataFrame = {
    val rowsFrame = Window
      .partitionBy("entity")
      .orderBy(col("event_time").asc_nulls_last, col("event_id"))
      .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    val peerFrame = Window
      .partitionBy("entity")
      .orderBy(col("event_time").asc_nulls_last)
      .rangeBetween(Window.unboundedPreceding, Window.currentRow)
    events
      .withColumn("rows_total", sum("amount").over(rowsFrame))
      .withColumn("peer_total", sum("amount").over(peerFrame))
      .select("event_id", "rows_total", "peer_total")
  }

  def previousEvidence(events: DataFrame): DataFrame = {
    val order =
      Window.partitionBy("entity").orderBy(col("event_time").asc_nulls_last, col("event_id"))
    events
      .withColumn("previous_id", lag(col("event_id"), 1).over(order))
      .withColumn("previous_time", lag(col("event_time"), 1).over(order))
      .withColumn(
        "gap_seconds",
        unix_timestamp(col("event_time")) - unix_timestamp(col("previous_time"))
      )
      .select("event_id", "previous_id", "gap_seconds")
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-019")
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
      val schema = StructType(
        Seq(
          StructField("event_id", LongType, false),
          StructField("entity", StringType, false),
          StructField("time_text", StringType, true),
          StructField("amount", LongType, false)
        )
      )
      val events = spark
        .createDataFrame(
          spark.sparkContext.parallelize(
            Seq(
              Row(1L, "A", "2024-01-01 00:00:00", 10L),
              Row(2L, "A", "2024-01-01 00:01:00", 20L),
              Row(3L, "A", "2024-01-01 00:01:00", 30L),
              Row(4L, "B", "2024-01-01 00:00:00", 40L),
              Row(5L, "B", "2024-01-01 00:02:00", 50L),
              Row(6L, "B", "2024-01-01 00:02:00", 60L),
              Row(7L, "C", null, 70L),
              Row(8L, "C", "2024-01-01 00:01:00", 80L)
            ),
            2
          ),
          schema
        )
        .withColumn("event_time", to_timestamp(col("time_text")))
      // Exercise 1: Validate identities before defining a winner
      validateCandidates(events)
      var rejected = false
      try validateCandidates(events.unionByName(events.filter(col("event_id") === 1L)))
      catch { case _: IllegalArgumentException => rejected = true }
      assert(rejected)
      // Exercise 2: Rank all candidates with an explicit NULL rule
      val ranked = rankCandidates(events)
      assert(
        ranked
          .select("event_id", "candidate_rank")
          .orderBy("event_id")
          .collect()
          .toSeq
          .map(r => (r.getLong(0), r.getInt(1))) == Seq(
          (1L, 3),
          (2L, 2),
          (3L, 1),
          (4L, 3),
          (5L, 2),
          (6L, 1),
          (7L, 2),
          (8L, 1)
        )
      )
      // Exercise 3: Select stable winners across physical layouts
      for (partitions <- Seq(1, 3, 4)) {
        assert(
          winners(events.repartition(partitions))
            .select("event_id")
            .orderBy("event_id")
            .collect()
            .toSeq
            .map(_.getLong(0)) == Seq(3L, 6L, 8L)
        )
      }
      events.createOrReplaceTempView("ds60_spark_019_events")
      val sqlWinners = spark.sql(
        "SELECT event_id FROM (SELECT *,row_number() OVER(PARTITION BY entity ORDER BY event_time DESC NULLS LAST,event_id DESC) AS rn FROM ds60_spark_019_events) WHERE rn=1 ORDER BY event_id"
      )
      assert(sqlWinners.collect().toSeq.map(_.getLong(0)) == Seq(3L, 6L, 8L))
      // Exercise 4: Prove why timestamp-only ordering is incomplete
      val top = topTimeCandidates(events)
      assert(
        top.select("event_id").orderBy("event_id").collect().toSeq.map(_.getLong(0)) == Seq(2L, 3L,
          5L, 6L, 8L)
      )
      assert(
        top
          .groupBy("entity")
          .count()
          .filter(col("count") > 1L)
          .select("entity")
          .orderBy("entity")
          .collect()
          .toSeq
          .map(_.getString(0)) == Seq("A", "B")
      )
      // Exercise 5: Distinguish occurrence totals from time-peer totals
      assert(
        runningTotals(events)
          .orderBy("event_id")
          .collect()
          .toSeq
          .map(r => (r.getLong(0), r.getLong(1), r.getLong(2))) == Seq(
          (1L, 10L, 10L),
          (2L, 30L, 60L),
          (3L, 60L, 60L),
          (4L, 40L, 40L),
          (5L, 90L, 150L),
          (6L, 150L, 150L),
          (7L, 150L, 150L),
          (8L, 80L, 80L)
        )
      )
      // Exercise 6: Interpret lag without claiming strict temporal availability
      assert(
        previousEvidence(events)
          .orderBy("event_id")
          .collect()
          .toSeq
          .map(r =>
            (
              r.getLong(0),
              if (r.isNullAt(1)) None else Some(r.getLong(1)),
              if (r.isNullAt(2)) None else Some(r.getLong(2))
            )
          ) == Seq(
          (1L, None, None),
          (2L, Some(1L), Some(60L)),
          (3L, Some(2L), Some(0L)),
          (4L, None, None),
          (5L, Some(4L), Some(120L)),
          (6L, Some(5L), Some(0L)),
          (7L, Some(8L), None),
          (8L, None, None)
        )
      )
      println(
        "spark-019: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString
      )
    } finally { spark.stop() }
  }
}

// Exercise 1: Validate identities before defining a winner. Inputs/task: Reject an input unless event_id is known, positive and unique and entity is known. Allow missing event_time under the declared last-priority policy. Return Unit/None on success. Expected: The eight-event fixture passes;adding another copy of event 1 fails. Missing-time event 7 is allowed. Verify: Assert normal acceptance and explicit rejection after unioning a duplicate identity.
// Exercise 2: Rank all candidates with an explicit NULL rule. Inputs/task: Add candidate_rank using row_number per entity, descending event_time with NULL last, then descending event_id. Keep all eight rows. Expected: Ranks byevent_id are 1:3,2:2,3:1,4:3,5:2,6:1,7:2,8:1. Verify: Assert the full ID/rank table and input count 8.
// Exercise 3: Select stable winners across physical layouts. Inputs/task: Validate candidates, rank them and retain rank 1. Compare winner IDs after repartitioning to 1,3 and 4 partitions, then compare an equivalentSQL row_number query. Expected: Every case yields event IDs[3,6,8], one per entity. SQL returns the same literal winners. Verify: Assert exact winners in every layout and SQL, not just equal row counts.
// Exercise 4: Prove why timestamp-only ordering is incomplete. Inputs/task: Use dense_rank ordered only by descending event_time with NULL last, returning all rank 1 candidates. Report the candidate IDs rather than choosing an arbitrary winner. Expected: Top-time candidates[2,3,5,6,8]. EntitiesA andB each have two admissible candidates under the incomplete rule. Verify: Assert the five candidate identities and the two ambiguous entity keys. Do not require unstable executions to change output.
// Exercise 5: Distinguish occurrence totals from time-peer totals. Inputs/task: Return event_id, rows_total, peer_total. ROWS uses ascending time NULL last then ID and an unbounded-preceding/current-row frame. RANGE uses only ascending time NULL last over the same cumulative boundary. Expected: By ID:1(10,10),2(30,60),3(60,60),4(40,40),5(90,150),6(150,150),7(150,150),8(80,80). Verify: Assert all eight tuples, especially tied IDs 2/3 and the missing-time event 7.
// Exercise 6: Interpret lag without claiming strict temporal availability. Inputs/task: Using ascending time NULL last then event_id, return event_id, previous_id, gap_seconds. Lag the event identity and time, then subtract epoch seconds. Expected: 1(NULL, NULL),2(1,60),3(2,0),4(NULL, NULL),5(4,120),6(5,0),7(8, NULL),8(NULL, NULL). Verify: Assert the complete identity/gap rows and explain zero gaps and the known previous ID with unknown duration.
