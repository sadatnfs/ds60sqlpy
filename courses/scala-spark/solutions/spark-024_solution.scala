import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  def canonicalRows(frame: DataFrame): Seq[(Long,Long,Long,Long)] = {
    frame.collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2),r.getLong(3))).sortBy(_._1)
  }
  def partitionLoads(frame: DataFrame, keys: Seq[String]): Seq[(Int,Long)] = {
    frame.repartition(8,keys.map(col):_*).select(spark_partition_id().as("pid"))
      .groupBy("pid").count().collect().toSeq.map(r => (r.getInt(0),r.getLong(1))).sortBy(_._1)
  }

  def keyFrequencies(facts: DataFrame): Seq[(Long,Long)] = {
    facts.groupBy("key").count().collect().toSeq.map(r => (r.getLong(0),r.getLong(1))).sortBy(_._1)
  }

  def baselineJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts.sparkSession.conf.set("spark.sql.adaptive.enabled","false")
    facts.join(dimension,Seq("key"),"inner").select("fact_id","key","amount","factor")
  }

  def adaptiveJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
    val conf = facts.sparkSession.conf
    conf.set("spark.sql.adaptive.enabled","true")
    conf.set("spark.sql.adaptive.skewJoin.enabled","true")
    conf.set("spark.sql.adaptive.coalescePartitions.enabled","false")
    conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor","2")
    conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes","1024")
    conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes","16384")
    facts.join(dimension,Seq("key"),"inner").select("fact_id","key","amount","factor")
  }

  def saltFacts(facts: DataFrame): DataFrame = {
    facts.withColumn("salt",when(col("key") === 0L,pmod(col("fact_id"),lit(4L))).otherwise(lit(0L)))
  }

  def expandDimension(dimension: DataFrame): DataFrame = {
    dimension.withColumn("salts",when(col("key") === 0L,array(lit(0L),lit(1L),lit(2L),lit(3L))).otherwise(array(lit(0L)))).withColumn("salt",explode(col("salts"))).drop("salts")
  }

  def saltedJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
    facts.join(dimension,Seq("key","salt"),"inner").select("fact_id","key","amount","factor")
  }

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder().appName("ds60-spark-024").master("local[2]")
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
      spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
      spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold","-1")
      spark.conf.set("spark.sql.join.preferSortMergeJoin","true")
      spark.conf.set("spark.sql.shuffle.partitions","4")
      val facts = spark.range(0L,10000L,1L,4).withColumnRenamed("id","fact_id").withColumn("key",when(col("fact_id") < 9000L,0L).otherwise((col("fact_id") - 9000L) % 10L + 1L)).withColumn("amount",lit(1L))
      val dimension = spark.range(0L,11L,1L,2).withColumnRenamed("id","key").withColumn("factor",col("key") + 1L)
      // Exercise 1: Measure the key-frequency imbalance
      val frequency = keyFrequencies(facts)
      assert(frequency == Seq((0L,9000L)) ++ (1L to 10L).map(key => (key,100L)))
      assert(frequency.map(_._2).sum == 10000L && frequency.head._2.toDouble/10000.0 == 0.9)
      // Exercise 2: Establish a baseline join with exact identity conservation
      val baseline = baselineJoin(facts,dimension)
      val baselineRows = canonicalRows(baseline)
      val expected = (0L until 10000L).map { id => val key = if(id < 9000L) 0L else (id-9000L)%10L+1L;(id,key,1L,key+1L) }
      assert(baselineRows == expected && baselineRows.map(_._3).sum == 10000L && baselineRows.map(r => r._3*r._4).sum == 15500L)
      println("baseline_plan=" + baseline.queryExecution.executedPlan.toString)
      // Exercise 3: Observe an adaptive plan before and after execution
      val adaptive = adaptiveJoin(facts,dimension)
      val initialPlan = adaptive.queryExecution.executedPlan.toString
      val adaptiveRows = canonicalRows(adaptive)
      val finalPlan = adaptive.queryExecution.executedPlan.toString
      assert(initialPlan.contains("AdaptiveSparkPlan") && finalPlan.contains("isFinalPlan=true"))
      assert(adaptiveRows == baselineRows)
      println("aqe_initial=" + initialPlan + ";aqe_final=" + finalPlan + ";skew_threshold=1024;advisory=16384")
      // Exercise 4: Split the hot logical key with a deterministic helper
      spark.conf.set("spark.sql.adaptive.enabled","false")
      val saltedFacts = saltFacts(facts)
      assert(saltedFacts.filter(col("key") === 0L).groupBy("salt").count().orderBy("salt").collect().toSeq.map(r => (r.getLong(0),r.getLong(1))) == (0L until 4L).map(salt => (salt,2250L)))
      val unsaltedLoads = partitionLoads(facts,Seq("key"));val saltedLoads = partitionLoads(saltedFacts,Seq("key","salt"))
      assert(unsaltedLoads.map(_._2).sum == 10000L && saltedLoads.map(_._2).sum == 10000L && unsaltedLoads.map(_._2).max >= 9000L)
      println("unsalted_row_loads=" + unsaltedLoads + ";salted_row_loads=" + saltedLoads)
      // Exercise 5: Replicate only the matching small-side hot row
      val expanded = expandDimension(dimension)
      assert(expanded.count() == 14L && expanded.select("key","salt").distinct().count() == 14L)
      assert(expanded.filter(col("key") === 0L).select("salt").orderBy("salt").collect().toSeq.map(_.getLong(0)) == Seq(0L,1L,2L,3L))
      assert(expanded.filter(col("key") =!= 0L && col("salt") =!= 0L).count() == 0L)
      // Exercise 6: Remove the physical helper and reconcile the business relation
      val salted = saltedJoin(saltedFacts,expanded)
      assert(salted.columns.toSeq == Seq("fact_id","key","amount","factor"))
      val saltedRows = canonicalRows(salted)
      assert(saltedRows == baselineRows && saltedRows == adaptiveRows && saltedRows.map(r => r._3*r._4).sum == 15500L)
      println("salted_plan=" + salted.queryExecution.executedPlan.toString)
      println("spark-024: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { () } finally { spark.stop() } }
  }
}

