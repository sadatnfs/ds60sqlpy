import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  def logicalMetrics(frame: DataFrame): (Long,Long,Long,Long) = {
    val row = frame.agg(count(lit(1)),countDistinct("fact_id"),sum("amount"),sum(col("amount") * col("factor"))).first()
    (row.getLong(0),row.getLong(1),row.getLong(2),row.getLong(3))
  }
  def joinPlan(frame: DataFrame): String = frame.queryExecution.executedPlan.toString

  def estimatedBytes(frame: DataFrame): BigInt =
    throw new UnsupportedOperationException("Complete estimatedBytes")

  def ordinaryJoin(facts: DataFrame, dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete ordinaryJoin")

  def withoutAutomaticBroadcast(facts: DataFrame, dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete withoutAutomaticBroadcast")

  def hintedJoin(facts: DataFrame, dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete hintedJoin")

  def unsupportedHint(facts: DataFrame, dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete unsupportedHint")

  def boundedBroadcast(dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete boundedBroadcast")

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder().appName("ds60-spark-023").master("local[2]")
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
      val facts = spark.range(0L,20000L,1L,4).withColumnRenamed("id","fact_id").withColumn("key",col("fact_id") % 20L).withColumn("amount",col("fact_id") % 7L + 1L)
      val dimension = spark.range(0L,20L,1L,2).withColumnRenamed("id","key").withColumn("factor",col("key") + 1L)
      spark.conf.set("spark.sql.autoBroadcastJoinThreshold","10485760")
      spark.conf.set("spark.sql.join.preferSortMergeJoin","true")
      locally {
        assert(facts.count() == 20000L && dimension.count() == 20L)
        assert(dimension.select("key").distinct().count() == 20L)
        println("Known finite build side:20 unique keys")
      }
      locally {
        val total = (0L until 20000L).map(i => (i%7L+1L)*(i%20L+1L)).sum
        assert(total == 839916L)
        println("Independent weighted-total oracle=" + total)
      }
      println("spark-023: worked examples passed; six task implementations remain")
    } finally { try { () } finally { spark.stop() } }
  }
}

// Exercise 1: Inspect statistics and the automatic threshold separately. Inputs/task: Return the optimized-plan size estimate for dimension as a nonnegative integer, and record the configured automatic broadcast threshold and actual dimension row count. Expected: A positive finite estimate below 10485760 bytes, threshold 10485760 and actual row count 20. The estimate is not a peak-memory measurement. Verify: Assert the finite estimate range and print estimate, threshold, rows andSpark version as separate fields.
// Exercise 2: Observe the automatic plan and verify its relational output. Inputs/task: Build an ordinary inner equality join on key, projecting fact_id, key, amount, factor. Execute logical metrics and record the physical plan chosen with the declared threshold. Expected: Metrics(20000,20000,79997,839916). The observed plan identifies a join strategy and is printed with current threshold. Verify: Assert all metrics and a join operator marker. Report the observed automatic strategy without treating a default as a universal guarantee.
// Exercise 3: Disable automatic broadcasting for a fresh comparison. Inputs/task: Set automatic broadcast threshold to-1, build a fresh ordinary join and record its plan withAQE disabled. Keep the logical result contract. Expected: Same metrics as automatic. No BroadcastHashJoin in this fresh query underAQEfalse and threshold-1. Verify: Assert all four metrics, the disabled setting and observed absence of BroadcastHashJoin.
// Exercise 4: Request an eligible explicit broadcast and reconcile bags. Inputs/task: Apply broadcast to the dimension for an inner equality join while automatic threshold remains-1. Project the same columns and compare duplicate-sensitive output with the ordinary join in both directions. Expected: BroadcastHashJoin and BroadcastExchange appear. Both exceptAll differences are empty and logical metrics remain exact. Verify: Assert the two operator markers, all metrics and both bag differences.
// Exercise 5: Observe an unsupported hint without changing the business result. Inputs/task: Request a broadcast dimension in a full outer equality join and inspect the chosen plan. Explain why this fixture still has the same output rows as the inner join. Expected: No BroadcastHashJoin for this unsupported full-outer hash strategy. Metrics remain(20000,20000,79997,839916) because both key domains are fully covered. Verify: Assert the observed absence of BroadcastHashJoin and exact output metrics;report a hint warning if emitted rather than hiding it.
// Exercise 6: Gate a broadcast candidate on explicit bounded evidence. Inputs/task: Reject streaming inputs, more than 100 rows, missing/duplicate keys, or an estimated size outside(0,1MiB]. Return the bounded dimension with a broadcast hint only after those checks. Expected: The 20-row dimension passes;the same dimension with a duplicate key and a101-row candidate fail. No unbounded input is collected or materialized by the gate. Verify: Assert accepted logical join metrics and explicit rejection for duplicate and row-budget cases.
