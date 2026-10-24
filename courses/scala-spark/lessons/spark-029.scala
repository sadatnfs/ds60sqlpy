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

  def productDigest(frame: DataFrame): String =
    throw new UnsupportedOperationException("Complete productDigest")

  def stageRun(spark: SparkSession, root: Path, runId: String, source: DataFrame): String =
    throw new UnsupportedOperationException("Complete stageRun")

  def validateStaged(spark: SparkSession, root: Path, runId: String): String =
    throw new UnsupportedOperationException("Complete validateStaged")

  def publishRun(spark: SparkSession, root: Path, runId: String, failBeforeReplace: Boolean): Unit =
    throw new UnsupportedOperationException("Complete publishRun")

  def readPublished(spark: SparkSession, root: Path): DataFrame =
    throw new UnsupportedOperationException("Complete readPublished")

  def retryProduct(spark: SparkSession, root: Path, runId: String, source: DataFrame): String =
    throw new UnsupportedOperationException("Complete retryProduct")

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
      locally {
        val ids = 0L until 30L
        assert(ids.map(_*2L).sum == 870L)
        println("Declared30-row product total=870")
      }
      locally {
        val a = receiptText("run-a","0"*64);val b = receiptText("run-b","0"*64)
        assert(mapper.readTree(a).get("data_path").asText() == "runs/run-a/data")
        assert(a != b)
        println("A publication points to one run-specific product")
      }
      println("spark-029: worked examples passed; six task implementations remain")
    } finally { try { if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Validate the product before computing its digest. Inputs/task: Require ordered fieldsid, value with bigint types, exactly 30 known unique IDs 0..29, known values equal to 2*id and total 870. ReturnSHA-256 of sorted SparkJSON lines joined by newline without a trailing newline. Expected: A64-character lowercase digest for the valid product. Wrong values, counts, types or identities are rejected before hashing. Verify: Assert a64-hex digest and equal digest after repartitioning;reject a31-row source.
// Exercise 2: Stage a run and validate the persisted readback. Inputs/task: Restrict run IDs to 1..32 lowercase letters, digits or hyphens. Validate input, write a fresh run-specific Parquet product, validate readback and save its receipt. If that run already exists, require its validated digest to match instead of appending. Expected: run-a has one 30-row data product and a receipt with the declared schema/count/path/digest. Reusing it never appends another product. Verify: Assert staged receipt existence and digest equality;all paths remain within the fresh owned root.
// Exercise 3: Validate a receipt against a fixed owned data path. Inputs/task: Read a run receipt and require its run_id, data_path, row_count, schema and digest to match the declared contract and actual Parquet readback. Construct the read path from validated runId rather than trusting arbitrary receipt text. Expected: Validrun-a receipt returns unchanged. A traversal-style run ID is rejected before path access. Verify: Assert receipt equality and explicit rejection of../outside.
// Exercise 4: Publish only a validated run at one explicit visibility point. Inputs/task: Validate the staged receipt, write it to a fresh temporary manifest beside current.json, and atomically replace current.json. Support an injected failure before replacement and clean any unpublished temporary manifest in finally. Expected: Publishingrun-a creates current.json selecting its 30-row product. No data is appended or rewritten during publication. Verify: Assert the current manifest equals the validated receipt and points torun-a.
// Exercise 5: Keep the previous publication readable after an interrupted replacement. Inputs/task: Read the current manifest, validate its selected run and return that product. Stage run-b, inject failure before its manifest replacement, and confirm the reader still seesrun-a. Expected: The injected error occurs, current.json bytes remain identical torun-a, and the published product still has 30 rows with the original digest. Verify: Assert the named exception, unchanged manifest and exact published product digest;run-b staging must not enter the reader population.
// Exercise 6: Replay the same input without appending another product. Inputs/task: Compose stage, validate/publish and readback for a repeated run ID. Retryrun-a with a different execution partition layout, then attempt an invalid 31-row product and confirm publication stays intact. Expected: Manifest bytes and data-file count are unchanged by validrun-a replay;published count remains 30. Invalid input fails before changing current.json. Verify: Assert digest, manifest bytes, file-count equality and negative-control rejection.
