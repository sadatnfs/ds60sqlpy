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

  def classifyFacts(raw: DataFrame): DataFrame = {
    raw.withColumn(
      "reason",
      when(col("fact_id").isNull, "missing_identity")
        .when(col("amount") < 0L, "negative_amount")
        .otherwise("accepted")
    )
  }

  def reviewDimension(raw: DataFrame): DataFrame = {
    val reviewed = raw.filter(col("approved")).select("key", "factor")
    val rows = reviewed.limit(101).count()
    require(
      rows <= 100L && reviewed.agg(countDistinct("key")).first().getLong(0) == rows,
      "Approved keys must be known,unique and bounded"
    )
    reviewed
  }

  def baselineProduct(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts
      .join(dimension, Seq("key"), "inner")
      .select("source_id", "fact_id", "key", "amount", "factor")
  }

  def broadcastProduct(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts
      .join(broadcast(dimension), Seq("key"), "inner")
      .select("source_id", "fact_id", "key", "amount", "factor")
  }

  def configurationReceipt(spark: SparkSession): Map[String, String] = {
    Map(
      "version" -> spark.version,
      "master" -> spark.sparkContext.master,
      "aqe" -> spark.conf.get("spark.sql.adaptive.enabled"),
      "automatic_broadcast" -> spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
    )
  }

  def chooseProduct(facts: DataFrame, dimension: DataFrame, useBroadcast: Boolean): DataFrame = {
    if (useBroadcast) broadcastProduct(facts, dimension) else baselineProduct(facts, dimension)
  }

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
      // Exercise 1: Classify facts and reconcile the whole source population
      val classified = classifyFacts(rawFacts)
      val accepted = classified.filter(col("reason") === "accepted").drop("reason")
      val rejected = classified.filter(col("reason") =!= "accepted")
      assert(
        rejected
          .select("source_id", "reason")
          .orderBy("source_id")
          .collect()
          .toSeq
          .map(r => (r.getLong(0), r.getString(1))) == Seq(
          (2001L, "missing_identity"),
          (2002L, "negative_amount")
        )
      )
      assert(accepted.count() == 2000L && rejected.count() == 2L && classified.count() == 2002L)
      val acceptedCounts = accepted.agg(countDistinct("fact_id"), count("amount")).first()
      assert((acceptedCounts.getLong(0), acceptedCounts.getLong(1)) == (2000L, 1800L))
      // Exercise 2: Select an approved unique dimension before tuning
      val reviewed = reviewDimension(rawDimension)
      assert(
        reviewed.orderBy("key").collect().toSeq.map(r => (r.getLong(0), r.getLong(1))) == (0L to 5L)
          .map(k => (k, k + 2L))
      )
      var conflictRejected = false
      try
        reviewDimension(
          rawDimension.unionByName(rawDimension.filter(col("key") === 0L && col("approved")))
        )
      catch { case _: IllegalArgumentException => conflictRejected = true }
      assert(conflictRejected)
      // Exercise 3: Produce the correct baseline and independent key summary
      val baseline = baselineProduct(accepted, reviewed)
      val baselineObservation = observe(baseline)
      assert(baselineObservation.values == expectedMetrics)
      val keySummary = baseline
        .groupBy("key")
        .agg(count(lit(1)), count("amount"), sum("amount"), sum(col("amount") * col("factor")))
        .orderBy("key")
        .collect()
        .toSeq
        .map(r => (r.getLong(0), r.getLong(1), r.getLong(2), r.getLong(3), r.getLong(4)))
      assert(
        keySummary == Seq(
          (0L, 1600L, 1440L, 5755L, 11510L),
          (1L, 100L, 100L, 401L, 1203L),
          (2L, 100L, 80L, 321L, 1284L),
          (3L, 100L, 100L, 398L, 1990L),
          (4L, 100L, 80L, 321L, 1926L)
        )
      )
      // Exercise 4: Compare a bounded broadcast strategy with the same business contract
      val candidate = broadcastProduct(accepted, reviewed)
      val candidateObservation = observe(candidate)
      assert(candidateObservation.values == expectedMetrics && sameBag(candidate, baseline))
      assert(candidate.queryExecution.executedPlan.toString.contains("BroadcastHashJoin"))
      // Exercise 5: Assemble an honest bounded comparison receipt
      val configuration = configurationReceipt(spark)
      assert(
        configuration == Map(
          "version" -> "4.0.1",
          "master" -> "local[2]",
          "aqe" -> "false",
          "automatic_broadcast" -> "-1"
        )
      )
      val frequencies = accepted
        .groupBy("key")
        .count()
        .orderBy("key")
        .collect()
        .toSeq
        .map(r => (r.getLong(0), r.getLong(1)))
      assert(frequencies == Seq((0L, 1600L), (1L, 100L), (2L, 100L), (3L, 100L), (4L, 100L)))
      assert(baselineObservation.exchanges.nonEmpty && candidateObservation.exchanges.nonEmpty)
      println(
        "configuration=" + configuration + ";key_frequencies=" + frequencies + ";baseline_metrics=" + baselineObservation.exchanges + ";candidate_metrics=" + candidateObservation.exchanges
      )
      println(
        "baseline_plan=" + baseline.queryExecution.executedPlan.toString + ";candidate_plan=" + candidate.queryExecution.executedPlan.toString
      )
      // Exercise 6: Roll back execution policy without rolling back data quality
      val rolledBack = chooseProduct(accepted, reviewed, false)
      assert(observe(rolledBack).values == expectedMetrics && sameBag(rolledBack, candidate))
      assert(!rolledBack.queryExecution.executedPlan.toString.contains("BroadcastHashJoin"))
      assert(sameBag(chooseProduct(accepted, reviewed, true), baseline))
      println(
        "spark-028: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString
      )
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