// Exercise 1: Measure the key-frequency imbalance. Inputs/task: Return ordered(key, n) counts for the fact relation. Derive total population and the hot-key fraction from this ledger. Expected: Key 0 has 9000;keys 1..10 each 100. Total 10000 and hot fraction 0.9. Verify: Assert all 11 ledger rows and the exact population/fraction.
// Exercise 2: Establish a baseline join with exact identity conservation. Inputs/task: Build an inner join withAQE disabled and broadcasting thresholds disabled, returning fact_id, key, amount, factor. Materialize the bounded result and compare every tuple with the generation formula. Expected: 10000 unique fact identities, amount total 10000 and weighted total 15500. The baseline plan contains a join and is printed. Verify: Assert all 10000 literal formula tuples and both totals before examining any optimization.
// Exercise 3: Observe an adaptive plan before and after execution. Inputs/task: Build a freshAQE-enabled join with skew handling enabled, coalescing disabled, skew factor 2, threshold 1024 bytes and advisory size 16384 bytes. Capture the initial plan, materialize the same DataFrame and capture the final plan. Expected: Initial/final text identifies AdaptiveSparkPlan;after materialization isFinalPlan=true. Every result tuple matches the baseline. Actual skew splitting is reported only if visible. Verify: Assert adaptive finalization and full row parity;print both plans and the small demonstration thresholds.
// Exercise 4: Split the hot logical key with a deterministic helper. Inputs/task: Add salt=fact_id modulo 4 only for key 0 and salt 0 otherwise. WithAQE disabled, compare eight-partition row-load ledgers by key and by(key, salt). Expected: Hot salt buckets 0..3 each have 2250 rows;cold facts all have salt 0. Both physical ledgers reconcile to 10000, and the unsalted maximum is at least 9000. Verify: Assert all four hot bucket counts and both reconciled ledgers;print actual salted loads without inventing perfect hash balance.
// Exercise 5: Replicate only the matching small-side hot row. Inputs/task: Expand dimension key 0 to salts 0,1,2,3 and every other dimension key to salt 0. Retain factor and verify uniqueness on the composite key. Expected: 14 dimension rows, with four key 0 variants and ten cold rows. Every(key, salt) pair is unique. Verify: Assert row count 14, distinct composite keys 14 and exact hot/cold salt populations.
// Exercise 6: Remove the physical helper and reconcile the business relation. Inputs/task: Join salted facts to the expanded dimension on key and salt, then project only fact_id, key, amount, factor. Compare the complete result with baseline and adaptive variants. Expected: All 10000 fact tuples remain exactly equal, with amount 10000 and weighted total 15500. Salt is absent from the final schema. Verify: Assert exact canonical bag equality and final column names;report the salted plan and row-load evidence separately from any speed claim.
