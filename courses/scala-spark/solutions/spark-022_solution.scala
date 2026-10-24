import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  def runGrouped(frame: DataFrame, group: String): Seq[(Long, Long)] = {
    val sc = frame.sparkSession.sparkContext
    sc.setJobGroup(group, "Bounded shuffle evidence", true)
    try frame.collect().toSeq.map(r => (r.getLong(0), r.getLong(1))).sortBy(_._1)
    finally sc.clearJobGroup()
  }

  def sourceMetrics(source: DataFrame): (Long, Long, Long) = {
    val row = source.agg(count(lit(1)), countDistinct("key"), sum("id")).first()
    (row.getLong(0), row.getLong(1), row.getLong(2))
  }

  def buildGrouped(source: DataFrame, partitions: Int): DataFrame = {
    require(partitions >= 1 && partitions <= 16, "Partition budget is1..16")
    source.sparkSession.conf.set("spark.sql.shuffle.partitions", partitions.toString)
    source.groupBy("key").agg(count(lit(1)).as("n"))
  }

  def exchangeMetrics(frame: DataFrame): Seq[Map[String, Long]] = {
    frame.queryExecution.executedPlan.collect {
      case node if node.nodeName == "Exchange" =>
        node.metrics.map { case (key, metric) => key -> metric.value }.toMap
    }
  }

  def stageEvidence(spark: SparkSession, group: String): Seq[(Int, Int, Int, Int)] = {
    val tracker = spark.sparkContext.statusTracker
    val stages = tracker
      .getJobIdsForGroup(group)
      .flatMap(id => tracker.getJobInfo(id).toSeq.flatMap(_.stageIds))
      .distinct
      .sorted
    stages
      .flatMap(id =>
        tracker
          .getStageInfo(id)
          .map(info => (id, info.numTasks, info.numCompletedTasks, info.numFailedTasks))
      )
      .toSeq
  }

  def compareResults(left: Seq[(Long, Long)], right: Seq[(Long, Long)]): Unit = {
    require(
      left == right && left.size == 1000 && left.map(_._2).sum == 20000L,
      "Grouped result contract changed"
    )
  }

  def workModel(reducers: Int): (Long, Long, Double) = {
    require(reducers > 0, "Positive reducer count required")
    (20000L / 4L, 4L * 1000L, 1000.0 / reducers)
  }

  def main(args: Array[String]): Unit = {

    val spark = SparkSession
      .builder()
      .appName("ds60-spark-022")
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
      val source = spark.range(0L, 20000L, 1L, 4).withColumn("key", col("id") % 1000L)
      val originalShuffle = spark.conf.get("spark.sql.shuffle.partitions")
      // Exercise 1: Establish the high-cardinality fixture oracle
      assert(sourceMetrics(source) == (20000L, 1000L, 199990000L))
      assert(20000L * 19999L / 2L == 199990000L)
      // Exercise 2: Build and execute a controlled grouped query
      val two = buildGrouped(source, 2)
      val twoRows = runGrouped(two, "ds60-spark-022-p2")
      val expected = (0L until 1000L).map(key => (key, 20L))
      assert(twoRows == expected && twoRows.map(_._2).sum == 20000L)
      assert(two.queryExecution.executedPlan.toString.contains("Exchange"))
      var rejected = false
      try buildGrouped(source, 0)
      catch { case _: IllegalArgumentException => rejected = true }
      assert(rejected)
      // Exercise 3: Read actual exchange metrics after the action
      val twoExchange = exchangeMetrics(two)
      assert(
        twoExchange.size == 1 && twoExchange.head("numPartitions") == 2L && twoExchange.head(
          "dataSize"
        ) > 0L
      )
      println("p2_exchange=" + twoExchange)
      // Exercise 4: Attach stage and task evidence to the named action
      val twoStages = stageEvidence(spark, "ds60-spark-022-p2")
      assert(
        twoStages.nonEmpty && twoStages.exists(_._2 == 2) && twoStages.forall(r =>
          r._2 >= 0 && r._3 >= 0 && r._4 >= 0
        )
      )
      println("p2_stages=" + twoStages)
      // Exercise 5: Change reduce parallelism while preserving the complete result
      val five = buildGrouped(source, 5)
      val fiveRows = runGrouped(five, "ds60-spark-022-p5")
      compareResults(twoRows, fiveRows); assert(fiveRows == expected)
      val fiveExchange = exchangeMetrics(five);
      val fiveStages = stageEvidence(spark, "ds60-spark-022-p5")
      assert(
        fiveExchange.size == 1 && fiveExchange.head("numPartitions") == 5L && fiveExchange.head(
          "dataSize"
        ) > 0L
      )
      assert(fiveStages.exists(_._2 == 5))
      println("p5_exchange=" + fiveExchange + ";p5_stages=" + fiveStages)
      // Exercise 6: Separate a workload model from measured evidence
      assert(workModel(2) == (5000L, 4000L, 500.0) && workModel(5) == (5000L, 4000L, 200.0))
      println(
        "version=" + spark.version + ";aqe=" + spark.conf.get(
          "spark.sql.adaptive.enabled"
        ) + ";master=" + spark.sparkContext.master + ";model_only=" + Seq(
          workModel(2),
          workModel(5)
        )
      )
      spark.conf.set("spark.sql.shuffle.partitions", originalShuffle)
      println(
        "spark-022: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString
      )
    } finally {
      try { () }
      finally { spark.stop() }
    }
  }
}

