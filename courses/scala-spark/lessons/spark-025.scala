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
  def sameBag(left: DataFrame, right: DataFrame): Boolean = {
    val columns = Seq("id", "day", "amount", "payload")
    val a = left.select(columns.map(col): _*); val b = right.select(columns.map(col): _*)
    a.exceptAll(b).count() == 0L && b.exceptAll(a).count() == 0L
  }

  def writeCompact(source: DataFrame, path: String): DataFrame =
    throw new UnsupportedOperationException("Complete writeCompact")

  def filteredProduct(frame: DataFrame): DataFrame =
    throw new UnsupportedOperationException("Complete filteredProduct")

  def scanEvidence(frame: DataFrame): Map[String, String] =
    throw new UnsupportedOperationException("Complete scanEvidence")

  def fileInventory(path: String): (Int, Long) =
    throw new UnsupportedOperationException("Complete fileInventory")

  def layoutReceipt(frame: DataFrame, path: String): (Int, Int, Int) =
    throw new UnsupportedOperationException("Complete layoutReceipt")

  def rejectExisting(source: DataFrame, path: String): Unit =
    throw new UnsupportedOperationException("Complete rejectExisting")

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-025")
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
        Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), ".ds60-spark-025-")
      val schema = StructType(
        Seq(
          StructField("id", LongType, false),
          StructField("day", StringType, false),
          StructField("amount", LongType, false),
          StructField("payload", StringType, false)
        )
      )
      val source = spark.createDataFrame(
        spark.sparkContext.parallelize(
          (0L until 2000L).map(id =>
            Row(
              id,
              if (id % 2L == 0L) "even" else "odd",
              id * 7L,
              "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            )
          ),
          4
        ),
        schema
      )
      val compactPath = ownedRoot.resolve("compact").toString
      val manyPath = ownedRoot.resolve("many").toString
      locally {
        assert(source.schema("id").dataType == LongType && source.count() == 2000L)
        assert(source.agg(sum("amount")).first().getLong(0) == 13993000L)
        println("Explicit-schema source:2000 rows,total13993000")
      }
      locally {
        val ids = (1990L until 2000L).filter(_ % 2L == 0L)
        assert(ids == Seq(1990L, 1992L, 1994L, 1996L, 1998L))
        println("Independent filtered identity oracle=" + ids)
      }
      println("spark-025: worked examples passed; six task implementations remain")
    } finally {
      try { if (ownedRoot != null) deleteOwned(ownedRoot) }
      finally { spark.stop() }
    }
  }
}

// Exercise 1: Write and validate a compact partitioned round trip. Inputs/task: Repartition source by day into 2 execution partitions, write Parquet with error-if-exists and partitionBy(day), then read it back. Compare field types and the complete duplicate-sensitive bag. Expected: 2000 rows and total 13993000 survive. Types remain id/amount bigints and day/payload strings;read nullability may differ. Verify: Assert type mapping and exceptAll emptiness in both directions, plus row count and amount total.
// Exercise 2: Read a narrow filtered projection with an independent oracle. Inputs/task: Select only id and amount for day=even and id>=1990. Return the five ordered tuples. Expected: (1990,13930),(1992,13944),(1994,13958),(1996,13972),(1998,13986). No payload column is requested. Verify: Assert every projected identity and amount and exact two-column output schema.
// Exercise 3: Locate partition, column and predicate evidence in the scan. Inputs/task: Capture a FORMATTED plan for the selected query on the owned Parquet view. Extract ReadSchema, PartitionFilters and PushedFilters lines and interpret each scope. Expected: ReadSchema has id and amount but not payload;PartitionFilters mentions day/even;PushedFilters includes the id lower bound. Verify: Assert the relevant field/predicate markers and retain the exact five-row output oracle;do not claim bytes skipped from the plan alone.
// Exercise 4: Compare a deliberately larger file count without changing data. Inputs/task: Write the same source after repartition 12 using the same day directory partitioning. Inventory only.parquet data files and their actual byte sizes for both layouts. Expected: Both round trips match the source bag. The many layout has more data files than compact;both byte totals are positive and below 32 MiB. Verify: Assert bag parity, file-count inequality and measured data-byte bounds. Ignore checksum and success-marker files in data counts.
// Exercise 5: Report storage partitions, files and scan partitions separately. Inputs/task: Return a receipt with the number of day= directories, the data-file count and the read DataFrame execution-partition count for each layout. Expected: Both layouts have 2 day directories. Data-file counts are the measured inventory values. Scan partitions are positive observed values and need not equal either other count. Verify: Assert two directory partitions and independent file-count consistency;print actual scan partition counts without imposing equality.
// Exercise 6: Reject an existing target and preserve its product. Inputs/task: Attempt a second error-if-exists write to the already owned compact path. Require the expected analysis error, then read the original product and reconcile its bag. Expected: The second write fails with an existing-path analysis exception;the original 2000-row product remains unchanged. Verify: Assert the exception and full original bag after the failed write. Do not delete or overwrite the target to make the retry succeed.
