import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files,Path,Paths}
import scala.jdk.CollectionConverters._

object Main {
  def deleteOwned(root: Path): Unit = {
    val paths = Files.walk(root)
    try paths.iterator().asScala.toSeq.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally paths.close()
  }
  def sameBag(left: DataFrame, right: DataFrame): Boolean = {
    val columns = Seq("id","day","amount","payload")
    val a = left.select(columns.map(col):_*);val b = right.select(columns.map(col):_*)
    a.exceptAll(b).count() == 0L && b.exceptAll(a).count() == 0L
  }

  def writeCompact(source: DataFrame, path: String): DataFrame = {
    source.repartition(2,col("day")).write.mode("errorifexists").partitionBy("day").parquet(path)
    source.sparkSession.read.parquet(path)
  }

  def filteredProduct(frame: DataFrame): DataFrame = {
    frame.filter(col("day") === "even" && col("id") >= 1990L).select("id","amount")
  }

  def scanEvidence(frame: DataFrame): Map[String,String] = {
    frame.createOrReplaceTempView("ds60_spark_025_read")
    val text = frame.sparkSession.sql("EXPLAIN FORMATTED SELECT id,amount FROM ds60_spark_025_read WHERE day='even' AND id>=1990").collect().map(_.getString(0)).mkString("\n")
    Seq("ReadSchema","PartitionFilters","PushedFilters").map(name => name -> text.linesIterator.filter(_.contains(name)).mkString("\n")).toMap
  }

  def fileInventory(path: String): (Int,Long) = {
    val stream = Files.walk(Paths.get(path))
    try {
     val files = stream.iterator().asScala.filter(p => Files.isRegularFile(p) && p.getFileName.toString.endsWith(".parquet")).toSeq
     (files.size,files.map(p => Files.size(p)).sum)
    } finally stream.close()
  }

  def layoutReceipt(frame: DataFrame, path: String): (Int,Int,Int) = {
    val stream = Files.list(Paths.get(path))
    val directories = try stream.iterator().asScala.count(p => Files.isDirectory(p) && p.getFileName.toString.startsWith("day=")) finally stream.close()
    (directories,fileInventory(path)._1,frame.rdd.getNumPartitions)
  }

