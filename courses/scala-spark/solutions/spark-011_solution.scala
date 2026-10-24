import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._


object Main {
  def ids(frame: DataFrame): Seq[Long] =
    frame.select("event_id").orderBy("event_id").collect().map(_.getLong(0)).toSeq

  def aboveTen(): Column = {
    col("amount_cents") > lit(10L)
  }

  def selectedIds(frame: DataFrame): Seq[Long] = {
    ids(frame.filter(aboveTen()))
  }

  def missingIds(frame: DataFrame): Seq[Long] = {
    ids(frame.filter(col("amount_cents").isNull))
  }

  def combinedIds(frame: DataFrame): Seq[Long] = {
    ids(frame.filter(col("amount_cents").isNotNull && (col("amount_cents") >= lit(10L)) && (col("event_id") < lit(4L))))
  }

  def projected(frame: DataFrame): DataFrame = {
    frame.select(col("event_id"),(col("amount_cents") + lit(1L)).as("amount_plus_one"))
  }

  def sqlIds(spark: SparkSession, frame: DataFrame): Seq[Long] = {
    frame.createOrReplaceTempView("ds60_spark_011_events")
    ids(spark.sql("SELECT event_id FROM ds60_spark_011_events WHERE amount_cents > 10 ORDER BY event_id"))
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-011").master("local[2]")
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
      val schema = StructType(Seq(
        StructField("event_id",LongType,false),
        StructField("amount_cents",LongType,true)))
      val rows = Seq(Row(1L,0L),Row(2L,20L),Row(3L,null),Row(4L,20L))
      val raw = spark.createDataFrame(spark.sparkContext.parallelize(rows,2),schema)
      // Exercise 1: Construct a predicate without collapsing it to a driver Boolean
      assert(ids(raw.filter(aboveTen())) == Seq(2L,4L))
      // Exercise 2: Apply the predicate and preserve event identity
      assert(selectedIds(raw) == Seq(2L,4L))
      assert(ids(raw) == Seq(1L,2L,3L,4L))
      // Exercise 3: Select missingness explicitly
      assert(missingIds(raw) == Seq(3L))
      assert(ids(raw.filter(col("amount_cents") === lit(0L))) == Seq(1L))
      // Exercise 4: Combine conditions with engine operators
      assert(combinedIds(raw) == Seq(2L))
      // Exercise 5: Preserve NULL through a derived column
      val projectedRows = projected(raw).orderBy("event_id").collect().toSeq.map(row => (row.getLong(0),if (row.isNullAt(1)) None else Some(row.getLong(1))))
      assert(projectedRows == Seq((1L,Some(1L)),(2L,Some(21L)),(3L,None),(4L,Some(21L))))
      // Exercise 6: Compare SQL and Columns with an independent expectation
      assert(sqlIds(spark,raw) == Seq(2L,4L))
      assert(selectedIds(raw) == Seq(2L,4L))
      println("spark-011: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString)
    } finally { spark.stop() }
  }
}

// Exercise 1: Construct a predicate without collapsing it to a driver Boolean. Inputs/task: Implement aboveTen/above_ten returning a Spark Column for amount_cents>10. Do not collect values or return a Python/Scala scalar Boolean. Expected: Passing the predicate to raw.filter retains IDs 2 and 4. In Python, bool(predicate) raises ValueError rather than choosing one row's truth value. Verify: Assert the exact filtered IDs and, in the PySpark reference, catch the scalar-Boolean conversion failure.
// Exercise 2: Apply the predicate and preserve event identity. Inputs/task: Return the ordered event IDs selected by aboveTen from this tiny fixture. Preserve both equal-valued 20-cent events and leave raw unchanged. Expected: The result is[2,4], and raw still contains IDs[1,2,3,4]. Projecting amount and calling distinct is not an acceptable implementation. Verify: Compare the selected IDs with literals and independently check all four raw IDs.
// Exercise 3: Select missingness explicitly. Inputs/task: Return ordered IDs whose amount_cents is SQL NULL. Do not compare the Column to JVM null/Python None using driver identity logic, and do not treat zero as missing. Expected: Only ID 3 is returned. The observed-zero ID 1 is absent from the missingness result. Verify: Assert[3] and separately assert that the zero-amount filter returns [1].
// Exercise 4: Combine conditions with engine operators. Inputs/task: Return ordered IDs with a known amount at least 10 and event_id less than 4. Combine parenthesized Column comparisons with engine Boolean operators in each language. Expected: Only ID 2 qualifies. ID 4 fails the ID bound, ID 3 is missing, and ID 1 is below the amount threshold. Verify: Assert the exact singleton and explain one exclusion reason for each other ID.
// Exercise 5: Preserve NULL through a derived column. Inputs/task: Return a DataFrame with event_id and amount_plus_one=amount_cents+1, without filling NULL or dropping identity. Keep a Long-compatible integer result. Expected: Ordered rows are(1,1),(2,21),(3, NULL),(4,21). The two 21 values remain separate events and unknown remains unknown. Verify: Compare every ordered row with literal expected values, including the NULL position.
// Exercise 6: Compare SQL and Columns with an independent expectation. Inputs/task: Register a session-local temporary view and return ordered IDs from SQL SELECT/WHERE amount_cents>10. Compare SQL and DataFrame paths to the literal expected IDs rather than only to one another. Expected: Both paths return [2,4]. The temporary view exists only in this owned session and no external database connection is opened. Verify: Assert SQL IDs and selectedIds against [2,4] independently, then let the complete program stop its session in finally.