// Exercise 1: Establish the high-cardinality fixture oracle. Inputs/task: Compute input row count, distinct key count and total id sum. Confirm the key formula supports exactly 20 occurrences per key. Expected: Metrics(20000,1000,199990000);keys 0..999 each occur 20 times by construction. Verify: Assert the aggregate tuple and independent arithmetic sum 0+...+19999.
// Exercise 2: Build and execute a controlled grouped query. Inputs/task: Require 1..16 shuffle partitions, set that configuration in the owned session and return key, n from groupBy/count. Execute the two-partition case under the supplied unique job group. Expected: Sorted output[(0,20),...,(999,20)], with total counts 20000 and an Exchange in the executed plan. Verify: Assert every key/count pair and the plan Exchange marker. Reject an out-of-budget partition request.
// Exercise 3: Read actual exchange metrics after the action. Inputs/task: Traverse the executed classic Spark plan, collecting each Exchange metric map. Use the version-pinned internal diagnostic API only for evidence after collection. Expected: One exchange map for this aggregate, with numPartitions 2 and dataSize>0. Record other available metrics without inventing units or missing values. Verify: Assert one observed exchange, its partition metric and positive serialized data size;print the complete available map.
// Exercise 4: Attach stage and task evidence to the named action. Inputs/task: Use the status tracker to find jobs for a supplied group and their retained stages. Return stage_id, num_tasks, completed_tasks, failed_tasks ordered by stage identity. Expected: Nonempty retained stage evidence for the p2 action, including a stage with 2 tasks. All task counters are nonnegative. Verify: Assert nonempty stage rows and a two-task stage, and print the actual counters rather than asserting a universal stage count.
// Exercise 5: Change reduce parallelism while preserving the complete result. Inputs/task: Run the same source aggregation with 5 shuffle partitions under its own job group. Compare all 1000 group tuples, then report exchange and stage evidence tied to p5. Expected: Exact output matches p2 and the literal oracle. Exchange numPartitions 5 and positive dataSize;retained task evidence includes a five-task stage. Verify: Assert result parity before inspecting the 5-partition metric and corresponding action-group stages.
// Exercise 6: Separate a workload model from measured evidence. Inputs/task: For the declared 20000-row,1000-key, four-mapper fixture, return source_rows_per_mapper, partial_group_upper and average_output_groups_per_reducer for a positive reducer count. Label them as arithmetic estimates and print version/configuration beside the actual metrics. Expected: For reducers 2:5000,4000,500. For reducers 5:5000,4000,200. These values do not assert actual balanced hash buckets or network bytes. Verify: Assert the two model tuples and print Spark 4.0.1, AQEfalse, local[2] with the distinct p2/p5 observations.
