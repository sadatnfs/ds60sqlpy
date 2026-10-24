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

  val testSchema=StructType(Seq(StructField("id",LongType,true),StructField("event_second",LongType,true),StructField("cents",LongType,true)))
  def runScenario(spark: SparkSession,input: Path,checkpoint: Path,output: Path,mode: String): RunReceipt = {
    require(Set("restart","duplicates","late","invalid").contains(mode))
    val raw=spark.readStream.schema(testSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(input.toString)
    val selected=mode match {
      case "duplicates" => raw.select("id","cents").dropDuplicates("id")
      case "late" => raw.filter(col("event_second") >= 90L).select("id","cents")
      case "invalid" => raw.filter(col("id").isNotNull && col("event_second").isNotNull && col("cents").isNotNull && col("id") > 0L && col("cents") >= 0L).select("id","cents")
      case _ => raw.select("id","cents")
    }
    val query=selected.writeStream.format("parquet").outputMode("append").option("checkpointLocation",checkpoint.toString).trigger(Trigger.AvailableNow()).start(output.toString)
    ownedQueries += query
    try {
      require(query.awaitTermination(45000L),"Scenario deadline exceeded")
      require(query.exception.isEmpty)
      RunReceipt(query.id.toString,query.runId.toString,query.recentProgress.map(_.numInputRows).sum,query.recentProgress.map(_.batchId).toSeq)
    } finally { if(query.isActive) query.stop() }
  }
  def prepareCase(root: Path,name: String,lines: Seq[String]): (Path,Path,Path) = {
    require(Set("restart","duplicates","late","invalid","demo").contains(name))
    val input=root.resolve(name+"-input")
    publishFile(root,input,"batch-01.json",lines)
    (input,root.resolve(name+"-checkpoint"),root.resolve(name+"-output"))
  }

  def baseline(spark: SparkSession,paths: (Path,Path,Path)): RunReceipt = {
    runScenario(spark,paths._1,paths._2,paths._3,"restart")
  }

  def restartEmpty(spark: SparkSession,paths: (Path,Path,Path)): RunReceipt = {
    runScenario(spark,paths._1,paths._2,paths._3,"restart")
  }

  def duplicateCase(spark: SparkSession,paths: (Path,Path,Path)): RunReceipt = {
    runScenario(spark,paths._1,paths._2,paths._3,"duplicates")
  }

  def lateCase(spark: SparkSession,paths: (Path,Path,Path)): RunReceipt = {
    runScenario(spark,paths._1,paths._2,paths._3,"late")
  }

  def invalidCase(spark: SparkSession,paths: (Path,Path,Path)): RunReceipt = {
    runScenario(spark,paths._1,paths._2,paths._3,"invalid")
  }

  def requireBag(actual: Seq[String],expected: Seq[String]): Unit = {
    require(actual==expected,"Canonical bag mismatch")
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-037").master("local[2]")
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
      ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-037-")
      val restartPaths=prepareCase(ownedRoot,"restart",Seq("""{"id":1,"event_second":100,"cents":100}""","""{"id":2,"event_second":110,"cents":200}"""))
      val duplicatePaths=prepareCase(ownedRoot,"duplicates",Seq("""{"id":1,"event_second":100,"cents":100}""","""{"id":1,"event_second":100,"cents":100}"""))
      val latePaths=prepareCase(ownedRoot,"late",Seq("""{"id":1,"event_second":80,"cents":100}""","""{"id":2,"event_second":90,"cents":200}""","""{"id":3,"event_second":110,"cents":300}"""))
      val invalidPaths=prepareCase(ownedRoot,"invalid",Seq("""{"id":null,"event_second":100,"cents":100}""","""{"id":2,"event_second":100,"cents":-1}""","""{"id":3,"event_second":100,"cents":300}"""))
      // Exercise 1: Establish a finite restart baseline
      val first=baseline(spark,restartPaths)
      assert(first.inputRows==2L && bag(spark,restartPaths._3)==Seq("1:100","2:200") && !ownedQueries.last.isActive)
      // Exercise 2: Prove no-input recovery without a sleep
      val again=restartEmpty(spark,restartPaths)
      assert(again.id==first.id && again.runId!=first.runId && again.inputRows==0L)
      assert(bag(spark,restartPaths._3)==Seq("1:100","2:200"))
      // Exercise 3: Test real streaming duplicate suppression
      val duplicate=duplicateCase(spark,duplicatePaths)
      assert(duplicate.inputRows==2L && bag(spark,duplicatePaths._3)==Seq("1:100"))
      // Exercise 4: Test the exact event-time boundary
      val late=lateCase(spark,latePaths)
      val lateRawRows=spark.read.schema(testSchema).json(latePaths._1.toString).count()
      val lateRows=bag(spark,latePaths._3)
      println("late_raw_rows="+lateRawRows+";progress_input_rows="+late.inputRows+";committed="+lateRows+";json_pushdown="+spark.conf.get("spark.sql.json.filterPushdown.enabled"))
      assert(lateRawRows==3L && lateRows==Seq("2:200","3:300") && late.inputRows>=lateRows.size && late.inputRows<=lateRawRows)
      // Exercise 5: Keep invalid rows visible in the case ledger
      val invalid=invalidCase(spark,invalidPaths)
      val invalidRows=bag(spark,invalidPaths._3)
      val rawCount=spark.read.schema(testSchema).json(invalidPaths._1.toString).count()
      println("invalid_raw_rows="+rawCount+";progress_input_rows="+invalid.inputRows+";committed="+invalidRows)
      assert(rawCount==3L && invalidRows==Seq("3:300") && invalid.inputRows>=invalidRows.size && invalid.inputRows<=rawCount)
      val invalidRaw=spark.read.schema(testSchema).json(invalidPaths._1.toString)
      assert(invalidRaw.filter(col("id").isNull || col("cents") < 0L).count()==2L)
      // Exercise 6: Prove the oracle rejects a plausible regression
      requireBag(bag(spark,duplicatePaths._3),Seq("1:100"))
      var mutationRejected=false
      try requireBag(Seq("1:100","1:100"),Seq("1:100")) catch { case e: IllegalArgumentException if e.getMessage.contains("Canonical bag mismatch") => mutationRejected=true }
      assert(mutationRejected && ownedQueries.forall(q => !q.isActive))
      println("spark-037: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { ownedQueries.foreach(q => if(q.isActive) q.stop())
require(!ownedQueries.exists(_.isActive),"Do not remove scratch while an owned query is active")
if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Establish a finite restart baseline. Inputs/task: Run the restart scenario with two supplied records and retain progress plus exact sink values. Expected: 2 input rows and bag 1:100,2:200. Verify: Assert the literal bag, input count 2 and inactive query.
// Exercise 2: Prove no-input recovery without a sleep. Inputs/task: Restart the compatible baseline with its existing checkpoint and no new file. Expected: Same query ID, new run ID, zero new rows and unchanged sink. Verify: Compare identities, input sum and exact bag;allow empty progress entries.
// Exercise 3: Test real streaming duplicate suppression. Inputs/task: Use native streaming dropDuplicates on the id key for two identical occurrences of 1:100. Expected: 2 source rows,1 committed row 1:100. Verify: Compare input count 2 and the one-row bag.
// Exercise 4: Test the exact event-time boundary. Inputs/task: Apply the explicitly declared admission cutoff event_second>=90 to rows at 80,90 and 110. Expected: 3 source rows;accepted IDs 2,3 with cents 200,300. Verify: Compare exact two-row bag and explain why 90 is retained.
// Exercise 5: Keep invalid rows visible in the case ledger. Inputs/task: Reject a NULL identity and a negative amount while retaining valid 3:300. Expected: 3 input occurrences,2 invalid,1 accepted. Verify: Compare raw source count 3, actual progress, sink bag 3:300 and static predicate count 2.
// Exercise 6: Prove the oracle rejects a plausible regression. Inputs/task: Compare the correct duplicate-case bag with an unsafe two-copy append result and reject the mismatch. Confirm every owned query is inactive before cleanup. Expected: Correct bag passes;duplicated bag raises an assertion-contract error;all owned queries are inactive. Verify: Catch the specific mismatch and compare the exact offending rows.
