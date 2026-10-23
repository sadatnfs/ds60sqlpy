import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.{StreamingQuery,Trigger}
import java.nio.file.{Files,Path,Paths,StandardOpenOption,StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import com.fasterxml.jackson.databind.ObjectMapper

object Main {
  val eventSchema = StructType(Seq(StructField("id",LongType,true),StructField("team",StringType,true),StructField("amount",LongType,true)))
  def deleteOwned(root: Path): Unit = {
    val paths = Files.walk(root)
    try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally paths.close()
  }

  def publishFile(root: Path, name: String, lines: Seq[String]): Unit =
    throw new UnsupportedOperationException("Complete publishFile")

  def inputStream(spark: SparkSession, root: Path): DataFrame =
    throw new UnsupportedOperationException("Complete inputStream")

  def teamSummary(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete teamSummary")

  def runAvailable(summary: DataFrame, checkpoint: Path, table: String): StreamingQuery =
    throw new UnsupportedOperationException("Complete runAvailable")

  def inputProgress(query: StreamingQuery): Seq[(Long,Long)] =
    throw new UnsupportedOperationException("Complete inputProgress")

  def summaryRows(frame: DataFrame): Seq[(String,Long,Long,Long)] =
    throw new UnsupportedOperationException("Complete summaryRows")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    var ownedTable: String = null
    val spark = SparkSession.builder().appName("ds60-spark-031").master("local[2]")
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
      spark.conf.set("spark.sql.streaming.stopTimeout","10000")
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-031-")
      Files.createDirectory(ownedRoot.resolve("input"));Files.createDirectory(ownedRoot.resolve("staging"))
      ownedTable = "ds60_s031_" + UUID.randomUUID().toString.replace("-","")
      val batches = Seq(
       Seq("""{"id":1,"team":"A","amount":10}""","""{"id":2,"team":"B","amount":20}""","""{"id":3,"team":"A","amount":0}"""),
       Seq("""{"id":4,"team":"B","amount":null}""","""{"id":5,"team":"C","amount":30}""","""{"id":6,"team":"A","amount":5}"""),
       Seq("""{"id":7,"team":"C","amount":0}""","""{"id":8,"team":"B","amount":15}""","""{"id":9,"team":"A","amount":null}"""))
      locally {
        assert(batches.map(_.size) == Seq(3,3,3) && batches.flatten.size == 9)
        println("Three complete fixture files will contain exactly nine records")
      }
      locally {
        val mapper = new ObjectMapper()
        val amounts = batches.flatten.map(line => mapper.readTree(line).get("amount")).filterNot(_.isNull).map(_.asLong())
        assert(amounts.size == 7 && amounts.sum == 80L)
        println("Independent known-count/amount oracle=7/80")
      }
      println("spark-031: worked examples passed; six task implementations remain")
    } finally { try { require(!spark.streams.active.exists(q => q.name == ownedTable),"Owned query still active; preserve scratch"); if(ownedTable != null) spark.catalog.dropTempView(ownedTable); if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Publish complete input files atomically. Inputs/task: Write each declared file in the owned staging directory, then atomically move it into input under a new batch-N.json name. Reject invalid names or an existing destination. Expected: Three input files, each with 3 completeJSON records;no staging temporary file remains. Reusing batch-0.json is rejected. Verify: Assert the file count and explicit existing-name rejection before starting any query.
// Exercise 2: Construct an explicit streaming relation without starting it. Inputs/task: Read the owned JSON input through readStream with the declared schema and maxFilesPerTrigger 1. Return the streamingDataFrame;do not call an ordinary batch collect on it. Expected: isStreaming istrue, columns areid, team, amount and their types arebigint, string, bigint. No query is started by construction alone. Verify: Assert streaming status and exact type mapping while the active query list remains empty.
// Exercise 3: Define a cumulative aggregate with separate completeness counts. Inputs/task: Group by team and compute row_count, known_amounts and total_amount. Use the same expression for streaming and batch relations without filling unknown amounts. Expected: The streaming result remains streaming and has one state/result row per team. Its eventual literal result isA(4,3,15), B(3,2,35), C(2,2,30). Verify: Assert output columns and streaming status now;verify the exact final tuples after bounded execution.
// Exercise 4: Run AvailableNow with a deadline and owned cleanup. Inputs/task: Start the aggregate in a uniquely named memory sink with complete mode, a fresh checkpoint and AvailableNow. Await at most 30 seconds, require termination and always stop the query in finally. Expected: The query terminates and isActive isfalse. The memory table holds the final finite aggregate;the checkpoint belongs only to this run. Verify: Assert bounded await success, no query exception and inactive state. No sleep or external producer is used.
// Exercise 5: Reconcile processed input through progress evidence. Inputs/task: Return(batch_id, num_input_rows) from retained query progress. Sum input rows and inspect positive-input batches without confusing cumulative sink snapshots with new input. Expected: Three positive-input batches of 3 records and total input 9. Any zero-input progress entry contributes zero to that total. Verify: Assert total 9, three positive batches of 3 and unique recorded batch IDs;print the actual ledger.
// Exercise 6: Compare final streaming output with batch and literal oracles. Inputs/task: Read the final memory table, compare its ordered summary tuples with a batch read of the same nine source records, and compare both with the literalA/B/C oracle. Expected: ExactlyA(4,3,15), B(3,2,35), C(2,2,30), whose record counts sum 9, known counts 7 and amounts 80. Verify: Assert both path comparisons and the independent literal tuple list;confirm no active query remains before cleanup.
