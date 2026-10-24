import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  case class Observation(values: Map[String, Long], exchanges: Seq[(String, Map[String, Long])])
  def observe(frame: DataFrame): Observation = {
    val summary = frame.agg(
      count(lit(1)),
      countDistinct("fact_id"),
      count("amount"),
      sum("amount"),
      sum(col("amount") * col("factor"))
    )
    val row = summary.collect().head
    val names = Seq("rows", "unique_facts", "known_amounts", "amount_total", "weighted_total")
    val values = names.zipWithIndex.map { case (name, index) => name -> row.getLong(index) }.toMap
    val exchanges = summary.queryExecution.executedPlan.collect {
      case node if node.nodeName.contains("Exchange") =>
        (node.nodeName, node.metrics.map { case (name, metric) => name -> metric.value }.toMap)
    }
    Observation(values, exchanges)
  }
  def sameBag(left: DataFrame, right: DataFrame): Boolean =
    left.exceptAll(right).count() == 0L && right.exceptAll(left).count() == 0L

  def classifyFacts(raw: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete classifyFacts")

  def reviewDimension(raw: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete reviewDimension")

  def baselineProduct(facts: DataFrame, dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete baselineProduct")

  def broadcastProduct(facts: DataFrame, dimension: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete broadcastProduct")

  def configurationReceipt(spark: SparkSession): Map[String, String] =
    throw new UnsupportedOperationException("Complete configurationReceipt")

  def chooseProduct(facts: DataFrame, dimension: DataFrame, useBroadcast: Boolean): DataFrame =
    throw new UnsupportedOperationException("Complete chooseProduct")

  def main(args: Array[String]): Unit = {

    val spark = SparkSession
      .builder()
      .appName("ds60-spark-028")
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
      spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
      val factSchema = StructType(
        Seq(
          StructField("source_id", LongType, false),
          StructField("fact_id", LongType, true),
          StructField("key", LongType, false),
          StructField("amount", LongType, true)
        )
      )
      val generated = (1L to 2000L).map { id =>
        Row(
          id,
          id,
          if (id <= 1600L) 0L else (id - 1601L) % 4L + 1L,
          if (id % 10L == 0L) null else java.lang.Long.valueOf(id % 7L + 1L)
        )
      }
      val rawFacts = spark.createDataFrame(
        spark.sparkContext
          .parallelize(generated ++ Seq(Row(2001L, null, 0L, 10L), Row(2002L, 2001L, 99L, -3L)), 4),
        factSchema
      )
      val dimSchema = StructType(
        Seq(
          StructField("key", LongType, false),
          StructField("factor", LongType, false),
          StructField("approved", BooleanType, false)
        )
      )
      val rawDimension = spark.createDataFrame(
        spark.sparkContext.parallelize(
          Seq(Row(0L, 1L, false), Row(0L, 2L, true)) ++ (1L to 5L).map(k => Row(k, k + 2L, true)),
          2
        ),
        dimSchema
      )
      val expectedMetrics = Map(
        "rows" -> 2000L,
        "unique_facts" -> 2000L,
        "known_amounts" -> 1800L,
        "amount_total" -> 7196L,
        "weighted_total" -> 17913L
      )
      locally {
        val predictedRawJoinRows = 1600L * 2L + 400L
        assert(predictedRawJoinRows == 3600L)
        println("Raw dimension multiplicity predicts3600 pairs for2000 accepted facts")
      }
      locally {
        val known = (1L to 2000L).filter(_ % 10L != 0L)
        val amountTotal = known.map(_ % 7L + 1L).sum
        val weighted = known.map { i =>
          val key = if (i <= 1600L) 0L else (i - 1601L) % 4L + 1L; (i % 7L + 1L) * (key + 2L)
        }.sum
        assert(known.size == 1800 && amountTotal == 7196L && weighted == 17913L)
        println("Independent formula totals=" + amountTotal + "," + weighted)
      }
      println("spark-028: worked examples passed; six task implementations remain")
    } finally {
      try { () }
      finally { spark.stop() }
    }
  }
}

// Exercise 1: Classify facts and reconcile the whole source population. Inputs/task: Add reason using missing fact identity, negative known amount, then accepted precedence. Retain all source records;acceptedNULL amounts remain unknown. Expected: Accepted 2000, rejected 2 with source 2001 missing_identity and 2002 negative_amount. Accepted unique fact IDs 2000 and known amounts 1800. Verify: Assert every rejection identity/reason, source reconciliation and accepted uniqueness/completeness counts.
// Exercise 2: Select an approved unique dimension before tuning. Inputs/task: Keep approved dimension rows, require at most 100 rows and known unique keys, then return key, factor. Reject a candidate with a second approved key 0 row. Expected: Reviewed keys 0..5, factors 2..7, six rows. The conflicting approved candidate fails before joining. Verify: Assert all six key/factor rows and the explicit duplicate-approved rejection.
// Exercise 3: Produce the correct baseline and independent key summary. Inputs/task: Build the ordinary equality join over accepted facts and reviewed dimension, projecting source_id, fact_id, key, amount, factor. Summarize per key with rows, known amounts, total amount and weighted total. Expected: Key 0:(1600,1440,5755,11510);1:(100,100,401,1203);2:(100,80,321,1284);3:(100,100,398,1990);4:(100,80,321,1926). Verify: Assert all five summary tuples and aggregate metrics 2000,2000,1800,7196,17913.
// Exercise 4: Compare a bounded broadcast strategy with the same business contract. Inputs/task: Broadcast the reviewed dimension for the same equality join and projection. Preserve all output occurrences using exceptAll in both directions against baseline. Expected: Identical metrics and empty directional bag differences. The candidate plan containsBroadcastHashJoin. Verify: Assert the full metric map, both distributed bag differences and the observed strategy marker.
// Exercise 5: Assemble an honest bounded comparison receipt. Inputs/task: Return version, master, AQE and automatic broadcast threshold as named fields. Attach key frequencies, the baseline/candidate plans and each observed summary-query exchange metric map. Expected: Spark 4.0.1, local[2], AQEfalse, threshold-1;key 0 frequency 1600 and others 100. Both runs expose actual nonempty exchange observations. No peak-memory or throughput value is invented. Verify: Assert controlled settings and frequency ledger, then print plans and separately labeled actual metric maps.
// Exercise 6: Roll back execution policy without rolling back data quality. Inputs/task: Choose baseline or broadcast using an explicit Boolean switch over the same accepted facts and reviewed dimension. Switch back to baseline and revalidate the complete product. Expected: Both switch positions satisfy the same metric map and bag contract. The disabled position has noBroadcastHashJoin under the controlled configuration. Verify: Assert golden metrics and bag equality after rollback, and inspect the restored baseline plan.
