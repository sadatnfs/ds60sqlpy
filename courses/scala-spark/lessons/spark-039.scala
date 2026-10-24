import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import org.apache.spark.sql.streaming.{StreamingQuery,Trigger}
import scala.collection.mutable.ArrayBuffer

object Main {
  val eventSchema = StructType(Seq(StructField("id",LongType,true),StructField("cents",LongType,true)))
  val ownedQueries = ArrayBuffer.empty[StreamingQuery]
  case class RunReceipt(id: String,runId: String,inputRows: Long,batches: Seq[Long])
  def deleteOwned(root: Path): Unit = {
    require(root.getFileName.toString.startsWith("spark-"))
    require(root.getParent == Paths.get(".").toAbsolutePath.normalize())
    val walk = Files.walk(root)
    try walk.iterator().asScala.toVector.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally walk.close()
  }
  def publishFile(root: Path,input: Path,name: String,lines: Seq[String]): Unit = {
    require(name.matches("batch-[0-9]{2}\\.json"))
    require(lines.size <= 8 && lines.forall(_.length <= 256))
    Files.createDirectories(input)
    val staged = root.resolve("pending-"+UUID.randomUUID().toString+".json")
    try {
      Files.writeString(staged,lines.mkString("\n")+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW)
      Files.move(staged,input.resolve(name),StandardCopyOption.ATOMIC_MOVE)
    } finally Files.deleteIfExists(staged)
  }
  def runParquet(spark: SparkSession,input: Path,checkpoint: Path,output: Path): RunReceipt = {
    val source = spark.readStream.schema(eventSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(input.toString)
    val query = source.writeStream.format("parquet").outputMode("append")
      .option("checkpointLocation",checkpoint.toString).trigger(Trigger.AvailableNow()).start(output.toString)
    ownedQueries += query
    try {
      require(query.awaitTermination(45000L),"Finite query exceeded45-second deadline")
      require(query.exception.isEmpty,"Finite query failed")
      RunReceipt(query.id.toString,query.runId.toString,query.recentProgress.map(_.numInputRows).sum,query.recentProgress.map(_.batchId).toSeq)
    } finally { if(query.isActive) query.stop() }
  }
  def bag(spark: SparkSession,path: Path): Seq[String] = {
    val frame=spark.read.parquet(path.toString)
    require(frame.schema.fields.map(f => (f.name,f.dataType.simpleString)).toSeq == Seq(("id","bigint"),("cents","bigint")))
    require(frame.count() <= 8L,"Tiny result bound exceeded")
    frame.orderBy("id","cents").collect().map(r => s"${r.getLong(0)}:${r.getLong(1)}").toSeq
  }

  case class BudgetReport(rows: Seq[(Long,Long)],partitions: Int,bucketRows: Seq[Long],files: Int,elapsedNanos: Long,metrics: Seq[(String,Map[String,Long])],stages: Seq[(Int,Int,Int,Int)])
  def allMetrics(frame: DataFrame): Seq[(String,Map[String,Long])] = frame.queryExecution.executedPlan.collect { case node => (node.nodeName,node.metrics.map { case (key,value) => key -> value.value }.toMap) }
  def metric(report: BudgetReport,key: String): Option[Long] = {
    val values=report.metrics.flatMap(_._2.get(key))
    if(values.isEmpty) None else Some(values.sum)
  }
  def retainedStages(spark: SparkSession,group: String): Seq[(Int,Int,Int,Int)] = {
    val tracker=spark.sparkContext.statusTracker
    val ids=tracker.getJobIdsForGroup(group).flatMap(id => tracker.getJobInfo(id).toSeq.flatMap(_.stageIds)).distinct.sorted
    ids.flatMap(id => tracker.getStageInfo(id).map(x => (id,x.numTasks,x.numCompletedTasks,x.numFailedTasks))).toSeq
  }
  def measured(spark: SparkSession,source: DataFrame,partitions: Int,root: Path): BudgetReport = {
    require(partitions>=1 && partitions<=8)
    val group="budget-"+partitions+"-"+UUID.randomUUID().toString
    val previous=spark.conf.get("spark.sql.shuffle.partitions")
    spark.conf.set("spark.sql.shuffle.partitions",partitions.toString)
    try {
      val shuffled=source.repartition(partitions,col("key"))
      val grouped=shuffled.groupBy("key").agg(count(lit(1)).as("n"))
      val begin=System.nanoTime()
      spark.sparkContext.setJobGroup(group,"Bounded budget comparison",true)
      val rows=try grouped.collect().toSeq.map(r => (r.getLong(0),r.getLong(1))).sortBy(_._1) finally spark.sparkContext.clearJobGroup()
      val elapsed=System.nanoTime()-begin
      val metrics=allMetrics(grouped);val stages=retainedStages(spark,group)
      val counts=shuffled.select(spark_partition_id().as("partition")).groupBy("partition").count().collect().map(r => r.getInt(0)->r.getLong(1)).toMap
      val bucketRows=(0 until partitions).map(id => counts.getOrElse(id,0L))
      val output=root.resolve("product-"+partitions)
      grouped.write.mode("errorifexists").parquet(output.toString)
      val readback=spark.read.parquet(output.toString).orderBy("key").collect().toSeq.map(r => (r.getLong(0),r.getLong(1)))
      require(readback==rows,"Persisted product differs")
      val listing=Files.list(output)
      val files=try listing.iterator().asScala.count(p => p.getFileName.toString.endsWith(".parquet")) finally listing.close()
      BudgetReport(rows,partitions,bucketRows,files,elapsed,metrics,stages)
    } finally spark.conf.set("spark.sql.shuffle.partitions",previous)
  }

  def fixtureMetrics(source: DataFrame): Seq[Long] =
    throw new UnsupportedOperationException("Complete fixtureMetrics")

  def measureTwo(spark: SparkSession,source: DataFrame,root: Path): BudgetReport =
    throw new UnsupportedOperationException("Complete measureTwo")

  def measureFour(spark: SparkSession,source: DataFrame,root: Path): BudgetReport =
    throw new UnsupportedOperationException("Complete measureFour")

  def imbalance(counts: Seq[Long]): Double =
    throw new UnsupportedOperationException("Complete imbalance")

  def estimatedCost(vcpu: Double,seconds: Double,gib: Double,days: Double): Double =
    throw new UnsupportedOperationException("Complete estimatedCost")

  def withinBudget(rows: Long,partitions: Int): Boolean =
    throw new UnsupportedOperationException("Complete withinBudget")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-039").master("local[2]")
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
      require(spark.version == "4.0.1","Prepared Spark4.0.1 required")
      spark.conf.set("spark.sql.streaming.stopTimeout","5000")
      ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-039-")
      val source=spark.range(0L,20000L,1L,4).withColumn("key",when(col("id")<16000L,lit(0L)).otherwise(col("id")%100L))
      locally {
        val expected=(0L until 100L).map(k => (k,if(k==0L)16040L else 40L))
        assert(expected.size==100 && expected.map(_._2).sum==20000L)
      }
      locally {
        val compute=2.0*(3600.0/3600.0)*0.05
        val storage=2.0*(30.0/30.0)*0.02
        assert(math.abs(compute+storage-0.14)<1e-12)
      }
      println("spark-039: worked examples passed; six task implementations remain")
    } finally { try { ownedQueries.foreach(q => if(q.isActive) q.stop())
require(!ownedQueries.exists(_.isActive),"Do not remove scratch while an owned query is active")
if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Validate the generated skewed fixture. Inputs/task: Require 20000 rows, IDs 0..19999,100 keys and total ID sum 199990000. Explain key 0 occurs 16040 times. Expected: Exact population tuple 20000,20000,100,199990000;key 0 count 16040, other keys 40. Verify: Compare aggregate counts and the independent formula 16000+4000/100.
// Exercise 2: Measure the two-partition configuration. Inputs/task: Execute the bounded grouped query under a unique job group, read actual executed metrics, measure partition row counts and persist/read back the product. Expected: 100 exact key/count pairs, total 20000;nonempty retained stage evidence;one or two data files. Verify: Compare all rows with the literal formula before accepting any work/time report.
// Exercise 3: Compare four partitions without assuming a speedup. Inputs/task: Repeat with 4 partitions and a separate output directory. Expected: All 100 result tuples match the same oracle;four buckets sum 20000 and one to four files are observed. Verify: Assert parity and print actual elapsed time/file/metric values without an ordering claim.
// Exercise 4: Interpret work imbalance and spill honestly. Inputs/task: Compute maximum bucket rows divided by mean bucket rows;report available dataSize, shuffleBytesWritten and spillSize metrics without inventing missing values. Expected: Both observed work ratios exceed 1;unavailable metrics remain None/None-equivalent. Verify: Assert row conservation and positive ratio, then print exact available metric maps and stage receipts.
// Exercise 5: Compute a separate hypothetical cost model. Inputs/task: Use a hypothetical rate 0.05 currency units per vCPU-hour and 0.02 per GiB-month. Evaluate 2 vCPUs for 1 hour plus 2 GiB retained for 30 days under a30-day month. Expected: Estimated 0.14 currency units, not an actual cloud bill or a price recommendation. Verify: Check each unit conversion and reject negative durations/resources.
// Exercise 6: Enforce the stop budget before scaling data. Inputs/task: Accept only row counts 1..20000 and partition counts 1..8 for this local exercise. Reject an attempted larger fixture before constructing it. Expected: 20000/4 accepted;20001/4 and 20000/9 rejected. Verify: Assert both refusals and confirm the session shuffle setting restored to 2.
