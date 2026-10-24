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

  val attempts = ArrayBuffer.empty[Long]
  val startedQueries = ArrayBuffer.empty[(String,String)]
  val mapper = new com.fasterxml.jackson.databind.ObjectMapper()
  def canonicalBatch(frame: DataFrame): String = {
    require(frame.schema.fields.map(f => (f.name,f.dataType.simpleString)).toSeq == Seq(("id","bigint"),("cents","bigint")))
    require(frame.count() <= 8L,"At most8 rows per teaching microbatch")
    require(frame.filter(col("id").isNull || col("cents").isNull || col("id") <= 0L || col("cents") < 0L).count() == 0L)
    frame.orderBy("id","cents").collect().map(r => s"${r.getLong(0)},${r.getLong(1)}\n").mkString
  }
  def sha(text: String): String = java.security.MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)).map(b => f"${b & 255}%02x").mkString
  def commitPath(root: Path,identity: String,batchId: Long): Path = {
    require(identity.matches("[a-z][a-z0-9-]{0,31}") && batchId >= 0L && batchId <= 1000L)
    root.resolve(identity).resolve(f"batch-$batchId%020d.json")
  }
  def publishBatch(root: Path,identity: String,batchId: Long,text: String,failBefore: Boolean): Boolean = {
    val target=commitPath(root,identity,batchId)
    Files.createDirectories(target.getParent)
    val node=mapper.createObjectNode();node.put("query_identity",identity);node.put("batch_id",batchId)
    node.put("sha256",sha(text));node.put("data",text)
    val bytes=mapper.writeValueAsString(node)
    if(Files.exists(target)) {
      val existing=mapper.readTree(Files.readString(target,StandardCharsets.UTF_8))
      val same=existing.isObject && existing.fieldNames().asScala.toSet==Set("query_identity","batch_id","sha256","data") &&
        existing.path("query_identity").isTextual && existing.path("query_identity").asText()==identity &&
        existing.path("batch_id").isIntegralNumber && existing.path("batch_id").longValue()==batchId &&
        existing.path("sha256").isTextual && existing.path("sha256").asText()==sha(text) &&
        existing.path("data").isTextual && existing.path("data").asText()==text
      require(same,"Batch key reused for different content")
      false
    } else {
      val staged=target.getParent.resolve("pending-"+UUID.randomUUID().toString+".json")
      try {
        Files.writeString(staged,bytes,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW)
        if(failBefore) throw new IllegalStateException("injected_before_publication")
        Files.move(staged,target,StandardCopyOption.ATOMIC_MOVE)
        true
      } finally Files.deleteIfExists(staged)
    }
  }
  def publishedRows(root: Path,identity: String): Seq[String] = {
    require(identity.matches("[a-z][a-z0-9-]{0,31}"))
    val directory=root.resolve(identity)
    if(!Files.exists(directory)) Seq.empty
    else {
      val stream=Files.list(directory)
      val files=try stream.iterator().asScala.filter(_.getFileName.toString.startsWith("batch-")).toVector.sortBy(_.getFileName.toString) finally stream.close()
      files.flatMap { path =>
        val node=mapper.readTree(Files.readString(path,StandardCharsets.UTF_8))
        val text=node.get("data").asText()
        require(node.get("query_identity").asText()==identity && node.get("sha256").asText()==sha(text))
        text.linesIterator.filter(_.nonEmpty).toSeq
      }.sorted
    }
  }
  def runForeach(spark: SparkSession,input: Path,checkpoint: Path,sink: Path,identity: String,failBefore: Boolean): RunReceipt = {
    commitPath(sink,identity,0L)
    val binding=sink.resolve(identity+"-binding.txt")
    val expected=input.toAbsolutePath.normalize().toString+"\n"+checkpoint.toAbsolutePath.normalize().toString+"\nid:bigint,cents:bigint"
    if(Files.exists(binding)) require(Files.readString(binding,StandardCharsets.UTF_8)==expected,"Query namespace bound to another source/checkpoint/schema")
    else Files.writeString(binding,expected,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW)
    val frame=spark.readStream.schema(eventSchema).option("maxFilesPerTrigger",1).option("mode","FAILFAST").json(input.toString)
    val query=frame.writeStream.option("checkpointLocation",checkpoint.toString).trigger(Trigger.AvailableNow())
      .foreachBatch { (batch: DataFrame,batchId: Long) =>
        attempts += batchId
        batch.persist()
        try publishBatch(sink,identity,batchId,canonicalBatch(batch),failBefore)
        finally batch.unpersist()
        ()
      }.start()
    ownedQueries += query;startedQueries += ((query.id.toString,query.runId.toString))
    try {
      require(query.awaitTermination(45000L),"Finite foreachBatch deadline exceeded")
      require(query.exception.isEmpty)
      RunReceipt(query.id.toString,query.runId.toString,query.recentProgress.map(_.numInputRows).sum,query.recentProgress.map(_.batchId).toSeq)
    } finally { if(query.isActive) query.stop() }
  }

  def encodeBatch(frame: DataFrame): String =
    throw new UnsupportedOperationException("Complete encodeBatch")

  def publishOnce(root: Path,identity: String,batchId: Long,text: String): Boolean =
    throw new UnsupportedOperationException("Complete publishOnce")

  def failCallback(spark: SparkSession,input: Path,checkpoint: Path,sink: Path): Unit =
    throw new UnsupportedOperationException("Complete failCallback")

  def recoverCallback(spark: SparkSession,input: Path,checkpoint: Path,sink: Path): RunReceipt =
    throw new UnsupportedOperationException("Complete recoverCallback")

  def unsafeAppend(path: Path,text: String): Unit =
    throw new UnsupportedOperationException("Complete unsafeAppend")

  def rejectCollision(root: Path,text: String): Unit =
    throw new UnsupportedOperationException("Complete rejectCollision")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-036").master("local[2]")
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
      ownedRoot=Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),"spark-036-")
      val input=ownedRoot.resolve("input");val checkpoint=ownedRoot.resolve("checkpoint");val sink=Files.createDirectory(ownedRoot.resolve("sink"))
      publishFile(ownedRoot,input,"batch-01.json",Seq("""{"id":1,"cents":100}""","""{"id":2,"cents":200}"""))
      val staticFrame=spark.read.schema(eventSchema).json(input.toString)
      locally {
        val demo=spark.read.schema(eventSchema).json(input.toString)
        val text=canonicalBatch(demo)
        assert(text=="1,100\n2,200\n")
        assert(publishBatch(sink,"demo-v1",0L,text,false))
        assert(!publishBatch(sink,"demo-v1",0L,text,false))
      }
      locally {
        var failed=false
        try publishBatch(sink,"demo-failure",0L,"1,100\n",true) catch { case e: IllegalStateException if e.getMessage=="injected_before_publication" => failed=true }
        assert(failed && publishedRows(sink,"demo-failure").isEmpty)
      }
      println("spark-036: worked examples passed; six task implementations remain")
    } finally { try { ownedQueries.foreach(q => if(q.isActive) q.stop())
require(!ownedQueries.exists(_.isActive),"Do not remove scratch while an owned query is active")
if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Define canonical bounded microbatch content. Inputs/task: Validate the explicit bigint schema, nonnegative cents, positive IDs and at most 8 rows;return sorted id, cents newline records preserving multiplicity. Expected: Exact text 1,100 newline 2,200 newline, with a stable SHA256 after repartitioning. Verify: Compare exact bytes and reject NULL cents before publication.
// Exercise 2: Publish one logical batch idempotently. Inputs/task: Publish the same canonical content twice under identity manual-v1 and batch 7. Compare the existing receipt instead of appending. Expected: First call publishes true;second returns false;exactly 2 logical rows remain. Verify: Assert return values, unchanged receipt bytes and one batch file.
// Exercise 3: Inject a real callback failure before publication. Inputs/task: Run the actual foreachBatch query with failure after staging and before rename. Retain the wrapped streaming exception and attempted batch ID. Expected: The query fails with injected_before_publication;no stream-v1 batch is visible and the attempted batch ID is 0. Verify: Check the exception marker, empty published rows and inactive query.
// Exercise 4: Recover the same checkpoint and observe replay. Inputs/task: Restart the same source/checkpoint/query namespace without failure. Compare attempts and logical query/run IDs. Expected: Batch 0 is attempted again and publishes 2 rows once. Query ID persists;run ID changes. Verify: Assert attempt sequence 0,0, exact rows and corresponding identities.
// Exercise 5: Expose a non-idempotent append counterexample. Inputs/task: Append the same canonical batch text twice to a separate unsafe-demo file, then compare it with the idempotent published batch. Expected: Unsafe append has 4 row occurrences;the committed batch remains 2. Verify: Compare exact repeated lines and preserve the unsafe file as a separate diagnostic until owned cleanup.
// Exercise 6: Reject identity collisions and admit the next batch. Inputs/task: Reject different content under an existing batch key, then publish a new source file 3:300 and resume the real query. Expected: The conflicting key fails without replacing its receipt. Stream batch 1 adds one row, leaving IDs 1,2,3 and total 600 across two batch files. Verify: Assert collision rejection, old receipt equality, attempt sequence 0,0,1 and exact 3-row sink.
