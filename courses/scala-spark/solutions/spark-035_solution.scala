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

  def validatedBag(frame: DataFrame): Seq[String] = {
    require(frame.schema.fields.map(f => (f.name,f.dataType.simpleString)).toSeq == Seq(("id","bigint"),("cents","bigint")))
    require(frame.count() <= 8L && frame.filter(col("id").isNull || col("cents").isNull || col("id") <= 0L || col("cents") < 0L).count() == 0L)
    frame.orderBy("id","cents").collect().map(r => s"${r.getLong(0)}:${r.getLong(1)}").toSeq
  }

  def firstRun(spark: SparkSession,input: Path,checkpoint: Path,output: Path): RunReceipt = {
    runParquet(spark,input,checkpoint,output)
  }

  def resumeNewFile(spark: SparkSession,root: Path,input: Path,checkpoint: Path,output: Path): RunReceipt = {
    publishFile(root,input,"batch-02.json",Seq("""{"id":2,"cents":200}""","""{"id":3,"cents":300}"""))
    runParquet(spark,input,checkpoint,output)
  }

  def resumeEmpty(spark: SparkSession,input: Path,checkpoint: Path,output: Path): RunReceipt = {
    runParquet(spark,input,checkpoint,output)
  }

  def separateReplay(spark: SparkSession,input: Path,checkpoint: Path,output: Path,oldCheckpoint: Path,oldOutput: Path): RunReceipt = {
    require(checkpoint!=oldCheckpoint && output!=oldOutput && !Files.exists(checkpoint) && !Files.exists(output))
    runParquet(spark,input,checkpoint,output)
  }

  def guaranteeLedger(frame: DataFrame): Seq[Long] = {
    validatedBag(frame)
    val r=frame.agg(count(lit(1)),countDistinct("id"),sum("cents")).first()
    Seq(r.getLong(0),r.getLong(1),r.getLong(2))
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-035").master("local[2]")
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
      ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-035-")
      val input=ownedRoot.resolve("input");val checkpoint=ownedRoot.resolve("checkpoint");val output=ownedRoot.resolve("output")
      publishFile(ownedRoot,input,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
      // Exercise 1: Validate the finite input and output grain
      val initial=spark.read.schema(eventSchema).json(input.toString)
      assert(validatedBag(initial)==Seq("1:100","2:200"))
      var nullRejected=false
      try validatedBag(initial.withColumn("id",lit(null).cast("long"))) catch { case _: IllegalArgumentException => nullRejected=true }
      assert(nullRejected)
      // Exercise 2: Run the first finite file stream
      val first=firstRun(spark,input,checkpoint,output)
      assert(first.inputRows==2L && first.batches.nonEmpty)
      assert(bag(spark,output)==Seq("1:100","2:200"))
      assert(!ownedQueries.last.isActive)
      // Exercise 3: Resume the same checkpoint after a new file
      val second=resumeNewFile(spark,ownedRoot,input,checkpoint,output)
      assert(second.id==first.id && second.runId!=first.runId && second.inputRows==2L)
      assert(bag(spark,output)==Seq("1:100","2:200","2:200","3:300"))
      // Exercise 4: Resume with no new source files
      val before=bag(spark,output)
      val empty=resumeEmpty(spark,input,checkpoint,output)
      assert(empty.id==first.id && empty.inputRows==0L && bag(spark,output)==before)
      // Exercise 5: Replay with a separate checkpoint and output
      val replay=separateReplay(spark,input,ownedRoot.resolve("replay-checkpoint"),ownedRoot.resolve("replay-output"),checkpoint,output)
      assert(replay.id!=first.id && replay.inputRows==4L)
      assert(bag(spark,ownedRoot.resolve("replay-output"))==before && bag(spark,output)==before)
      assert(Files.isDirectory(checkpoint))
      // Exercise 6: Write a guarantee ledger from exact counts
      assert(guaranteeLedger(spark.read.parquet(output.toString))==Seq(4L,3L,800L))
      println("spark-035: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { ownedQueries.foreach(q => if(q.isActive) q.stop())
require(!ownedQueries.exists(_.isActive),"Do not remove scratch while an owned query is active")
if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Validate the finite input and output grain. Inputs/task: Read a static copy of the two-row schema fixture and require bigint id/cents, known nonnull values and at most 8 rows. Return its canonical ordered bag without removing duplicates. Expected: The first bag is 1:100,2:200. A NULL identity or cents value is rejected. Verify: Compare the exact two-row bag and reject an explicit null-id DataFrame.
// Exercise 2: Run the first finite file stream. Inputs/task: Execute the AvailableNow Parquet query with its owned checkpoint/output and retain query ID, run ID, input count and batch IDs. Expected: Two input rows and exactly 1:100,2:200 in the committed sink. Verify: Assert the progress input count is 2, query is terminated, and readback bag is exact.
// Exercise 3: Resume the same checkpoint after a new file. Inputs/task: Publish a second file with 2:200 and 3:300, then restart the compatible query with the same checkpoint and sink. Expected: Only 2 new input rows are processed. The sink bag is 1:100,2:200,2:200,3:300. Query ID persists and run ID changes. Verify: Compare both identities, progress count and all 4 output occurrences.
// Exercise 4: Resume with no new source files. Inputs/task: Run the same compatible query again without adding input and compare output before/after. Expected: Zero new input rows and an unchanged 4-row output bag. Verify: Assert zero progress input sum and exact unchanged sink rows.
// Exercise 5: Replay with a separate checkpoint and output. Inputs/task: Start from a new checkpoint only when the output namespace is also new. Replay the same source and preserve the old checkpoint/sink. Expected: The separate output has 4 rows, with a new logical query ID. The old output remains 4 rows. Verify: Assert checkpoint/output paths differ and both independent bags equal the literal 4-row oracle.
// Exercise 6: Write a guarantee ledger from exact counts. Inputs/task: Return output row count, distinct business IDs and total cents, then explain why source recovery is not business-ID deduplication or a universal exactly-once guarantee. Expected: 4 occurrences,3 distinct IDs, total 800. Verify: Compare all three independent values and preserve the duplicate occurrence.