  def rejectExisting(source: DataFrame, path: String): Unit = {
    var rejected = false
    try source.write.mode("errorifexists").parquet(path) catch { case _: org.apache.spark.sql.AnalysisException => rejected = true }
    require(rejected,"Existing path unexpectedly accepted")
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession.builder().appName("ds60-spark-025").master("local[2]")
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
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-025-")
      val schema = StructType(Seq(StructField("id",LongType,false),StructField("day",StringType,false),StructField("amount",LongType,false),StructField("payload",StringType,false)))
      val source = spark.createDataFrame(spark.sparkContext.parallelize((0L until 2000L).map(id => Row(id,if(id%2L==0L) "even" else "odd",id*7L,"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")),4),schema)
      val compactPath = ownedRoot.resolve("compact").toString
      val manyPath = ownedRoot.resolve("many").toString
      // Exercise 1: Write and validate a compact partitioned round trip
      val compact = writeCompact(source,compactPath)
      assert(sameBag(source,compact) && compact.count() == 2000L)
      assert(compact.schema.fields.map(f => f.name->f.dataType.typeName).toMap == Map("id"->"long","day"->"string","amount"->"long","payload"->"string"))
      assert(compact.agg(sum("amount")).first().getLong(0) == 13993000L)
      // Exercise 2: Read a narrow filtered projection with an independent oracle
      val selected = filteredProduct(compact)
      assert(selected.columns.toSeq == Seq("id","amount"))
      assert(selected.orderBy("id").collect().toSeq.map(r => (r.getLong(0),r.getLong(1))) == Seq(1990L,1992L,1994L,1996L,1998L).map(id => (id,id*7L)))
      // Exercise 3: Locate partition, column and predicate evidence in the scan
      val evidence = scanEvidence(compact)
      assert(evidence("ReadSchema").contains("id:bigint") && evidence("ReadSchema").contains("amount:bigint") && !evidence("ReadSchema").contains("payload"))
      assert(evidence("PartitionFilters").contains("day") && evidence("PartitionFilters").contains("even"))
      assert(evidence("PushedFilters").contains("GreaterThanOrEqual(id,1990)"))
      println(evidence)
      // Exercise 4: Compare a deliberately larger file count without changing data
      source.repartition(12).write.mode("errorifexists").partitionBy("day").parquet(manyPath)
      val many = spark.read.parquet(manyPath)
      assert(sameBag(source,many))
      val compactFiles = fileInventory(compactPath);val manyFiles = fileInventory(manyPath)
      assert(compactFiles._1 > 0 && manyFiles._1 > compactFiles._1)
      assert(compactFiles._2 > 0L && manyFiles._2 > 0L && compactFiles._2 + manyFiles._2 < 32L*1024L*1024L)
      println("compact_data_files_bytes=" + compactFiles + ";many_data_files_bytes=" + manyFiles)
      // Exercise 5: Report storage partitions, files and scan partitions separately
      val compactReceipt = layoutReceipt(compact,compactPath);val manyReceipt = layoutReceipt(many,manyPath)
      assert(compactReceipt._1 == 2 && manyReceipt._1 == 2 && compactReceipt._2 == compactFiles._1 && manyReceipt._2 == manyFiles._1)
      assert(compactReceipt._3 > 0 && manyReceipt._3 > 0)
      println("layout_directory_file_scan_counts=" + Seq(compactReceipt,manyReceipt))
      // Exercise 6: Reject an existing target and preserve its product
      rejectExisting(source,compactPath)
      assert(sameBag(source,spark.read.parquet(compactPath)))
      println("spark-025: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { try { if(ownedRoot != null) deleteOwned(ownedRoot) } finally { spark.stop() } }
  }
}

// Exercise 1: Write and validate a compact partitioned round trip. Inputs/task: Repartition source by day into 2 execution partitions, write Parquet with error-if-exists and partitionBy(day), then read it back. Compare field types and the complete duplicate-sensitive bag. Expected: 2000 rows and total 13993000 survive. Types remain id/amount bigints and day/payload strings;read nullability may differ. Verify: Assert type mapping and exceptAll emptiness in both directions, plus row count and amount total.
// Exercise 2: Read a narrow filtered projection with an independent oracle. Inputs/task: Select only id and amount for day=even and id>=1990. Return the five ordered tuples. Expected: (1990,13930),(1992,13944),(1994,13958),(1996,13972),(1998,13986). No payload column is requested. Verify: Assert every projected identity and amount and exact two-column output schema.
// Exercise 3: Locate partition, column and predicate evidence in the scan. Inputs/task: Capture a FORMATTED plan for the selected query on the owned Parquet view. Extract ReadSchema, PartitionFilters and PushedFilters lines and interpret each scope. Expected: ReadSchema has id and amount but not payload;PartitionFilters mentions day/even;PushedFilters includes the id lower bound. Verify: Assert the relevant field/predicate markers and retain the exact five-row output oracle;do not claim bytes skipped from the plan alone.
// Exercise 4: Compare a deliberately larger file count without changing data. Inputs/task: Write the same source after repartition 12 using the same day directory partitioning. Inventory only.parquet data files and their actual byte sizes for both layouts. Expected: Both round trips match the source bag. The many layout has more data files than compact;both byte totals are positive and below 32 MiB. Verify: Assert bag parity, file-count inequality and measured data-byte bounds. Ignore checksum and success-marker files in data counts.
// Exercise 5: Report storage partitions, files and scan partitions separately. Inputs/task: Return a receipt with the number of day= directories, the data-file count and the read DataFrame execution-partition count for each layout. Expected: Both layouts have 2 day directories. Data-file counts are the measured inventory values. Scan partitions are positive observed values and need not equal either other count. Verify: Assert two directory partitions and independent file-count consistency;print actual scan partition counts without imposing equality.
// Exercise 6: Reject an existing target and preserve its product. Inputs/task: Attempt a second error-if-exists write to the already owned compact path. Require the expected analysis error, then read the original product and reconcile its bag. Expected: The second write fails with an existing-path analysis exception;the original 2000-row product remains unchanged. Verify: Assert the exception and full original bag after the failed write. Do not delete or overwrite the target to make the retry succeed.
