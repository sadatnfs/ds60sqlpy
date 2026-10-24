import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {


  def canonical(frame: DataFrame): Seq[(Long,Long,Long)] = {
    frame.select("id","key","value").orderBy("id").collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2)))
  }

  def keyedLayout(facts: DataFrame): DataFrame = {
    facts.repartition(6,col("key"))
  }

  def reduceLayout(frame: DataFrame): DataFrame = {
    frame.coalesce(2)
  }

  def partitionLedger(frame: DataFrame): DataFrame = {
    frame.select(col("id"),spark_partition_id().as("partition_id")).groupBy("partition_id").agg(count(lit(1)).as("row_count"),sum("id").as("id_total"))
  }

  def localOrder(frame: DataFrame): DataFrame = {
    frame.sortWithinPartitions(col("key"),col("id"))
  }

  def preview(frame: DataFrame): Seq[(Long,Long,Long)] = {
    frame.orderBy(col("key").desc,col("id").asc).limit(5).select("id","key","value").collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2)))
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-020").master("local[2]")
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
      val facts = spark.range(0L,24L,1L,4).withColumn("key",col("id") % 4L).withColumn("value",col("id") * 10L)
      assert(spark.conf.get("spark.sql.adaptive.enabled") == "false")
      // Exercise 1: Establish logical content independently of layout
      val expected = (0L until 24L).map(id => (id,id%4L,id*10L))
      assert(canonical(facts) == expected)
      val metrics = facts.agg(count(lit(1)),countDistinct("id"),sum("id"),sum("value")).first()
      assert((0 until 4).map(metrics.getLong) == Seq(24L,24L,276L,2760L))
      // Exercise 2: Request keyed redistribution and test colocation
      val keyed = keyedLayout(facts)
      assert(keyed.rdd.getNumPartitions == 6 && canonical(keyed) == expected)
      val colocated = keyed.withColumn("partition_id",spark_partition_id()).groupBy("key").agg(countDistinct("partition_id").as("partitions")).orderBy("key").collect()
      assert(colocated.length == 4 && colocated.forall(_.getLong(1) == 1L))
      // Exercise 3: Reduce partitions without assuming balanced redistribution
      val reduced = reduceLayout(keyed)
      assert(reduced.rdd.getNumPartitions == 2 && canonical(reduced) == expected)
      val notIncreased = facts.coalesce(10)
      assert(notIncreased.rdd.getNumPartitions == 4 && canonical(notIncreased) == expected)
      // Exercise 4: Reconcile an occupied-partition ledger
      for(frame <- Seq(keyed,reduced)) {
       val total = frame.rdd.getNumPartitions
       val ledger = partitionLedger(frame).collect().toSeq
       assert(ledger.map(_.getLong(1)).sum == 24L && ledger.map(_.getLong(2)).sum == 276L)
       assert(ledger.size <= total && ledger.forall(r => r.getInt(0) >= 0 && r.getInt(0) < total))
       println("partition_count=" + total + ";occupied=" + ledger.size + ";ledger=" + ledger.mkString(","))
      }
      // Exercise 5: Verify ordering only within its promised scope
      val locallySorted = localOrder(facts.repartition(6))
      val observed = locallySorted.select(spark_partition_id().as("pid"),col("key"),col("id")).collect().toSeq
      for((_,partitionRows) <- observed.groupBy(_.getInt(0))) {
       val pairs = partitionRows.map(r => (r.getLong(1),r.getLong(2)))
       assert(pairs == pairs.sorted)
      }
      assert(canonical(locallySorted) == expected)
      // Exercise 6: Create a globally ordered bounded preview
      val expectedPreview = Seq(3L,7L,11L,15L,19L).map(id => (id,3L,id*10L))
      for(frame <- Seq(facts,keyed,reduced)) assert(preview(frame) == expectedPreview)
      println("spark-020: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Establish logical content independently of layout. Inputs/task: Return the ordered list of(id, key, value) tuples for the declared 24-row fixture. Compare its full bag with the literal arithmetic rule and compute count, distinct IDs, sum(id), sum(value). Expected: IDs 0..23 appear once, key=id%4, value=10*id. Metrics are 24,24,276,2760. Verify: Assert every canonical tuple and all four aggregate values.
// Exercise 2: Request keyed redistribution and test colocation. Inputs/task: Return facts repartitioned to 6 partitions by key. Record its partition count and check that each logical key is observed in exactly one execution partition. Expected: Six partitions requested;all 24 rows unchanged. Each of four keys has one observed partition ID;different keys may share one. Verify: Assert partition metadata 6, canonical equality and per-key countDistinct(partition_id)=1.
// Exercise 3: Reduce partitions without assuming balanced redistribution. Inputs/task: Coalesce a six-partition input to 2 and return it. Separately request coalesce 10 on the original four-partition relation. Preserve canonical content in both cases. Expected: The first has 2 partitions;the attempted increase remains 4. Both retain the 24-row bag and sum 2760. Verify: Assert both partition counts and complete canonical equality.
// Exercise 4: Reconcile an occupied-partition ledger. Inputs/task: Return partition_id, row_count, id_total for occupied partitions of the supplied relation. Record total partition metadata separately and do not manufacture empty-partition rows. Expected: Ledger row_count sums 24 and id_total sums 276;each recorded partition ID lies in[0, total_partitions). Occupied count may be lower than total. Verify: Assert reconciliation and partition-ID bounds for both keyed 6 and coalesced 2 layouts.
// Exercise 5: Verify ordering only within its promised scope. Inputs/task: Return a relation sorted within each partition by key ascending, id ascending. Inspect the sequence of(key, id) pairs within each recorded partition and preserve the logical bag. Expected: Every occupied partition sequence is sorted;the complete canonical relation is unchanged. No raw global collect sequence is required. Verify: Assert per-partition sorted sequences and canonical equality without asserting that raw concatenation must be sorted or unsorted.
// Exercise 6: Create a globally ordered bounded preview. Inputs/task: Order key descending then event identity id ascending and return the first 5 rows. Repeat after several input layouts. Expected: IDs[3,7,11,15,19], allkey 3 and values[30,70,110,150,190]. The final sixthkey 3 row is outside the limit. Verify: Assert all five ordered tuples from original, keyed and coalesced inputs.
