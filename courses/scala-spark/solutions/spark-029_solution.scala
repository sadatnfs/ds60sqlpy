import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.UUID
import scala.jdk.CollectionConverters._
import com.fasterxml.jackson.databind.ObjectMapper

object Main {
  val mapper = new ObjectMapper()
  val schemaText = "id:bigint,value:bigint"
  def checkRunId(runId: String): Unit = require(runId.matches("[a-z0-9-]{1,32}"),"Invalid run ID")
  def receiptText(runId: String, digest: String): String = {
    val node = mapper.createObjectNode()
    node.put("run_id",runId);node.put("data_path","runs/"+runId+"/data");node.put("row_count",30)
    node.put("schema",schemaText);node.put("sha256",digest)
    node.toString
  }
  def deleteOwned(root: Path): Unit = {
    val paths = Files.walk(root)
    try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally paths.close()
  }
  def dataFileCount(root: Path): Int = {
    val paths = Files.walk(root)
    try paths.iterator().asScala.count(p => Files.isRegularFile(p) && p.getFileName.toString.endsWith(".parquet"))
    finally paths.close()
  }

  def productDigest(frame: DataFrame): String = {
    require(frame.schema.fields.toSeq.map(f => (f.name,f.dataType.simpleString)) == Seq(("id","bigint"),("value","bigint")),"Product schema mismatch")
    val metrics = frame.agg(count(lit(1)),countDistinct("id"),min("id"),max("id"),sum("value")).first()
    require(metrics.toSeq == Seq(30L,30L,0L,29L,870L),"Product population mismatch")
    require(frame.filter(col("id").isNull || col("value").isNull || col("value") =!= col("id")*2L).count() == 0L,"Product value mismatch")
    val canonical = frame.orderBy("id").toJSON.collect().mkString("\n")
    MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8)).map(b => f"${b & 0xff}%02x").mkString
  }

  def stageRun(spark: SparkSession, root: Path, runId: String, source: DataFrame): String = {
    checkRunId(runId)
    val digest = productDigest(source)
    val run = root.resolve("runs").resolve(runId)
    if(Files.exists(run)) {
     val existing = validateStaged(spark,root,runId)
     require(mapper.readTree(existing).get("sha256").asText() == digest,"Run identity has different content")
     existing
    } else {
     Files.createDirectory(run)
     source.write.mode("errorifexists").parquet(run.resolve("data").toString)
     require(productDigest(spark.read.parquet(run.resolve("data").toString)) == digest,"Staging readback mismatch")
     val text = receiptText(runId,digest)
     Files.writeString(run.resolve("receipt.json"),text,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW)
     text
    }
  }

  def validateStaged(spark: SparkSession, root: Path, runId: String): String = {
    checkRunId(runId)
    val run = root.resolve("runs").resolve(runId)
    val text = Files.readString(run.resolve("receipt.json"),StandardCharsets.UTF_8)
    val node = mapper.readTree(text)
    require(node.path("run_id").asText() == runId && node.path("data_path").asText() == "runs/"+runId+"/data","Receipt identity/path mismatch")
    require(node.path("row_count").asInt() == 30 && node.path("schema").asText() == schemaText,"Receipt schema/count mismatch")
    require(node.path("sha256").asText() == productDigest(spark.read.parquet(run.resolve("data").toString)),"Receipt content mismatch")
    text
  }

  def publishRun(spark: SparkSession, root: Path, runId: String, failBeforeReplace: Boolean): Unit = {
    val text = validateStaged(spark,root,runId)
    val pending = root.resolve("manifest-pending-"+UUID.randomUUID().toString+".json")
    try {
     Files.writeString(pending,text,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW)
     if(failBeforeReplace) throw new IllegalStateException("injected_before_publication")
     Files.move(pending,root.resolve("current.json"),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING)
    } finally Files.deleteIfExists(pending)
  }

  def readPublished(spark: SparkSession, root: Path): DataFrame = {
    val current = Files.readString(root.resolve("current.json"),StandardCharsets.UTF_8)
    val node = mapper.readTree(current)
    val runId = node.path("run_id").asText()
    val validated = validateStaged(spark,root,runId)
    require(mapper.readTree(validated) == node,"Published manifest differs from validated receipt")
    spark.read.parquet(root.resolve("runs").resolve(runId).resolve("data").toString)
  }

  def retryProduct(spark: SparkSession, root: Path, runId: String, source: DataFrame): String = {
    stageRun(spark,root,runId,source)
    publishRun(spark,root,runId,false)
    productDigest(readPublished(spark,root))
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-029").master("local[2]")
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
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-029-")
      Files.createDirectory(ownedRoot.resolve("runs"))
      val source = spark.range(0L,30L,1L,2).withColumn("value",col("id")*2L)
      // Exercise 1: Validate the product before computing its digest
      val digest = productDigest(source)
      assert(digest == "b4eaf827f5ce5797e0df60939b503b2ca6f264c0c167c9ca557db2aeb6cc2879" && productDigest(source.repartition(3)) == digest)
      var rejectedProduct = false
      try productDigest(spark.range(31L).withColumn("value",col("id")*2L)) catch { case _: IllegalArgumentException => rejectedProduct = true }
      assert(rejectedProduct)
      // Exercise 2: Stage a run and validate the persisted readback
      val stagedA = stageRun(spark,ownedRoot,"run-a",source)
      assert(Files.isRegularFile(ownedRoot.resolve("runs/run-a/receipt.json")))
      assert(mapper.readTree(stagedA).get("sha256").asText() == digest)
      // Exercise 3: Validate a receipt against a fixed owned data path
      assert(validateStaged(spark,ownedRoot,"run-a") == stagedA)
      var rejectedPath = false
      try validateStaged(spark,ownedRoot,"../outside") catch { case _: IllegalArgumentException => rejectedPath = true }
      assert(rejectedPath)
      // Exercise 4: Publish only a validated run at one explicit visibility point
      publishRun(spark,ownedRoot,"run-a",false)
      val publishedA = Files.readString(ownedRoot.resolve("current.json"),StandardCharsets.UTF_8)
      assert(publishedA == stagedA && mapper.readTree(publishedA).get("run_id").asText() == "run-a")
      // Exercise 5: Keep the previous publication readable after an interrupted replacement
      stageRun(spark,ownedRoot,"run-b",source)
      var failedPublication = false
      try publishRun(spark,ownedRoot,"run-b",true) catch { case e: IllegalStateException if e.getMessage == "injected_before_publication" => failedPublication = true }
      assert(failedPublication && Files.readString(ownedRoot.resolve("current.json"),StandardCharsets.UTF_8) == publishedA)
      assert(productDigest(readPublished(spark,ownedRoot)) == digest)
      // Exercise 6: Replay the same input without appending another product
      val filesBefore = dataFileCount(ownedRoot)
      assert(retryProduct(spark,ownedRoot,"run-a",source.repartition(3)) == digest)
      assert(dataFileCount(ownedRoot) == filesBefore && Files.readString(ownedRoot.resolve("current.json"),StandardCharsets.UTF_8) == publishedA)
      var invalidRetry = false
      try retryProduct(spark,ownedRoot,"run-c",spark.range(31L).withColumn("value",col("id")*2L)) catch { case _: IllegalArgumentException => invalidRetry = true }
      assert(invalidRetry && Files.readString(ownedRoot.resolve("current.json"),StandardCharsets.UTF_8) == publishedA)
      assert(readPublished(spark,ownedRoot).count() == 30L)
      println("spark-029: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Validate the product before computing its digest. Inputs/task: Require ordered fieldsid, value with bigint types, exactly 30 known unique IDs 0..29, known values equal to 2*id and total 870. ReturnSHA-256 of sorted SparkJSON lines joined by newline without a trailing newline. Expected: A64-character lowercase digest for the valid product. Wrong values, counts, types or identities are rejected before hashing. Verify: Assert a64-hex digest and equal digest after repartitioning;reject a31-row source.
// Exercise 2: Stage a run and validate the persisted readback. Inputs/task: Restrict run IDs to 1..32 lowercase letters, digits or hyphens. Validate input, write a fresh run-specific Parquet product, validate readback and save its receipt. If that run already exists, require its validated digest to match instead of appending. Expected: run-a has one 30-row data product and a receipt with the declared schema/count/path/digest. Reusing it never appends another product. Verify: Assert staged receipt existence and digest equality;all paths remain within the fresh owned root.
// Exercise 3: Validate a receipt against a fixed owned data path. Inputs/task: Read a run receipt and require its run_id, data_path, row_count, schema and digest to match the declared contract and actual Parquet readback. Construct the read path from validated runId rather than trusting arbitrary receipt text. Expected: Validrun-a receipt returns unchanged. A traversal-style run ID is rejected before path access. Verify: Assert receipt equality and explicit rejection of../outside.
// Exercise 4: Publish only a validated run at one explicit visibility point. Inputs/task: Validate the staged receipt, write it to a fresh temporary manifest beside current.json, and atomically replace current.json. Support an injected failure before replacement and clean any unpublished temporary manifest in finally. Expected: Publishingrun-a creates current.json selecting its 30-row product. No data is appended or rewritten during publication. Verify: Assert the current manifest equals the validated receipt and points torun-a.
// Exercise 5: Keep the previous publication readable after an interrupted replacement. Inputs/task: Read the current manifest, validate its selected run and return that product. Stage run-b, inject failure before its manifest replacement, and confirm the reader still seesrun-a. Expected: The injected error occurs, current.json bytes remain identical torun-a, and the published product still has 30 rows with the original digest. Verify: Assert the named exception, unchanged manifest and exact published product digest;run-b staging must not enter the reader population.
// Exercise 6: Replay the same input without appending another product. Inputs/task: Compose stage, validate/publish and readback for a repeated run ID. Retryrun-a with a different execution partition layout, then attempt an invalid 31-row product and confirm publication stays intact. Expected: Manifest bytes and data-file count are unchanged by validrun-a replay;published count remains 30. Invalid input fails before changing current.json. Verify: Assert digest, manifest bytes, file-count equality and negative-control rejection.
