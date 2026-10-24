import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files, Path, Paths}
import scala.jdk.CollectionConverters._

object Main {
  def deleteOwned(root: Path): Unit = {
    val paths = Files.walk(root)
    try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally paths.close()
  }

  def projectionResult(spark: SparkSession, query: String): Seq[(Long, Long)] =
    throw new UnsupportedOperationException("Complete projectionResult")

  def explainText(spark: SparkSession, query: String, mode: String): String =
    throw new UnsupportedOperationException("Complete explainText")

  def readSchemaEvidence(formatted: String): String =
    throw new UnsupportedOperationException("Complete readSchemaEvidence")

  def aggregateResult(spark: SparkSession, query: String): Seq[(Long, Long, Long)] =
    throw new UnsupportedOperationException("Complete aggregateResult")

  def normalizeEvidence(plan: String, root: String): String =
    throw new UnsupportedOperationException("Complete normalizeEvidence")

  def configurationReceipt(spark: SparkSession): Map[String, String] =
    throw new UnsupportedOperationException("Complete configurationReceipt")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-021")
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
      ownedRoot =
        Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-021-")
      val fixture = spark
        .range(0L, 12L, 1L, 2)
        .withColumn("group_id", col("id") % 3L)
        .withColumn("amount", col("id") * 10L)
        .withColumn("unused_payload", lit("xxxxxxxxxxxxxxxx"))
      val dataPath = ownedRoot.resolve("data").toString
      fixture.write.mode("errorifexists").parquet(dataPath)
      val input = spark.read.parquet(dataPath)
      input.createOrReplaceTempView("ds60_spark_021_input")
      val projectionQuery =
        "SELECT id,amount*2 AS doubled FROM ds60_spark_021_input WHERE amount>=30"
      val aggregateQuery =
        "SELECT group_id,COUNT(*) AS n,SUM(amount) AS total FROM ds60_spark_021_input WHERE amount>=30 GROUP BY group_id"
      locally {
        assert(input.count() == 12L)
        assert(input.columns.toSeq == Seq("id", "group_id", "amount", "unused_payload"))
        println("Owned Parquet fixture has four stored columns and12 rows")
      }
      locally {
        val rows = spark.sql(projectionQuery).orderBy("id").collect()
        assert(rows.length == 9 && rows.head.getLong(0) == 3L && rows.last.getLong(0) == 11L)
        spark.sql("EXPLAIN FORMATTED " + projectionQuery).show(false)
      }
      println("spark-021: worked examples passed; six task implementations remain")
    } finally {
      try { if (ownedRoot != null) deleteOwned(ownedRoot) }
      finally { spark.stop() }
    }
  }
}

// Exercise 1: Check the query meaning before its execution plan. Inputs/task: Execute the projection query and return ordered(id, doubled) tuples. Compare all nine rows with the literal rule id 3..11, doubled=20*id. Expected: Nine tuples from(3,60) through(11,220), with no missing or extra identities. Verify: Assert the complete tuple list, not only the first/last rows or a printed plan.
// Exercise 2: Capture each extended planning stage. Inputs/task: Return EXPLAIN EXTENDED text for the supplied query. Permit only EXTENDED or FORMATTED as the mode and reject another mode. Expected: Text includes Parsed Logical Plan, Analyzed Logical Plan, Optimized Logical Plan and Physical Plan sections. An invalid mode is rejected. Verify: Assert all four section labels and an explicit invalid-mode exception.
// Exercise 3: Inspect the scan scope for column pruning. Inputs/task: Capture FORMATTED output and extract lines containing ReadSchema. Verify that the projection scan requests id and amount but not group_id or unused_payload. Also locate Filter and Project operators. Expected: ReadSchema includes id:bigint and amount:bigint only among the four stored fields. Filter and Project evidence are present. Verify: Assert needed/excluded fields in the extracted scan lines rather than in the entire extended plan.
// Exercise 4: Connect grouped output to a redistribution boundary. Inputs/task: Execute the grouped aggregate and capture its FORMATTED plan. Return group_id, n, total and locate aggregate plus Exchange operators under the fixed AQE-disabled configuration. Expected: Groups 0,1,2 each have n3 with totals 180,210,240. The plan shows aggregation and an Exchange. Verify: Assert all group tuples independently, then assert the relevant operator markers and recorded AQE setting.
// Exercise 5: Normalize incidental identifiers without erasing semantics. Inputs/task: Replace expression-number suffixes such as#123 with#ID and the exact owned root path with<owned-root> in plan text. Preserve operators, field names, predicates and partitioning descriptions. Expected: A synthetic Project id#123L becomes Project id#IDL;the current temporary root is absent from normalized actual plan text. Verify: Assert the synthetic replacement and required semantic tokens after normalizing the actual plan.
// Exercise 6: Compare equivalent query forms with separate semantic and plan evidence. Inputs/task: Execute a nested projection/filter form of the direct query and compare its exact rows. Capture its extended plan and return a bounded receipt containing Spark version, ANSI, AQE and shuffle partition settings. Expected: The nested query has the same nine tuples. Receipt shows Spark 4.0.1, ANSItrue, AQEfalse, shuffle partitions 2. Both extended plans expose an optimized stage. Verify: Assert full output parity with the literal oracle and exact controlled settings;do not assert whole-plan byte equality or faster execution.
